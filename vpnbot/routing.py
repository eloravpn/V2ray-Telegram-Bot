import json
import traceback
import uuid as UUID
from email.utils import parseaddr

import emoji
from hurry.filesize import size
from logzero import logger as log
from prettytable import PrettyTable
from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

from vpnbot import appglobals, captions, messages, util
from vpnbot.const import CallbackActions
from vpnbot.models import User, Account
from vpnbot.xui import get_all_client_infos, get_client_infos, get_client


def callback_router(update: Update, context: CallbackContext) -> int:
    obj = json.loads(str(update.callback_query.data))
    user = update.effective_user

    try:
        if "a" in obj:
            action = obj["a"]

            # BOTLISTCHAT
            if action == CallbackActions.REGISTER:
                register(update=update, context=context)

            log.info('Action: ' + str(action))

    except Exception as e:
        traceback.print_exc()

        # get the callback action in plaintext
        actions = dict(CallbackActions.__dict__)
        a = next(k for k, v in actions.items() if v == obj.get("a"))
        log.error('Action: ' + util.escape_markdown(a))
        log.error(e)

    finally:
        context.bot.answerCallbackQuery(update.callback_query.id)
        return ConversationHandler.END


def reply_router(update: Update, context: CallbackContext):
    text = update.effective_message.reply_to_message.text

    query = update.message.text

    log.debug(text)
    log.debug(query)


def ban_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Ban?",
        reply_markup=ForceReply(selective=True),
    )


def register(update: Update, context: CallbackContext):
    message = update.callback_query.message
    bot = context.bot
    user = User.from_update(update)

    log.info('You talk with user: ' + user.markdown_short)
    log.debug("Chat ID: {} ".format(user.chat_id))

    bot.sendMessage(chat_id=appglobals.ADMIN_CHAT_ID,
                    text=messages.REGISTER_ADMIN_ALERT.format(user.markdown_short,
                                                              user.chat_id),
                    disable_web_page_preview=True)

    message.reply_text(text=messages.REGIATER_SUCCESS,
                       parse_mode='HTML', timeout=60)


def start(update: Update, context: CallbackContext):
    user = User.from_update(update)

    keyboard = [
        [InlineKeyboardButton(emoji.emojize(':eight-spoked_asterisk: ') +
                              captions.REGISTER,
                              callback_data=util.callback_for_action(CallbackActions.REGISTER, None))]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_markdown(text=messages.WELCOME_MESSAGE.format(user.plaintext, appglobals.ADMIN_USER_NAME),

                                  disable_web_page_preview=True, reply_markup=reply_markup)


def add_user(update: Update, context: CallbackContext):
    only_admin(update.message, update, context)

    try:
        chat_id = int(context.args[0])
        uuid = str(context.args[1])
        email = str(context.args[2])

        user = User.by_chat_id(chat_id)
        UUID.UUID(uuid)
        # validate_email_address(email)

        account = Account(user=User.by_chat_id(chat_id), email=email,
                          uuid=uuid)
        account.save()

        update.message.reply_text('A new account is created for ' + user.markdown_short)
    except Exception as e:
        traceback.print_exc()
        update.message.reply_text('An Exception occurred: ' + str(e))


def get_accounts_info(update: Update, context: CallbackContext):
    only_admin(update.message, update, context)

    bot = context.bot

    limit = int(context.args[0]) if len(context.args) > 0 else 0
    offset = int(context.args[1]) if len(context.args) > 1 else 20

    log.info(f"Get Accounts Limit {limit} from {offset}")

    x = PrettyTable()
    client_list = get_all_client_infos(limit, offset)
    x.field_names = ["Chat ID", "UUID", "User", "Email", "UP", "Down", "Total", "Expire"]

    for client in client_list:
        try:
            account = Account.by_email(client['email'])
            user = account.user
            x.add_row([user.chat_id, account.uuid, user.plaintext, client['email'], size(client['up']),
                       size(client['down']), size(client['total']), client['expiry_time']])

        except Account.DoesNotExist:
            inbound_client = get_client(appglobals.V2RAY_INBOUND_ID, client['email'])
            if inbound_client:
                x.add_row(["0", inbound_client['id'], "No User", client['email'],
                           size(client['up']), size(client['down']), size(client['total']),
                           client['expiry_time']])
            log.error("Account does not exist with email: " + client['email'])

    log.info(x)

    bot.sendMessage(chat_id=appglobals.ADMIN_CHAT_ID,
                    text=f'<pre>{x}</pre>', parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True)


def get_my_accounts_info(update: Update, context: CallbackContext):
    user = User.from_update(update)

    x = PrettyTable()
    accounts = Account.select().where(Account.user == user)

    x.field_names = ["Chat ID", "User", "Email", "UP", "Down", "Total"]

    for account in accounts:
        client_info = get_client_infos(account.email)[0]
        log.info(client_info)
        update.message.reply_text(text=messages.MY_ACCOUNT_MESSAGE.format('Active',
                                                                          account.uuid,
                                                                          size(client_info['up']),
                                                                          size(client_info['down']),
                                                                          size(client_info['total']),
                                                                          client_info['expiry_time'],
                                                                          appglobals.V2RAY_SUB_URL, account.uuid),
                                  parse_mode='HTML', timeout=60)


def get_users(update: Update, context: CallbackContext):
    only_admin(update.message, update, context)

    page = int(context.args[0]) if len(context.args) > 0 else 0
    paginate_by = int(context.args[1]) if len(context.args) > 1 else 20

    log.info(f"Get users Page {page} by {paginate_by}")

    bot = context.bot

    x = PrettyTable()
    x.field_names = ["Chat ID", "User", "Accounts", "User Name"]

    for user in User.select().paginate(page, paginate_by):
        account_count = Account.select().where(Account.user == user).count()
        x.add_row([user.chat_id, user.markdown_short, account_count, user.username])

    log.info(x)

    bot.sendMessage(chat_id=appglobals.ADMIN_CHAT_ID,
                    text=f'<pre>{x}</pre>', parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True)


def only_admin(message, update: Update, context: CallbackContext):
    if not is_admin(update):
        message.reply_text(
            text="This function is restricted to the channel creator.")
        raise Exception("Try to access admin console!")


def is_admin(update: Update):
    return bool(User.from_update(update).chat_id == int(appglobals.ADMIN_CHAT_ID))


def validate_email_address(email_address):
    if '@' not in parseaddr(email_address)[1]:
        raise Exception("Email Address is not valid!")

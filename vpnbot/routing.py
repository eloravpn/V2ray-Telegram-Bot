import json
import traceback
import uuid as UUID
from email.utils import parseaddr

import emoji
from hurry.filesize import size
from logzero import logger as log
from prettytable import PrettyTable
from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardRemove
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

from vpnbot import appglobals, captions, messages, util, mdformat
from vpnbot.const import CallbackActions
from vpnbot.models import User, Account
from vpnbot.report import get_top_accounts_usage
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
            elif action == CallbackActions.GET_USERS:
                get_users(update=update, context=context)
            elif action == CallbackActions.GET_ACCOUNTS:
                get_accounts_info(update=update, context=context)

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


def main_menu(update: Update, context: CallbackContext):
    only_admin(update.message, update, context)

    bot = context.bot
    # chat_id = User.from_update(update).chat_id

    admin = is_admin(update)
    reply_markup = (
        ReplyKeyboardMarkup(
            main_menu_buttons(admin), resize_keyboard=True, one_time_keyboard=True
        )
        if util.is_private_message(update)
        else ReplyKeyboardRemove()
    )

    bot.sendMessage(
        appglobals.ADMIN_CHAT_ID,
        mdformat.action_hint("What would you like to do?"),
        reply_markup=reply_markup,
    )


def main_menu_buttons(admin=False):
    buttons = [
        # [
        #     KeyboardButton(captions.CATEGORIES),
        #     KeyboardButton(captions.EXPLORE),
        #     KeyboardButton(captions.FAVORITES),
        # ],
        # [KeyboardButton(captions.SEARCH)],
        [KeyboardButton(captions.HELP)],
        [KeyboardButton(captions.EXIT)],
    ]
    if admin:
        buttons.insert(1, [KeyboardButton(captions.ADMIN_MENU)])
    return buttons


def admin_menu(update: Update, context: CallbackContext):
    only_admin(update.message, update, context)

    uid = update.effective_user.id
    admin = is_admin(update)

    buttons = _admin_buttons(send_botlist_button=admin, logs_button=admin)

    txt = "🛃 Administration menu"
    context.bot.send_message(
        uid, txt, reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def _admin_buttons(send_botlist_button=False, logs_button=False):
    buttons = [
        [KeyboardButton(captions.USER_LIST),
         KeyboardButton(captions.ACCOUNT_LIST),
         KeyboardButton(captions.TOP_USAGE_ACCOUNTS)],
        [
            KeyboardButton(captions.EXIT)
        ],
    ]

    return buttons


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
                    parse_mode='HTML',
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


def get_top_usage_accounts(update: Update, context: CallbackContext):
    only_admin(update.message, update, context)

    bot = context.bot

    callback_data = util.callback_data_from_update(update)
    if callback_data:
        offset = callback_data['page']
    else:
        offset = 0
    limit = 50

    table = PrettyTable()

    report_items = get_top_accounts_usage(3, limit)

    table.field_names = ["User", "Usage"]

    for index, item in enumerate(report_items):
        try:
            account = Account.select().where(Account.id == item['account_id']).get()
            user = account.user

            table.add_row([user.plaintext,
                           util.get_readable_size(item['upload'] + item['download'])])
        except Account.DoesNotExist:
            log.error("Account does not exist with id: " + item['account_id'])

    log.info(table)

    send_or_edit_message_to_admin(bot, None, update, table)


def get_accounts_info(update: Update, context: CallbackContext):
    only_admin(update.message, update, context)

    bot = context.bot

    callback_data = util.callback_data_from_update(update)

    if callback_data:
        offset = callback_data['page']
    else:
        offset = 0
    limit = 20

    log.info(f"Get Accounts Limit {limit} from {offset}")

    table = PrettyTable()
    client_list = get_all_client_infos(appglobals.V2RAY_INBOUND_ID, limit, offset)
    table.field_names = ["#", "Chat ID", "UUID", "User", "Email", "Usage", "Expire"]

    for index, client in enumerate(client_list):
        try:
            account = Account.by_email(client['email'])
            user = account.user
            table.add_row([index + offset + 1, user.chat_id, account.uuid, user.plaintext, client['email'],
                           util.get_readable_size(client['up'] + client['down']) + '/' + util.get_readable_size_short(
                               client['total']), client['expiry_time']])

        except Account.DoesNotExist:
            inbound_client = get_client(appglobals.V2RAY_INBOUND_ID, client['email'])
            if inbound_client:
                table.add_row([index + offset + 1, "0", inbound_client['id'], "No User", client['email'],
                               util.get_readable_size(
                                   client['up'] + client['down']) + '/' + util.get_readable_size_short(
                                   client['total']),
                               client['expiry_time']])
            log.error("Account does not exist with email: " + client['email'])

    log.info(table)

    reply_markup = util.get_pagination_keyboard(CallbackActions.GET_ACCOUNTS, offset, limit)

    send_or_edit_message_to_admin(bot, reply_markup, update, table)


def send_or_edit_message_to_admin(bot, reply_markup, update, message):
    if update.callback_query:
        bot.edit_message_text(chat_id=appglobals.ADMIN_CHAT_ID,
                              message_id=update.callback_query.message.message_id,
                              text=f'<pre>{message}</pre>', parse_mode=ParseMode.HTML,
                              reply_markup=reply_markup,
                              disable_web_page_preview=True)
    else:
        bot.sendMessage(chat_id=appglobals.ADMIN_CHAT_ID,
                        text=f'<pre>{message}</pre>', parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
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
                                                                          util.get_readable_size(client_info['up']),
                                                                          util.get_readable_size(client_info['down']),
                                                                          util.get_readable_size(
                                                                              client_info['down'] + client_info['up']),
                                                                          util.get_readable_size(client_info['total']),
                                                                          client_info['expiry_time'],
                                                                          appglobals.V2RAY_SUB_URL, account.uuid),
                                  parse_mode='HTML', timeout=60)


def get_users(update: Update, context: CallbackContext):
    only_admin(update.message, update, context)

    callback_data = util.callback_data_from_update(update)

    if callback_data:
        page = callback_data['page']
    else:
        page = 1
    paginate_by = 30

    log.info(f"Get users Page {page} by {paginate_by}")

    bot = context.bot

    table = PrettyTable()
    table.field_names = ["#", "Chat ID", "User", "Accounts", "User Name"]

    for index, user in enumerate(User.select().paginate(page, paginate_by).order_by(User.date_added.desc())):
        account_count = Account.select().where(Account.user == user).count()
        table.add_row(
            [index + 1 + (paginate_by * (page - 1)), user.chat_id, user.markdown_short, account_count, user.username])

    log.info(table)

    reply_markup = util.get_pagination_keyboard(CallbackActions.GET_USERS, page, 1)

    send_or_edit_message_to_admin(bot, reply_markup, update, table)


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

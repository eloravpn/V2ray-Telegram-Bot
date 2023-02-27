import json
import traceback
from datetime import datetime

import emoji
import pytz
from logzero import logger as log
from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

from vpnbot import appglobals, captions, messages, util
from vpnbot.const import CallbackActions
from vpnbot.models.user import User


def callback_router(update: Update, context: CallbackContext) -> None:
    obj = json.loads(str(update.callback_query.data))
    user = update.effective_user

    try:
        if "a" in obj:
            action = obj["a"]

            # BOTLISTCHAT
            if action == CallbackActions.REGISTER:
                register(update=update, context=context)

            log.info('Action: '+str(action))

    except Exception as e:
        traceback.print_exc()

        # get the callback action in plaintext
        actions = dict(CallbackActions.__dict__)
        a = next(k for k, v in actions.items() if v == obj.get("a"))
        log.error('Action: '+util.escape_markdown(a))
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

    log.info('You talk with user: '+user.markdown_short)
    log.debug("Chat ID: {} ". format(user.chat_id))

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
    # try:
    utc = pytz.UTC

    uuid = str(context.args[0])
    telegram_chat_id = int(context.args[1])
    mail = str(context.args[2])
    time = datetime.now(utc).strftime("%B %d, %Y %I:%M%p")

    update.message.reply_text('The Acount is created ' + uuid)
    # except Error as e:
    #     update.message.reply_text('An Exception ocourd: ' + str(e))

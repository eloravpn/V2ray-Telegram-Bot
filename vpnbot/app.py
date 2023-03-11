from telegram.ext import CallbackQueryHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.updater import Updater
from telegram.update import Update

from vpnbot import routing, appglobals
from vpnbot.proxy import load_proxy


if appglobals.ENABLE_PROXY:
    load_proxy()

updater = Updater(appglobals.BOT_TOKE,
                  use_context=True)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


updater.dispatcher.add_handler(CommandHandler('start', routing.start))
updater.dispatcher.add_handler(CommandHandler('adduser', routing.add_user))
updater.dispatcher.add_handler(CommandHandler('getaccounts', routing.get_accounts_info))
updater.dispatcher.add_handler(CommandHandler('getusers', routing.get_users))
updater.dispatcher.add_handler(CommandHandler('myaccounts', routing.get_my_accounts_info))

# updater.dispatcher.add_handler(CommandHandler('ban', routing.ban_handler))
# updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.dispatcher.add_handler(CallbackQueryHandler(
    routing.callback_router,
    pass_chat_data=True,
    pass_user_data=True,
    pass_job_queue=True,
))

updater.dispatcher.add_handler(MessageHandler(
    Filters.reply, routing.reply_router, pass_chat_data=True), group=-1)

updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(
    # Filters out unknown commands
    Filters.command, unknown))

# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.start_polling()

from datetime import datetime

import telegram
from apscheduler.schedulers.blocking import BlockingScheduler
from logzero import logger as log
from telegram.ext import CallbackQueryHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.updater import Updater
from telegram.update import Update

from vpnbot import routing, appglobals, captions
from vpnbot.proxy import load_proxy
from vpnbot.report import save_current_accounts_traffic

if appglobals.ENABLE_PROXY:
    load_proxy()

scheduler = BlockingScheduler(timezone="Asia/Tehran")


def print_time():
    print('dask train_model! The time is: %s' % datetime.now())


# scheduler.add_job(print_time, 'cron', hour='*', minute='*')
# scheduler.add_job(print_time, 'interval', seconds = 5)

updater = Updater(appglobals.BOT_TOKE,
                  use_context=True)

j = updater.job_queue


def callback_minute(context: telegram.ext.CallbackContext):
    log.info('Save current account traffics')
    save_current_accounts_traffic()


job_minute = j.run_repeating(callback_minute, interval=appglobals.XUI_TRAFFIC_SYNC_INTERVAL, first=10)


# scheduler.start()

def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


updater.dispatcher.add_handler(CommandHandler("menu", routing.main_menu))
updater.dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex(captions.EXIT), routing.main_menu))
updater.dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex(captions.ADMIN_MENU), routing.admin_menu))

updater.dispatcher.add_handler(CommandHandler('start', routing.start))
updater.dispatcher.add_handler(CommandHandler('adduser', routing.add_user))
# updater.dispatcher.add_handler(CommandHandler('getaccounts', routing.get_accounts_info))
# updater.dispatcher.add_handler(CommandHandler('getusers', routing.get_users))
updater.dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex(captions.USER_LIST),
                                              routing.get_users))
updater.dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex(captions.ACCOUNT_LIST),
                                              routing.get_accounts_info))
updater.dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex(captions.ACCOUNT_DEACTIVATED_LIST),
                                              routing.get_accounts_deactivated_info))
updater.dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex(captions.TOP_USAGE_ACCOUNTS),
                                              routing.get_top_usage_accounts))

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
updater.idle()

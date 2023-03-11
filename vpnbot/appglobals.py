import asyncio
import os
from pathlib import Path

from decouple import config
from peewee import Proxy
from playhouse.sqlite_ext import SqliteExtDatabase

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

ACCOUNTS_DIR = Path(ROOT_DIR) / "accounts"

ADMIN_CHAT_ID = config('ADMIN_USER_ID')

ADMIN_USER_NAME = config('ADMIN_USER_NAME')

BOT_TOKE = config('BOT_TOKE')

ENABLE_PROXY = config('ENABLE_PROXY', default=False)

DATABASE_PATH = config('DATABASE_URL', default='./v2raybot.sqlite3')

XUI_DB_PATH = config('XUI_DB_URL', default='./x-ui.db')

_auto_typed_db = SqliteExtDatabase(DATABASE_PATH)
_auto_typed_db.autorollback = True

db = Proxy()
db.initialize(_auto_typed_db)

loop = asyncio.get_event_loop()

""" Global singleton ptb job_queue as I'm too lazy to rewrite everything to say `use_context=True` and propagating
the `pass_job_queue` flag across all handlers would be an even bigger nightmare. 
At some point this is going to be replaced with `CallbackContext`, but for now we're gonna live with a global. """
# job_queue: JobQueue = None

# V2ray CONFS

V2RAY_SNI = config('V2RAY_SNI')
V2RAY_PORT = config('V2RAY_PORT')
V2RAY_PATH = config('V2RAY_PATH')
V2RAY_REMARK = config('V2RAY_REMARK')

V2RAY_SUB_URL = config('V2RAY_SUB_URL')

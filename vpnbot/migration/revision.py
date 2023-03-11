from datetime import datetime

from peewee import *
from playhouse.migrate import SqliteMigrator, migrate
from playhouse.sqlite_ext import SqliteExtDatabase

from vpnbot import appglobals

db = SqliteExtDatabase(appglobals.DATABASE_PATH)


migrator = SqliteMigrator(db)
date_added = DateTimeField(null=False, default=datetime.utcnow())

with db.transaction():
    migrate(
        migrator.add_column('user', 'date_added', date_added),
    )


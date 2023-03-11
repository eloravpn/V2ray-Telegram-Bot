import sys
from pathlib import Path

v2raybot_path = str((Path(__file__).parent.parent).absolute())
sys.path.append(v2raybot_path)

from peewee import Proxy
from playhouse.db_url import connect
from playhouse.sqlite_ext import SqliteExtDatabase

from vpnbot import appglobals
from vpnbot.models import *
from vpnbot.models import User, Account



# from playhouse.migrate import PostgresqlMigrator


connection = SqliteExtDatabase(appglobals.DATABASE_PATH)
# connection = connect("sqlite:///:memory:")

connection.autorollback = True
database = Proxy()
database.initialize(connection)

# postgresql_migrator = PostgresqlMigrator(database)

create_order = [
    User,
    Account
]

delete_order = [
    Account,
    User,
]

for model in create_order:
    # noinspection PyProtectedMember
    model._meta.database = database


def delete_models():
    sure = input("Deleting all existing models... Are you sure? (y/n) ")
    if sure == "y":
        for m in delete_order:
            m.drop_table(safe=True)
        print("All models dropped.")
    else:
        print("Nothing deleted.")


def try_create_models():
    for m in create_order:
        m.create_table(safe=True)
    print("Created models if they did not exist yet.")
    
def verify_database():
    try_create_models()


if __name__ == "__main__":
    print(v2raybot_path)

    if "recreate" in sys.argv:
        delete_models()
        try_create_models()
    if "verify" in sys.argv:
        verify_database()

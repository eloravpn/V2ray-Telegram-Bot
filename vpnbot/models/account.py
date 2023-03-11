# -*- coding: utf-8 -*-
from datetime import datetime

from peewee import *

from vpnbot.models import User
from vpnbot.models.basemodel import BaseModel


class Account(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User)
    date_added = DateTimeField(null=False, default=datetime.utcnow)

    uuid = CharField(null=False, unique=True)
    email = CharField(null=False,unique=True)

    @staticmethod
    def by_email(email: str):

        result = Account.select().where(
            (Account.email == email)
        )
        if len(result) > 0:
            return result[0]
        else:
            raise Account.DoesNotExist()

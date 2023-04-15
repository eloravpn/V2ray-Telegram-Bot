# -*- coding: utf-8 -*-
from datetime import datetime

from peewee import *

from vpnbot.models import Account
from vpnbot.models.basemodel import BaseModel


class AccountTraffic(BaseModel):
    id = PrimaryKeyField()
    account = ForeignKeyField(Account)
    date_added = DateTimeField(null=False, default=datetime.utcnow)

    upload = IntegerField(default=0)
    download = IntegerField(default=0)
    total = IntegerField(default=0)

# -*- coding: utf-8 -*-
from peewee import *

from telegram import User as TelegramUser

from datetime import datetime

from vpnbot import util
from vpnbot.models.basemodel import BaseModel


class User(BaseModel):
    id = PrimaryKeyField()
    chat_id = IntegerField()
    date_added = DateTimeField(null=False, default=datetime.utcnow())

    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    photo = CharField(null=True)
    banned = BooleanField(default=False)

    @staticmethod
    def from_telegram_object(user: TelegramUser):
        try:
            u = User.get(User.chat_id == user.id)
            u.first_name = user.first_name
            u.last_name = user.last_name
            u.username = user.username
        except User.DoesNotExist:
            u = User(chat_id=user.id, username=user.username,
                     first_name=user.first_name, last_name=user.last_name)

        u.save()
        return u

    @staticmethod
    def from_update(update):
        return User.from_telegram_object(update.effective_user)

    def __str__(self):
        text = '👤 '  # emoji
        full_name = ' '.join([
            self.first_name if self.first_name else '',
            self.last_name if self.last_name else ''
        ])
        if self.username:
            text += '[{}](https://t.me/{})'.format(full_name, self.username)
        else:
            text += full_name
        return text.encode('utf-8').decode('utf-8')

    @property
    def markdown_short(self):
        displayname = ''
        if self.first_name:
            displayname = util.escape_markdown(
                self.first_name.encode('utf-8').decode('utf-8'))
        if self.username:
            text = '[👤 {}](https://t.me/{})'.format(displayname,
                                                    self.username)
        else:
            text = displayname
        return text.encode('utf-8').decode('utf-8')

    @property
    def plaintext(self):
        text = '👤 '  # emoji
        if self.first_name:
            text += self.first_name
        if self.last_name:
            text += " " + self.last_name
        return text.encode('utf-8').decode('utf-8')

    @property
    def plaintext_with_id(self):
        text = '👤 '  # emoji
        if self.first_name:
            text += self.first_name
        if self.last_name:
            text += " " + self.last_name
        if self.username:
            text += " [" + self.username + "]"
        return text.encode('utf-8').decode('utf-8')

    @staticmethod
    def by_username(username: str):
        if username[0] == '@':
            username = username[1:]
        result = User.select().where(
            (fn.lower(User.username) == username.lower())
        )
        if len(result) > 0:
            return result[0]
        else:
            raise User.DoesNotExist()

    @staticmethod
    def by_chat_id(chat_id: str):

        result = User.select().where(
            (User.chat_id == chat_id)
        )
        if len(result) > 0:
            return result[0]
        else:
            raise User.DoesNotExist()

import sqlite3

import pytz
from persiantools.jdatetime import JalaliDateTime

from vpnbot import appglobals
import json


def get_all_client_infos():
    conn = sqlite3.connect(appglobals.XUI_DB_PATH)
    cursor = conn.execute(f"select email,up,down,total,expiry_time from client_traffics")
    client_info_list = []
    for c in cursor:
        expire_time = 'Not limited'
        if c[4] != 0:
            expire_time = get_jalali_date(c[4])
        client_info_list.append({'email': c[0], 'up': c[1], 'down': c[2], 'total': c[3],
                                 'expiry_time': expire_time})
    conn.close()
    return client_info_list


def get_client_infos(email: str):
    conn = sqlite3.connect(appglobals.XUI_DB_PATH)
    cursor = conn.execute(f"select email,up,down,total,expiry_time from client_traffics where email ='{email}'")
    client_info_list = []
    for c in cursor:
        expire_time = 'Not limited'
        if c[4] != 0:
            expire_time = get_jalali_date(c[4])
        client_info_list.append({'email': c[0], 'up': c[1], 'down': c[2], 'total': c[3], 'expiry_time': expire_time})
    conn.close()
    return client_info_list


def get_jalali_date(ms: int):
    return JalaliDateTime.fromtimestamp(ms / 1000,
                                               pytz.timezone("Asia/Tehran")).strftime("%Y/%m/%d")


def get_client(inbound_id, email):
    conn = sqlite3.connect(appglobals.XUI_DB_PATH)
    cursor = conn.execute(
        f"select id,settings from inbounds where id = '{inbound_id}'")

    for c in cursor:
        data = json.loads(c[1])

    conn.close()
    try:
        for i in data['clients']:
            if i['email'] == email:
                return i
    except StopIteration:
        pass




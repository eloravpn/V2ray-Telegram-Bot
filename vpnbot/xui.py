import sqlite3
from vpnbot import appglobals


def get_all_client_infos():
    conn = sqlite3.connect(appglobals.XUI_DB_PATH)
    cursor = conn.execute(f"select email,up,down,total from client_infos")
    client_info_list = []
    for c in cursor:
        client_info_list.append({'email': c[0], 'up': c[1], 'down': c[2], 'total': c[3]})
    conn.close()
    return client_info_list


def get_client_infos(email: str):
    conn = sqlite3.connect(appglobals.XUI_DB_PATH)
    cursor = conn.execute(f"select email,up,down,total from client_infos where email ='{email}'")
    client_info_list = []
    for c in cursor:
        client_info_list.append({'email': c[0], 'up': c[1], 'down': c[2], 'total': c[3]})
    conn.close()
    return client_info_list

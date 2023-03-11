import re

ip_list = './ip.txt'


def get_v2ray_configs(fstring, port, uuid, host, path, remark):
    # declaring the regex pattern for IP addresses
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

    # initializing the list object
    lst = []

    for line in fstring:

        if pattern.search(line) is None:
            continue
        v2rayn_template = {
            "v": "2",
            "ps": remark,
            "add": pattern.search(line)[0],
            "port": port,
            "id": uuid,
            "aid": 0,
            "net": "ws",
            "type": "none",
            "host": host,
            "path": path,
            "tls": "tls"
        }
        lst.append(v2rayn_template)
    return lst

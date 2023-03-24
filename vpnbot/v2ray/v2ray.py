import re
import urllib.parse

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


def get_v2ray_vless_configs(fstring, type, port, uuid, host, path, remark):
    # declaring the regex pattern for IP addresses
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    alpn = 'h2,http/1.1'

    # initializing the list object
    lst = []

    for line in fstring:

        if pattern.search(line) is None:
            continue
        ip = pattern.search(line)[0]
        prefixTxt = '%s@%s:%s' % (uuid, ip, port)

        prefix = 'vless://' + prefixTxt
        postfixList = []

        # print(urllib.parse.quote(path.encode('utf8')))
        postfixList.append('path=%s' % urllib.parse.quote(path.encode('utf8')))
        postfixList.append('security=%s' % 'tls')
        postfixList.append('encryption=%s' % 'none')
        postfixList.append('host=%s' % host)
        postfixList.append('fp=%s' % 'chrome')
        postfixList.append('type=%s' % type)
        postfixList.append('sni=%s' % host)
        # postfixList.append('alpn=%s' % urllib.parse.quote(alpn.encode('utf8')))

        ilink = prefix + '?' + '&'.join(postfixList) + '#' + urllib.parse.quote(remark.encode('utf8'))

        lst.append(ilink)
    return lst

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
        link = generate_vless(host, ip, path, port, remark, type, uuid)

        lst.append(link)
    return lst


def generate_vless(host, ip, path, port, remark, network_type, uuid):
    prefix_txt = '%s@%s:%s' % (uuid, ip, port)
    prefix = 'vless://' + prefix_txt
    postfix_list = ['path=%s' % urllib.parse.quote(path.encode('utf8')), 'security=%s' % 'tls',
                    'encryption=%s' % 'none', 'host=%s' % host, 'fp=%s' % 'chrome', 'type=%s' % network_type, 'sni=%s' % host]
    # postfix_list.append('alpn=%s' % urllib.parse.quote(alpn.encode('utf8')))
    link = prefix + '?' + '&'.join(postfix_list) + '#' + urllib.parse.quote(remark.encode('utf8'))
    return link

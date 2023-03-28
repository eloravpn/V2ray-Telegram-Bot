import base64
import random
import csv

from flask import Flask, request
from flask import Response

from vpnbot import appglobals
from vpnbot.v2ray.v2ray import get_v2ray_vless_configs, get_v2ray_configs, generate_vless
from vpnbot.v2ray.vmess2sub import Str2Base64, Conf2v2rayN

app = Flask(__name__, template_folder='./')


@app.route('/')
def index():
    # opening and reading the file
    args = request.args
    num_to_select = args.get("size", default=32, type=int)  # set the number to select here.
    pt = args.get("pt", default='VLESS', type=str)  # set the protocol type VMESS or VLESS
    uuid = args.get("uuid", type=str)
    if uuid is None:
        return Response('', mimetype='text/plain')
    ip_list = './ip.txt'
    with open(ip_list) as fh:
        fstring = fh.readlines()

    if pt == 'VMESS':
        configs = get_v2ray_configs(fstring, appglobals.V2RAY_PORT, uuid,
                                    appglobals.V2RAY_SNI, appglobals.V2RAY_PATH,
                                    appglobals.V2RAY_REMARK)
    else:
        if pt == 'VLESS':
            configs = get_v2ray_vless_configs(fstring, 'ws', appglobals.V2RAY_PORT, uuid,
                                              appglobals.V2RAY_SNI, appglobals.V2RAY_PATH,
                                              appglobals.V2RAY_REMARK)

    list_of_random_items = random.sample(configs, num_to_select)

    if pt == 'VMESS':
        configs_v2rayn = Conf2v2rayN(list_of_random_items)
        # configs_v2rayn = Conf2sr(configs)
        text = '\n'.join(configs_v2rayn)
        html = Str2Base64(text)
    else:
        static_configs = get_vless_static(appglobals.V2RAY_SNI, appglobals.V2RAY_PATH, appglobals.V2RAY_PORT,
                                          'ws', uuid)
        text = '\n'.join(static_configs) + '\n'
        text = text + '\n'.join(list_of_random_items)
        html = base64.b64encode(text.encode('utf-8'))

    # return Response(json.dumps(configs_v2rayn, default=vars), mimetype='application/json')
    return Response(html, mimetype='text/plain')

    # return  Response(json.dumps(V2RAYN_TEMPLATE, default=vars),  mimetype='application/json')


def get_vless_static(host, path, port, network_type, uuid):
    vless = './vless.csv'
    rows = []
    file = open(vless, encoding='utf8')
    csvreader = csv.reader(file)

    for row in csvreader:
        rows.append(generate_vless(host, row[1], path, port, row[0].strip(), network_type, uuid))

    return rows

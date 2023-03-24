import base64
import random

from flask import Flask, request
from flask import Response

from vpnbot import appglobals
from vpnbot.v2ray.v2ray import get_v2ray_vless_configs, get_v2ray_configs
from vpnbot.v2ray.vmess2sub import Str2Base64, Conf2v2rayN

app = Flask(__name__, template_folder='./')


@app.route('/')
def index():
    # opening and reading the file
    args = request.args
    num_to_select = args.get("size", default=50, type=int)  # set the number to select here.
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

    configs_v2rayn = Conf2v2rayN(list_of_random_items)
    # configs_v2rayn = Conf2sr(configs)

    if pt == 'VMESS':
        text = '\n'.join(configs_v2rayn)
        html = Str2Base64(text)
    else:
        text = '\n'.join(list_of_random_items)
        html = base64.b64encode(text.encode('utf-8'))

    # return Response(json.dumps(configs_v2rayn, default=vars), mimetype='application/json')
    return Response(html, mimetype='text/plain')

    # return  Response(json.dumps(V2RAYN_TEMPLATE, default=vars),  mimetype='application/json')

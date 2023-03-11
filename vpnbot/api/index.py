import random

from flask import Flask, request
from flask import Response

from vpnbot import appglobals
from vpnbot.v2ray.v2ray import get_v2ray_configs
from vpnbot.v2ray.vmess2sub import Conf2v2rayN, Str2Base64

app = Flask(__name__, template_folder='./')


@app.route('/')
def index():
    # opening and reading the file
    args = request.args
    num_to_select = args.get("size", default=50, type=int)  # set the number to select here.
    uuid = args.get("uuid", type=str)
    if uuid is None:
        return Response('', mimetype='text/plain')
    ip_list = './ip.txt'
    with open(ip_list) as fh:
        fstring = fh.readlines()
    # displaying the extracted IP addresses
    print(appglobals.V2RAY_SNI)
    configs = get_v2ray_configs(fstring, appglobals.V2RAY_PORT, uuid,
                                appglobals.V2RAY_SNI, appglobals.V2RAY_PATH,
                                appglobals.V2RAY_REMARK)

    list_of_random_items = random.sample(configs, num_to_select)

    configs_v2rayn = Conf2v2rayN(list_of_random_items)
    # configs_v2rayn = Conf2sr(configs)

    text = '\n'.join(configs_v2rayn)
    html = Str2Base64(text)

    # return Response(json.dumps(configs_v2rayn, default=vars), mimetype='application/json')
    return Response(html, mimetype='text/plain')

    # return  Response(json.dumps(V2RAYN_TEMPLATE, default=vars),  mimetype='application/json')

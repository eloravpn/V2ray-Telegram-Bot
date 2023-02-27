import os

from logzero import logger as log


def load_proxy():
    proxy = 'http://localhost:1090'

    log.debug('Start Proxy: '+proxy)

    os.environ['http_proxy'] = proxy

    os.environ['HTTP_PROXY'] = proxy
    os.environ['https_proxy'] = proxy
    os.environ['HTTPS_PROXY'] = proxy

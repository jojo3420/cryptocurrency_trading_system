import time
import pybithumb
import math
from common.bithumb_api import *


def read_keys(filepath):
    key_dict = {}
    try:
        with open(filepath) as stream:
            for line in stream:
                k, v = line.strip().split('=')
                key_dict[k] = v
        return key_dict
    except FileNotFoundError:
        print('File Not Found!')


# result = [('KRW-ADA', 1.1), ('BTC-XRP', 2)]

# bithumb_keys = read_keys('.env.local')
# print(bithumb_keys)
# bithumb = pybithumb.Bithumb(conkey=bithumb_keys['ConnectKey'], seckey=bithumb_keys['SecretKey'])
# _total_btc, used_btc, total_krw, used_krw = bithumb.get_balance('BTC')
# kew_cash = total_krw - used_krw


if __name__ == '__main__':
    r, order_desc = buy_or_cancel_krw_market('XRP', 5000, 1)
    print(r, order_desc)

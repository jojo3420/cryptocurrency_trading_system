from common.utils import *
from common.bithumb_api import *
import time
from common.math_util import get_uptic_price, get_downtic_price

bit_keys: dict = read_bithumb_key('.env.local')
secretKey, connectKey = tuple(bit_keys.values())
bithumb = pybithumb.Bithumb(connectKey, secretKey)

#  주문 취소하기

ticker = 'XLM'
order_book = pybithumb.get_orderbook(ticker)
print(order_book)
bids = order_book['bids']  # 매수호가
upest_price = bids[0].get('price')
uptic_price = get_uptic_price(str(upest_price), 1)
downtic_price = get_downtic_price(str(upest_price), -3)
qty = 2
print(ticker, uptic_price, downtic_price, qty)
order_desc = bithumb.buy_limit_order(ticker, downtic_price, qty)
print(order_desc)


if isinstance(order_desc, dict) and 'status' in order_desc.keys():
    status = order_desc.get('status')
    message = order_desc.get('message')
    # if status == '5600':


# order_desc = buy_limit_price(ticker, 100, 10)
# print(order_desc)

time.sleep(3)  # delay
#
cancel_desc: bool = bithumb.cancel_order(order_desc)
print('주문 취소 결과:', cancel_desc)

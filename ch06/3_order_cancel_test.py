from common.utils import *
from common.bithumb_api import *
import time

bit_keys: dict = read_bithumb_key('.env.local')
secretKey, connectKey = tuple(bit_keys.values())
bithumb = pybithumb.Bithumb(connectKey, secretKey)


#  주문 취소하기

ticker = 'XLM'
order_desc = buy_limit_price(ticker, 100, 10)
print(order_desc)

time.sleep(10)  # delay 10 seconds

cancel_desc: bool = bithumb.cancel_order(order_desc)
print('주문 취소 결과:', cancel_desc)



import time
import pybithumb
from common.utils import *
from common.bithumb_api import *

total_krw, use_krw = get_krw_balance()
print('총잔고:', total_krw)
print('주문가능금액: ', total_krw - use_krw)

ticker = 'BTC'
ticker = 'XLM'

quantity = calc_buy_quantity(ticker)
print(quantity)
qty = 10

# order_info: tuple = buy_market_price('XLM', 3)
# print(order_info)


# TODO : 원화마켓에서 코인마다 매수호가 소수점 지원 여부가 다르다.
# 비트코인, 이더리움 은 매수시 정수 원화 로 값 입력해야함(아니면 파라미터 확인 예외발생)
# XLM(잡코인)은 소수점 원화 주문가능..


order_book = pybithumb.get_orderbook(order_currency=ticker)
print(order_book)
bids = order_book.get('bids')

price = bids[0].get('price')
price = 250.1
print(f'매수가: {price:,}, type: {type(price)}')
order = buy_limit_price(ticker, price, qty)
print(order)

# order_desc = bithumb.buy_limit_order('XLM', 200, 2)
# print(order_desc)

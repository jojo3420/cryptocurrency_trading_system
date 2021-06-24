import time
import pybithumb
from common.utils import *
from volatility_breakthrough_trading import *

if __name__ == '__main__':
    # 지정가 매수
    # order_desc = buy_limit_price('XRP', 300, 2)
    # print(order_desc)
    # ticker = 'KLAY'
    # # 시장가 매수
    # order_book: dict = pybithumb.get_orderbook(ticker)
    # bids: list = order_book['bids']
    # asks: list = order_book['asks']
    #
    # ask_price = int(asks[0]['price'])
    # print('최저 매도가:', ask_price)
    # print(type(ask_price))
    # order_desc = buy_limit_price('KLAY', ask_price,  1)
    # print(order_desc)
    #
    # # ('bid', 'XRP', 'C0106000000241177047', 'KRW')
    # # ('bid', 'XRP', 'C0106000000241177048', 'KRW')
    #
    # # buy_coin('XRP', 0.01, 1)
    order_dsc = None
    if order_dsc is None:
        order_dsc = {"name": 'park'}
    print(order_dsc)
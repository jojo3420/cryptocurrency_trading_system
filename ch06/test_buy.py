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
    # order_no = buy_coin('XRP', 0.01, 1)
    # print(order_no)

    ticker = 'XRP'
    buy_qty = 2
    # 지정가 주문
    order_desc: tuple = buy_limit_price(ticker, 500, buy_qty)
    print(order_desc)
    # 지정가므로 체결보장 X:  매수호가에 유지됨
    # order_desc = ('bid', 'XRP', 'C0106000000252216142', 'KRW')
    # order_no = 'C0106000000252216142'
    # print(get_my_order_completed_info(order_desc))
    # print(bithumb.get_order_completed(order_desc))
    # {'status': '0000', 'data': {'order_date': '1625101599535835', 'type': 'bid', 'order_status': 'Pending', 'order_currency': 'XRP', 'payment_currency': 'KRW', 'watch_price': '0', 'order_price': '700', 'order_qty': '1', 'cancel_date': '', 'cancel_type': '', 'contract': []}}


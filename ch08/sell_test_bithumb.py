import pybithumb
from common.bithumb_api import sell_limit_price, get_balance_coin, get_my_coin_balance
from common.math_util import get_downtic_price

exclusion_list = ['BTC', 'ETH']

# ticker = 'ONG'
my_coin_balance = get_my_coin_balance()
for ticker, (_total, _used, available) in my_coin_balance.items():
    if ticker not in exclusion_list:
        total, used = get_balance_coin(ticker)
        qty = total - used
        order_book = pybithumb.get_orderbook(ticker)
        print(order_book)
        bids = order_book['asks']
        sell_wish_price = int(bids[0]['price'])
        downtic_price = get_downtic_price(sell_wish_price)
        print('downtic_price: ', downtic_price, type(sell_wish_price))
        print(f'qty: {qty} 매도가: {sell_wish_price}, 매도가타입: {type(sell_wish_price)},  수량 타입:{type(qty)}')
        # order_desc = sell_limit_price(ticker, price=sell_wish_price, quantity=qty)
        # print(order_desc)

# order_desc = sell_limit_price(ticker, , 5)
# ('ask', 'ADA', 'C0150000000176084876', 'KRW')
# print(order_desc)

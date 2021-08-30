import pybithumb

from common.bithumb_api import sell_limit_price, get_coin_quantity, get_my_coin_balance

# ticker = 'ADA'
for ticker, (_total, _used, available) in get_my_coin_balance():
    qty = get_coin_quantity(ticker)
    qty = qty[0] - qty[1]
    order_book = pybithumb.get_orderbook(ticker)
    print(order_book)
    # {'timestamp': '1630245727447', 'payment_currency': 'KRW',
    # 'order_currency': 'ADA',
    # 'bids': [{'price': 3396.0, 'quantity': 6936.0342},
    #  {'price': 3395.0, 'quantity': 6150.0},
    #  {'price': 3394.0, 'quantity': 11694.1668},
    #  {'price': 3393.0, 'quantity': 1048.0358},
    #  {'price': 3391.0, 'quantity': 2040.0}],
    #  'asks': [{'price': 3398.0, 'quantity': 2610.1011},
    #  {'price': 3399.0, 'quantity': 792.21},
    #  {'price': 3400.0, 'quantity': 3514.3079},
    #  {'price': 3401.0, 'quantity': 3600.0},
    #  {'price': 3402.0, 'quantity': 162.8981}]}
    bids = order_book['asks']
    sell_wish_price = int(bids[0]['price'])
    print(qty, sell_wish_price, type(sell_wish_price), type(qty))
    order_desc = sell_limit_price(ticker, price=sell_wish_price, quantity=qty)
    print(order_desc)


# order_desc = sell_limit_price(ticker, , 5)
# ('ask', 'ADA', 'C0150000000176084876', 'KRW')
# print(order_desc)

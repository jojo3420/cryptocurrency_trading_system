import pybithumb
import math
from common.bithumb_api import get_krw_balance, calc_buy_quantity, buy_limit_price


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

total_krw, used_krw = get_krw_balance()
csah = total_krw - used_krw
print(f'cash: {csah:,.0f}')



# buy bithumb
# for idx, (symbol, yields) in enumerate(result):
#     if idx < 3:
#         print(f'buy -> {symbol} yield: {yields}')
#         sym = symbol.split('-')
#         payment_currency = sym[0]
#         ticker = sym[1]
#         qty = math.floor(calc_buy_quantity(ticker))
#         # qty = 1
#         print(f'매수가능 수량: {qty}')
#         orderbook = pybithumb.get_orderbook(ticker, payment_currency=payment_currency)
#         print(orderbook)
#         # {'timestamp': '1630244818732', 'payment_currency': 'KRW',
#         # 'order_currency': 'ADA',
#         # 'bids': [{'price': 3404.0, 'quantity': 2194.3964},
#         # {'price': 3402.0, 'quantity': 9932.746},
#         # {'price': 3401.0, 'quantity': 1500.0},
#         # {'price': 3400.0, 'quantity': 636.0},
#         # {'price': 3398.0, 'quantity': 142.0653}],
#         # 'asks': [{'price': 3407.0, 'quantity': 3612.0364},
#         # {'price': 3409.0, 'quantity': 3506.0474},
#         # {'price': 3410.0, 'quantity': 683.2079},
#         # {'price': 3411.0, 'quantity': 149.9753},
#         # {'price': 3412.0, 'quantity': 33757.0}]}
#         asks = orderbook['asks']
#         if asks and len(asks) > 0:
#             buy_wish_price = asks[1]['price']
#             print(buy_wish_price)
#             order_desc = buy_limit_price(ticker, price=buy_wish_price, quantity=qty)
#             print(order_desc)

ticker ='ONG'
price = pybithumb.get_current_price(ticker)
print(price, type(price))
temp = {}
temp[ticker] = price
print(temp)
prev_price = temp.get(ticker, 0)
print(prev_price, type(prev_price))

# qty = calc_buy_quantity(ticker) -1
# order_d = buy_limit_price(ticker, price, qty)
# print(order_d)
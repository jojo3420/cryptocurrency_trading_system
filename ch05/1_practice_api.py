# import pybithumb
from pybithumb import Bithumb
import time
from datetime import datetime

all_ticker: list = Bithumb.get_tickers()
print(type(all_ticker), len(all_ticker))
print(all_ticker)

# for ticker in all_ticker:
# print(ticker)
# price = Bithumb.get_current_price(ticker)
# print(ticker, price)
# time.sleep(0.1)  # 1초에 10개
# time.sleep(0.05)  # 1초에 20개


# 거래소 시세 정보(거래)

# 24시간 동안의 저가/고가/거래금액/거래량
btc_price_info = Bithumb.get_market_detail('BTC')
print(btc_price_info)
# (시가, 고가, 저가, 종가, 거래량)
open, high, low, close, volume = btc_price_info
print(open, high, low, close, volume)

# 주문 호가창 데이터
orderbook = Bithumb.get_orderbook('BTC')
print(orderbook)
_timestamp = orderbook['timestamp']
now_tm = datetime.fromtimestamp(int(_timestamp) / 1000)
print(now_tm)
buy_orders: list = orderbook['bids']
sell_orders: list = orderbook['asks']
# print(buy_orders)
# print(sell_orders)

for order in buy_orders:
    print('buy =>', order['price'], order['quantity'])


all_current_price: dict = Bithumb.get_current_price('ALL')
for k, v in all_current_price.items():
    print(k, v)
    # print(v['opening_price'])
import time

import pybithumb
from pandas import DataFrame, Series
from pybithumb import Bithumb
import pykorbit

# btc = Bithumb.get_ohlc('BTC')
# print(btc)

# deprecated!
# btc_price: DataFrame = pybithumb.get_ohlcv('BTC')
# print(type(btc_price))
# print(btc_price)

btc_prices: DataFrame = Bithumb.get_candlestick('BTC')
print(btc_prices)

close: Series = btc_prices['close']
print(type(close))
print(close)

# 이동평균 구하기
print('MA5 =>', close[0] + close[1] + close[2] + close[3] + close[4] / 5)
print('MA5 =>', close[1] + close[2] + close[3] + close[4] + close[5] / 5)
print('MA5 =>', close[2] + close[3] + close[4] + close[5] + close[6] / 5)

BTC_MA5 = close.rolling(5).mean()
btc_prices['MA5'] = BTC_MA5
print(btc_prices)


def moving_average_by(ticker: str, days: int = 5) -> DataFrame:
    """ 특정 이동평균 구해진 DataFrame 리턴

    6-13일 MA3: 11, 12, 13일 close
    ( 2724000.0 + 2811000.0 + 2840000.0 ) / 3

    2021-06-09 00:00:00, close: 2840000.0, MA3: 2941000.0
    2021-06-10 00:00:00, close: 2919000.0, MA3: 2842666.6666666665
    2021-06-11 00:00:00, close: 2840000.0, MA3: 2866333.3333333335
    2021-06-12 00:00:00, close: 2811000.0, MA3: 2856666.6666666665
    2021-06-13 16:00:00, close: 2724000.0, MA3: 2791666.6666666665
    """

    prices: DataFrame = Bithumb.get_candlestick(ticker)
    close = prices['close']
    MA = close.rolling(days).mean()
    prices[f'MA{days}'] = MA
    prices = prices.dropna()
    return prices


def fetch_ohlcv(ticker: str) -> DataFrame:
    prices: DataFrame = Bithumb.get_candlestick(ticker)
    prices = prices.dropna()
    return prices


eth_prices: DataFrame = moving_average_by('ETH', 3)
print(eth_prices.tail())
# for tup in eth_prices.itertuples():
#     print(tup)

for tup in eth_prices.tail().itertuples():
    print(tup)
    date, open, high, low, close, volume, MA3 = tup
    print(f'{date}, close: {close}, MA3: {MA3}')


eth_prev_ma3: float = eth_prices['MA3'][-2]
print(eth_prev_ma3)
# print(type(eth_prev_ma3))

current_price = Bithumb.get_current_price('ETH')

print(int(current_price))
print(int(eth_prev_ma3))
print(type(current_price))

if current_price > eth_prev_ma3:
    print('상승장')
else:
    print('하락장')


def is_bull_market(ticker: str) -> bool:
    df = Bithumb.get_candlestick(ticker)
    MA5 = df['close'].rolling(window=5).mean()
    current_price = Bithumb.get_current_price(ticker)
    prev_ma5 = MA5[-2]
    if current_price > prev_ma5:
        return True
    return False


#
# for ticker in Bithumb.get_tickers():
#     is_bull = is_bull_market(ticker)
#     if is_bull:
#         print(ticker, '상승장')
#     else:
#         print(ticker, '하락장')
#         time.sleep(0.1)
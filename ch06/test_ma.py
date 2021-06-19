from common.utils import *
from common.bithumb_api import *
from volatility_breakthrough_trading import *

if __name__ == '__main__':
    # 3일 이동평균 구하기: 호출일 close 계산에 포함됨!
    days = 3
    ticker = 'ETH'
    prices: DataFrame = pybithumb.get_candlestick(ticker)
    print(prices.tail())
    close: Series = prices['close']
    MA: Series = close.rolling(days).mean()
    print(MA.tail())
    price = MA[-1]
    print(price)

    print(calc_moving_average_by('ETH', 3))
from common.utils import *
from common.bithumb_api import *
from volatility_breakthrough_trading import *

if __name__ == '__main__':
    # 3일 이동평균 구하기: 호출일 close 계산에 포함됨!
    days = 3
    ticker = 'ETH'
    prices: DataFrame = pybithumb.get_candlestick(ticker)
    # print(prices.tail())
    close: Series = prices['close']
    print(close.tail())
    MA: Series = close.rolling(days).mean()
    print(MA.tail())
    price = MA[-1]
    print(f'3일 이동평균가격: {price:,}')

    print(f'{calc_moving_average_by("ETH", 3):,}')

    MA3 = calc_moving_average_by('BTC', 3)
    MA5 = calc_moving_average_by('BTC', 5)
    MA10 = calc_moving_average_by('BTC', 10)
    MA20 = calc_moving_average_by('BTC', 20)
    print(MA3, MA5, MA10, MA20)
    print('current: ', pybithumb.get_current_price('BTC'))
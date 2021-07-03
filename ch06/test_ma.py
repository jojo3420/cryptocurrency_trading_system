from common.utils import *
from common.bithumb_api import *
from volatility_breakthrough_trading import *
import pandas as pd





if __name__ == '__main__':
    # row 생략 없이 출력
    pd.set_option('display.max_rows', None)
    # col 생략 없이 출력
    pd.set_option('display.max_columns', None)

    # 3일 이동평균 구하기: 호출일 close 계산에 포함됨!
    days = 5
    ticker = 'ETH'
    # prices: DataFrame = pybithumb.get_candlestick(ticker)
    # # print(prices.tail())
    # close: Series = prices['close']
    # print(close.tail())
    # MA: Series = close.rolling(days).mean()
    # print(MA.tail())
    # price = MA[-1]
    # print(f'3일 이동평균가격: {price:,}')
    #
    # print(f'{calc_moving_average_by("ETH", 3):,}')
    #
    # MA3 = calc_moving_average_by('BTC', 3)
    MA5 = calc_moving_average_by(ticker, days)
    # MA10 = calc_moving_average_by('BTC', 10)
    # MA20 = calc_moving_average_by('BTC', 20)
    # print(MA3, MA5, MA10, MA20)
    # print('current: ', pybithumb.get_current_price('BTC'))

    # 당일 시세 포함 이동평균가격
    print(MA5)
    # print((2812000+2662000+2649000+2504000+2372000)/5)

    # 당일 시세 제외 이동평균가격
    print(calc_prev_moving_average_by(ticker, 5))
    # print((2820000+2812000+2662000+2649000+2504000)/5)
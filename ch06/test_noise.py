from volatility_breakthrough_trading import *
import pybithumb
from pandas import DataFrame, Series
import pandas


def money_management(ticker: str) -> None:
    """ 자금 관리
    종목당 투자 비율 공식
        1)투자비율 = (전일고가 - 저가) / 전일종가 * 100
        1)투자비율이 특정 k 값을 넘어가지 않도록 변경
    """
    prices: DataFrame = pybithumb.get_candlestick(ticker)
    if not prices.empty:
        rates: DataFrame = (prices['high'] - prices['low']) / prices['close'] * 100
        print(rates.tail(10))
        target_loss_ratio = 2
        money_ratio: Series = target_loss_ratio / rates
        print(money_ratio.tail(10))
        return money_ratio[-1]


if __name__ == '__main__':
    pandas.set_option('display.max_rows', None)
    # 30일 노이즈 이동평균값
    noise = calc_noise_ma_by('BTC', 20)
    print(f'BTC noise: {noise}')


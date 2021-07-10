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

    coin_buy_wish_list, _, __ = get_buy_wish_list()
    bull_coin_list, _, __ = get_bull_coin_list()
    print(bull_coin_list)
    for ticker in coin_buy_wish_list + bull_coin_list:
        name = get_coin_name(ticker)
        current_noise = get_current_noise(ticker)
        MA3_NOISE = calc_noise_ma_by(ticker, 3)
        MA5_NOISE = calc_noise_ma_by(ticker, 5)
        MA10_NOISE = calc_noise_ma_by(ticker, 10)
        MA20_NOISE = calc_noise_ma_by(ticker, 20)
        R = calc_R(ticker, 0.5)
        print(
            f'{name} \n'
            f'R: {R} \n'
            f'curr_noise: {current_noise}\n'
            f'MA3_NOISE: {MA3_NOISE}\n'
            f'MA5_NOISE: {MA5_NOISE}\n'
            f'MA10_NOISE: {MA10_NOISE}\n'
            f'MA20_NOISE: {MA20_NOISE}')
        print('-' * 100)
        time.sleep(0.5)

    # print(f'current_noise: {get_prev_noise("BTC")}')

    # while True:
    #     print(f'current_noise: {get_current_noise("BTC")}')
    #     time.sleep(1)

    tickers = pybithumb.get_tickers()
    # for ticker in tickers:
    #     noise = get_current_noise(ticker)
    #     # print(f'noise: {curr_noise}')
    #     # noise = calc_noise_ma_by(ticker, 3)
    #     if noise < 0.3:
    #         print(f'추세적인 코인 {ticker}')
    #     # print(f'{ticker} 추세 평균 {calc_average_ma_by(ticker)}')

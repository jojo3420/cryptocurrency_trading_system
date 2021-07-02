import os
import sys

if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
else:
    sys.path.append('/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system')

from volatility_breakthrough_trading import *
from common.utils import *
from common.bithumb_api import *


def find_bull_coin_with_noise() -> None:
    """
    변동성 돌파한 코인 찾기
    조건
    1) 현재가격이 돌파
    2) 3일 이동평균 보다 큼
    3) 노이즈 0.55 미만
    :return:
    """
    # result_list = []
    tickers: list = pybithumb.get_tickers()
    today = get_today_format()
    sql = 'INSERT INTO bull_coin_list ' \
          ' (date, ticker, name) ' \
          ' VALUES (%s, %s, %s) '
    for t in tickers:
        R = calc_R(t, 0.5)
        MA3 = calc_moving_average_by(t, 3)
        target_price = calc_williams_R(t, R)
        current_price = pybithumb.get_current_price(t)
        if target_price and current_price > target_price and current_price > MA3:
            diff = current_price - target_price
            expected_diff_percent = round((diff / current_price * 100), 3)
            if expected_diff_percent < 0.5:
                curr_noise = get_current_noise(t)
                # MA30_VOLUME = calc_prev_ma_volume(ticker, 30)
                # curr_volume = get_current_volume(ticker)
                MA3_NOISE = calc_noise_ma_by(ticker, 3)
                if curr_noise < 0.55 and MA3_NOISE < 0.55:
                    print(f'매수할 종목: {t}')
                    mutation_db(sql, (today, t, get_coin_name(t)))
                    # result_list.append(t)
    # return result_list


if __name__ == '__main__':
    bull_ticker = []
    # print('prev_volume: ', get_prev_volume('BTC'))
    # print('MA30_volume: ', calc_prev_ma_volume('BTC', 30))
    # print('current_volume', get_current_volume('BTC'))

    find_bull_coin_with_noise()

    # for t in tickers:
    #     is_bull: bool = is_bull_market(t)
    #     if is_bull:
    #         msg = f'상승장: {t} {is_bull}'
    #         print(msg)
    #         mutation_db(sql, (today, t, get_coin_name(t)))
    #     time.sleep(0.1)

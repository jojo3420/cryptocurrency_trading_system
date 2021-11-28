import os
import sys

if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
else:
    sys.path.append('/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system')

from math_helper import *
from db_helper import *
from common.utils import get_today_format


def find_bull_market_list(R=0.5) -> list:
    """
    상승코인 찾기
     1) 현재가격 > EMA3 OR EMA5
     2) 노이즈값 0.55 미만
    :return:
    """
    bull_coins = []
    all_symbol_list = pyupbit.get_tickers(fiat='KRW')
    print(all_symbol_list)
    for symbol in all_symbol_list:
        try:
            curr_price = pyupbit.get_current_price(symbol)
            today_open_price = get_today_open(symbol)
            today_percent = (curr_price / today_open_price - 1) * 100
            target_price = calc_target_price(symbol, R)
            MA3 = calc_ema(symbol, 3)
            # curr_noise = calc_noise_ma_by(symbol, 1)
            if curr_price >= MA3 and curr_price > target_price and today_percent > 5.0:
                print(f'상승 불코인: {symbol} ')
                bull_coins.append(symbol)
            time.sleep(1)
        except Exception as E:
            print(str(E))
    return bull_coins


def main():
    bull_coins = find_bull_market_list()
    print('bull_coins: ', bull_coins)
    # bought_symbol_list = get_bought_list()
    # if bull_coins:
    #     today = get_today_format()
    #     sql = 'REPLACE INTO bull_coin_list ' \
    #           ' (date, ticker, name, ratio, R, ' \
    #           ' disabled, alrealdy_buy ) ' \
    #           ' VALUES ( %s, %s, %s, %s, %s, ' \
    #           ' %s, %s)'
    #     for symbol in bull_coins:
    #         name = ''
    #         ratio = 0.1
    #         R = 0.5
    #         data = (today, symbol, name, ratio, R,
    #                 False, False
    #                 )
    #         if symbol not in bought_symbol_list:
    #             mutation_db(sql, data)


if __name__ == '__main__':
    # while True:
    print('5분마다 불장 코인 찾기!')
    main()
    # time.sleep(1 * 60 * 5)  # 5분

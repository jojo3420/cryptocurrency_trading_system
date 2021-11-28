import os
import  sys
if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
else:
    sys.path.append('/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system')

from math_helper import *
from db_helper import *
from common.utils import get_today_format


def main():
    bull_coins = find_bull_market_list()
    print('bull_coins: ', bull_coins)
    bought_symbol_list = get_bought_list()
    if bull_coins:
        today = get_today_format()
        sql = 'REPLACE INTO bull_coin_list ' \
              ' (date, ticker, name, ratio, R, ' \
              ' disabled, alrealdy_buy ) ' \
              ' VALUES ( %s, %s, %s, %s, %s, ' \
              ' %s, %s)'
        for symbol in bull_coins:
            name = ''
            ratio = 0.1
            R = 0.5
            data = (today, symbol, name, ratio, R,
                    False, False
                    )
            if symbol not in bought_symbol_list:
                mutation_db(sql, data)


if __name__ == '__main__':
    while True:
        print('5분마다 불장 코인 찾기!')
        main()
        time.sleep(1 * 60 * 5)  # 5분

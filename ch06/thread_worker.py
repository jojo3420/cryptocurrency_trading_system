import threading
import os
import sys
import time
from datetime import datetime

if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
else:
    sys.path.append('/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system')

from volatility_breakthrough_trading import buy_coin, get_buy_wish_list, get_coin_bought_list, get_total_yield, calc_R, \
    trailing_stop, trading_rest_time
from common.utils import log


class Worker(threading.Thread):
    """
    """
    def __init__(self, name):
        super().__init__()
        # self.daemon = True
        self.name = name

    def run(self):
        f = open(f'{self.name}.txt', 'wt')
        cnt = 0
        while cnt < 100:
            data = f'{self.name}-{cnt}\n'
            f.write(data)
            print(data, end="")
            cnt += 1
            time.sleep(0.1)
        f.close()


if __name__ == '__main__':
    w1 = Worker('w1')
    w2 = Worker('w2')
    w1.run()
    w2.run()
    j = 0
    while j < 100:
        print(j)
        j += 1
        time.sleep(0.1)

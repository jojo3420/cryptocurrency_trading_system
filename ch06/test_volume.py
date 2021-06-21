from volatility_breakthrough_trading import *
import pybithumb
from pandas import DataFrame



if __name__ == '__main__':
    print(get_prev_volume('BTC'))
    print(calc_prev_ma_volume('BTC'))
    vm_MA5 = (3461.521761 + 3775.877740 + 3554.461462 + 3424.405924 + 3475.311863) / 5
    print(vm_MA5)

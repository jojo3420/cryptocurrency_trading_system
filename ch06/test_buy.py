import time
import pybithumb
from common.utils import *
from volatility_breakthrough_trading import *


if __name__ == '__main__':
    order_desc = buy_limit_price('XRP', 1020.0, 2)
    print(order_desc)
import time
import pybithumb
from common.utils import *
from volatility_breakthrough_trading import *


if __name__ == '__main__':

    # 지정가 매수
    order_desc = buy_limit_price('XRP', 300, 2)
    print(order_desc)

    # 시장가 매수

    order_desc = buy_market_price('XRP', 2)
    print(order_desc)

    # ('bid', 'XRP', 'C0106000000241177047', 'KRW')
    # ('bid', 'XRP', 'C0106000000241177048', 'KRW')

    # buy_coin('XRP', 0.01, 1)

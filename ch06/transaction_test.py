import pybithumb
from common.utils import *
from common.bithumb_api import *
from ch06.volatility_breakthrough_trading import *






if __name__ == '__main__':
    # 시장 체결 내역 같음
    # eth_trans = bithumb.get_transaction_history('ETH')
    # for tr in eth_trans:
    #     print(tr)

    # print(bithumb.get_btci())

    """ type: 'bid', 'ask', ticker, order_id, 통화  """
    order_desc = ('bid', 'ETH', 'C0102000000252266772', 'KRW')
    # print(bithumb.get_order_completed(order_desc))

    print(get_my_order_completed_info(order_desc))
import time

from upbit_helper import *

if __name__ == '__main__':
    upbit = UpbitHelper()
    # symbol = 'KRW-XRP'
    # ret = upbit.buy(symbol, quantity=10, bid=900)
    # print(ret)
    # # {'uuid': 'c5db4768-387a-4a41-94b4-702fd8639c0b', 'side': 'bid', 'ord_type': 'limit', 'price': '900.0', 'state': 'wait', 'market': 'KRW-XRP', 'created_at': '2021-09-13T20:54:20+09:00', 'volume': '10.0', 'remaining_volume': '10.0', 'reserved_fee': '4.5', 'remaining_fee': '4.5', 'paid_fee': '0.0', 'locked': '9004.5', 'executed_volume': '0.0', 'trades_count': 0}
    #
    # time.sleep(10)
    # uuid = ret.get('uuid')
    # print(uuid)
    # order_state = upbit.order_cancel(uuid)
    # print(order_state)
    #
    # asks, bids = get_orderbook(symbol).values()
    # print(asks)
    # print(bids)


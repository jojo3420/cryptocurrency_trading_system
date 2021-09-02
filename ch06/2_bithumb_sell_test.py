from ch06.volatility_breakthrough_trading import get_coin_bought_list
from common.utils import *
from common.bithumb_api import *


#
# # 매도
# bit_keys: dict = read_bithumb_key('.env.local')
# secretKey, connectKey = tuple(bit_keys.values())
# bithumb = pybithumb.Bithumb(connectKey, secretKey)
#
#
#
#
# # total_coin_q, sell_use = get_balance_coin('XLM')
# # sell_limit_price('XLM', 400, total_coin_q - sell_use)
#
# order_info = sell_market_price('XLM', 5)
# print(order_info)



while True:
    _sell_list = get_coin_bought_list()
    sell_list = [ticker for ticker in _sell_list if ticker != 'BTC']
    print(sell_list)
    if len(sell_list) == 0:
        break

    for ticker in sell_list:
        order_book = pybithumb.get_orderbook(ticker)
        asks = order_book.get('asks', [])
        if asks:
            ask = asks[0].get('price')
            # print(ask)
            order_desc = sell_limit_price(ticker, ask, quantity=(qty - used))
            print(order_desc)
            time.sleep(3)

            qty, used = get_balance_coin(ticker)
            quantity = qty - used
            if quantity > 0:
                cancel = cancel_order(order_desc)
                print(f'주문취소: {cancel}')



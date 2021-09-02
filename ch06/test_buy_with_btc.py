import time

from common.bithumb_api import buy_limit_price, get_balance_coin, cancel_order, sell_limit_price, calc_buy_quantity
from common.math_util import get_uptic_price, get_downtic_price
import pybithumb

BTC_TICKER = 'BTC'
ticker = 'KSM'

btc_balance, used = get_balance_coin(BTC_TICKER)
btc_balance -= used
position_size = calc_buy_quantity(ticker, order_btc=btc_balance / 4)
print(btc_balance, position_size)


order_book = pybithumb.get_orderbook(ticker, payment_currency=BTC_TICKER)
bids = order_book.get('bids', [])
if bids:
    bid = bids[0].get('price')
    # downtic_bid = get_downtic_price(bid)
    print(f'bid: {bid}, position_size: {position_size}')
    order_desc = buy_limit_price(ticker, bid, quantity=position_size, market=BTC_TICKER)
    print(order_desc)

    time.sleep(1)

    target_coin_qty, _used = get_balance_coin(ticker)
    if target_coin_qty == 0:
        cancel = cancel_order(order_desc)
        print(f'cancel: {cancel}')
    elif target_coin_qty > 0:
        while True:
            target_coin_qty, _used = get_balance_coin(ticker)
            if target_coin_qty == 0:
                break

            order_book = pybithumb.get_orderbook(ticker, payment_currency="KRW")
            asks = order_book.get('asks', [])
            if asks:
                ask = asks[0].get('price')
            order_desc = sell_limit_price(ticker, ask, target_coin_qty)
            time.sleep(3)

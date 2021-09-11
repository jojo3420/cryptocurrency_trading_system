import math

from common.bithumb_api import *



if __name__ == '__main__':
    ticker = 'XRP'
    quantity = calc_buy_quantity(ticker, order_btc=0.00230)
    print(f'qty: {quantity}')
    qty = math.floor(quantity * 0.1)
    print(qty)
    buy_coin_btc_market(ticker, qty)

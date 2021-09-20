import math

from common.bithumb_api import *



if __name__ == '__main__':
    """
    
    BTC 마켓에서 SNX 코인 매수하기
[2021-09-20 08:19:46.180819] 매도호가: 0.00037900, 진입가: 0.00025001
[2021-09-20 08:19:46.181486] 지정가 매수 주문 실패(api 실패): {'status': '5600', 'message': '최소 주문금액은 0.0002 BTC 입니다.'}
order_desc: {'status': '5600', 'message': '최소 주문금액은 0.0002 BTC 입니다.'}
Traceback (most recent call last):
    """
    ticker = 'SNX'
    quantity = calc_buy_quantity(ticker, order_btc=0.00230)
    print(f'qty: {quantity}')
    qty = math.floor(quantity * 0.1)
    print(qty)
    buy_coin_btc_market(ticker, qty)

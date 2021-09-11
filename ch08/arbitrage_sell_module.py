import time

from common.bithumb_api import *
from common.math_util import get_downtic_price

KRW_SYM = 'KRW'
BTC_SYM = 'BTC'


def sell_and_cancel_krw_market(ticker: str, qty: float):
    while True:
        if qty == 0:
            print(f'{qty} => sleep')
            time.sleep(3)
        try:
            krw_order_book = pybithumb.get_orderbook(ticker, payment_currency=KRW_SYM)
            asks = krw_order_book['asks']
            ask_price = asks[0].get('price', 0)
            downtic_price = get_downtic_price(ask_price)
            # KRW 마켓에서 매도
            print(ask_price, type(ask_price))
            print(downtic_price, type(downtic_price))
            order_desc = sell_limit_price(ticker, ask_price, qty)
            print(f'매도 주문정보: {order_desc}')
            time.sleep(3)
            qty, _ = get_balance_coin(ticker)
            if qty > 0:
                cancel = cancel_order(order_desc)
                print(f'매도 주문 취소: {cancel}')
                # BTC 마켓에서 매도호가로 매도주문 실행!
                # sell_limit_price()
            elif qty == 0:
                print(f'{ticker} 매도 주문 성공: {qty}')
                # btc_curr_price = pybithumb.get_current_price(BTC_SYM, payment_currency=KRW_SYM)
                # entry_price_krw = entry_price * btc_curr_price
                # print(
                #     f'진입가격: {entry_price_krw:,.f}, 청산가격: {ask_price:,.f}, 수익률: {(ask_price / entry_price_krw - 1) * 100}')
                print('매도종료!')
                break
            time.sleep(0.3)
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            time.sleep(3)


def restfull_sell_main():
    while True:
        try:
            balance = get_my_coin_balance('ALL')
            # print(balance)
            for ticker, (total_coin, used, available) in balance.items():
                # print(ticker, total_coin, used, available)
                if ticker == 'BTC' or ticker == 'ETH':
                    continue
                else:
                    print(f'sell: {ticker} {available}')
                    sell_and_cancel_krw_market(ticker, available)
                time.sleep(0.3)
            print(f'-' * 100)
            time.sleep(1)
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            time.sleep(3)


if __name__ == '__main__':
    restfull_sell_main()

import time

from common.bithumb_api import *
from common.math_util import get_downtic_price
from common.utils import save_transaction_history_data

KRW_SYM = 'KRW'
BTC_SYM = 'BTC'
BTC_SLIPPAGE = 0.00001059


# def buy_btc():
#     while True:
#         total_krw, used = get_krw_balance()
#         krw = total_krw - used
#         entry_price, order_desc = buy_or_cancel_krw_market(BTC_SYM, krw, 5)
#         if entry_price and order_desc:
#             btc_qty, btc_used = get_balance_coin(BTC_SYM)
#             btc = btc_qty - btc_used
#             if btc > BTC_SLIPPAGE:
#                 break


def sell_and_cancel_krw_market(ticker: str, qty: float):
    while True:
        if qty == 0:
            print(f'{qty} => sleep')
            time.sleep(3)
        try:
            krw_order_book = pybithumb.get_orderbook(ticker, payment_currency=KRW_SYM)
            asks = krw_order_book['asks']
            curr_krw_price = pybithumb.get_current_price(ticker, 'KRW')
            downtic_price = get_downtic_price(curr_krw_price)
            ask_price = asks[0].get('price', 0)
            # KRW 마켓에서 매도
            print(f'현재시세(KRW): {curr_krw_price:,.8f}')
            print(f'down_tic(KRW): {downtic_price:,.8f}')
            # 현재시세(KRW): 5.96900000 down_tic(KRW): 5.96899999 => 주문틱이 있음
            print(f'매도호가(KRW): {ask_price:,.8f}')
            order_desc = sell_limit_price(ticker, curr_krw_price, qty)
            print(f'매도 주문결과: {order_desc}')
            time.sleep(3)
            after_qty, _ = get_balance_coin(ticker)
            if after_qty > 0:
                cancel = cancel_order(order_desc)
                print(f'매도 주문 취소: {cancel}')
                # BTC 마켓에서 매도호가로 매도주문 실행!
                # sell_limit_price()
            elif after_qty == 0:
                print(f'{ticker} 매도 주문 성공: {qty}')
                # btc_curr_price = pybithumb.get_current_price(BTC_SYM, payment_currency=KRW_SYM)
                # entry_price_krw = entry_price * btc_curr_price
                # print(
                #     f'진입가격: {entry_price_krw:,.f}, 청산가격: {ask_price:,.f}, 수익률: {(ask_price / entry_price_krw - 1) * 100}')
                print('매도종료!')
                #               ' (order_no, date, ticker, position, price, ' \
                #               'quantity, fee, transaction_krw_amount, type)' \
                fee = (ask_price * qty) * 0.0025
                params = (order_desc[2], get_today_format(), ticker, 'ask', ask_price,
                          qty, fee, round(ask_price * qty, 1), 'arbt')
                save_transaction_history_data(params)
                # buy_btc()
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
                if ticker not in ['BTC', 'ETH']:
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

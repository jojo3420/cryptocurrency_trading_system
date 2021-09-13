import math
import time
import pybithumb
import websockets
import asyncio
import json

from ch06.volatility_breakthrough_trading import *
from common.utils import save_transaction_history_data

BTC_TICKER = 'BTC'
_btc_market_tickers = pybithumb.get_tickers(payment_currency=BTC_TICKER)
btc_market_tickers = [f'{ticker}_BTC' for ticker in _btc_market_tickers]


async def bithumb_ws_client():
    """
    api doc: https://apidocs.bithumb.com/docs/websocket_public
    :return:
    """

    uri = 'wss://pubwss.bithumb.com/pub/ws'
    async with websockets.connect(uri, ping_interval=None) as socket:
        response = await socket.recv()
        # trader_system = TradingSystem()
        print(f'response: {response}')
        subscribe_fmt = {
            # 티커
            # 'type': 'ticker',
            # 'symbols': ['BTC_KRW'],
            # 'symbols': btc_market_tickers,
            # 'tickTypes': ['30M'],

            # 변경 호가
            # 'type': 'orderbookdepth',
            # 'symbols': ['BTC_KRW'],

            # 체결
            "type": "transaction",
            "symbols": btc_market_tickers

        }
        subscribe_json = json.dumps(subscribe_fmt)
        await socket.send(subscribe_json)

        while True:
            raw_data: 'json' = await socket.recv()
            data: dict = json.loads(raw_data)
            # print(data)
            content = data.get('content', '')
            # print(content)
            if content:
                temp_list = content.get('list', [])
                # print(len(temp_list))
                if len(temp_list) > 0:
                    transaction = temp_list[0]
                    symbol = transaction.get('symbol', '')
                    btc_market_contract_price = float(transaction.get('contPrice', 0))
                    analysis_transaction(symbol, btc_market_contract_price)


async def main():
    await bithumb_ws_client()


def restfull_buy_main():
    while True:
        try:
            # BTC 풀매수
            total_krw, used = get_krw_balance()
            krw = total_krw - used
            if krw >= 100000:
                print(f'원화 잔고: {krw:,.0f}')
                order_book = pybithumb.get_orderbook(BTC_TICKER)
                bids = order_book.get('bids', [])
                bid = bids[0].get('price', 0)
                quantity = calc_buy_quantity(BTC_TICKER, krw)
                print(f'qty: {quantity}')
                order_desc = buy_limit_price('BTC', bid, quantity)
                print(f'BTC 매수주문결과: {order_desc}')

            tickers = pybithumb.get_tickers(payment_currency=BTC_TICKER)
            for ticker in tickers:
                # print(ticker)
                symbol = f'{ticker}_BTC'
                btc_curr_price = pybithumb.get_current_price(ticker, payment_currency='BTC')
                # print(symbol, btc_curr_price)
                analysis_transaction(symbol, btc_curr_price)
                time.sleep(1)
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            time.sleep(3)


def get_btc_balance():
    """ BTC 잔고 조회 """
    btc_balance, used = get_balance_coin(BTC_TICKER)
    btc_balance = (btc_balance - used) - 0.00001059
    btc_qty = round(btc_balance, 8)
    return btc_qty


def analysis_transaction(symbol: str, btc_market_contract_price: float):
    """

    :param symbol: buy_ticker_payment_currency(BTC) 형식 ex)XRP_BTC
    :param btc_market_contract_price: 매수할 코인 체결 가격(BTC)
    :return:
    """
    type = 'arbt'
    btc_qty = get_btc_balance()
    ticker, payment_currency = symbol.split('_')
    # print(ticker)

    btc_curr_price = pybithumb.get_current_price(BTC_TICKER)
    btc_converted_krw_price = btc_market_contract_price * btc_curr_price
    krw_market_curr_price = pybithumb.get_current_price(ticker)
    if isinstance(krw_market_curr_price, dict):
        return
    else:
        print(f'원화 환산: {btc_converted_krw_price:,.2f} 원화 가격: {krw_market_curr_price:,.2f}')
        diff_percent = (krw_market_curr_price / btc_converted_krw_price - 1) * 100
        print(f'{round(diff_percent, 2)}%')
        if diff_percent >= 7:
            # BTC 마켓에서 매수후 원화로 팔기
            print('차이 갭 발생!', ticker)
            # 매수 호가, 매수호가 1단계 위, 매수호가 2단계 위 => 3건 매수 건다.
            if btc_qty > 0:
                qty = calc_buy_quantity(ticker, order_btc=btc_qty, market=payment_currency)
                print(f'qty: {qty}')
                qty = round(qty / 1, 4)
                print(f'after qty: {qty}')
                entry_price, order_desc = buy_or_cancel_btc_market(ticker, qty, delay=5, is_uptic=True)
                print(f'진입가: {entry_price}, 주문결과: {order_desc}')
                if entry_price and order_desc:
                    print(f'진입 BTC: {entry_price:.8f} ')
                    target_coin_qty, _ = get_balance_coin(ticker)
                    print(f'주문정보: {order_desc}, 현재 전체 수량: {target_coin_qty}')
                    save_bought_list((ticker, order_desc[2], type))
                    #               ' (order_no, date, ticker, position, price, ' \
                    #               'quantity, fee, transaction_krw_amount, type)' \
                    fee = round(entry_price * qty * 0.0025, 3)
                    params = (
                        order_desc[2], get_today_format(), ticker, 'bid', entry_price,
                        qty, fee, btc_converted_krw_price, type)
                    save_transaction_history_data(params)
            else:
                # BTC 잔고 부족하여 BTC 충전하기
                while True:
                    total_krw, used = get_krw_balance()
                    available = total_krw - used
                    if available <= 0 and available <= 10000:
                        break
                    entry_price, order_desc = buy_or_cancel_krw_market(BTC_TICKER, available)
                    if entry_price and order_desc:
                        btc_qty = get_btc_balance()
                        print(f'BTC잔고: {format(btc_qty, ".8f")}')

        elif diff_percent <= -7:
            print('원화로 매수후 비트코인 마켓에서 코인 매도')
            total_cash, used = get_krw_balance()
            krw_size = total_cash - used
            qty = calc_buy_quantity(ticker, order_krw=krw_size)
            entry_price, order_desc = buy_or_cancel_krw_market(ticker, position_size_cash=krw_size, is_uptic=True)
            print(f'원화 매수 => entry_price: {entry_price}, order_desc: {order_desc}')
            if entry_price and order_desc:
                #  ' (order_no, date, ticker, position, price, ' \
                #  'quantity, fee, transaction_krw_amount, type)' \
                fee = round(entry_price * qty * 0.0025, 3)
                params = (
                    order_desc[2], get_today_format(), ticker, 'bid', entry_price,
                    qty, fee, btc_converted_krw_price, type)
                save_transaction_history_data(params)
            else:
                print(f'krw 매수주문 실패 {ticker}')

        print('-' * 80)


if __name__ == '__main__':
    # asyncio.run(main())
    restfull_buy_main()

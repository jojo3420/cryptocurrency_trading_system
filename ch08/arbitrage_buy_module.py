import math
import time
import pybithumb
import websockets
import asyncio
import json

from ch06.volatility_breakthrough_trading import *
# from common.bithumb_api import *
from common.math_util import get_uptic_price, get_downtic_price

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
            tickers = pybithumb.get_tickers(payment_currency=BTC_TICKER)
            for ticker in tickers:
                # print(ticker)
                symbol = f'{ticker}_BTC'
                btc_curr_price = pybithumb.get_current_price(ticker, payment_currency='BTC')
                print(symbol, btc_curr_price)
                analysis_transaction(symbol, btc_curr_price)
                time.sleep(1)
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            time.sleep(3)


def analysis_transaction(symbol: str, btc_market_contract_price: float):
    """

    :param symbol: buy_ticker_payment_currency(BTC) 형식 ex)XRP_BTC
    :param btc_market_contract_price: 매수할 코인 체결 가격(BTC)
    :return:
    """
    type = 'arbt'
    btc_balance, used = get_balance_coin(BTC_TICKER)
    btc_balance = (btc_balance - used) - 0.00001059
    btc_qty = round(btc_balance, 8)
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
        if diff_percent >= 4:
            # BTC 마켓에서 매수후 원화로 팔기
            print('차이 갭 발생!', ticker)
            order_book = pybithumb.get_orderbook(ticker, payment_currency=payment_currency)
            # print(order_book)
            # 매수 호가, 매수호가 1단계 위, 매수호가 2단계 위 => 3건 매수 건다.
            if btc_qty > 0:
                qty = calc_buy_quantity(ticker, order_btc=btc_qty, market=payment_currency)
                print(f'qty: {qty}')
                qty = round(qty / 1, 4)
                print(f'after qty: {qty}')
                entry_price, order_desc = buy_or_cancel_btc_market(ticker, qty, delay=5, is_uptic=True)
                if entry_price and order_desc:
                    print(f'진입 BTC: {entry_price:.8f} ')
                    target_coin_qty, _ = get_balance_coin(ticker)
                    print(f'주문정보: {order_desc}, 현재 전체 수량: {target_coin_qty}')
                    save_bought_list((ticker, order_desc[2], type))
                    params = (
                        order_desc[2], get_today_format(), ticker, 'bid', entry_price,
                        qty, 0.001, btc_converted_krw_price, type)
                    save_transaction_history(params)
        elif diff_percent <= -5:
            print('원화로 매수후 비트코인 마켓에서 코인 매도')
            # total_cash, used = get_krw_balance()
            # cash = total_cash - used
            # print(cash, cash / 2)
            # entry_price, order_desc = buy_or_cancel_krw_market(ticker, position_size_cash=cash/2,
            #                                                is_uptic=True)
            # print(f'entry_price: {entry_price}, order_desc: {order_desc}')
        print('-' * 80)


def save_transaction_history(params: tuple) -> None:
    """
    주문 거래 내역 저장하기 DB
    """
    try:
        sql = 'INSERT INTO coin_transaction_history ' \
              ' (order_no, date, ticker, position, price, ' \
              'quantity, fee, transaction_krw_amount, type)' \
              ' VALUES (%s, %s, %s, %s, %s,' \
              '          %s, %s, %s %s)'
        mutation_db(sql, params)
    except Exception as e:
        log(f' save_transaction_history() 예외발생.. 매수실패 {str(e)}')
        traceback.print_exc()


if __name__ == '__main__':
    # asyncio.run(main())
    restfull_buy_main()

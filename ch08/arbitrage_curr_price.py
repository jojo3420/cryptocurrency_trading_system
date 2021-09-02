import math
import time
import pybithumb
import websockets
import asyncio
import json


from common.bithumb_api import buy_limit_price, get_my_coin_balance, cancel_order, calc_buy_quantity, get_krw_balance, sell_limit_price, get_balance_coin
from common.math_util import get_uptic_price

_btc_market_tickers = pybithumb.get_tickers(payment_currency='BTC')
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
            # print(raw_data)
            data: dict = json.loads(raw_data)
            # print(isinstance(data, dict))
            # print(data)
            analysis_transaction(data)


async def main():
    await bithumb_ws_client()


def analysis_transaction(data: dict):
    # total_cash, used_cash = get_krw_balance()
    # cash = total_cash - used_cash
    # cash = cash / 4
    # TODO BTC 잔고 확보해야


    content = data.get('content', '')
    # print(content)
    if content:
        temp_list = content.get('list', [])
        # print(len(temp_list))
        if len(temp_list) > 0:
            transaction = temp_list[0]
            symbol = transaction.get('symbol', '')
            ticker, payment_currency = symbol.split('_')
            print(ticker)
            btc_market_contract_price = float(transaction.get('contPrice', 0))
            btc_curr_price = pybithumb.get_current_price('BTC')
            btc_converted_krw_price = btc_market_contract_price * btc_curr_price
            krw_market_curr_price = pybithumb.get_current_price(ticker)
            if isinstance(krw_market_curr_price, dict):
                return
            else:
                print(f'원화 환산: {btc_converted_krw_price:,.2f} 원화 가격: {krw_market_curr_price:,.2f}')
                print('-' * 80)
                diff_percent = (krw_market_curr_price / btc_converted_krw_price - 1) * 100
                print(diff_percent)
                if diff_percent >= 2:
                    print('차이 갭 발생!', ticker)
                    order_book = pybithumb.get_orderbook(ticker, payment_currency='BTC')
                    print(order_book)
                    # 매수 호가, 매수호가 1단계 위, 매수호가 2단계 위
                    # 3건 매수 건다.
                    order_book = pybithumb.get_orderbook(ticker)
                    print(order_book)
                    # bids = order_book['bids']  # 매수호가
                    # upest_price = bids[0].get('price')
                    # uptic_price1 = get_uptic_price(upest_price, 1)
                    # uptic_price2 = get_uptic_price(upest_price, 2)
                    # step_one_buy_price = float(upest_price)

                    # qty = calc_buy_quantity(ticker, order_krw=cash)
                    # qty = round(qty / 3, 6)
                    # order_response = []
                    # for price in [uptic_price1, uptic_price2, step_one_buy_price]:
                    #     # TODO: btc market buy logic!
                    #     order_desc = buy_limit_price(ticker, price, qty, market='BTC')
                    #     print(order_desc)
                    #     order_response.append(order_desc)
                    #
                    # time.sleep(3)
                    #
                    # coin_qty, _ = get_my_coin_balance(ticker)
                    # if coin_qty == 0:
                    #     for order_desc in order_response:
                    #         r = cancel_order(order_desc)
                    #         if r is True:
                    #             print(f'{order_desc} 주문 취소!')
                    #
                    # elif coin_qty > 0:
                    #     # TODO sell logic
                    #     sell_limit_price(ticker, price, coin_qty)
                    #
                    #
                    #
                    #









if __name__ == '__main__':
    asyncio.run(main())

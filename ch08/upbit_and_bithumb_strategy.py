import time
import pyupbit
import pybithumb
import math
from datetime import datetime
from common.bithumb_api import get_krw_balance, calc_buy_quantity, buy_limit_price, get_my_coin_balance, \
    get_coin_quantity, sell_limit_price


def calc_diff_seconds(time_tm1: datetime, time_tm2: datetime):
    diff = time_tm1 - time_tm2
    return diff.total_seconds()


def log(message, *args, **kwargs):
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{now_str}] {message}')
    if args:
        print(f'args: {args}')
    if kwargs:
        print(f'kwargs: {kwargs}')


def read_keys(filepath):
    key_dict = {}
    try:
        with open(filepath) as stream:
            for line in stream:
                k, v = line.strip().split('=')
                key_dict[k] = v
        return key_dict
    except FileNotFoundError:
        print('File Not Found!')


log('프로그램 시작')
# upbit
_upbit_krw_tickers = pyupbit.get_tickers(fiat='KRW')
upbit_krw_tickers = [ticker.replace('KRW-', '') for ticker in _upbit_krw_tickers]
_upbit_btc_tickers = pyupbit.get_tickers(fiat='BTC')
upbit_btc_tickers = [ticker.replace('BTC-', '') for ticker in _upbit_btc_tickers]

# bithumb
bithumb_krw_tickers = pybithumb.get_tickers(payment_currency='KRW')
bithumb_btc_tickers = pybithumb.get_tickers(payment_currency='BTC')

common_krw_tickers = list(set(bithumb_krw_tickers).intersection(set(upbit_krw_tickers)))
common_btc_tickers = list(set(bithumb_btc_tickers).intersection(set(upbit_btc_tickers)))
print(f'원화마켓 공통 코인갯수: {len(common_krw_tickers)}, BTC마켓 공통 코인갯수:{len(common_btc_tickers)}')

_now = datetime.now()
t1_tm = _now.replace(hour=8, minute=59, second=0, microsecond=0)
t2_tm = _now.replace(hour=8, minute=59, second=58, microsecond=0)

while True:
    log('프로그램 재시작!')
    today_tm = datetime.now()
    if today_tm < t1_tm:
        diff_seconds = calc_diff_seconds(t1_tm, today_tm)
        log(f'8:59:00 까지 대기하기 => {diff_seconds}')
        time.sleep(diff_seconds)

    log('1차 시세 데이터 수집')
    before_tm = datetime.now()
    upbit_price_history = {}
    bithumb_price_history = {}
    for ticker in common_krw_tickers:
        ticker = 'KRW-' + ticker
        upbit_price_history[ticker] = pyupbit.get_current_price(ticker)
        bithumb_price_history[ticker] = pybithumb.get_current_price(ticker)
        time.sleep(0.05)
    # print(symbols)

    # for ticker in common_btc_tickers:
    #     ticker = 'BTC-' + ticker
    #     curr_price = pyupbit.get_current_price(ticker)
    #     symbols[ticker] = curr_price
    #     time.sleep(0.05)
    print('-' * 80)

    today_tm = datetime.now()
    if today_tm < t2_tm:
        diff_seconds = calc_diff_seconds(t2_tm, today_tm)
        log(f'8:59:58 까지 대기하기 => {diff_seconds}')
        time.sleep(diff_seconds)

    log('2차 시세 데이터 수집')
    result = []
    for ticker, prev_price in upbit_price_history.items():
        curr_price = pyupbit.get_current_price(ticker)
        if prev_price and curr_price:
            yields = (curr_price / prev_price - 1) * 100
            # log(f'{ticker} yields: {yields:.4f}')
            if yields > 5.0:
                result.append((ticker, yields))
        time.sleep(0.05)
    log('2차 데이터 수집 완료!')

    log('수익률 5% 이상 급등 코인 목록', result)
    result.sort(key=lambda tup: tup[1], reverse=True)
    print('정렬완료 => ', result)
    result = result[0: 3]
    print('Top3', result)

    total_krw, used_krw = get_krw_balance()
    total_cash = total_krw - used_krw
    print(f'cash: {total_cash:,.0f}')
    # buy bithumb
    bought_history = {}
    if len(result) > 2:
        position_size = total_cash / 3
    else:
        position_size = total_cash / (len(result) | 1)

    if position_size > 0:
        for symbol, yields in result:
            log(f'buy -> {symbol} yield: {yields}')
            sym = symbol.split('-')
            payment_currency = sym[0]
            ticker = sym[1]
            qty = calc_buy_quantity(ticker, order_krw=position_size)
            orderbook = pybithumb.get_orderbook(ticker, payment_currency=payment_currency)
            asks = orderbook['asks']
            if asks and len(asks) > 0:
                buy_wish_price = int(asks[1]['price'])
                log(f'매수호가: {buy_wish_price} 수량: {qty}')
                prev_bithumb_price = bithumb_price_history[ticker]
                gap_yields = (buy_wish_price / prev_bithumb_price -1) * 100
                # 빗썸에서도 따라서 상승중 이면 매수!
                if gap_yields >= 2.5:
                    order_desc = buy_limit_price(ticker, price=buy_wish_price, quantity=qty)
                    log(order_desc)
                    if isinstance(order_desc, tuple):
                        bought_history[ticker] = buy_wish_price
    else:
        log('코인당 투자 캐쉬:', position_size)

    bought_coins = get_my_coin_balance()
    log(f'bought_coins: {bought_coins}')
    log(f'bought_history: {bought_history}')
    time.sleep(2)

# while len(bought_coins := get_my_coin_balance()) > 0:
#     for ticker, (_total, _used, available) in bought_coins.items():
#         print(f'{ticker}, 수량: {available}')
#         current_price = pybithumb.get_current_price(ticker)
#         bought_price = bought_history.get(ticker, 0)
#         # print(current_price, bought_price)
#         # if bought_price == 0:
#         #     bought_price = get_bought_price(ticker)
#         if current_price and bought_price:
#             curr_yields = (curr_price / bought_price - 1) * 100
#             if curr_yields > 7.0:
#                 qty = get_coin_quantity(ticker)
#                 qty = qty[0] - qty[1]
#                 order_book = pybithumb.get_orderbook(ticker)
#                 print(order_book)
#                 bids = order_book['asks']
#                 sell_wish_price = int(bids[0]['price'])
#                 print(qty, sell_wish_price, type(sell_wish_price), type(qty))
#                 order_desc = sell_limit_price(ticker, price=sell_wish_price, quantity=qty)
#                 print(order_desc)
#                 # ('ask', 'ADA', 'C0150000000176084876', 'KRW')
#                 # order_id = order_desc[2]

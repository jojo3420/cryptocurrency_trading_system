import time
import pyupbit
import pybithumb
import math
from datetime import datetime
import sys

sys.path.extend(['/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system'])
from common.telegram_bot import send_coin_bot
from common.utils import mutation_db, get_today_format, select_db
from common import bithumb_api


def calc_diff_seconds(time_tm1: datetime, time_tm2: datetime):
    diff = time_tm1 - time_tm2
    return diff.total_seconds()


def log(message, *args, **kwargs):
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    args_str = ''
    for arg in args:
        args_str += str(arg) + ' '
    kwargs_str = ''
    for k, v in kwargs.items():
        kwargs_str += k + ': ' + str(v)
    print(f'[{now_str}] {message} {args_str if args_str else ""} {kwargs_str if kwargs_str else ""}')


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


def save_bought_coin(order_no, ticker):
    """
    매수한 종목 기록
    :param order_no:
    :param ticker:
    :return:
    """
    today = get_today_format()
    sql = f"INSERT INTO coin_bought_list " \
          f" (order_no, date, ticker, type, is_sell)" \
          f" VALUES (%s, %s, %s, %s, %s) "
    mutation_db(sql, (order_no, today, ticker, 'trnd', False))


def get_bought_coin(ticker) -> str:
    """ 현재 보유한 종목의 order_no 리턴 """
    sql = f'SELECT order_no FROM coin_bought_list ' \
          f' WHERE ticker = %s AND is_sell = %s AND type = %s'
    temp_t = select_db(sql, (ticker, False, 'trnd'))
    if temp_t:
        return temp_t[0][0]


def get_bought_coin_detail_info(order_no, ticker) -> tuple:
    sql = f'SELECT price, quantity FROM coin_transaction_history' \
          f' WHERE order_no = %s AND ticker = %s'
    temp_t = select_db(sql, (order_no, ticker))
    print(temp_t)
    if temp_t:
        price, quantity = temp_t[0]
        return price, quantity


log('프로그램 시작')
# upbit
_upbit_krw_tickers = pyupbit.get_tickers(fiat='KRW')
upbit_krw_tickers = [ticker.replace('KRW-', '') for ticker in _upbit_krw_tickers]
# _upbit_btc_tickers = pyupbit.get_tickers(fiat='BTC')
# upbit_btc_tickers = [ticker.replace('BTC-', '') for ticker in _upbit_btc_tickers]

# bithumb
bithumb_krw_tickers = pybithumb.get_tickers(payment_currency='KRW')
# bithumb_btc_tickers = pybithumb.get_tickers(payment_currency='BTC')

common_krw_tickers = list(set(bithumb_krw_tickers).intersection(set(upbit_krw_tickers)))
# common_btc_tickers = list(set(bithumb_btc_tickers).intersection(set(upbit_btc_tickers)))
print(f'원화마켓 공통 코인갯수: {len(common_krw_tickers)}')
buy_target_coin_list = []
upbit_price_history = {}
bithumb_price_history = {}

while True:
    log('프로그램 재시작!')
    buy_target_coin_list.clear()  # 매수 희망종목 리스트 비움
    upbit_price_history.clear()  # 매수 희망종목 리스트 비움
    bithumb_price_history.clear()  # 매수 희망종목 리스트 비움
    log('1차 시세 데이터 수집')

    for clear_ticker in common_krw_tickers:
        symbol = 'KRW-' + clear_ticker
        upbit_price_history[symbol] = pyupbit.get_current_price(symbol)
        bithumb_price_history[symbol] = pybithumb.get_current_price(clear_ticker)
        time.sleep(0.05)
    print(upbit_price_history)
    print(bithumb_price_history)

    # for ticker in common_btc_tickers:
    #     ticker = 'BTC-' + ticker
    #     curr_price = pyupbit.get_current_price(ticker)
    #     symbols[ticker] = curr_price
    #     time.sleep(0.05)

    print('1차 싯세 데이터 수집 완료')
    print('-' * 80)
    log('59 초 대기....')
    time.sleep(59)
    # time.sleep(59)
    log('2차 시세 데이터 수집')
    for ticker, prev_price in upbit_price_history.items():
        curr_price = pyupbit.get_current_price(ticker)
        if prev_price and curr_price:
            yields = (curr_price / prev_price - 1) * 100
            # log(f'{ticker} yields: {yields:.4f}')
            if yields > 5.0:
                buy_target_coin_list.append((ticker, yields))
        time.sleep(0.05)
    log('2차 데이터 수집 완료!')

    log(f'수익률 5% 이상 급등 코인 목록, {buy_target_coin_list}')
    buy_target_coin_list.sort(key=lambda tup: tup[1], reverse=True)
    log(f'정렬완료 => {buy_target_coin_list}')
    buy_target_coin_list = buy_target_coin_list[0: 3]
    log(f'상승률 Top3 추림: {buy_target_coin_list}')

    total_krw, used_krw = bithumb_api.get_krw_balance()
    total_cash = total_krw - used_krw
    if len(buy_target_coin_list) > 2:
        position_size = total_cash / 3
    else:
        position_size = total_cash / (len(buy_target_coin_list) | 1)
    print(f'total_cash: {total_cash:,.0f}, position_size: {position_size:,.0f}')

    if position_size > 0 and len(buy_target_coin_list) > 0:
        for symbol, yields in buy_target_coin_list:
            log(f'buy -> {symbol} yield: {yields}')
            sym = symbol.split('-')
            payment_currency = sym[0]
            clear_ticker = sym[1]
            qty = bithumb_api.calc_buy_quantity(clear_ticker, order_krw=position_size)
            orderbook = pybithumb.get_orderbook(clear_ticker, payment_currency=payment_currency)
            asks = orderbook['asks']
            if asks:
                prev_bithumb_price = bithumb_price_history.get(symbol, 1)
                ask_price = int(asks[0]['price'])
                log(f'매도호가: {ask_price} 수량: {qty}')
                if ask_price and prev_bithumb_price:
                    gap_yields = (ask_price / prev_bithumb_price - 1) * 100
                    # 빗썸에서도 따라서 상승중 이면 매수!
                    if gap_yields >= 2.5:
                        order_desc = bithumb_api.buy_limit_price(clear_ticker, price=ask_price, quantity=qty)
                        log(f'order_desc: {order_desc}')
                        if isinstance(order_desc, tuple):
                            send_coin_bot(f'업비트 추세 따라매수 {clear_ticker}, 매수희망가격: {ask_price:,.2f}, 주문수량: {qty} ')
                            save_bought_coin(order_desc[2], clear_ticker)
    else:
        log(f'매수할 종목이 없거나, 캐쉬가 없음! len: {len(buy_target_coin_list)} position_size: {position_size:,.0f}')

    bought_coins = bithumb_api.get_my_coin_balance()
    if bought_coins:
        log(f'bought_coins: {bought_coins}')
    time.sleep(2)
    print('-' * 70)

    for ticker, (_total, _used, available_qty) in bought_coins.items():
        print(f'{ticker}, 매도 주문가능 수량: {available_qty}')
        current_price = pybithumb.get_current_price(ticker)
        order_no = get_bought_coin(ticker)
        bought_price, _quantity = get_bought_coin_detail_info(order_no, ticker)
        print(f'현재시세: {current_price}, 진압가: {bought_price}')
        if current_price and bought_price:
            curr_yields = (curr_price / bought_price - 1) * 100
            if curr_yields > 7.0:
                order_book = pybithumb.get_orderbook(ticker)
                print(order_book)
                asks = order_book['asks']
                ask_price = int(asks[0]['price'])
                print(available_qty, ask_price, type(ask_price), type(available_qty))
                order_desc = bithumb_api.sell_limit_price(ticker, price=ask_price, quantity=available_qty)
                print(order_desc)
                # ('ask', 'ADA', 'C0150000000176084876', 'KRW')

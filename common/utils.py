import os
import pybithumb
import pymysql
import sys
from datetime import datetime, timedelta
import traceback
import time
from pandas import DataFrame, Series
import math


if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
else:
    sys.path.append('/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system')

ymd_format = '%Y-%m-%d'


def create_conn(filepath: str) -> 'conn':
    """ Create DB connect func """
    import constant
    os.chdir(constant.ROOT_DIR)
    config = {}
    try:
        with open(filepath) as stream:
            for line in stream:
                k, v = line.strip().split('=')
                config[k] = v
        config['port'] = int(config['port'])
        conn = pymysql.connect(**config)
        return conn
    except FileNotFoundError:
        print('File Not Found!')


def log(msg, *args, **kwargs) -> None:
    now_tm = datetime.now()
    if args or kwargs:
        print(f'[{now_tm}] {msg} {args} {kwargs}')
    else:
        print(f'[{now_tm}] {msg}')


def mutation_db(sql: str, rows: tuple = None) -> None:
    conn = create_conn('.env')
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, rows)
            conn.commit()
    except Exception as e:
        log(f'DB mutation 예외발생 {str(e)}')
        print(sql, rows)
        traceback.print_exc()
    except TimeoutError:
        print("mutation_db() TimeoutError, sleeping 1second.")
        time.sleep(1)
        mutation_db(sql, rows)
    finally:
        if conn:
            conn.close()


def mutation_many(sql: str, rows: tuple = None) -> None:
    conn = create_conn('.env')
    try:
        with conn.cursor() as cursor:
            cursor.executemany(sql, rows)
            conn.commit()
    except Exception as e:
        log(f'DB mutation_many 예외발생 {str(e)}')
        print(sql, rows)
        traceback.print_exc()
    except TimeoutError:
        print("mutation_db() TimeoutError, sleeping 1 minute.")
        time.sleep(60)
        mutation_many(sql, rows)
    finally:
        if conn:
            conn.close()


def select_db(sql: str, rows: tuple = None) -> tuple:
    conn = create_conn('.env')
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, rows)
            return cursor.fetchall()
    except Exception as e:
        log(f'select_db() 예외발생 {str(e)}')
        print(sql, rows)
        traceback.print_exc()
    except TimeoutError:
        print("select_db() TimeoutError, sleeping 1 minute.")
        time.sleep(60)
        select_db(sql, rows)
    finally:
        if conn:
            conn.close()


def get_today_format(format: str = '%Y-%m-%d') -> str:
    today = datetime.today()
    today = today.strftime(format)
    return today


def calc_williams_R(ticker: str, R: float = 0.5) -> float:
    """
    래리 윌리엄스 변동성 돌파 계산하기
    :param ticker:
    :param R:
    :return: target_price
    """
    df: DataFrame = pybithumb.get_candlestick(ticker)
    # print(df.tail())
    if not df.empty:
        yesterday_s: Series = df.iloc[-2]
        today_s: Series = df.iloc[-1]
        today_open: Series = today_s['open']
        yesterday_high = yesterday_s['high']
        yesterday_low = yesterday_s['low']
        target_price = today_open + ((yesterday_high - yesterday_low) * R)
        if not math.isnan(target_price):
            return int(target_price)
    return None


def calc_moving_average_by(ticker: str, days: int = 3) -> float or None:
    """
     days 이동평균 구하기 (당일 close  계산에 포함)
    """
    try:
        prices: DataFrame = pybithumb.get_candlestick(ticker)
        close: Series = prices['close']
        MA: Series = close.rolling(days).mean()
        # print(MA.tail())
        # 당일값 시세를 반영하려면 당일 close 가격이 포함된 당일 이동평균값 -1 사용!
        # 당일값 시세를 제외하려면 -2 전일 close 가격까지 포함된 전일 이동평균값 -2 사용
        ma_close_price = MA[-1]
        return ma_close_price
    except Exception as e:
        print(str(e))
        traceback.print_exc()


def calc_fix_moving_average_by(ticker: str, days: int = 3) -> float or None:
    """
    기준일 이동평균 구하기 (당일 close 가격 제외한 이동평균)
    :param ticker:
    :param days:
    :return:
    """
    prices: DataFrame = pybithumb.get_candlestick(ticker)
    if not prices.empty:
        close = prices['close']
        # print(close.tail(6))
        MA = close.rolling(window=days).mean()
        # print(MA)
        return MA[-2]
    return None


def calc_now_volatility(ticker: str) -> float:
    """ 당일 코인의 1일 변동성 계산
    :param ticker: 코인티커
       (당일고가 - 당일저가) / 시가  * 100
    """
    prices: 'df' = pybithumb.get_candlestick(ticker)
    if not prices.empty:
        row = prices.iloc[-1]
        open, high, low, close, volume = tuple(row)
        volatility = ((high - low) / open) * 100
        return round(volatility, 4)
    return None


def calc_prev_volatility(ticker: str) -> float:
    """ 전일 코인의 1일 변동성 계산
    :param ticker: 코인티커
       (당일고가 - 당일저가) / 시가  * 100
    """
    prices: 'df' = pybithumb.get_candlestick(ticker)
    if not prices.empty:
        row = prices.iloc[-2]
        open, high, low, close, volume = tuple(row)
        volatility = ((high - low) / open) * 100
        return round(volatility, 4)
    return None


def calc_average_volatility_by_days(ticker: str, days: int) -> float:
    """
    주어진 days 기간의 평균 변동성 계산
    :param ticker: 코인티커
    :param days: 기준 일수
    :return: days 기준 평균 변동성 값(%)
    """
    prices: 'DataFrame' = pybithumb.get_candlestick(ticker)
    if not prices.empty:
        rows = prices.iloc[days * -1:]
        volatility = ((rows['high'] - rows['low']) / rows['open']) * 100
        print(volatility)
        average = volatility.rolling(days).mean()
        print(average)
        return average[-1]
    return None


def remove_peak_log(ticker: str) -> None:
    """
    매도후 peak 로그 삭제
    :param ticker:
    :return:
    """
    sql = 'DELETE FROM peak WHERE ticker = %s'
    mutation_db(sql, ticker)


def get_bought_order_no(ticker: str) -> str or None:
    """
    매수 주문한 식별자 조회
    :param ticker:
    :param today:
    :return:
    """
    sql = 'SELECT order_no FROM coin_bought_list ' \
          ' WHERE is_sell = %s AND ticker = %s'
    temp_t = select_db(sql, (False, ticker))
    if len(temp_t) > 0:
        order_no = temp_t[0][0]
        return order_no


def get_target_price_from(order_no: str, ticker: str) -> int:
    """
     거래내역 테이블에서 윌리엄스 R 가격에 의한 타켓가격 조회
    :param order_no:
    :return:
    """
    # print(f'order_no: {order_no}')
    if order_no:
        sql = "SELECT ticker, target_price FROM coin_transaction_history " \
              " WHERE order_no = %s"
        temp_t = select_db(sql, order_no)
        if temp_t and len(temp_t) > 0:
            ticker, target_price = temp_t[0]
            if target_price:
                return int(target_price)

    return calc_williams_R(ticker, calc_williams_R(ticker, 0.5))


def get_bull_coin_list() -> list:
    """ DB에 저장된 상승중인 코인 목록 리스트로 조회 """
    today = get_today_format()
    sql = 'SELECT ticker, ratio, R FROM bull_coin_list' \
          ' WHERE date = %s ' \
          ' AND disabled = %s ' \
          ' AND already_buy = %s'
    temp_t = select_db(sql, (today, False, False))
    bull_coin_list = []
    bull_ratio_list = []
    bull_r_list = []
    for ticker, ratio, R in temp_t:
        bull_coin_list.append(ticker)
        bull_ratio_list.append(ratio)
        bull_r_list.append(R)

    return bull_coin_list, bull_ratio_list, bull_r_list


def get_daily_profit_list() -> list:
    """
    당일에 청산한 종목 조회
    :return:
    """
    sql = 'SELECT ticker FROM daily_profit_list ' \
          ' WHERE date = %s'
    temp_t = select_db(sql, get_today_format())
    profit_list = [ticker[0] for ticker in temp_t]
    return profit_list


def save_daily_profit_list(ticker, name, yield_ratio):
    """
    당일에 차익실현 장목 저장 목록
    :return:
    """
    sql = 'REPLACE INTO daily_profit_list ' \
          ' (date, ticker, name, yield_ratio) ' \
          ' VALUES (%s, %s, %s, %s) '
    today = get_today_format()
    mutation_db(sql, (today, ticker, name, yield_ratio))


def get_daily_loss_sell_list() -> list:
    """
    당일 손절매 한 종목 리스트
    :return:
    """
    sql = 'SELECT ticker FROM daily_loss_sell_list ' \
          ' WHERE date = %s'
    temp_t = select_db(sql, get_today_format())
    loss_coin_list = [ticker[0] for ticker in temp_t]
    return loss_coin_list


def save_daily_loss_sell_list(ticker, name, yield_ratio):
    """
    당일 손절매 한 코인 DB에 기록
    :return:
    """
    sql = 'REPLACE INTO daily_loss_sell_list ' \
          ' (date, ticker, name, yield_ratio) ' \
          ' VALUES (%s, %s, %s, %s) '
    today = get_today_format()
    mutation_db(sql, (today, ticker, name, yield_ratio))


def save_daily_profit_and_loss():
    """
    거래내역 기준(transaction_history) 당일 매수/매도 기록에 따른
    수익 / 손실 비율 기록
    시스템 종료 시점에 실행
    """

    def _calc(r_tuple: list) -> tuple:
        _r, _sum, _cnt, _avg = [], 0, 0, 0
        for _ticker, _yield_ratio in r_tuple:
            print(_ticker, _yield_ratio)
            _r.append(_yield_ratio)

        if _r:
            _sum = sum(_r)
            _cnt = len(_r)
            _avg = _sum / _cnt
        return _sum, _avg, _cnt

    # 손실 거래내역
    sql = 'SELECT ticker, yield_ratio ' \
          ' FROM coin_transaction_history ' \
          ' WHERE date = %s ' \
          ' AND position = %s ' \
          ' AND type IN (%s, %s)'
    today = get_today_format()
    loss_t = select_db(sql, (today, 'S', '손절매', '반전하락'))
    loss_sum, loss_avg, loss_cnt = _calc(loss_t)

    sql = 'SELECT ticker, yield_ratio ' \
          ' FROM coin_transaction_history ' \
          ' WHERE date = %s' \
          ' AND position = %s ' \
          ' AND type IN (%s, %s, %s)'
    profit_t = select_db(sql, (today, 'S', '시가청산', '당일청산', '상한가도달'))
    profit_sum, profit_avg, profit_cnt = _calc(profit_t)

    simple_total = profit_sum + loss_sum
    print('당일 트레이딩 단순 합계 결과:', simple_total)

    save_sql = ' INSERT INTO daily_profit_and_loss_history ' \
               ' (date, profit_sum, profit_avg, profit_cnt, loss_sum, loss_avg, loss_cnt, simple_total) ' \
               ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    mutation_db(save_sql, (today, profit_sum, profit_avg, profit_cnt, loss_sum, loss_avg, loss_cnt, simple_total))


def calc_target_volatility_ratio(ticker: str, target_loss_ratio=2) -> float:
    """
    목표(허용) 가능한 변동성 수준만큼 투자자산의 전일 변동성에 따른 투자 비율 계산
    허용가능한 손실% / 전일 변동성
    :param ticker:
    :param target_loss_ratio:

    :return:
    """
    prev_volatility = calc_prev_volatility(ticker)
    return round(target_loss_ratio / prev_volatility, 5)


def save_yield_history(total_yield: float, stock_cnt: int) -> None:
    """
    수익률 계산후 저장
     - 주어진 +총수익률에 손절매 합계하여 현재 수익률 DB 저장
    """
    today = get_today_format()
    loss_sql = 'SELECT yield_ratio FROM coin_transaction_history ' \
               ' WHERE date = %s AND position = %s'
    loss_tup = select_db(loss_sql, (today, 'ask'))
    loss_list = [yields[0] for yields in loss_tup]
    total_loss_yield = 0
    if loss_list:
        total_loss_yield = sum(loss_list) / len(loss_list)

    yields = total_yield + total_loss_yield
    sql = 'INSERT INTO coin_yield_timeline ' \
          ' (date, yield_rate, stock_cnt) ' \
          ' VALUES (%s, %s, %s)'
    mutation_db(sql, (today, yields, stock_cnt))


def disabled_buy_wish_list(ticker: str, is_major: bool) -> None:
    if is_major:
        sql = 'UPDATE coin_buy_wish_list ' \
              ' SET is_loss_sell = %s ' \
              ' WHERE ticker = %s '
    else:
        sql = 'UPDATE bull_coin_list ' \
              ' SET disabled = %s ' \
              ' WHERE ticker = %s'
    mutation_db(sql, (True, ticker))


def is_bull_coin(ticker: str) -> bool:
    """
        급등 코인 여부 True/False
    """
    sql = 'SELECT ticker FROM coin_buy_wish_list'
    major_coin_list = select_db(sql)
    if ticker in major_coin_list:
        return True
    return False


def clear_prev_bull_coin_history(date):
    """ 이전 상승코인 목록 삭제  """
    sql = 'DELETE FROM bull_coin_list WHERE date = %s'
    mutation_db(sql, date)


def save_bull_coin(bull_tickers: list) -> None:
    """ 상승 코인 목록 DB 저장"""
    from common.bithumb_api import get_coin_name
    rows = []
    today = get_today_format()
    sql = 'INSERT INTO bull_coin_list ' \
          ' (date, ticker, name, ratio)' \
          ' VALUES (%s, %s, %s, %s)  '
    init_ratio = 0.01
    for ticker in bull_tickers:
        # noise_weight = calc_add_noise_weight(ticker)
        # ratio = calc_target_volatility_ratio(ticker)
        # ratio = init_ratio + (ratio / len(bull_tickers)) + noise_weight
        ratio = 0.03
        rows.append((today, ticker, get_coin_name(ticker), ratio))
    mutation_many(sql, rows)


if __name__ == '__main__':
    # conn = create_conn('.env')
    # print(conn)
    print(get_today_format())

    # print('비트코인 오늘 변동성: ', calc_now_volatility('BTC'))
    # print('비트코인 전일 변동성: ', calc_prev_volatility('BTC'))
    # print('이더리움 오늘 변동성', calc_now_volatility('ETH'))
    # print('이더리움 전일 변동성', calc_prev_volatility('ETH'))
    # order_no = get_bought_order_no('BTC', '2021-06-29')
    # target_price = get_target_price_from(order_no)
    # print(f'{target_price:,}')
    # _loss_target_price = int(round(target_price - (target_price * 0.005), 5))
    # print(f'{_loss_target_price:,}')
    #
    # print(pybithumb.get_orderbook('BTC'))

    # print(calc_fix_moving_average_by('BTC', 3))
    # print(get_bull_coin_list())
    # print(get_bought_order_no('LTC'))
    # print(calc_target_volatility_ratio('SAND'))
    print(is_bull_coin('SAND'))

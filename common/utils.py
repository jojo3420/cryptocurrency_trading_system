import os
import pybithumb
import pymysql
import sys
from datetime import datetime, timedelta
import traceback
import time

if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')

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
    except TimeoutError:
        print("mutation_db() TimeoutError, sleeping 1 minute.")
        time.sleep(60)
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
        log(f'DB mutation 예외발생 {str(e)}')
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
        log(f'DB mutation 예외발생 {str(e)}')
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


if __name__ == '__main__':
    conn = create_conn('.env')
    # print(conn)
    # print(get_today_format())

    print('비트코인 오늘 변동성: ', calc_now_volatility('BTC'))
    print('비트코인 전일 변동성: ', calc_prev_volatility('BTC'))
    print('이더리움 오늘 변동성', calc_now_volatility('ETH'))
    print('이더리움 전일 변동성', calc_prev_volatility('ETH'))

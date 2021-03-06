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
    now_tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if args and kwargs:
        print(f'[{now_tm}] {msg} {args} {kwargs}')
    elif args:
        print(f'[{now_tm}] {msg} {args}')
    elif kwargs:
        print(f'[{now_tm}] {msg} {kwargs}')
    else:
        print(f'[{now_tm}] {msg}')


def mutation_db(sql: str, rows: tuple = None) -> None:
    conn = create_conn('.env')
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, rows)
            conn.commit()
    except Exception as e:
        log(f'DB mutation μμΈλ°μ {str(e)}')
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
        log(f'DB mutation_many μμΈλ°μ {str(e)}')
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
        log(f'select_db() μμΈλ°μ {str(e)}')
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
    λλ¦¬ μλ¦¬μμ€ λ³λμ± λν κ³μ°νκΈ°
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
     days μ΄λνκ·  κ΅¬νκΈ° (λΉμΌ close  κ³μ°μ ν¬ν¨)
    """
    try:
        prices: DataFrame = pybithumb.get_candlestick(ticker)
        close: Series = prices['close']
        MA: Series = close.rolling(days).mean()
        # print(MA.tail())
        # λΉμΌκ° μμΈλ₯Ό λ°μνλ €λ©΄ λΉμΌ close κ°κ²©μ΄ ν¬ν¨λ λΉμΌ μ΄λνκ· κ° -1 μ¬μ©!
        # λΉμΌκ° μμΈλ₯Ό μ μΈνλ €λ©΄ -2 μ μΌ close κ°κ²©κΉμ§ ν¬ν¨λ μ μΌ μ΄λνκ· κ° -2 μ¬μ©
        ma_close_price = MA[-1]
        return ma_close_price
    except Exception as e:
        print(str(e))
        traceback.print_exc()


def calc_fix_moving_average_by(ticker: str, days: int = 3) -> float or None:
    """
    κΈ°μ€μΌ μ΄λνκ·  κ΅¬νκΈ° (λΉμΌ close κ°κ²© μ μΈν μ΄λνκ· )
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
    """ λΉμΌ μ½μΈμ 1μΌ λ³λμ± κ³μ°
    :param ticker: μ½μΈν°μ»€
       (λΉμΌκ³ κ° - λΉμΌμ κ°) / μκ°  * 100
    """
    prices: 'df' = pybithumb.get_candlestick(ticker)
    if not prices.empty:
        row = prices.iloc[-1]
        open, high, low, close, volume = tuple(row)
        volatility = ((high - low) / open) * 100
        return round(volatility, 4)
    return None


def calc_prev_volatility(ticker: str) -> float:
    """ μ μΌ μ½μΈμ 1μΌ λ³λμ± κ³μ°
    :param ticker: μ½μΈν°μ»€
       (λΉμΌκ³ κ° - λΉμΌμ κ°) / μκ°  * 100
    """
    print(f'ticker: {ticker}')
    prices: 'df' = pybithumb.get_candlestick(ticker)
    print(prices)
    if not prices.empty:
        row = prices.iloc[-2]
        open, high, low, close, volume = tuple(row)
        volatility = ((high - low) / open) * 100
        return round(volatility, 4)
    return None


def calc_average_volatility_by_days(ticker: str, days: int) -> float:
    """
    μ£Όμ΄μ§ days κΈ°κ°μ νκ·  λ³λμ± κ³μ°
    :param ticker: μ½μΈν°μ»€
    :param days: κΈ°μ€ μΌμ
    :return: days κΈ°μ€ νκ·  λ³λμ± κ°(%)
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
    λ§€λν peak λ‘κ·Έ μ­μ 
    :param ticker:
    :return:
    """
    sql = 'DELETE FROM peak WHERE ticker = %s'
    mutation_db(sql, ticker)


def get_bought_order_no(ticker: str) -> str or None:
    """
    λ§€μ μ£Όλ¬Έν μλ³μ μ‘°ν
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
     κ±°λλ΄μ­ νμ΄λΈμμ μλ¦¬μμ€ R κ°κ²©μ μν νμΌκ°κ²© μ‘°ν
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
    """ DBμ μ μ₯λ μμΉμ€μΈ μ½μΈ λͺ©λ‘ λ¦¬μ€νΈλ‘ μ‘°ν """
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
    λΉμΌμ μ²­μ°ν μ’λͺ© μ‘°ν
    :return:
    """
    sql = 'SELECT ticker FROM daily_profit_list ' \
          ' WHERE date = %s'
    temp_t = select_db(sql, get_today_format())
    profit_list = [ticker[0] for ticker in temp_t]
    return profit_list


def save_daily_profit_list(ticker, name, yield_ratio):
    """
    λΉμΌμ μ°¨μ΅μ€ν μ₯λͺ© μ μ₯ λͺ©λ‘
    :return:
    """
    sql = 'REPLACE INTO daily_profit_list ' \
          ' (date, ticker, name, yield_ratio) ' \
          ' VALUES (%s, %s, %s, %s) '
    today = get_today_format()
    mutation_db(sql, (today, ticker, name, yield_ratio))


def get_daily_loss_sell_list() -> list:
    """
    λΉμΌ μμ λ§€ ν μ’λͺ© λ¦¬μ€νΈ
    :return:
    """
    sql = 'SELECT ticker FROM daily_loss_sell_list ' \
          ' WHERE date = %s'
    temp_t = select_db(sql, get_today_format())
    loss_coin_list = [ticker[0] for ticker in temp_t]
    return loss_coin_list


def save_daily_loss_sell_list(ticker, name, yield_ratio):
    """
    λΉμΌ μμ λ§€ ν μ½μΈ DBμ κΈ°λ‘
    :return:
    """
    sql = 'REPLACE INTO daily_loss_sell_list ' \
          ' (date, ticker, name, yield_ratio) ' \
          ' VALUES (%s, %s, %s, %s) '
    today = get_today_format()
    mutation_db(sql, (today, ticker, name, yield_ratio))


def save_daily_profit_and_loss():
    """
    κ±°λλ΄μ­ κΈ°μ€(transaction_history) λΉμΌ λ§€μ/λ§€λ κΈ°λ‘μ λ°λ₯Έ
    μμ΅ / μμ€ λΉμ¨ κΈ°λ‘
    μμ€ν μ’λ£ μμ μ μ€ν
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

    # μμ€ κ±°λλ΄μ­
    sql = 'SELECT ticker, yield_ratio ' \
          ' FROM coin_transaction_history ' \
          ' WHERE date = %s ' \
          ' AND position = %s ' \
          ' AND type IN (%s, %s)'
    today = get_today_format()
    loss_t = select_db(sql, (today, 'S', 'μμ λ§€', 'λ°μ νλ½'))
    loss_sum, loss_avg, loss_cnt = _calc(loss_t)

    sql = 'SELECT ticker, yield_ratio ' \
          ' FROM coin_transaction_history ' \
          ' WHERE date = %s' \
          ' AND position = %s ' \
          ' AND type IN (%s, %s, %s)'
    profit_t = select_db(sql, (today, 'S', 'μκ°μ²­μ°', 'λΉμΌμ²­μ°', 'μνκ°λλ¬'))
    profit_sum, profit_avg, profit_cnt = _calc(profit_t)

    simple_total = profit_sum + loss_sum
    print('λΉμΌ νΈλ μ΄λ© λ¨μ ν©κ³ κ²°κ³Ό:', simple_total)

    save_sql = ' INSERT INTO daily_profit_and_loss_history ' \
               ' (date, profit_sum, profit_avg, profit_cnt, loss_sum, loss_avg, loss_cnt, simple_total) ' \
               ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    mutation_db(save_sql, (today, profit_sum, profit_avg, profit_cnt, loss_sum, loss_avg, loss_cnt, simple_total))


def calc_target_volatility_ratio(ticker: str, target_loss_ratio=2) -> float:
    """
    λͺ©ν(νμ©) κ°λ₯ν λ³λμ± μμ€λ§νΌ ν¬μμμ°μ μ μΌ λ³λμ±μ λ°λ₯Έ ν¬μ λΉμ¨ κ³μ°
    νμ©κ°λ₯ν μμ€% / μ μΌ λ³λμ±
    :param ticker:
    :param target_loss_ratio:

    :return:
    """
    prev_volatility = calc_prev_volatility(ticker)
    return round(target_loss_ratio / prev_volatility, 5)


def save_yield_history(total_yield: float, stock_cnt: int) -> None:
    """
    μμ΅λ₯  κ³μ°ν μ μ₯
     - μ£Όμ΄μ§ +μ΄μμ΅λ₯ μ μμ λ§€ ν©κ³νμ¬ νμ¬ μμ΅λ₯  DB μ μ₯
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
        κΈλ± μ½μΈ μ¬λΆ True/False
    """
    sql = 'SELECT ticker FROM coin_buy_wish_list'
    major_coin_list = select_db(sql)
    if ticker in major_coin_list:
        return True
    return False


def clear_prev_bull_coin_history(date):
    """ μ΄μ  μμΉμ½μΈ λͺ©λ‘ μ­μ   """
    sql = 'DELETE FROM bull_coin_list WHERE date = %s'
    mutation_db(sql, date)


def save_bull_coin(bull_tickers: list) -> None:
    """ μμΉ μ½μΈ λͺ©λ‘ DB μ μ₯"""
    from common.bithumb_api import get_coin_name, calc_add_noise_weight
    rows = []
    today = get_today_format()
    sql = 'INSERT INTO bull_coin_list ' \
          ' (date, ticker, name, ratio)' \
          ' VALUES (%s, %s, %s, %s)  '
    init_ratio = 0.01
    for ticker in bull_tickers:
        noise_weight = calc_add_noise_weight(ticker)
        ratio = calc_target_volatility_ratio(ticker)
        position_size = init_ratio + (ratio / len(bull_tickers)) + noise_weight
        # ratio = 0.03
        rows.append((today, ticker, get_coin_name(ticker), position_size))
    mutation_many(sql, rows)


def save_transaction_history_data(params: tuple):
    """
     μ£Όλ¬Έ κ±°λ λ΄μ­ μ μ₯νκΈ° DB
     """
    try:
        sql = 'INSERT INTO coin_transaction_history ' \
              ' (order_no, date, ticker, position, price, ' \
              ' quantity, fee, transaction_krw_amount, type)' \
              ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        mutation_db(sql, params)
    except Exception as e:
        log(f' save_transaction_history() μμΈλ°μ.. λ§€μμ€ν¨ {str(e)}')
        traceback.print_exc()


if __name__ == '__main__':
    # conn = create_conn('.env')
    # print(conn)
    print(get_today_format())

    # print('λΉνΈμ½μΈ μ€λ λ³λμ±: ', calc_now_volatility('BTC'))
    # print('λΉνΈμ½μΈ μ μΌ λ³λμ±: ', calc_prev_volatility('BTC'))
    # print('μ΄λλ¦¬μ μ€λ λ³λμ±', calc_now_volatility('ETH'))
    # print('μ΄λλ¦¬μ μ μΌ λ³λμ±', calc_prev_volatility('ETH'))
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

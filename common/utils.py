import os
import pybithumb
import pymysql
import sys
from datetime import datetime, timedelta
import traceback
import time

# if os.name == 'nt':
#     sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
#     sys.path.append('C:\\source_code\\cryptocurrency_trading_system')


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




if __name__ == '__main__':
    conn = create_conn('.env')
    print(conn)
    print(get_today_format())

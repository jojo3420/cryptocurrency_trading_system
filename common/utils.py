import os
import pybithumb
import pymysql
import sys
from datetime import datetime, timedelta
import traceback

# if os.name == 'nt':
#     sys.path.append('C:\\source_code\\python\\python_stock_data_analysis')
#     sys.path.append('C:\\source_code\\python_stock_data_analysis')

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


def read_bithumb_key(filepath: str) -> dict:
    import constant
    os.chdir(constant.ROOT_DIR)
    key_dict = {}
    try:
        with open(filepath) as stream:
            for line in stream:
                k, v = line.strip().split('=')
                key_dict[k] = v
        return key_dict
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
    finally:
        if conn:
            conn.close()





def get_today_format(format: str = '%Y-%m-%d') -> str:
    today = datetime.today()
    today = today.strftime(format)
    return today

if __name__ == '__main__':
    print('')
    # conn = create_conn('.env')
    # print(conn)
    # key_dict = read_bithumb_key('.env.local')
    # print(key_dict)
    print(get_today_format())

from common.utils import mutation_db, select_db, log, get_today_format
import traceback


def get_buy_wish_list() -> tuple:
    """
    매수 희망 코인 조회
     - 당일 손절매한 종목 재매수 금지!
    :return:
    """
    try:
        sql = 'SELECT ticker, ratio, R ' \
              ' FROM coin_buy_wish_list ' \
              ' WHERE is_active = %s ' \
              ' AND exchange_name = %s ' \
              ' AND is_loss_sell = %s '
        _buy_wish_list: tuple = select_db(sql, (True, 'upbit', False))  # 0.55)
        _coin_buy_wish_list = []
        _coin_ratio_list = []
        _coin_r_list = []
        for _ticker, _ratio, _R in _buy_wish_list:
            _coin_buy_wish_list.append(_ticker)
            _coin_ratio_list.append(_ratio)
            _coin_r_list.append(_R)
        return _coin_buy_wish_list, _coin_ratio_list, _coin_r_list
    except Exception as ex:
        log(f'get_buy_wish_list() 예외발생 {str(ex)}')
        traceback.print_exc()


def save_bought_list(uuid, symbol) -> bool:
    """
    매수한 종목 기록
    :param uuid: 주문 uuid
    :param symbol: KRW-BTC, KRW-ETH, KRW-ADA 형식
    :return: bool
    """
    today = get_today_format()
    sql = f"INSERT INTO coin_bought_list " \
          f" ( order_no, date, ticker, type, is_sell, " \
          f" exchange_name" \
          f" )" \
          f" VALUES ( %s, %s, %s, %s, %s, " \
          f" %s" \
          f") "
    mutation_db(sql, (uuid, today, symbol, 'vol', False,
                      'upbit'
                      )
                )
    return True


def update_bought_list(symbol: str, is_sell=True) -> bool:
    """
    주문한 코인 매수 처리 => coin_buy_wish_list 테이블 매수(True) 처리
    :param ticker:
    :return:
    """
    try:
        sql = 'UPDATE coin_bought_list ' \
              ' SET is_sell = %s ' \
              ' WHERE ticker = %s ' \
              ' AND type = %s AND exchange_name = %s'
        mutation_db(sql, (is_sell, symbol, 'vol', 'upbit'))
        return True
    except Exception as e:
        log(f' update_bought_list() 예외발생.. 매수실패 {str(e)}')
        traceback.print_exc()


def save_transaction_history(data_dict: dict) -> None:
    """
    주문 거래 내역 저장하기 DB
    :param order_desc => order_type, ticker, order_no,
                        currency, price, quantity, target_price, R
    data_dict = {
        'position': side, 'symbol': symbol,
        'uuid': uuid, 'sub_uuid': sub_uuid,
        'price': entry_price, 'quantity': quantity,
        'funds': funds, 'fee': paid_fee,
        'target_price': target_price, 'R': R,
    }
    :return:
    """
    today = get_today_format()
    exchange_name = 'upbit'
    type_str = 'vol'
    try:
        uuid = data_dict.get('uuid', '')
        sub_uuid = data_dict.get('sub_uuid', '')
        symbol = data_dict.get('symbol', '')
        position = data_dict.get('position', '')
        price = data_dict.get('price', '')
        quantity = data_dict.get('quantity', '')
        fee = data_dict.get('fee', '')
        funds = data_dict.get('funds', '')
        if position == 'bid':  # 매수 거래
            sql = 'INSERT INTO coin_transaction_history ' \
                  ' (' \
                  ' order_no, sub_uuid, type, date, ticker, ' \
                  ' position, price, quantity, target_price, stop_loss_price, ' \
                  ' R, fee, transaction_krw_amount, exchange_name, allowable_loss_amount' \
                  ' ) ' \
                  ' VALUES (' \
                  ' %s, %s, %s, %s, %s,' \
                  ' %s, %s, %s, %s, %s,' \
                  ' %s, %s, %s, %s, %s' \
                  ')'
            target_price = data_dict.get('target_price', 0)
            R = data_dict.get('R', 0.5)
            stop_loss_price = data_dict.get('stop_loss_price', 0)
            allowable_loss_amount = data_dict.get('allowable_loss_amount', 0)
            mutation_db(sql, (uuid, sub_uuid, type_str, today, symbol,
                              position, price, quantity, target_price, stop_loss_price,
                              R, fee, funds, exchange_name, allowable_loss_amount)
                        )
        elif position == 'ask':  # 매도 거래
            print('매도거래 =>', data_dict)
            yield_ratio = data_dict.get('yield', 0)
            sql = 'INSERT INTO coin_transaction_history ' \
                  ' (order_no, type, date, ticker, position, ' \
                  ' price, quantity, fee, transaction_krw_amount, yield_ratio,' \
                  ' exchange_name)' \
                  ' VALUES (' \
                  ' %s, %s, %s, %s, %s, ' \
                  ' %s, %s, %s, %s, %s,' \
                  ' %s' \
                  ')'
            mutation_db(sql, (uuid, type_str, today, symbol, position,
                              price, quantity, fee, funds, yield_ratio,
                              exchange_name)
                        )
    except Exception as e:
        log(f' save_transaction_history() 예외발생.. 매수실패 {str(e)}')
        traceback.print_exc()


def get_entry_price(uuid: str) -> int:
    """ 진입가(매수가격) 조회 """
    sql = 'SELECT price FROM coin_transaction_history ' \
          ' WHERE order_no = %s AND position = %s AND exchange_name =%s'
    temp_t = select_db(sql, (uuid, 'bid', 'upbit'))
    if temp_t:
        return temp_t[0][0]
    return 0


def get_entry_order_uuid(symbol: str, is_sell: bool) -> str:
    """ 매수주문 uuid 조회 """
    sql = 'SELECT order_no AS uuid FROM coin_bought_list ' \
          ' WHERE ticker = %s AND is_sell = %s AND exchange_name = %s'
    temp_t = select_db(sql, (symbol, is_sell, 'upbit'))
    if temp_t:
        return temp_t[0][0]


def get_transaction_history(ticker: str, uuid: str) -> tuple:
    """ 거래내역 조회 """
    sql = 'SELECT * FROM coin_transaction_history ' \
          'WHERE ticker = %s AND uuid = %s AND exchange_name = %s '
    temp_t = select_db(sql, (ticker, uuid, 'upbit'))
    if temp_t:
        return temp_t[0]


def get_transaction_history_by_day(day, position):
    sql = 'SELECT * FROM coin_transaction_history ' \
          'WHERE date = %s AND exchange_name = %s' \
          ' AND position = %s'
    temp_t = select_db(sql, (day, 'upbit', position))
    if temp_t:
        return temp_t


def get_bought_list():
    """
    현재 보유한 코인 리스트 조회
    :return:
    """
    sql = "SELECT ticker as symbol FROM coin_bought_list " \
          " WHERE is_sell = %s AND exchange_name = %s " \
          " AND type = %s"
    tickers_tup: tuple = select_db(sql, (False, 'upbit', 'vol'))
    if tickers_tup:
        return [tup[0] for tup in tickers_tup]
    elif isinstance(tickers_tup, tuple) and len(tickers_tup) == 0:
        return []


def get_stop_loss_price_by(ticker: str, position: str):
    type_str = 'vol'
    exchange = 'upbit'
    today = get_today_format()
    sql = "SELECT stop_loss_price FROM coin_transaction_history " \
          " WHERE ticker = %s AND position = %s " \
          " AND type = %s AND exchange_name = %s " \
          " AND date = %s "
    tup = select_db(sql, (ticker, position, type_str, exchange, today))
    if tup:
        return tup[0][0]


def get_telegram_msg():
    """
    텔레그램 메시지 만들기
    :return:
    """
    today = get_today_format()
    print(get_transaction_history_by_day(today, 'bid'))
    print(get_transaction_history_by_day(today, 'ask'))


if __name__ == '__main__':
    print('TEST')
    # 매수 희망 종목 조회
    buy_symbol_list, ratio_list, r_list = get_buy_wish_list()
    print(buy_symbol_list, ratio_list, r_list)
    uuid = get_entry_order_uuid('KRW-XRP', False)
    print(uuid)
    print(get_stop_loss_price_by('KRW-FLOW', 'bid'))
    get_telegram_msg()

import os, sys, time
if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
from datetime import datetime
from pandas import DataFrame, Series
from common import telegram_bot
from common.bithumb_api import *
from common.utils import mutation_db, select_db, get_today_format


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
        target_price = today_open + (yesterday_high - yesterday_low) * R
        return target_price
    return None


def calc_moving_average_by(ticker: str, days: int = 3) -> DataFrame:
    """
     이돌평균 구하기 (변형)
    3일 이동평균: (2일 이동평균값 + 현재가) / 2
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


def save_bought_list(order_desc: tuple) -> None:
    """
      매수한 목록 DB 저장
      :param order_desc = 코인티커, 가격, 수량
      정상 매수 => ('DOGE', 377.4, 9.859565447800742)
      예외 => dict: {status: '5600', msg: '입력값을 확인해주세요'}

    """
    if type(order_desc) is dict:
        print('매수 예외발생 =>', order_desc)
        return
    # print(order_desc)
    _ticker, order_no = order_desc
    sql = f"INSERT INTO coin_bought_list " \
          f" (date, ticker, is_sell, order_no)" \
          f" VALUES (%s, %s, %s, %s) "
    mutation_db(sql, (get_today_format(), _ticker, 0, order_no))


def save_transaction_history(order_desc: list) -> None:
    """
    주문 거래 내역 저장하기 DB
    :param order_desc => order_type, ticker, order_no,
                        currency, price, quantity, target_price, R
    :return:
    """
    order_type = order_desc[0]
    if order_type == 'bid':  # 매수 거래
        order_type, ticker, order_no, currency, price, quantity, target_price, R, fee, transaction_krw_amount = tuple(
            order_desc)
        sql = 'REPLACE INTO coin_transaction_history ' \
              ' (order_no, date, ticker, position, price, quantity, target_price, R, fee, transaction_krw_amount)' \
              ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        mutation_db(sql, (order_no, get_today_format(), ticker, order_type, price, quantity, target_price, R, fee,
                          transaction_krw_amount))
    elif order_type == 'ask':  # 매도 거래
        order_type, ticker, order_no, currency, price, quantity, fee, transaction_krw_amount = tuple(order_desc)
        sql = 'REPLACE INTO coin_transaction_history ' \
              ' (order_no, date, ticker, position, price, quantity, fee, transaction_krw_amount)' \
              ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        mutation_db(sql, (order_no, get_today_format(), ticker, order_type, price, quantity,
                          fee, transaction_krw_amount))


def update_bought_list(ticker: str) -> None:
    """
    주문한 코인 매수 처리 => coin_buy_wish_list 테이블 1 처리
    :param ticker:
    :return:
    """
    sql = 'UPDATE coin_bought_list SET is_sell = 1 ' \
          ' WHERE ticker = %s'
    mutation_db(sql, ticker)


def buy_coin(ticker: str, buy_ratio: float, R: float = 0.5) -> None:
    try:
        if is_in_market(ticker):
            # print('매수 종목 => ' + ticker)
            # 동적으로 매수코인이 변경됨으로서 최소주문갯수 없음..
            # sql = f"SELECT quantity FROM coin_min_order_quantity WHERE ticker = %s"
            # tup: tuple = select_db(sql, ticker)
            # min_order_quantity = tup[0][0]
            # print('min_order_quantity:', min_order_quantity)

            total_krw, used_krw = get_krw_balance()
            buy_cash = total_krw - used_krw
            current_price = pybithumb.get_current_price(ticker)
            # 종목별 주문 금액 계산(원으로 계산됨)
            available_amount = int(buy_cash * buy_ratio)
            buy_qty: float = available_amount / current_price
            # if buy_qty > min_order_quantity:
            if buy_qty > 0:
                target_price = calc_williams_R(ticker, R)
                MA3 = calc_moving_average_by(ticker, 3)
                if (current_price > target_price) and (current_price > MA3):
                    log(f'변동성 돌파 AND 3일 이동평균 돌파 => target_price: {target_price:,}, {buy_qty}개')
                    order_book = pybithumb.get_orderbook(ticker)
                    asks = order_book['asks']
                    ask_price = asks[0]['price']
                    # log(f'ask_price: {ask_price}')
                    # 지정가 주문 api 불안정
                    order_desc: tuple = buy_limit_price(ticker, ask_price, buy_qty)
                    if type(order_desc) is dict and order_desc['status'] != '0000':
                        # 시장가 매수 주문!
                        order_desc: tuple = buy_market_price(ticker, buy_qty)
                    time.sleep(0.5)
                    # order_desc: ('bid', 'KLAY', 'C0538000000004404555', 'KRW')
                    # 체결 정보
                    completed_order: tuple = get_my_order_completed_info(order_desc)
                    # 거래타입, 코인티커, 가격, 수량 ,수수료(krw), 거래금액)
                    order_type, _ticker, price, order_qty, fee, transaction_krw_amount = completed_order
                    # insert bought list
                    save_bought_list((ticker, order_desc[2]))
                    order_desc = list(order_desc)
                    order_desc.extend([price, order_qty, target_price, R, fee, transaction_krw_amount])
                    save_transaction_history(order_desc)
                    log(f'매수주문성공: {order_desc[2]}')
                    msg = f'[매수알림] {ticker} \n' \
                          f'가격: {price} 수량: {round(buy_qty, 4)}개'
                    telegram_bot.send_coin_bot(msg)
                else:
                    log(f'변동성 돌파 하지 못함: {ticker}')
            else:
                print(f'{ticker} 주문가능 수량이 부족합니다.')
    except Exception as e:
        log(f' sell_all() 예외발생.. 매도실패 {str(e)}')
        sys.exit(0)


def sell_all():
    """
    보유 코인 다음날 시가 청산
    :return:
    """
    try:
        while True:
            sql = 'SELECT ticker FROM coin_bought_list WHERE is_sell = 0'
            bought_list: tuple = select_db(sql)
            _coin_bought_list = [t[0] for t in bought_list]

            if len(_coin_bought_list) == 0:
                log('매도할 코인 없음 => 종료')
                return True

            for ticker in _coin_bought_list:
                total_qty, used_qty = get_coin_quantity(ticker)
                coin_quantity = total_qty - used_qty
                if coin_quantity > 0:
                    log(f'sell() => {ticker} {coin_quantity}개')
                    order_desc: tuple = sell_market_price(ticker, coin_quantity)
                    log(f'매도 주문 성공,  order_no: {order_desc[2]}')
                    update_bought_list(ticker)
                    order_completed_info: tuple = get_my_order_completed_info(order_desc)
                    order_type, _ticker, price, order_qty, fee, transaction_krw_amount = order_completed_info
                    order_desc: list = list(order_desc)
                    order_desc.extend([price, coin_quantity, fee, transaction_krw_amount])
                    save_transaction_history(order_desc)

                    msg = f'[청산 매도알림] {ticker} \n' \
                          f'가격: {price} 수량: {round(order_qty, 4)}개'
                    telegram_bot.send_coin_bot(msg)
                    time.sleep(1)
            time.sleep(0.5)
    except Exception as e:
        log(f' sell_all() 예외발생.. 매도실패 {str(e)}')
        sys.exit(0)


def sell(ticker, quantity) -> bool:
    """
    [공통] 매도하기
        1) 정상매도
        sell() => XRP 2.0개
        매도 주문 요청, order_desc: ('ask', 'XRP', 'C0106000000241177536', 'KRW')

        2) 매도실패 - 보유수랑 없음
        매도 주문 요청,  order_desc: {'status': '5500', 'message': 'Invalid Parameter'}
        체결된 주문 내역 조회 실패 => 'NoneType' object is not subscriptable
        sell() 예외발생! e =>cannot unpack non-iterable NoneType object
    :param ticker:
    :param quantity:
    :return:
    """
    log(f'sell() => {ticker} {quantity}개')
    try:
        order_desc: tuple = sell_market_price(ticker, quantity)
        time.sleep(0.1)
        log(f'매도 주문 요청,  order_desc: {order_desc}')
        if type(order_desc) is tuple and order_desc[2]:
            update_bought_list(ticker)
            order_completed_info: tuple = get_my_order_completed_info(order_desc)
            order_type, _ticker, price, order_qty, fee, transaction_krw_amount = order_completed_info
            order_desc: list = list(order_desc)
            order_desc.extend([price, quantity, fee, transaction_krw_amount])
            save_transaction_history(order_desc)
            msg = f'[매도알림] {ticker} \n' \
                  f'가격: {price} 수량: {order_qty}개'
            telegram_bot.send_coin_bot(msg)
            return True
    except Exception as e:
        log(f'sell() 예외발생! e =>{str(e)}')
        traceback.print_exc()
        return False


def loss_sell(ticker: str):
    """
    손절매 시장가 매도하기
    :param ticker:
    :return:
    """
    if is_in_market(ticker):
        total_qty, used_qty = get_coin_quantity(ticker)
        quantity = total_qty - used_qty
        coin_yield = get_yield(ticker)
        if (quantity > 0) and (coin_yield < -2.0):
            log(f'{ticker} 손실발생 => {coin_yield}%')
            sell(ticker, quantity)


def get_yield(ticker: str) -> float:
    # 매수가격 확인 - DB
    try:
        # total_coin, used_coin = get_coin_quantity(ticker)
        sql = 'SELECT order_no FROM coin_bought_list ' \
              ' WHERE is_sell = 0 AND ticker = %s'
        result: tuple = select_db(sql, ticker)
        if len(result) > 0:
            order_no = result[0][0]
            sql = 'SELECT position, ticker, order_no FROM coin_transaction_history ' \
                  ' WHERE ticker = %s AND order_no = %s'
            result: tuple = select_db(sql, (ticker, order_no))
            # print(result)
            if len(result) > 0:
                order_desc = list(result[0])
                order_desc.append('KRW')
                trans_buy_info: tuple = get_my_order_completed_info(tuple(order_desc))
                # print(trans_buy_info)  # ('bid', 'ETH', 2991000.0, 0.0013, 9.72, 3888)
                order_type, _ticker, price, quantity, fee, trans_krw_amount = trans_buy_info
                current_price = bithumb.get_current_price(ticker)
                yield_rate = (current_price / price - 1) * 100
                # log(f'{ticker} 수익률: {round(yield_rate, 2)}%')
                return round(yield_rate, 3)
        else:
            return 0
    except Exception as e:
        log(f' get_yield() 예외발생.. {str(e)}')


def check_loss(ticker: str, loss_ratio: float = -2.0) -> bool:
    # print(f'손절매 대상 확인: {ticker}')
    try:
        yield_rate: float = get_yield(ticker)
        if yield_rate < loss_ratio:
            log(f'마이너스 수익률 발생 => {ticker} {yield_rate}%')
            return True
        return False
    except Exception as e:
        log(f' get_yield() 예외발생.. {str(e)}')


def send_report() -> None:
    """ 텔레그램 봇 수익률 메시지 전송 """
    sql = 'SELECT ticker FROM coin_bought_list WHERE is_sell = 0'
    _bought_list: tuple = select_db(sql)
    _coin_bought_list = [t[0] for t in _bought_list]
    msg = f'[가상화폐 수익률 알림] \n'
    for _ticker in _coin_bought_list:
        yield_rate: float = get_yield(_ticker)
        msg += f'{_ticker} {yield_rate}% \n'

    if len(_coin_bought_list) == 0:
        msg += '보유 코인 없음'
    telegram_bot.send_coin_bot(msg)


def profit_take_sell(take_yield=10.0):
    """
    트레일 - 이익 보전 익절 매도
    """
    log(f'이익 보전 익절 매도: {take_yield}%')
    sql = 'SELECT ticker FROM coin_bought_list ' \
          ' WHERE is_sell = %s AND date = %s'
    _bought_list: tuple = select_db(sql, (0, get_today_format()))
    _coin_bought_list = [t[0] for t in _bought_list]
    for _ticker in _coin_bought_list:
        yield_rate: float = get_yield(_ticker)
        if take_yield < yield_rate:
            total_qty, used_qty = get_coin_quantity(ticker)
            quantity = total_qty - used_qty
            if quantity > 0:
                sell(ticker, quantity)
                time.sleep(0.5)
        time.sleep(0.5)

    for _ticker in _coin_bought_list:
        sql = 'SELECT R FROM coin_buy_wish_list WHERE ticker = %s'
        r_tuple = select_db(sql, _ticker)
        R = r_tuple[0][0]
        print(f'R: {R}')
        target_price = calc_williams_R(ticker, R)
        print(f'target_price: {target_price}')
        curr_price = bithumb.get_current_price(_ticker)
        if target_price > curr_price:
            log('돌파 실패로 매도해야 하나?')
        time.sleep(0.5)


def get_buy_wish_list() -> tuple:
    sql = 'SELECT ticker, ratio, R FROM coin_buy_wish_list ' \
          ' WHERE is_active = 1 ORDER BY id'
    _buy_wish_list: tuple = select_db(sql)
    _coin_buy_wish_list = []
    _coin_ratio_list = []
    _coin_r_list = []
    for _ticker, _ratio, _R in _buy_wish_list:
        _coin_buy_wish_list.append(_ticker)
        _coin_ratio_list.append(_ratio)
        _coin_r_list.append(_R)
    return _coin_buy_wish_list, _coin_ratio_list, _coin_r_list


def calc_ratio_by_ma():
    """
    현재가격이 3, 5, 10, 20일 이동평균 비교하여 포트폴리오 매수 비율 구함
    :return:
    """
    result = dict()
    coin_buy_wish_list, coin_ratio_list, coin_r_list = get_buy_wish_list()
    # val = 1 / len(coin_buy_wish_list)
    val = 0.1 / len(coin_buy_wish_list)  # test 기간 보유비중 1/10 줄임
    for i, ticker in enumerate(coin_buy_wish_list):
        MA3 = calc_moving_average_by(ticker, 3)
        MA5 = calc_moving_average_by(ticker, 5)
        MA10 = calc_moving_average_by(ticker, 10)
        MA20 = calc_moving_average_by(ticker, 20)
        current_price = bithumb.get_current_price(ticker)
        ratio = 0
        if current_price > MA3:
            ratio += 1
        elif current_price > MA5:
            ratio += 1
        elif current_price > MA10:
            ratio += 1
        elif current_price > MA20:
            ratio += 1
        ratio: float = ratio / 4
        value = round(val * ratio, 3)
        coin_ratio_list[i] = value
        result[ticker] = value
        sql = 'UPDATE coin_buy_wish_list SET ratio = %s WHERE ticker = %s'
        mutation_db(sql, (value, ticker))
    print('포트폴리오 장세의 따른 보유 비율:', result)


def get_bull_coin_by(ticker: str, days: int = 5) -> tuple:
    """
    현재 코인티커의 이동평균가격과 윌리엄스R 목표가 돌파했는지 여부 리턴
    :param ticker: 코인티커
    :param days: 이동평균 기준 일자
    :return: ( MA, 돌파여부 bool)
    """
    try:
        volatility = False
        MA = calc_moving_average_by(ticker, days)
        current_price = pybithumb.get_current_price(ticker)
        target_price = calc_williams_R(ticker, 0.2)
        # print(f'target_price: {target_price}')
        if current_price > target_price:
            volatility = True
        return MA, volatility
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        return None, None


def find_bull_market_list() -> list:
    """
        현재가격이 3, 5, 10, 20 일 이동평균 가격 위에 있으면서
        가격이 윌리엄스 R 가격 돌파된 종목
        """
    bull_tickers = []
    all_tickers = pybithumb.get_tickers()
    for _ticker in all_tickers:
        print(_ticker)
        current_price = bithumb.get_current_price(_ticker)
        info_3 = get_bull_coin_by(_ticker, 3)
        MA3, volatility_3 = info_3
        info_5 = get_bull_coin_by(_ticker, 5)
        MA5, volatility_5 = info_5
        info_10 = get_bull_coin_by(_ticker, 10)
        MA10, volatility_10 = info_10
        info_20 = get_bull_coin_by(_ticker, 20)
        MA20, volatility_20 = info_20
        if (volatility_3 and volatility_5 and volatility_10 and volatility_20) \
                and (current_price > MA3 and current_price > MA5 \
                     and current_price > MA10 and current_price > MA20):
            bull_tickers.append(_ticker)
    print('상승 추세 코인 찾기 완료')
    return bull_tickers


def update_coin_buy_wish_list() -> None:
    """
    상승장 코인들을 찾아서 매수 희망 리스트에 DB 저장
    (기존 매수희망 리스트 삭제)
    :return: None
    """
    bull_tickers = find_bull_market_list()
    # 시가 총액순.?
    sql = 'DELETE FROM coin_buy_wish_list WHERE 1=1'
    mutation_db(sql)
    rows = []
    sql = 'REPLACE INTO coin_buy_wish_list ' \
          ' (ticker, name, ratio, R, is_active) ' \
          ' VALUES (%s, %s, %s, %s, %s) '
    for symbol in bull_tickers:
        rows.append((symbol, get_coin_name(symbol), 1 / len(bull_tickers), 0.2, 1))
    mutation_many(sql, rows)


def get_coin_bought_list() -> list:
    """"""
    sql = 'SELECT ticker FROM coin_bought_list' \
          '  WHERE date = %s ORDER BY ticker ASC'
    _bought_list: tuple = select_db(sql, get_today_format())
    _coin_bought_list = [t[0] for t in _bought_list]
    return _coin_bought_list


def get_total_yield() -> float:
    """ 현재 포트폴리오 코인 총 수익률 """
    yields = 0
    _coin_bought_list = get_coin_bought_list()
    for sym in _coin_bought_list:
        yid = get_yield(sym)
        if yid is not None:
            yields += yid
    return yields


if __name__ == '__main__':
    update_coin_buy_wish_list()
    calc_ratio_by_ma()
    loss_ratio = -2.0

    while True:
        coin_buy_wish_list, coin_ratio_list, coin_r_list = get_buy_wish_list()
        coin_bought_list: list = get_coin_bought_list()
        total_krw, use_krw = get_krw_balance()
        yields: float = get_total_yield()
        log(f'총원화: {total_krw:,} 사용한 금액: {use_krw:,} \n 추정 총수익률: {yields}%s')
        krw_balance = total_krw - use_krw
        today = datetime.now()

        # 전일 코인자산 청산 시간
        start_sell_tm = today.replace(hour=8, minute=40, second=0, microsecond=0)
        end_sell_tm = today.replace(hour=8, minute=59, second=0, microsecond=0)

        # 윌리엄스 R 돌파 전략 트레이딩 시간
        start_trading_tm = today.replace(hour=0, minute=5, second=0, microsecond=0)
        start_trading_tm = today.replace(hour=9, minute=1, second=0, microsecond=0)
        end_trading_tm = today.replace(hour=8, minute=0, second=0, microsecond=0)
        end_trading_tm = today.replace(hour=20, minute=0, second=0, microsecond=0)
        exit_tm = today.replace(hour=9, minute=0, second=0, microsecond=0)

        start_update_buy_tickers = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_update_buy_tickers = today.replace(hour=0, minute=5, second=0, microsecond=0)

        now_tm = datetime.now()

        # 시스템 종료 - 휴식?
        # if exit_tm < now_tm:
        #     log('system exit!')
        #     sys.exit(0)

        # 상승코인 목록 업데이트
        if start_update_buy_tickers < now_tm < end_update_buy_tickers:
            update_coin_buy_wish_list()
            calc_ratio_by_ma()

        if start_sell_tm < now_tm < end_sell_tm:
            log('아침에 포트폴리오 청산')
            sell_all()
            time.sleep(1)

        # 총수익률이  -6 이하일 경우 종목의 손절 비율 올림
        # 목적: 손절라인을 타이트하게 가져가서 마이너스 코인 손절매도 되게 함.
        if yields < - 6.0:
            loss_ratio = loss_ratio * 0.7
        # elif loss_ratio > 0:
        #     loss_ratio = -2.0

        if start_trading_tm < now_tm < end_trading_tm:
        # if True:
            # 손절매 확인
            for ticker in coin_bought_list:
                is_loss = check_loss(ticker, loss_ratio)
                if is_loss:
                    loss_sell(ticker)
                    time.sleep(1)

            # 이익보전 - 익절매도
            # profit_take_sell(10.0)
            # time.sleep(0.2)

            # 매수하기 - 변동성 돌파
            for i, ticker in enumerate(coin_buy_wish_list):
                if ticker not in coin_bought_list:
                    buy_coin(ticker, coin_ratio_list[i], coin_r_list[i])
                    time.sleep(1)
            # 텔레그램 수익률 보고!
            if now_tm.minute == 0 and 0 <= now_tm.second <= 5:
                send_report()
                time.sleep(1)
        else:
            log('트레이딩 휴식시간: 30초')
            time.sleep(1 * 30)

        print('-' * 150)
        time.sleep(1)

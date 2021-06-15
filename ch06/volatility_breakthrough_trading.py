from common.utils import *
from common.bithumb_api import *
import time, sys
from datetime import datetime
import pybithumb
from pandas import DataFrame, Series
from common import telegram_bot

def calc_williams_R(ticker: str, R: float = 0.5) -> float:
    """
    래리 윌리엄스 변동성 돌파 계산하기
    :param ticker:
    :param R:
    :return: target_price
    """
    df: DataFrame = pybithumb.get_candlestick(ticker)
    # print(df.tail())
    yesterday_s: Series = df.iloc[-2]
    today_s: Series = df.iloc[-1]
    today_open: Series = today_s['open']
    yesterday_high = yesterday_s['high']
    yesterday_low = yesterday_s['low']
    target_price = today_open + (yesterday_high - yesterday_low) * R
    return target_price


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

    print(order_desc)
    ticker, price, quantity = order_desc
    today_f: str = get_today_format()
    sql = f"REPLACE INTO coin_bought_list " \
          f" (date, ticker, quantity, is_sell)" \
          f" VALUES (%s, %s, %s, %s) "
    mutation_db(sql, (today_f, ticker, quantity, 0))


def save_transaction_history(order_desc: list) -> None:
    """
    주문 거래 내역 저장하기 DB
    :param order_desc => order_type, ticker, order_no,
                        currency, price, quantity, target_price, R
    :return:
    """
    order_type = order_desc[0]
    if order_type == 'bid':  # 매수 거래
        order_type, ticker, order_no, currency, price, quantity, target_price, R = tuple(order_desc)
        sql = 'REPLACE INTO coin_transaction_history ' \
              ' (order_no, date, ticker, position, price, quantity, target_price, R)' \
              ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        mutation_db(sql, (order_no, get_today_format(), ticker, order_type, price, quantity, target_price, R))
    elif order_type == 'ask':  # 매도 거래
        order_type, ticker, order_no, currency, quantity = tuple(order_desc)
        sql = 'REPLACE INTO coin_transaction_history ' \
              ' (order_no, date, ticker, position, quantity)' \
              ' VALUES (%s, %s, %s, %s, %s)'
        mutation_db(sql, (order_no, get_today_format(), ticker, order_type, quantity))


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
    if is_in_market(ticker):
        print('매수 종목 => ' + ticker)

        sql = f"SELECT quantity FROM coin_min_order_quantity WHERE ticker = %s"
        tup: tuple = select_db(sql, ticker)
        min_order_quantity = tup[0][0]
        # print('min_order_quantity:', min_order_quantity)

        total_krw, used_krw = get_krw_balance()
        buy_cash = total_krw - used_krw
        current_price = pybithumb.get_current_price(ticker)
        # 종목별 주문 금액 계산(원으로 계산됨)
        available_amount = int(buy_cash * buy_ratio)
        buy_qty: float = available_amount / current_price
        if buy_qty > min_order_quantity:
            target_price = calc_williams_R(ticker, R)
            MA3 = calc_moving_average_by(ticker, 3)
            if (current_price > target_price) and (current_price > MA3):
                log(f'변동성 돌파 AND 3일 이동평균 돌파 => target_price: {target_price:,}, {buy_qty}개')
                order_book = pybithumb.get_orderbook(ticker)
                asks = order_book['asks']
                ask_price = asks[0]['price']
                log(f'ask_price: {ask_price}')
                # 지정가 주문 api 불안정
                order_desc: tuple = buy_limit_price(ticker, ask_price, buy_qty)
                if type(order_desc) is dict and order_desc['status'] != '0000':
                    # 시장가 매수 주문!
                    order_desc: tuple = buy_market_price(ticker, buy_qty)
                order_desc: list = list(order_desc)
                order_desc.extend([ask_price, buy_qty, target_price, R])
                log(f'order_desc: {order_desc}')
                save_bought_list((ticker, ask_price, buy_qty))
                save_transaction_history(order_desc)
                log(f'주문성공: {order_desc[2]}')
            else:
                log(f'변동성 돌파 하지 못함: {ticker}')
        else:
            print('주문가능 수량이 부족합니다.')


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
                    order_desc: list = list(order_desc)
                    order_desc.append(coin_quantity)
                    log(f'매도 주문 성공,  order_no: {order_desc[2]}')
                    update_bought_list(ticker)
                    save_transaction_history(order_desc)
    except Exception as e:
        log(f' sell_all() 예외발생.. 매도실패 {str(e)}')
        sys.exit(0)


# def _sell(ticker, quantity) -> None: ...


def loss_sell(ticker: str):
    """
    손절매 시장가 매도하기
    :param ticker:
    :return:
    """
    if is_in_market(ticker):
        total_qty, used_qty = get_coin_quantity(ticker)
        coin_quantity = total_qty - used_qty
        if coin_quantity > 0:
            log(f'sell() => {ticker} {coin_quantity}개')
            order_desc: tuple = sell_market_price(ticker, coin_quantity)
            order_desc: list = list(order_desc)
            order_desc.append(coin_quantity)
            log(f'매도 주문 성공,  order_no: {order_desc[2]}')
            update_bought_list(ticker)
            save_transaction_history(order_desc)


def get_yield(ticker: str) -> float:
    # 매수가격 확인 - DB
    try:
        sql = 'SELECT position, ticker, order_no FROM coin_transaction_history ' \
              ' WHERE ticker = %s AND date = %s AND position = %s' \
              ' ORDER BY regi_date DESC'
        result: tuple = select_db(sql, (ticker, get_today_format(), 'bid'))
        # print(result)
        if len(result) > 0:
            order_desc = list(result[0])
            order_desc.append('KRW')
            trans_buy_info: tuple = get_my_order_completed_info(tuple(order_desc))
            # print(trans_buy_info)  # ('bid', 'ETH', 2991000.0, 0.0013, 9.72, 3888)
            order_type, _ticker, price, quantity, fee, trans_krw_amount = trans_buy_info
            current_price = bithumb.get_current_price(ticker)
            yield_rate = (current_price / price - 1) * 100
            log(f'{ticker} 수익률: {round(yield_rate, 2)}%)')
            return round(yield_rate, 3)
    except Exception as e:
        log(f' get_yield() 예외발생.. {str(e)}')


def check_loss(ticker: str) -> bool:
    print(f'손절매 대상 확인: {ticker}')
    try:
        yield_rate: float = get_yield(ticker)
        if yield_rate < -2.0:
            log(f'마이너스 수익률 발생 => {ticker} {yield_rate}%')
            return True
        return False
    except Exception as e:
        log(f' get_yield() 예외발생.. {str(e)}')


def send_report() -> None:
    msg = f'[가상화폐 수익률 알림]'
    for ticker in bought_list:
        yield_rate: float = get_yield(ticker)
        msg += f'{ticker} {yield_rate}% \n'
    telegram_bot.send_coin_bot(msg)


def t():
    """
    트레일 - 이익 보전 익절 매도

    """


if __name__ == '__main__':
    sql = 'SELECT ticker, ratio, R FROM coin_buy_wish_list WHERE is_active = 1'
    buy_wish_list: tuple = select_db(sql)
    coin_buy_wish_list = []
    coin_ratio_list = []
    coin_r_list = []
    for ticker, ratio, R in buy_wish_list:
        # print(ticker, ratio, R)
        coin_buy_wish_list.append(ticker)
        coin_ratio_list.append(ratio)
        coin_r_list.append(R)

    total_krw, use_krw = get_krw_balance()
    log(f'총원화: {total_krw:,} 사용한 금액: {use_krw:,}')
    krw_balance = total_krw - use_krw

    while True:
        sql = 'SELECT ticker FROM coin_bought_list WHERE is_sell = 0'
        bought_list: tuple = select_db(sql)
        coin_bought_list = [t[0] for t in bought_list]
        # print(coin_bought_list)

        today = datetime.now()
        # 전일 코인자산 청산 시간
        start_sell_tm = today.replace(hour=8, minute=40, second=0, microsecond=0)
        end_sell_tm = today.replace(hour=8, minute=50, second=0, microsecond=0)
        # 윌리엄스 R 돌파 전략 트레이딩 시간
        start_trading_tm = today.replace(hour=8, minute=41, second=0, microsecond=0)
        end_trading_tm = today.replace(hour=23, minute=58, second=0, microsecond=0)
        # 시스템 종료
        exit_tm = today.replace(hour=23, minute=59, second=0, microsecond=0)
        now_tm = datetime.now()

        # # 시스템 종료 - 휴식?
        if exit_tm < now_tm:
            log('system exit!')
            sys.exit(0)

        if start_sell_tm < now_tm < end_sell_tm:
        # if True:
            log('다음날 시가 포트폴리오 청산')
            sell_all()

        if start_trading_tm < now_tm < end_trading_tm:
            # 매수하기 - 변동성 돌파
            for i, ticker in enumerate(coin_buy_wish_list):
                if ticker not in coin_bought_list:
                    buy_coin(ticker, coin_ratio_list[i], coin_r_list[i])
                    time.sleep(0.1)

            # 손절매 확인
            for ticker in coin_bought_list:
                is_loss = check_loss(ticker)
                if is_loss:
                    loss_sell(ticker)
                    time.sleep(0.1)

            # 텔레그램 수익률 보고!
            if now_tm.minute == 0 and 0 <= now_tm.second <= 7:
                send_report()
                time.sleep(1)

        print('-' * 150)
        time.sleep(2)

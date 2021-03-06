import os, sys
import threading
from datetime import datetime

if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
else:
    sys.path.append('/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system')
from common import telegram_bot
from common.bithumb_api import *
from common.utils import *


def save_bought_list(order_desc: tuple, type='bk') -> None:
    """
      매수한 목록 DB 저장
      :param order_desc = 코인티커, 가격, 수량
      정상 매수 => (ticker, order_no)
      예외 => dict: {status: '5600', msg: '입력값을 확인해주세요'}

    """
    try:
        if isinstance(order_desc, dict):
            print('매수 예외발생 =>', order_desc)
            return
        # print(order_desc)
        ticker, order_no = order_desc
        sql = f"INSERT INTO coin_bought_list " \
              f" (order_no, date, ticker, type, is_sell)" \
              f" VALUES (%s, %s, %s, %s, %s) "
        mutation_db(sql, (order_no, get_today_format(), ticker, type, False))

        is_bull = is_bull_coin(ticker)
        if is_bull is True:
            sql = 'UPDATE bull_coin_list SET already_buy = %s ' \
                  ' WHERE ticker = %s'
            mutation_db(sql, (True, ticker))

    except Exception as e:
        log(f'save_bought_list() 예외발생.. 매수실패 {str(e)}')
        traceback.print_exc()


def save_transaction_history(order_desc: list) -> None:
    """
    주문 거래 내역 저장하기 DB
    :param order_desc => order_type, ticker, order_no,
                        currency, price, quantity, target_price, R
    :return:
    """
    try:
        order_type = order_desc[0]
        if order_type == 'bid':  # 매수 거래
            _order_type, ticker, order_no, currency, price, quantity, target_price, R, fee, \
            transaction_krw_amount, diff, diff_percent, curr_noise, noise_ma20, type_str = tuple(
                order_desc)
            sql = 'INSERT INTO coin_transaction_history ' \
                  ' (order_no, date, ticker, position, price, quantity, target_price, R, fee, transaction_krw_amount, ' \
                  ' diff, diff_percent, curr_noise, noise_ma20, type)' \
                  ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,' \
                  ' %s, %s, %s, %s, %s)'
            mutation_db(sql, (order_no, get_today_format(), ticker, order_type, price, quantity, target_price, R, fee,
                              transaction_krw_amount,
                              diff, diff_percent, curr_noise, noise_ma20, type_str))
        elif order_type == 'ask':  # 매도 거래
            _order_type, ticker, order_no, currency, price, quantity, fee, transaction_krw_amount, yield_ratio, type_str = tuple(
                order_desc)
            sql = 'INSERT INTO coin_transaction_history ' \
                  ' (order_no, date, ticker, position, price, quantity, fee, transaction_krw_amount, yield_ratio, type)' \
                  ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            mutation_db(sql, (order_no, get_today_format(), ticker, order_type, price, quantity,
                              fee, transaction_krw_amount, yield_ratio, type_str))
    except Exception as e:
        log(f' save_transaction_history() 예외발생.. 매수실패 {str(e)}')
        traceback.print_exc()


def update_bought_list(ticker: str) -> None:
    """
    주문한 코인 매수 처리 => coin_buy_wish_list 테이블 1 처리
    :param ticker:
    :return:
    """
    try:
        sql = 'UPDATE coin_bought_list ' \
              ' SET is_sell = %s ' \
              ' WHERE ticker = %s'
        mutation_db(sql, (True, ticker))
    except Exception as e:
        log(f' update_bought_list() 예외발생.. 매수실패 {str(e)}')
        traceback.print_exc()


def check_volatility_breakthrough_list() -> list:
    """ 매수 희망 종목에서 당일에 변동성돌파 하는 종목 리스트 리턴 """
    volatility_break_list = []
    _coin_buy_wish_list, _coin_ratio_list, _coin_r_list = get_buy_wish_list()
    for idx, _ticker in enumerate(_coin_buy_wish_list):
        current_price = pybithumb.get_current_price(ticker)
        _R = calc_R(_ticker, _coin_r_list[idx])
        time.sleep(0.1)
        target_price = calc_williams_R(_ticker, _R)
        if current_price > target_price:
            volatility_break_list.append(ticker)

    return volatility_break_list


def buy_coin(ticker: str, buy_ratio: float, R: float = 0.5) -> bool or None:
    """
    코인 매수
    지정가 매수후 실패시 시장가 매수
    :param ticker:
    :param buy_ratio:
    :param R:
    :return: 매수 성공: True, 의도적으로 매수방지할 경우: False, 기타 상황 None
    """
    try:
        if is_in_market(ticker):
            total_krw, used_krw = get_krw_balance()
            buy_cash = total_krw - used_krw
            current_price = pybithumb.get_current_price(ticker)
            # 종목별 주문 금액 계산(원으로 계산됨)
            available_amount = int(buy_cash * buy_ratio)
            # log(f'매수에 쓸 돈: {ticker} {available_amount:,}')
            buy_qty: float = available_amount / current_price
            if buy_qty > 0:
                target_price = calc_williams_R(ticker, R)
                # 현재 close 시가 포함된 이동평균
                # MA3 = calc_moving_average_by(ticker, 3)
                # 당일 시세 제외  이동평균!
                MA3 = calc_fix_moving_average_by(ticker, 3)
                MA5 = calc_fix_moving_average_by(ticker, 5)
                if (current_price > target_price) and (current_price > MA3) \
                        and (current_price > MA5):
                    log(f'{ticker} 변동성 돌파 AND 3일 이동평균 돌파')
                    type_str = '돌파추세'
                    order_book = pybithumb.get_orderbook(ticker)
                    asks = order_book['asks']
                    ask_price = asks[0]['price']
                    expected_diff = ask_price - target_price
                    expected_diff_percent = round((expected_diff / ask_price * 100), 3)

                    # 메이저 코인과, 급등코인 노이즈, 슬리피지비율 차등 부여
                    major_coin_list, _, __ = get_buy_wish_list()
                    is_major = True
                    if ticker in major_coin_list:
                        standard_noise = 0.55
                        standard_diff_p = 0.7

                    else:
                        standard_noise = 0.3
                        standard_diff_p = 3.0
                        is_major = False

                    if expected_diff_percent > standard_diff_p:
                        msg = f'체결오차(슬리피지)가 너무 크므로 매수 방지: {ticker} '
                        msg += f'오차비율: {expected_diff_percent}%'
                        disabled_buy_wish_list(ticker, is_major)
                        log(msg)
                        return False
                    current_noise = get_current_noise(ticker)
                    noise_ma20 = calc_noise_ma_by(ticker, 20)
                    if current_noise > standard_noise:
                        msg2 = f'당일 시장상태 노이즈 심함! curr_noise: {current_noise} '
                        msg2 += f'{ticker} 매수 방지!'
                        log(msg2)
                        return False
                    # ------------------------------------------------------------
                    # 지정가 매수 주문: 미체결될수 있으므로 반드시 주문 확인해야 함
                    buy_krw = ask_price * buy_qty
                    if buy_krw < 1000:
                        buy_qty *= 5
                    order_desc: tuple = buy_limit_price(ticker, ask_price, buy_qty)
                    time.sleep(0.1)
                    # ------------------------------------------------------------
                    # 체결 정보
                    # order_desc: ('bid', 'KLAY', 'C0538000000004404555', 'KRW')
                    #  지정가 매수 주문 실패(api 실패):
                    #  {'status': '5600', 'message': '최소 주문금액은 500 KRW 입니다.'}
                    if order_desc and isinstance(order_desc, tuple):
                        completed_order = get_my_order_completed_info(order_desc)
                        log(f'completed_order: {completed_order}')
                        # 거래타입, 코인티커, 가격, 수량 ,수수료(krw), 거래금액)
                        if completed_order:
                            order_type, _ticker, price, order_qty, fee, transaction_krw_amount = completed_order
                            # insert bought list
                            save_bought_list((ticker, order_desc[2]))
                            order_desc = list(order_desc)
                            diff = price - target_price
                            diff_percent = round(diff / price * 100, 3)
                            order_desc.extend(
                                [price, order_qty, target_price, R, fee, transaction_krw_amount, diff, diff_percent,
                                 current_noise, noise_ma20, type_str])
                            save_transaction_history(order_desc)
                            log(f'매수주문성공: {ticker} {order_desc[2]}')
                            msg = f'[매수알림] {ticker} \n' \
                                  f'가격: {price} 수량: {round(buy_qty, 4)}개 \n' \
                                  f'슬리피지: {diff} \n' \
                                  f'슬리피지 비율: {round(diff_percent, 3)}%'
                            telegram_bot.send_coin_bot(msg)
                            return True
                    elif order_desc and type(order_desc) is dict and order_desc['status'] != '0000':
                        log(order_desc)
                        log('지정가 매수 주문 실패')
                        log(ticker, ask_price, buy_qty)
                    else:
                        log(f'{ticker} 매수 실패 주문 결과 확인: {order_desc}')
                        is_cancel: bool = bithumb.cancel_order(order_desc)
                        log(f'{ticker} 주문 취소 => {is_cancel}')
                        while is_cancel is False:
                            log(f'주문취소 재요청 {order_desc}')
                            is_cancel = bithumb.cancel_order(order_desc)
                else:
                    log(f'변동성 돌파 하지 못함: {ticker}')
            else:
                log(f'{ticker} 주문가능 수량이 부족합니다. 수량: {buy_qty}')
    except Exception as e:
        log(f' buy_coin() 예외발생.. 매수실패 {str(e)}')
        traceback.print_exc()


def sell_all():
    """
    보유 코인 다음날 시가 청산
    :return:
    """
    try:
        type_str = '시가매도'
        while True:
            _coin_bought_list = get_coin_bought_list()

            if len(_coin_bought_list) == 0:
                log('매도할 코인 없음 => 종료')
                return True

            # 당일 추세 있는 코인 매도 항목 제외시킴
            today_volatility_list = check_volatility_breakthrough_list()
            target_sell_list = set(_coin_bought_list) - set(today_volatility_list)
            if len(target_sell_list) == 0:
                log('당일 추세 코인을 제외하면 매도할 코인이 없음 => 매도종료')
                return True

            for ticker in _coin_bought_list:
                total_qty, used_qty = get_balance_coin(ticker)
                coin_quantity = total_qty - used_qty
                if coin_quantity > 0:
                    buy_price, _qty = get_bought_price_and_qty(ticker)
                    log(f'sell() => {ticker} {coin_quantity}개')
                    order_desc: tuple = sell_market_price(ticker, coin_quantity)
                    log(f'매도 주문 성공,  order_no: {order_desc[2]}')
                    time.sleep(0.1)
                    update_bought_list(ticker)
                    order_completed_info: tuple = get_my_order_completed_info(order_desc)
                    order_type, _ticker, sell_price, order_qty, fee, transaction_krw_amount = order_completed_info
                    order_desc: list = list(order_desc)
                    # yield_ratio = get_yield(ticker)
                    yield_ratio = round((buy_price / sell_price - 1) * 100, 5)
                    order_desc.extend([sell_price, coin_quantity, fee, transaction_krw_amount, yield_ratio, type_str])
                    save_transaction_history(order_desc)
                    remove_peak_log(ticker)
                    msg = f'[청산 매도알림] {ticker} \n' \
                          f'체결가격: {sell_price} 수량: {round(order_qty, 4)}개 \n' \
                          f'수익률: {yield_ratio}%'
                    telegram_bot.send_coin_bot(msg)
                    time.sleep(1)
            time.sleep(0.5)
    except Exception as e:
        log(f' sell_all() 예외발생.. 매도실패 {str(e)}')
        traceback.print_exc()


def sell(ticker: str, quantity: float, is_market=False) -> bool:
    """
    [공통] 매도하기
        1) 정상매도
        sell() => XRP 2.0개
        매도 주문 요청, order_desc: ('ask', 'XRP', 'C0106000000241177536', 'KRW')

        2) 매도실패 - 보유수랑 없음
        매도 주문 요청,  order_desc: {'status': '5500', 'message': 'Invalid Parameter'}
        체결된 주문 내역 조회 실패 => 'NoneType' object is not subscriptable
        sell() 예외발생! e =>cannot unpack non-iterable NoneType object

    하는일
        1) 매수후 매수한 종목리스트(bought_list) 제외
        2) 매도 거래내역(transaction_history) 기록
        3) 피크 테이블 삭제
    :param ticker:
    :param quantity:
    :return:
    """
    log(f'매도 sell() => {ticker} {quantity}개')
    type_str = ''
    try:
        if is_market is True:
            type_str = '시장가청산'
            order_desc: tuple = sell_market_price(ticker, quantity)
        else:
            order_book = pybithumb.get_orderbook(ticker)
            bids: list = order_book['bids']
            # print('매수호가 :', bids)
            bid_price = int(bids[0]['price'])
            order_desc: tuple = sell_limit_price(ticker, bid_price, quantity)
            print(f'order_desc: {order_desc}')
            time.sleep(0.1)
            if type(order_desc) is dict and order_desc['status'] != '0000':
                return sell(ticker, quantity, is_market=False)
        log(f'매도 주문 요청,  order_desc: {order_desc}')
        if order_desc and isinstance(order_desc, tuple):
            yield_ratio = get_yield(ticker)
            order_completed_info: tuple = get_my_order_completed_info(order_desc)
            log(f'order_completed_info: {order_completed_info}')
            if order_completed_info:
                update_bought_list(ticker)
                order_type, _ticker, price, order_qty, fee, transaction_krw_amount = order_completed_info
                order_desc: list = list(order_desc)
                order_desc.extend([price, quantity, fee, transaction_krw_amount, yield_ratio, type_str])
                save_transaction_history(order_desc)
                remove_peak_log(ticker)
                msg = f'[매도알림] {ticker} \n' \
                      f'가격: {price} 수량: {order_qty}개 \n' \
                      f'수익률: {yield_ratio}%'
                telegram_bot.send_coin_bot(msg)
                return True
    except Exception as e:
        log(f'sell() 예외발생! e =>{str(e)}')
        traceback.print_exc()
        return False


def check_loss_sell(ticker: str, basic_loss_ratio=2.0) -> bool:
    """
    해당 코인 손절 대상 검사후 손절매 시장가 매도하기
    (+추가) 기본 손절 비율에  (1 - 당일 변동성) 더해줌
    => 당일 변동성이 높으면 손절 라인 타이트하게 됨
    :param ticker: 매도코인
    :return:
    """
    try:
        loss_standard = basic_loss_ratio * -1
        curr_yield: float = get_yield(ticker)
        if curr_yield <= loss_standard:
            log(f'손절 => {ticker}, yield_rate:{curr_yield}%, noise_loss:{loss_standard}')
            # sell!
            total_qty, used_qty = get_balance_coin(ticker)
            quantity = total_qty - used_qty
            # ------------------------------------------
            r = sell(ticker, quantity, is_market=False)
            print(f'손절매 결과: {r}')
            # ------------------------------------------
            # 손절매 매도 표시(당일 재매수 방지)
            if r is True:
                sql = 'UPDATE coin_buy_wish_list ' \
                      ' SET is_loss_sell = %s' \
                      ' WHERE ticker = %s'
                mutation_db(sql, (True, ticker))
                save_daily_loss_sell_list(ticker, get_coin_name(ticker), curr_yield)
            return r
        else:
            return False
    except Exception as e:
        log(f' check_loss_sell() 예외발생.. {str(e)}')
        traceback.print_exc()


def profit_sell(ticker: str) -> bool:
    """
    손실 발생전 익절 매도
    :param ticker: 매도코인
    :return:
    """
    try:
        if is_in_market(ticker):
            total_qty, used_qty = get_balance_coin(ticker)
            quantity = total_qty - used_qty
            # coin_yield = get_yield(ticker)
            if quantity > 0:
                r: bool = sell(ticker, quantity, is_market=False)
                print(f'트레이링 스탑 매도 결과: {r}')
                sql = 'UPDATE coin_buy_wish_list SET is_loss_sell = %s WHERE ticker = %s'
                mutation_db(sql, (1, ticker))
                return r
    except Exception as e:
        log(f'profit_sell() 예외발생.. {str(e)}')
        traceback.print_exc()


def get_yield(ticker: str) -> float:
    """
    수익률 계산하기
        매수가격 확인하기 위해 거래내역(traction_history 테이블) 에서 order_no 조회후 매수가 산출
    :param ticker:
    :return:
    """
    try:
        sql = 'SELECT order_no FROM coin_bought_list ' \
              ' WHERE is_sell = %s AND ticker = %s'
        result: tuple = select_db(sql, (0, ticker))
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
                name = get_coin_name(ticker)
                log(f'{name}({ticker}) 수익률: {round(yield_rate, 2)}%')
                return round(yield_rate, 4)
        else:
            log(f'{ticker} order_no 조회 결과 없음으로 수익률 0 리턴: {result}')
            return 0
    except Exception as e:
        log(f' get_yield() 예외발생.. {str(e)}')
        traceback.print_exc()


def send_report() -> None:
    """ 텔레그램 봇 수익률 메시지 전송 """
    try:
        _coin_bought_list = get_coin_bought_list()
        msg = f'[가상화폐 수익률 알림] \n'
        total_yield = 0
        for _ticker in _coin_bought_list:
            yield_rate: float = get_yield(_ticker)
            msg += f'{_ticker} {yield_rate}% \n'
            total_yield += yield_rate

        msg += f'총 수익률: {total_yield}'
        if len(_coin_bought_list) == 0:
            msg += '보유 코인 없음'

        telegram_bot.send_coin_bot(msg)
    except Exception as e:
        log(f' send_report() 예외발생.. {str(e)}')
        traceback.print_exc()


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
              ' AND is_loss_sell = %s ' \
              ' AND type != %s'
        _buy_wish_list: tuple = select_db(sql, (True, False, 'upbit'))  # 0.55)
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
        return [], [], []


def is_bull_coin_by(ticker: str, days: int = 5) -> tuple:
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


def get_coin_bought_list() -> list:
    """
    현재 코인 보유 리스트 with bithumb
    """
    try:
        coin_balance: dict = get_my_coin_balance()
        if coin_balance:
            return list(coin_balance.keys())
        elif isinstance(coin_balance, dict) and len(coin_balance) == 0:
            return []
    except Exception as ex:
        log(f'get_coin_bought_list() 예외발생 {str(ex)}')
        traceback.print_exc()
        sql = "SELECT ticker FROM coin_bought_list WHERE is_sell = %s"
        tickers_tup: tuple = select_db(sql, False)
        if tickers_tup:
            return [tup[0] for tup in tickers_tup]
        elif isinstance(tickers_tup, tuple) and len(tickers_tup) == 0:
            return []


def get_total_yield() -> float:
    """ 현재 포트폴리오 코인 총 수익률 """
    try:
        total_yield = 0
        coin_bought_list = get_coin_bought_list()
        for sym in coin_bought_list:
            yid = get_yield(sym)
            if yid:
                total_yield += yid
        if coin_bought_list:
            total_yield = round(total_yield / len(coin_bought_list), 5)
        return total_yield
    except Exception as ex:
        log(f'get_total_yield() 예외발생 {str(ex)}')
        traceback.print_exc()
        return 0.0


def calc_position_ratio_by_ma_score(_ticker: str, ma_days=[3, 5, 10, 20]) -> float:
    """
    이동평균 스코어 종목 비율 계산
    :param _ticker:
    :return:
    """
    ma_list = [calc_fix_moving_average_by(_ticker, day) for day in ma_days]
    current_price = bithumb.get_current_price(_ticker)
    init_ratio = 0
    for MA in ma_list:
        if current_price > MA:
            init_ratio += 1
    ratio: float = init_ratio / len(ma_days)
    return round(ratio, 3)


def calc_position_size_by_score() -> None:
    """
    자금관리: 포트폴리오 보유 비중 계산 with MA
    현재가격이 3, 5, 10, 20일 이동평균 비교하여 포트폴리오 매수 비율 구함
    이동평균
    당일 시가 포함 이평: calc_moving_average_by(),
    당일 close 시가 제외 이평: calc_fix_moving_average_by()
    :return: 매수할 코인 목록
    """
    try:
        result = dict()
        sql = 'SELECT ticker FROM coin_buy_wish_list WHERE is_active = %s'
        temp_t = select_db(sql, True)
        coin_buy_wish_list = [ticker_tup[0] for ticker_tup in temp_t]
        init_ratio = 1 / (len(coin_buy_wish_list) * 1.5)
        for ticker in coin_buy_wish_list:
            score_ratio = calc_position_ratio_by_ma_score(ticker)
            ratio = round(init_ratio * score_ratio, 7)
            result[ticker] = ratio
            sql = 'UPDATE coin_buy_wish_list SET ratio = %s WHERE ticker = %s'
            mutation_db(sql, (ratio, ticker))
        print('포트폴리오 장세의 따른 보유 비율:', result)
        _list = [k for k, v in result.items() if v > 0]
        if len(_list) == 0:
            log('매수할 종목 없음. 하락장은 피하고, 상승장에서만 투자 한다.')
            time.sleep(1 * 60 * 5)
    except Exception as ee:
        print(str(ee))
        traceback.print_exc()


def is_bull_market(ticker: str) -> bool:
    """
    상승장 기준 체크
    :param ticker:
    :return:
    """
    try:
        current_noise = get_current_noise(ticker)
        MA3_NOISE = calc_noise_ma_by(ticker, 3)
        curr_price = pybithumb.get_current_price(ticker)
        prices = pybithumb.get_candlestick(ticker)
        # 당일 시세 포함된 이동평균
        # MA3 = calc_moving_average_by(ticker, 3)
        # MA5 = calc_moving_average_by(ticker, 5)
        # MA10 = calc_moving_average_by(ticker, 10)
        # MA20 = calc_moving_average_by(ticker, 20)
        time.sleep(0.1)
        MA3 = calc_fix_moving_average_by(ticker, 3)
        MA5 = calc_fix_moving_average_by(ticker, 5)
        MA10 = calc_fix_moving_average_by(ticker, 10)
        MA20 = calc_fix_moving_average_by(ticker, 20)
        val = 0
        if curr_price > MA3:
            val += 1
        if curr_price > MA5:
            val += 1
        if curr_price > MA10:
            val += 1
        if curr_price > MA20:
            val += 1
        value = val / 4

        # prev_volume = get_prev_volume(ticker)
        # MA30_VOLUME = calc_prev_ma_volume(ticker, 30)

        if not prices.empty:
            close = prices['close']
            open = prices['open']
            volume = prices['volume']
            prev_close = close.iloc[-2]
            open_price = open.iloc[-1]

            prev_volume = volume.iloc[-2]
            curr_volume = volume.iloc[-1]
            MA30_VOLUME = volume.rolling(window=30).mean()

            # print(close.tail())
            # 현재가가 어제 종가보다 크고 오늘 시가 보다 크면서, 당일 노이즈가 0.3 보다 작고
            if curr_price > prev_close and curr_price > open_price \
                    and current_noise <= 0.3 and MA3_NOISE < 0.4 and value >= 1 \
                    and prev_volume < curr_volume and MA30_VOLUME < curr_volume:
                print('현재가가 어제종가 보다 크고, 오늘 시가보다 크면서 \n'
                      '당일 노이즈 0.3 이하 3일평균 노이즈가 0.4 미만일 경우\n'
                      '동시에 3, 5, 10, 20일 이평선 위에 가격에 있으면 상승장으로 판단'
                      '추가: 거래량 30일 평균')
                return True
            else:
                return False
    except Exception as X:
        log(f'is_bull_market() 예외 {str(X)}')
        traceback.print_exc()
        return False


def calc_R(symbol: str, sub_R: float) -> float:
    """
    윌리엄스 R에 사용할 R 값 구하기(당일 노이즈 가중치)
    공식
    R = (당일 노이즈 + 3MA 노이즈) / 2
    :param symbol: 코인티커
    :param sub_R: 예외발생시 기존 R 값 리턴
    :return: R
    """
    try:
        # R = calc_fix_noise_ma_by(symbol, 20)
        R = calc_noise_ma_by(symbol, 20)
        # curr_noise = get_current_noise(symbol)
        # R = round((MA3_R + curr_noise) / 2, 5)
        # R = calc_noise_ma_by(symbol, 20)
        return R
    except Exception as E:
        log_msg = f'trailing_stop() 예외발생 {symbol} -> {str(E)}'
        log(log_msg)
        traceback.print_exc()
        return sub_R


def calc_position_size_by_volatility() -> None:
    """
    자금관리: 가상화폐 변동성에 높을 경우 보유비중을 줄이고,
            변동성이 낮을 경우 보유비중을 높힌다.
    (감당할수 있는 변동성 / 전일 변동성)  / 투자코인수
    ex)코인당 2% 하락 ok 라면
    (2% / 7%(전일 변동성))  / len(buy_wish_list)
    :return: 매수할 코인 목록
    """
    try:
        coin_buy_wish_list, _, __ = get_buy_wish_list()
        size = len(coin_buy_wish_list)
        result = {}
        target_loss_ratio = 2.0
        for ticker in coin_buy_wish_list:
            target_ratio = calc_target_volatility_ratio(ticker, target_loss_ratio)
            position_size = round(target_ratio / size, 4)
            result[ticker] = position_size
            sql = 'UPDATE coin_buy_wish_list SET ratio = %s WHERE ticker = %s'
            mutation_db(sql, (position_size, ticker))
        msg = f'포트폴리오 장세의 따른 보유 비율:\n'
        for k, v in result.items():
            msg += f'{k} {v}%  '
        log(msg)
    except Exception as ex:
        log(f'calc_position_size_by_volatility() 예외발생 {str(ex)}')
        traceback.print_exc()


def modify_R(ticker: str, R: float) -> None:
    """
        변동성 돌파 상수 R 값 변경
    """
    try:
        sql = 'UPDATE coin_buy_wish_list SET R = %s WHERE ticker = %s'
        mutation_db(sql, (R, ticker))
    except Exception as ex:
        log(f'modify_R() 예외발생 {str(ex)}')
        traceback.print_exc()


def get_bought_price_and_qty(ticker: str) -> tuple:
    """
    현재 보유중인 코인 매수가 리턴
    :param ticker:
    :return: 매수가격, 수량
    """
    try:
        _coin_bought_list = get_coin_bought_list()
        if ticker in _coin_bought_list:
            sql = 'SELECT order_no FROM coin_bought_list ' \
                  ' WHERE is_sell = %s AND ticker = %s'
            order_no_tup: tuple = select_db(sql, (False, ticker))
            if len(order_no_tup) > 0:
                prices = []
                qty = []
                for order_no in order_no_tup:
                    sql = 'SELECT price, quantity FROM coin_transaction_history ' \
                          ' WHERE order_no = %s'
                    price_tup = select_db(sql, order_no)
                    if len(price_tup) > 0:
                        prices.append(price_tup[0][0])
                        qty.append(price_tup[0][1])
                avg_bought_price = sum(prices) / len(prices)
                avg_quantity = sum(qty) / len(qty)
                return avg_bought_price, avg_quantity
            else:
                log(f'order_no 조회결과 데이터 없음. {ticker} {order_no_tup}')
                return 0, 0
        else:
            log(f'get_bought_price() => 요청한 {ticker}는 현재 보유하고 있지않음!')
            return 0, 0
    except Exception as E:
        log_msg = f'get_bought_price() 예외발생 {ticker} -> {str(E)}'
        log(log_msg)
        traceback.print_exc()


def trailing_stop(ticker: str) -> None:
    """
    트레이링 스탑
    트레일링 스탑이란 현재가가 고점 대비 일정수준의 하락이 이루어지면
    해당 종목에 대하여 매도(청산)주문을 실행하는 것을 말합니다.
    감시시작시점을 기준으로 최소한의 이익을 보장하고자 하면 목표가를 설정하여
    현재가가 목표가에 도달 후 일정수준의 하락이 이루어지면 주문이 실행되고,
    현재가(고가)가 목표가를 돌파한 후 하락하지 않고 계속 상승할 경우
    고가갱신에 따라 목표가도 갱신되어 더 많은 이익을 낼 수 있습니다.
    https://download.kiwoom.com/hero3_help_new/hero100/qa27.htm

    나의 목표
    1) 최고점 기록: 매 반복 루틴마다 현재가격이 최고점인지 확인하여 최고점이면 peak 테이블에
    현재가격과 현재 수익률을 기록한다.

    2) 차익실현: 현재가격이 피크가격보다 낮으면서 수익률이 최고점 찍고 하락하여 1%로 떨어졌으면 최소 손익을 보장하기 위해
    익절 매도하여 차익 실현한다.

    3) 초기화: 매도 요청후 해당 종목 peak 테이블 row 을 삭제한다.
    """
    try:
        bought_price, quantity = get_bought_price_and_qty(ticker)
        if bought_price > 0 and quantity > 0:
            current_price = pybithumb.get_current_price(ticker)
            # 내가 매수한 가격보다 현재 가격이 높을 경우 피크가격임!
            sql = 'SELECT peak_price, yield_ratio FROM peak WHERE ticker = %s'
            peak_t = select_db(sql, ticker)
            m_sql = 'INSERT INTO peak ' \
                    ' (date, ticker, name, bought_price, peak_price, yield_ratio) ' \
                    ' VALUES (%s, %s, %s, %s, %s, %s)'
            name = get_coin_name(ticker)
            current_yield = round((current_price / bought_price - 1) * 100, 3)
            prev_peak_price, prev_yield = (0, 0)
            if peak_t and len(peak_t) > 0:
                prev_peak_price, prev_yield = peak_t[0]
            if bought_price < current_price:
                if len(peak_t) == 0:
                    #  최초 peak 가격 저장하기
                    row = (get_today_format(), ticker, name, bought_price, current_price, current_yield)
                    mutation_db(m_sql, row)
                elif len(peak_t) > 0 and current_price > prev_peak_price:
                    # 피크 가격 최고가로 갱신
                    m_sql = "UPDATE peak SET peak_price = %s, yield_ratio = %s" \
                            "  WHERE ticker = %s "
                    mutation_db(m_sql, (current_price, current_yield, ticker))
                else:
                    standard_prev_yield = prev_yield / 2
                    total, used = get_balance_coin(ticker)
                    qty = total - used
                    if prev_yield > 5.0 and current_yield <= standard_prev_yield:
                        log(f'{name} 차익실현 {current_yield:.3f} ')
                        # 매도시 매도 로직을 sell() 내부에서 함
                        sell_ok: bool = sell(ticker, qty, is_market=False)
                        log(f'수익보전 매도 결과:{sell_ok} => {name} {quantity}')
                        # 손절매 처리는 하지 않음: 재매수 될수 있음
                        save_daily_profit_list(ticker, name, current_yield)
            else:
                # 하락 반전: 마이너스 수익 기록중!
                total, used = get_balance_coin(ticker)
                qty = total - used
                log(f'[알림] {name}({ticker}): 현재 가격이 돌파 목표가격 이하로 주저 앉음')
                order_no = get_bought_order_no(ticker)
                if order_no:
                    target_price: int = get_target_price_from(order_no, ticker)
                    loss_standard_price = target_price - (target_price * 0.02)
                    if current_price < loss_standard_price:
                        _sell_ok: bool = sell(ticker, qty, is_market=False)
                        log(f'하락 반전 매도결과: {_sell_ok} => {name} {qty}')
                        # 손절매 처리는 하지 않음: 재매수 될수 있음
    except Exception as e:
        log_msg = f'trailing_stop() 예외발생 {ticker} -> {str(e)}'
        traceback.print_exc()
        log(log_msg)


def dynamic_change_R() -> None:
    """
    시간대별 동적으로 R 변경하기
    """
    try:
        R1 = None
        now_tm = datetime.now()
        log(now_tm)
        if now_tm.hour == 1 and now_tm.minute == 0 and 0 <= now_tm.second <= 7:
            # 새벽 1시
            R1 = 0.3
        if now_tm.hour == 2 and now_tm.minute == 0 and 0 <= now_tm.second <= 7:
            # 새벽 2시
            R1 = 0.2
        if now_tm.hour == 3 and now_tm.minute == 0 and 0 <= now_tm.second <= 7:
            # 새벽 3시
            R1 = 0.1
        if now_tm.hour == 4 and now_tm.minute == 0 and 0 <= now_tm.second <= 7:
            # 새벽 4
            R1 = 0
        if now_tm.hour == 7 and now_tm.minute == 0 and 0 <= now_tm.second <= 7:
            R1 = 0.5
        if now_tm.hour == 8 and now_tm.minute == 0 and 0 <= now_tm.second <= 7:
            R1 = 0.6
        if now_tm.hour == 9 and now_tm.minute == 0 and 0 <= now_tm.second <= 7:
            R1 = 0.7
        if R1 is not None:
            msg = f'시간대별 동적으로 R 변경하기: {R1}'
            log(msg)
            telegram_bot.send_coin_bot(msg)
            for _symbol in coin_buy_wish_list:
                modify_R(_symbol, R1)
    except Exception as ex:
        log(f'dynamic_change_R() 예외발생 {str(ex)}')
        traceback.print_exc()


def trading_rest_time():
    """
    트레이딩 시작전 휴식시간 23:55 부터 6분간 초기화
    1) R값 0.5로 초기화
    2)  is_loss_sell 값 0으로 초기화
    :return:
    """
    try:
        log('트레이딩 새로 시작전 휴식시간(10)')
        # 손절매 여부 초기화
        sql = 'UPDATE coin_buy_wish_list ' \
              ' SET is_loss_sell = %s ' \
              ' WHERE is_active = %s'
        mutation_db(sql, (False, True))

        # 당일 거래 결산 - 이익/손익 통계 저장
        save_daily_profit_and_loss()
    except Exception as ex:
        log(f'trading_rest_time() 예외발생 {str(ex)}')
        traceback.print_exc()


def filter_buy_wish_list() -> None:
    """
    필터링: 20일 이동평균 매일 계산: buy_wish_list 테이블 noise_ma20 컬럼 추가
    """
    sql = 'SELECT ticker FROM coin_buy_wish_list ' \
          ' WHERE is_active = %s '
    temp_t = select_db(sql, True)
    _buy_wish_list = [ticker[0] for ticker in temp_t]
    for _ticker in _buy_wish_list:
        # MA20_NOISE = calc_noise_ma_by(_ticker, 20)
        #  당일 제외 노이즈
        MA20_NOISE = calc_fix_noise_ma_by(_ticker, 20)
        sql = 'UPDATE coin_buy_wish_list ' \
              ' SET noise = %s ' \
              ' WHERE ticker = %s AND is_active = %s'
        mutation_db(sql, (MA20_NOISE, _ticker, True))


class CheckLossWorker(threading.Thread):
    """
    손절매 담당 쓰레드
    """

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.basic_loss_ratio = 1.5  # 1.5 + noise

    def run(self):
        total_yields: float = get_total_yield()
        log(f'계좌 총 수익률: {total_yields:.2f}')
        # 총수익률이  특정 수익률 이하일 경우 종목의 손절 비율 타이트 만듬
        if total_yields < -8.0:
            self.basic_loss_ratio *= 0.7
            msg = f'계좌 총 수익률 -8% 도달 \n 손절라인 변경: {self.basic_loss_ratio}'
            log(msg)
            telegram_bot.send_coin_bot(msg)
        while True:
            for ticker in get_coin_bought_list():
                check_loss_sell(ticker, self.basic_loss_ratio)
                time.sleep(0.1)
                trailing_stop(ticker)
                time.sleep(0.1)
            time.sleep(0.5)
            print('-' * 100)


def find_bull_market_list() -> list:
    """
    상승코인 찾기
     - 이동평균 3,5 상승 변동성 돌파 및 노이즈 필터링 통과
    :return:
    """
    bull_coins = []
    for ticker in pybithumb.get_tickers():
        try:
            curr_price = pybithumb.get_current_price(ticker)
            R = calc_R(ticker, 0.5)
            target_price = calc_williams_R(ticker, R)
            MA3 = calc_fix_moving_average_by(ticker, 3)
            MA5 = calc_fix_moving_average_by(ticker, 5)
            curr_noise = get_current_noise(ticker)
            noise_ma3 = calc_fix_noise_ma_by(ticker, 3)
            noise_ma5 = calc_fix_noise_ma_by(ticker, 5)
            if curr_price > MA3 and curr_price > MA5 \
                    and curr_price > target_price and curr_noise < 0.3 \
                    and noise_ma3 < 0.55 and noise_ma5 < 0.55:
                print(f'상승 불코인: {ticker}')
                bull_coins.append(ticker)
        except Exception as E:
            print(str(E))
    return bull_coins


class FindBullCoinWorker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        while True:
            _bull_tickers = find_bull_market_list()
            print('급등 코인 목록: ', _bull_tickers)
            clear_prev_bull_coin_history(get_today_format())
            save_bull_coin(_bull_tickers)
            time.sleep(1 * 60)


def setup() -> None:
    """
    프로그램 시작전 초기화
    :return:
    """
    try:
        # calc_position_size_by_score()
        calc_position_size_by_volatility()  # 테스트 위해 소량으로 매수 시도해봄.
        filter_buy_wish_list()
        _coin_buy_wish_list, _, __ = get_buy_wish_list()
        for t in _coin_buy_wish_list:
            is_bull: bool = is_bull_market(t)
            if is_bull:
                msg = f'상승장: {t} {is_bull}'
                print(msg)
                telegram_bot.send_coin_bot(msg)
            else:
                print(f'상승장 아님: {t}')
            time.sleep(0.1)

    except Exception as e:
        log(f'setup() 예외 e: {str(e)}')


if __name__ == '__main__':
    FindBullCoinWorker().start()
    # CheckLossWorker().start()
    try:
        setup()
        basic_loss_ratio = 2.0  # 기본 손절선
        while True:
            # 메이저 코인 리스트
            coin_buy_wish_list, coin_ratio_list, coin_r_list = get_buy_wish_list()
            # 급등 코인 리스트
            bull_coin_list, bull_ratio_list, bull_r_list = get_bull_coin_list()
            coin_buy_wish_list = coin_buy_wish_list + bull_coin_list
            coin_ratio_list = coin_ratio_list + bull_ratio_list
            coin_r_list = coin_r_list + bull_r_list
            coin_bought_list: list = get_coin_bought_list()

            total_krw, use_krw = get_krw_balance()
            log(f'가용 원화: {total_krw:,} 사용한 금액: {use_krw:,}')
            krw_balance = total_krw - use_krw
            today = datetime.now()
            # 전일 코인자산 청산 시간
            start_sell_tm = today.replace(hour=23, minute=55, second=1, microsecond=0)
            end_sell_tm = today.replace(hour=23, minute=59, second=59, microsecond=0)
            # 트레이딩 시간
            start_trading_tm = today.replace(hour=0, minute=0, second=1, microsecond=0)
            end_trading_tm = today.replace(hour=23, minute=55, second=0, microsecond=0)
            now_tm = datetime.now()
            if start_sell_tm < now_tm < end_sell_tm:
                log('포트폴리오 모두 청산!')
                r = sell_all()
                time.sleep(1)
                if r is True and len(get_coin_bought_list()) == 0:
                    end_sell_tm = datetime.now()
                    start_trading_tm = datetime.now()

            for ticker in get_coin_bought_list():
                check_loss_sell(ticker, basic_loss_ratio)
                time.sleep(0.1)
                trailing_stop(ticker)
                time.sleep(0.1)

            if start_trading_tm < now_tm < end_trading_tm:
                # 매수하기 - 변동성 돌파
                for i, ticker in enumerate(coin_buy_wish_list):
                    # if ticker in daily_profit_list + daily_loss_coin_list:
                    # 당일 수익창출 또는 당일 손절매 코인 당일 재매수 제외
                    # continue
                    if coin_bought_list is None:
                        break
                    if ticker not in coin_bought_list:
                        R = calc_R(ticker, coin_r_list[i])
                        buy_coin(ticker, coin_ratio_list[i], R)
                        time.sleep(0.1)

            # 10분 마다 수익률 기록
            if (now_tm.minute == 0 and 0 <= now_tm.second <= 9) \
                    or (now_tm.minute == 10 and 0 <= now_tm.second <= 9) \
                    or (now_tm.minute == 20 and 0 <= now_tm.second <= 9) \
                    or (now_tm.minute == 30 and 0 <= now_tm.second <= 9) \
                    or (now_tm.minute == 40 and 0 <= now_tm.second <= 9) \
                    or (now_tm.minute == 50 and 0 <= now_tm.second <= 9):
                save_yield_history(get_total_yield(), len(coin_bought_list))

            # 텔레그램 수익률 보고!
            if now_tm.minute == 0 and 0 <= now_tm.second <= 7:
                send_report()
                # calc_position_size_by_score()
                calc_position_size_by_volatility()
                time.sleep(3)

            if now_tm.hour == 23 and now_tm.minute == 59 and 0 > now_tm.second > 10:
                trading_rest_time()
                time.sleep(3)

            # 매수 종목 없으면 강제 휴식
            if len(coin_buy_wish_list) == 0:
                log('매수할 코인 없음. 휴식 10초')
                time.sleep(10)

            print('-' * 150)
            time.sleep(1)
    except Exception as e:
        msg = f'가상화폐 시스템 메인 로직 예외 발생. 시스템 종료됨 => {str(e)}'
        log(msg)
        traceback.print_exc()
        telegram_bot.system_log(msg)

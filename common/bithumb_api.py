import time

import pybithumb
import os
import sys

if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
else:
    sys.path.append('/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system')

from common.utils import log, select_db, mutation_many
import traceback
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame, Series


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


"""
빗썸 private api 생성
:return: api 객체
"""
bit_keys: dict = read_bithumb_key('.env.local')
secretKey, connectKey = tuple(bit_keys.values())
bithumb = pybithumb.Bithumb(connectKey, secretKey)


def is_in_market(ticker: str) -> bool:
    """ 해당 코인티커가 빗썸시장에 상장되어 있는지 확인 체크 """
    all_tickers = pybithumb.get_tickers()
    return ticker in all_tickers


def get_krw_balance() -> tuple:
    """
    보유 원화 금액 조회하기
    :return: 주문 가능 금액
    """
    try:
        _balance = bithumb.get_balance('BTC')
        _total_coin, _coin_use_quantity, total_krw, _buy_use_krw = _balance
        # print(f'{total_krw:,}')
        return int(total_krw), int(_buy_use_krw)
    except Exception as e:
        log(f'get_krw_balance() 예외 발생:  {str(e)}')
        traceback.print_exc()
        return 0, 0


def calc_buy_quantity(ticker: str) -> float:
    """
    매수 가능한 수량 계산(수수료 미고려)
    본인 계좌의 원화 잔고를 조회후 최우선 매도 호가금액을 조회후 매수할수 있는 갯수 계산
    :param ticker: 코인티커
    :return: quantity: 주문 가능한 수량
    """
    try:
        active_ticker: list = pybithumb.get_tickers()
        if ticker in active_ticker:
            total_krw, use_krw = get_krw_balance()
            order_krw = total_krw - use_krw
            # print(f'보유 원화: {total_krw:,}')
            orderbook: dict = pybithumb.get_orderbook(ticker)
            # 매도 호가
            asks: list = orderbook['asks']
            if (len(asks) > 0) and (order_krw > 0):
                min_sell_price: float = asks[0]['price']
                # print(min_sell_price)
                quantity: float = order_krw / min_sell_price
                return quantity
    except Exception as e:
        log(f'calc_buy_quantity() 예외 발생:  {str(e)}')
        traceback.print_exc()
        return 0


def buy_limit_price(ticker: str, price: float, quantity: float) -> tuple or None:
    """
    지정가 매수 주문
    :param ticker:
    :param price:
    :param quantity:
    :return: 주문 정보 ('bid', 'XLM', 'C0504000000166659595', 'KRW')
        주문타입, 코인티커, 주문번호, 주문 통화
    """
    try:
        if ticker in pybithumb.get_tickers():
            # 지정가 주문
            total_krw, use_krw = get_krw_balance()
            order_krw = total_krw - use_krw
            orderbook = pybithumb.get_orderbook(ticker)
            asks = orderbook['asks']
            possible_order_quantity = order_krw / asks[0]['price']
            if len(asks) > 0 and order_krw > 0:
                if possible_order_quantity >= quantity:
                    order_desc = bithumb.buy_limit_order(ticker, int(price), quantity)
                    if type(order_desc) is dict and order_desc['status'] != '0000':
                        log(f'지정가 매수 주문 실패(api 실패): {order_desc}')
                        return None
                    else:
                        return order_desc
                else:
                    log('주문가능 수량보다 더 많은 수량을 주문했습니다.')
                    log(f'quantity: {quantity}, possible_order_quantity: {possible_order_quantity} ')
                    return None
            else:
                log('주문 호가가 존재하지 않습니다.')
    except Exception as e:
        log(f'buy_limit_price() 예외 발생:  {str(e)}')
        traceback.print_exc()


def buy_market_price(ticker: str, quantity: float) -> tuple:
    """
    시장가 매수하기
    :param ticker: 코인 티커
    :param quantity:  수량
    :return:  ('bid', 'XLM', 'C0504000000166655824', 'KRW')
    주문타입, 코인티커, 주문번호, 주문에 사용된 통화
    """
    try:
        active_ticker: list = pybithumb.get_tickers()
        if ticker in active_ticker:
            orderbook: dict = pybithumb.get_orderbook(ticker)
            # 매도 호가 목록
            asks: list = orderbook['asks']
            if len(asks) > 0:
                order_no = bithumb.buy_market_order(ticker, quantity)
                return order_no
    except Exception as e:
        log(f'buy_market_price() 예외 발생:  {str(e)}')
        traceback.print_exc()


def get_coin_quantity(ticker: str) -> tuple:
    """
     코인 잔고 조회
    :param ticker: 코인티커
    :return: (총 보유수랑, 매수/매도에 사용된 수량)
    """
    try:
        if is_in_market(ticker):
            total_coin, used_coin, _krw_total, _krw_use = bithumb.get_balance(ticker)
            return total_coin, used_coin
    except Exception as e:
        log(f'get_coin_quantity() 예외 발생:  {str(e)}')
        traceback.print_exc()


def sell_market_price(ticker: str, quantity: float) -> tuple:
    """
    시장가 매도하기
    :param ticker: 코인티커
    :return: 주문 정보
    """
    try:
        coin_total, coin_use = get_coin_quantity(ticker)
        order_coin_qty = coin_total - coin_use
        order_book: dict = bithumb.get_orderbook(ticker)
        bids: list = order_book['bids']
        if len(bids) > 0:
            if order_coin_qty >= quantity:
                order = bithumb.sell_market_order(ticker, quantity)  # 시장가 매도
                return order
            else:
                log(f'주문 실패: 주문가능수량:{order_coin_qty}, 요청 수량: {quantity}')
        else:
            log(f'매수 호가가 존재하지 않습니다. {bids}')
    except Exception as e:
        log('지정가 매도 주문 실패 => ', str(e))
        traceback.print_exc()


def sell_limit_price(ticker: str, price: float, quantity: float) -> tuple:
    """
    지정가 매도
    :param ticker: 코인티커
    :param price: 매도가격
    :param quantity: 수량
    :return: 주문번호
    """
    try:
        coin_total, coin_use = get_coin_quantity(ticker)
        order_coin_qty = coin_total - coin_use
        orderbook: dict = bithumb.get_orderbook(ticker)
        bids: list = orderbook['bids']
        if len(bids) > 0:
            if order_coin_qty >= quantity:
                order = bithumb.sell_limit_order(ticker, price, quantity)
                return order
            else:
                log(f'주문 실패: 주문가능수량:{order_coin_qty}, 요청 수량: {quantity}')
        else:
            log(f'매수 호가가 존재하지 않습니다. {bids}')
    except Exception as e:
        log('지정가 매도 주문 실패 => ', str(e))


def get_my_order_completed_info(order_desc: tuple) -> tuple:
    """
    체결된 주문 내역 조회
    :param order_desc:
        (type: 'bid' or 'ask', ticker, order_id, 통화 )
        ex: ('bid', 'ETH', 'C1231242131', 'KRW')
    :return: tuple
        체결 1건일 경우: (거래타입, 코인티커, 체결가격, 수량 ,수수료(krw), 거래금액)
        여러건 채결일 경우: (거래타입, 코인티커, 체결평균가격, 총수량, 총수수료, 거래금액)
    """
    try:
        res: dict = bithumb.get_order_completed(order_desc)
        if res['status'] == '0000':
            data: dict = res['data']
            order_type = data['type']
            order_status = data['order_status']
            if order_status == 'Completed':
                ticker = data['order_currency']
                # order_price = data['order_price']  # 시장가 주문시 비어있음
                contract: list = data['contract']
                transaction_krw_amount = 0
                if len(contract) == 1:
                    tr = contract[0]
                    buy_price = float(tr['price'])
                    order_qty = float(tr['units'])
                    fee = float(tr['fee'])
                    transaction_krw_amount = int(tr['total'])
                    return (order_type, ticker, buy_price, order_qty, fee, transaction_krw_amount)
                elif len(contract) > 1:
                    total_order_qty = 0
                    total_fee = 0
                    avg_buy_price = 0
                    for tr in contract:
                        avg_buy_price += float(tr['price'])
                        total_order_qty += float(tr['units'])
                        total_fee += float(tr['fee'])
                        transaction_krw_amount += int(tr['total'])

                    avg_buy_price = avg_buy_price / len(contract)
                    return (order_type, ticker, avg_buy_price, total_order_qty, total_fee, transaction_krw_amount)
            else:
                log(f'현재 주문 미체결 상태(호가창에 주문대기): {order_status}')
                is_cancel: bool = bithumb.cancel_order(order_desc)
                if is_cancel is False:
                    time.sleep(1)
                    return get_my_order_completed_info(order_desc)
                else:
                    return None

    except Exception as e:
        log(f'체결된 주문 내역 조회 실패 => {str(e)}')
        return None


def crawling_cryptocurrency_info():
    """
    빗썸 코인 목록 클롤링후 디비 저장
    :return:
    """
    url = 'https://www.bithumb.com/'
    response = requests.get(url, headers={"user-agent": "Mozilla"})
    content = response.content
    # print(content)
    soup = BeautifulSoup(content, 'html5lib')
    items: list = soup.select('tbody.coin_list tr td:first-child')
    # print(items)
    data = dict()
    rows = []
    for item in items:
        # print(item.text)
        name = item.select('strong')
        name = name[0].text
        name = name.split(' ')[0]
        symbol = item.select('span.sort_coin')
        symbol = symbol[0].text
        symbol, currency = symbol.split('/')
        # print(name)
        # print(symbol)
        data[symbol] = name
        data['currency'] = currency
        rows.append((symbol, name))

    sql = 'REPLACE INTO coin_name (ticker, name) ' \
          ' VALUES (%s, %s)'
    # print(rows)
    mutation_many(sql, rows)
    return data


def crawling_cryptocurrency_info(ticker: str) -> None:
    """
    빗썸 최소 주문 갯수 수집후 DB 저장
    :return:
    """
    url = f'https://www.bithumb.com/trade/order/{ticker}_KRW'
    response = requests.get(url, headers={"user-agent": "Mozilla"})
    content = response.content
    soup = BeautifulSoup(content, 'html5lib')
    input_item: list = soup.select('div>input#coinQtyBuy')
    print(input_item[0])


def get_coin_name(ticker: str) -> str:
    """ 코인 이름 조회 """
    sql = 'SELECT name FROM coin_name WHERE ticker = %s'
    name_tup = select_db(sql, ticker)
    if name_tup:
        name = name_tup[0][0]
        return name
    else:
        crawling_cryptocurrency_info()
        get_coin_name(ticker)


def get_my_coin_balance() -> dict or None:
    """ 보유한 코인 장고 조회
    조건: 보유 수량이 0.0001 보다 많으면서 보유한 코인 평가금액이 1000원 이상인 코인
    return  {'ticker': (total, used, available)}
    보유한 잔고가 없을경우 빈 dict 리턴
    통신 오류일 경우 None 리턴
    """
    all_balance = bithumb.get_balance('ALL')
    tickers = pybithumb.get_tickers()
    balance = {}
    if all_balance['status'] == '0000':
        data = all_balance['data']
        for ticker in tickers:
            total = float(data[f'total_{ticker.lower()}'])
            used = float(data[f'in_use_{ticker.lower()}'])
            available = total - used
            if total > 0.0001:
                curr_price = pybithumb.get_current_price(ticker)
                if curr_price * total > 1000:
                    balance[ticker] = (total, used, available)
        return balance
    else:
        log(f"통신오류 => 예외코드: {all_balance['status']}")
        return None


def get_prev_volume(ticker: str) -> float or None:
    """
    이전 거래일 거래량
    :param ticker:
    :return: 거래량
    """
    try:
        prices: DataFrame = pybithumb.get_candlestick(ticker)
        if not prices.empty:
            # print(prices.tail())
            volume = prices['volume']
            return volume.iloc[-2]
        return None
    except Exception as E:
        msg = f'get_prev_volume() 예외 발생. 시스템 종료되었음. {str(E)}'
        log(msg)
        traceback.print_exc()


def calc_prev_ma_volume(ticker: str, days: int = 5) -> float or None:
    """
    거래량 이동평균 값(당일 제외)
    :param ticker:
    :param days:
    :return: 거래량
    """
    try:
        prices: DataFrame = pybithumb.get_candlestick(ticker)
        if not prices.empty:
            # print(prices.tail(6))
            volume = prices['volume']
            MA = volume.rolling(window=days).mean()
            return MA[-2]
    except Exception as E:
        msg = f'calc_prev_ma_volume() 예외 발생. 시스템 종료되었음. {str(E)}'
        log(msg)
        traceback.print_exc()


def get_current_volume(ticker: str) -> float:
    """
    당일(현재) 거래량
    :param ticker:
    :return:
    """
    try:
        prices: DataFrame = pybithumb.get_candlestick(ticker)
        if not prices.empty:
            # print(prices.tail(6))
            volume = prices['volume']
            return volume.iloc[-1]
    except Exception as E:
        msg = f'calc_prev_ma_volume() 예외 발생. 시스템 종료되었음. {str(E)}'
        log(msg)
        traceback.print_exc()


def calc_noise_ma_by(ticker: str, days: int = 30) -> float:
    """
    실시간 이동 평균 노이즈값 계산
    (당일 가격정보 포함됨)
    개별 노이즈 공식
        1 - abs(시가 - 종가) / (고가 - 저가)
    :param ticker:
    :param days:
    :return:
    """
    try:
        prices: DataFrame = pybithumb.get_candlestick(ticker)
        if type(prices) is not None and not prices.empty:
            # print(prices.tail(10))
            # 당일 노이즈 값
            noise: Series = 1 - abs(prices['open'] - prices['close']) / (prices['high'] - prices['low'])
            # print(noise.tail(days))
            # return noise[-1]
            MA_noise = noise.rolling(window=days).mean()
            # print(MA_noise.tail(days))
            return MA_noise[-1]
    except Exception as E:
        msg = f'calc_noise_ma_by() 예외 발생. {str(E)}'
        log(msg)
        traceback.print_exc()
        return 0.5


def calc_average_ma_by(ticker) -> float:
    try:
        prices: DataFrame = pybithumb.get_candlestick(ticker)
        if not prices.empty:
            # print(prices.tail(10))
            noise: Series = 1 - abs(prices['open'] - prices['close']) / (prices['high'] - prices['low'])
            avg = noise.sum() / noise.size
            return avg
        else:
            raise ValueError('가격 데이터(DataFrame) 비어있습니다.')
    except Exception as E:
        msg = f'calc_noise_ma_by() 예외 발생. 시스템 종료되었음. {str(E)}'
        log(msg)
        traceback.print_exc()


def get_prev_noise(ticker: str) -> float:
    """ 이전거래일 노이즈값 """
    try:
        prices: DataFrame = pybithumb.get_candlestick(ticker)
        if not prices.empty:
            # 당일 노이즈 값
            noise: Series = 1 - abs(prices['open'] - prices['close']) / (prices['high'] - prices['low'])
            # print(noise.tail(10))
            return noise[-2]
    except Exception as E:
        msg = f'calc_noise_ma_by() 예외 발생. 시스템 종료되었음. {str(E)}'
        log(msg)
        traceback.print_exc()


def get_current_noise(ticker: str) -> float:
    """ 현재 코인의 노이즈 값
        1 - abs(시가 - 종가) / 고가 - 저가
    """
    try:
        prices: DataFrame = pybithumb.get_candlestick(ticker)
        if not prices.empty:
            # print(prices.tail(10))
            # 당일 노이즈 값
            noise: Series = 1 - abs(prices['open'] - prices['close']) / (prices['high'] - prices['low'])
            # print(noise.tail())
            return noise[-1]
    except Exception as E:
        msg = f'calc_noise_ma_by() 예외 발생. 시스템 종료되었음. {str(E)}'
        log(msg)
        traceback.print_exc()


if __name__ == '__main__':
    # bithumb = _create_bithumb_api()
    print(f'{get_krw_balance():}')
    # print('btc 매수 가능 수량:', calc_buy_quantity('BTC'))

    # order_desc = buy_limit_price('XRP', 1020.0, 3)
    # print(order_desc)
    # order_2 = bithumb.buy_limit_order('XRP', 1020.0, 1)
    # print(order_2)

    # order3 = bithumb.buy_market_order('XRP', 1)
    # print(order3)

    # crawling_cryptocurrency_info('CHZ')
    # print(f'get_my_coin_balance() {get_my_coin_balance()}')
    # bithumb.

    order_desc = ('ask', 'BTC', 'C0101000000415579850', 'KRW')
    info = get_my_order_completed_info(order_desc)
    print(info)
    print(get_my_coin_balance())

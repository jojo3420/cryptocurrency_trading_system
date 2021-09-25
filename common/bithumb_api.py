import time
import traceback
import requests
import pybithumb
import os
import sys

if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
else:
    sys.path.append('/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system')

from bs4 import BeautifulSoup
from pandas import DataFrame, Series
from common.utils import log, select_db, mutation_many, get_today_format, mutation_db, calc_target_volatility_ratio


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


def calc_buy_quantity(ticker: str, order_krw=None, order_btc=None, market="KRW") -> float:
    """
    매수 가능한 수량 계산(수수료 미고려)
    본인 계좌의 원화 잔고를 조회후 최우선 매도 호가금액을 조회후 매수할수 있는 갯수 계산
    :param ticker: 코인티커
    :return: quantity: 주문 가능한 수량
    """
    try:
        active_ticker: list = pybithumb.get_tickers()
        if ticker in active_ticker:
            if market == 'KRW':
                if order_krw is None:
                    total_krw, use_krw = get_krw_balance()
                    order_krw = total_krw - use_krw - 5000
                else:
                    order_krw -= 5000
                # print(f'보유 원화: {total_krw:,}')
                order_book: dict = pybithumb.get_orderbook(ticker)
                # 매도 호가
                asks: list = order_book.get('asks', [])
                if asks and order_krw > 0:
                    lower_sell_price: float = asks[0]['price']
                    # print(min_sell_price)
                    quantity: float = order_krw / lower_sell_price
                    return round(quantity, 7)
            elif market == 'BTC':
                if order_btc is None:
                    total_btc, used = get_balance_coin(market)
                    order_btc = total_btc - used
                order_book: dict = pybithumb.get_orderbook(ticker, payment_currency=market)
                asks = order_book.get('asks', [])
                if asks and order_btc > 0:
                    lower_sell_price = asks[0]['price']
                    quantity = order_btc / lower_sell_price
                    return round(quantity, 7)
            else:
                raise ValueError('지원하지 않는 마켓입니다. => ', market)





    except Exception as e:
        log(f'calc_buy_quantity() 예외 발생:  {str(e)}')
        traceback.print_exc()
        return 0


def buy_limit_price(ticker: str, entry_price: float, quantity: float, market='KRW') -> tuple or None:
    """
    지정가 매수 주문
    :param ticker:
    :param entry_price:
    :param quantity:
    :return: 주문 정보 ('bid', 'XLM', 'C0504000000166659595', 'KRW')
        주문타입, 코인티커, 주문번호, 주문 통화
    """
    try:
        if ticker in pybithumb.get_tickers(payment_currency=market):
            # 지정가 주문
            total_krw, used_krw = get_krw_balance()
            cash = total_krw - used_krw
            order_book = pybithumb.get_orderbook(ticker, payment_currency=market)
            asks = order_book['asks']
            if market == 'KRW':
                if len(asks) > 0 and cash > 0:
                    ask_price = asks[0]['price']
                    possible_order_quantity = cash / entry_price
                    if possible_order_quantity >= quantity:
                        _integer_part, decimal_part = str(float(entry_price)).split('.')
                        if int(decimal_part) == 0:
                            entry_price = int(float(entry_price))
                        order_desc = bithumb.buy_limit_order(ticker, entry_price, quantity, payment_currency=market)
                        log(f'매도호가: {ask_price:,.0f}, 진입가: {entry_price:,.0f}')
                        if isinstance(order_desc, dict) and order_desc['status'] != '0000':
                            log(f'지정가 매수 주문 실패(api 실패): {order_desc}')
                        return order_desc
                    else:
                        log('주문가능 수량보다 더 많은 수량을 주문했습니다.')
                        log(f'quantity: {quantity}, possible_order_quantity: {possible_order_quantity} ')
                        return None
                else:
                    log('주문 호가가 존재하지 않거나 캐쉬가 충분하지 않습니다.')
                    log(asks, cash)
            elif market == 'BTC':
                print(f'BTC 마켓에서 {ticker} 코인 매수하기')
                if len(asks) > 0 and cash > 0:
                    btc_qty = cash
                    qty = btc_qty / entry_price
                    if qty >= quantity:
                        ask = asks[0].get("price")
                        order_desc = bithumb.buy_limit_order(ticker, entry_price, quantity, payment_currency=market)
                        log(f'매도호가: {ask:.8f}, 진입가: {entry_price:.8f}')
                        if isinstance(order_desc, dict) and order_desc['status'] != '0000':
                            log(f'지정가 매수 주문 실패(api 실패): {order_desc}')
                        return order_desc
                    else:
                        log('주문가능 수량보다 더 많은 수량을 주문했습니다.')
                        log(f'주문요구수량: {quantity}, 주문가능수량: {qty} ')
                        return None
        else:
            log(f'{ticker} 가 매수할수 있는 종류의 마켓{market}에 없습니다.')
            return None
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


def get_balance_coin(ticker: str) -> tuple:
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
        log(f'get_balance_coin() 예외 발생:  {str(e)}')
        traceback.print_exc()


def sell_market_price(ticker: str, quantity: float) -> tuple:
    """
    시장가 매도하기
    :param ticker: 코인티커
    :return: 주문 정보
    """
    try:
        coin_total, coin_use = get_balance_coin(ticker)
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


def sell_limit_price(ticker: str, price: int, quantity: float) -> tuple:
    """
    지정가 매도
    :param ticker: 코인티커
    :param price: 매도가격
    :param quantity: 수량
    :return: 주문번호
    """
    try:
        coin_total, coin_use = get_balance_coin(ticker)
        order_coin_qty = coin_total - coin_use
        orderbook: dict = bithumb.get_orderbook(ticker)
        bids: list = orderbook['bids']
        asks: list = orderbook['asks']
        if bids and len(bids) > 0:
            if order_coin_qty >= quantity:
                bid = bids[0].get('price')
                _integer_part, decimal_part = str(bid).split('.')
                if int(decimal_part) == 0:
                    price = int(float(price))
                log(f'시장매도호가: {asks[0].get("price")}, 시장매수호가: {bid}')
                log(f'나의 매도 주문가: {price:,.8f} 수량: {quantity}')
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


def get_my_coin_balance(symbol='ALL') -> dict or tuple:
    """ 보유한 코인 장고 조회
    조건: 보유 수량이 0.0001 보다 많으면서 보유한 코인 평가금액이 1000원 이상인 코인
    return  {'ticker': (total, used, available)}
    보유한 잔고가 없을경우 빈 dict 리턴
    통신 오류일 경우 None 리턴
    """
    if symbol == 'ALL':
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
                    if curr_price * total > 2000:
                        balance[ticker] = (total, used, available)
            return balance
    else:
        coin_qty, used_coin_qty, _total_krw, _used_krw = bithumb.get_balance(symbol)
        return coin_qty, used_coin_qty


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


def calc_fix_noise_ma_by(ticker: str, days: int = 30) -> float:
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
        if '-' in ticker:
            return
        print('calc_fix_noise_ma_by: ', ticker)
        prices: DataFrame = pybithumb.get_candlestick(ticker)
        if type(prices) is not None and not prices.empty:
            # print(prices.tail(10))
            # 당일 노이즈 값
            noise: Series = 1 - abs(prices['open'] - prices['close']) / (prices['high'] - prices['low'])
            # print(noise.tail(10))
            MA_noise = noise.rolling(window=days).mean()
            # print(MA_noise.tail(10))
            return MA_noise[-2]
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
            return round(noise[-1], 6)
    except Exception as E:
        msg = f'calc_noise_ma_by() 예외 발생. 시스템 종료되었음. {str(E)}'
        log(msg)
        traceback.print_exc()


def calc_add_noise_weight(ticker: str) -> float:
    """
    포트폴리오 노이즈 가중치 계산
    공식
        (1 - 3일 이동평균 노이즈) / 4
    :param ticker:
    :return:
    """
    noise_ma3 = calc_fix_noise_ma_by(ticker, 3)
    noise_weight = (1 - noise_ma3) / 4
    return noise_weight


def cancel_order(order_desc) -> bool:
    return bithumb.cancel_order(order_desc)


def buy_or_cancel_btc_market(ticker, quantity, delay=3, is_uptic=False, loop_cnt=0) -> tuple:
    """
    BTC 마켓에서 BTC 코인로 티커 코인 bid 가격으로 매수
      일정 시간(3초) 지연시킨 후 체결시 매수 주문 취소
      체결 완료 될때 까지 무한루프!

    :param ticker:
    :param quantity:
    :return:

    정상 매수시 출력 로그
    매도 호가
    4 0.00002652, 1,573, 4366.000000
    3 0.00002632, 1,561, 15013.000000
    2 0.00002631, 1,561, 15000.000000
    1 0.00002621, 1,555, 1463.000000
    0 0.00002617, 1,553, 549.806500
    매수 호가
    1 0.00002608, 1,547, 45.029000
    2 0.00002607, 1,547, 446.000000
    3 0.00002604, 1,545, 4991.260500
    4 0.00002599, 1,542, 557.910800
    5 0.00002598, 1,541, 15000.000000
    ----------------------------------------------------------------------------------------------------
    BTC 마켓에서 BTC로 매수하기
    [2021-09-06 21:41:48.055668] 매도호가: 2.617e-05, 진입가: 2.608e-05
    ('bid', 'XRP', 'C0106000000291416149', 'BTC')
    매수주문 체결 안됨. 취소 주문진행!
    cancel: True
    """
    from common.math_util import get_uptic_price
    if loop_cnt > 5:
        return 0, ()

    market = 'BTC'
    quantity = round(quantity, 4)
    order_book = pybithumb.get_orderbook(ticker, payment_currency=market)
    asks = order_book.get('asks')
    bids = order_book.get('bids')
    print('매도 호가')
    btc_curr_price = pybithumb.get_current_price(market)
    for end_idx in range(len(asks) - 1, -1, -1):
        print(
            f'{end_idx} {asks[end_idx].get("price"):.8f}BTC, {asks[end_idx].get("price") * btc_curr_price:,.0f}KRW, {format(asks[end_idx].get("quantity"), "f")}개')

    print('매수 호가')
    for st_idx, bid in enumerate(bids, 1):
        # print(bid)
        print(
            f'{st_idx} {bid.get("price"):.8f}BTC, {bid.get("price") * btc_curr_price:,.0f}KRW, {format(bid.get("quantity"), "f")}개')
    bid_price = bids[0]['price']
    print(f'bid_price: {format(bid_price, ".8f")}')
    if is_uptic:
        bid_price = get_uptic_price(bid_price, 1)
        print(f'after: {format(bid_price, ".8f")}')
    before_coin_balance, _used = get_balance_coin(ticker)
    print(f'진입 BTC: {format(quantity * bid_price, ".8f")}')
    order_desc = buy_limit_price(ticker, bid_price, quantity, market=market)
    print(f'order_desc: {order_desc}')
    time.sleep(delay)
    coin_balance, used = get_balance_coin(ticker)
    coin_balance -= used
    if coin_balance == before_coin_balance:
        print('매수주문 체결 안됨. 취소 주문진행!')
        cancel = cancel_order(order_desc)
        print(f'cancel: {cancel}')
        print('-' * 100)
        if cancel is True:
            return buy_or_cancel_btc_market(ticker, quantity, delay=delay, is_uptic=is_uptic, loop_cnt=loop_cnt + 1)
    elif coin_balance > before_coin_balance:
        total_qty, _used = get_balance_coin(ticker)
        print('매수성공!', total_qty)
        return bid_price, order_desc


def buy_or_cancel_krw_market(ticker, position_size_cash, delay=3, is_uptic=False, loop_cnt=0) -> tuple:
    """
    원화 마켓 코인 매수 주문후 지연(초)후 미체결시 주문 취소 (Immediate Or Cancel)
    :param delay: 매수 주문 요청후 대기후(기본:3초) 잔고 수량 확인
    :param ticker: 매수할 코인 티커
    :param position_size_cash: 매수 주문에 사용할 금액
    :return:
    """
    from common.math_util import get_uptic_price

    if loop_cnt > 5:
        return 0, ()

    total_krw, used_krw = get_krw_balance()
    cash = total_krw - used_krw
    print(f'cash: {cash:,.0f}')
    if cash >= position_size_cash:
        order_book = pybithumb.get_orderbook(ticker, payment_currency='KRW')
        bids = order_book['bids']
        asks = order_book['asks']
        print('매수 호가')
        for start_idx, bid_dict in enumerate(bids, start=1):
            bid = bid_dict.get('price', 0)
            print(f'{start_idx} {bid:,}')
        print('매도 호가')
        for start_idx, ask_dict in enumerate(asks, start=1):
            ask = ask_dict.get('price', 0)
            print(f'{start_idx} {ask:,}')
        print('-' * 100)
        curr_price = pybithumb.get_current_price(ticker)
        if curr_price > cash:
            print(f'현재 보유원화로 1개도 매수할수 없습니다. 현재시세: {curr_price:,} 원화: {cash:,} ')
            return 0, ()
        else:
            qty = calc_buy_quantity(ticker, order_krw=position_size_cash, market="KRW")
            print(f'매수 수량: {qty}')
            before_coin_balance, _used_coin = get_balance_coin(ticker)
            entry_price = bids[0].get('price', 0)
            if entry_price and is_uptic:
                entry_price = int(get_uptic_price(entry_price))
            print(f'진압가: {entry_price:,.8f}')
            order_desc = buy_limit_price(ticker, entry_price, qty)
            print(f'매수 주문 결과: {order_desc}')
            time.sleep(delay)
            total_coin_balance, _used = get_balance_coin(ticker)
            print(f'매수주문후 잔고: {total_coin_balance}')
            if before_coin_balance == total_coin_balance:
                r = cancel_order(order_desc)
                print(f'매수 체결 안됨.. 주문취소: {r}')
                if r:
                    print('-' * 100)
                    return buy_or_cancel_krw_market(ticker, position_size_cash, delay=delay, loop_cnt=loop_cnt + 1)
            else:
                print(f'주문 성공=> 이전수량: {before_coin_balance} 요청수량: {qty} : 현재수량:{total_coin_balance}')
                print('-' * 100)
                return entry_price, order_desc
    else:
        print(f'cash 부족 => {cash}')
        return 0, ()


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

    # order_desc = ('ask', 'BTC', 'C0101000000415579850', 'KRW')
    # info = get_my_order_completed_info(order_desc)
    # print(info)
    # print(get_my_coin_balance())
    # print(calc_fix_noise_ma_by('BTC', 5))

    # _balance = bithumb.get_balance('ENJ')
    # print(_balance)
    # print(calc_target_volatility_ratio('ENJ'))
    print(pybithumb.get_candlestick('ETH'))
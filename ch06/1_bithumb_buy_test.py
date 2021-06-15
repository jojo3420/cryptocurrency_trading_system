import time
import pybithumb
from common.utils import *

bit_keys: dict = read_bithumb_key('.env.local')
print(bit_keys)
secretKey, connectKey = tuple(bit_keys.values())
bithumb = pybithumb.Bithumb(connectKey, secretKey)


# btc_balance: tuple = bithumb.get_balance('BTC')
# 총잔고, 코인수량, 보유중인 총원화, 주문에 사영된 원화
# print(btc_balance)
# print(format(btc_balance[0], 'f'))  # 보기좋게 포맷팅


def buy_limit_price(ticker: str, price: float, quantity: float) -> tuple:
    """
    지정가 매수 주문
    :param ticker:
    :param price:
    :param quantity:
    :return: 주문 정보 ('bid', 'XLM', 'C0504000000166659595', 'KRW')
        주문타입, 코인티커, 주문번호, 주문 통화

    """
    if ticker in pybithumb.get_tickers():
        # 지정가 주문
        total_krw, _use_krw = get_krw_balance()
        order_krw = total_krw - _use_krw
        orderbook = pybithumb.get_orderbook(ticker)
        asks = orderbook['asks']
        possible_order_quantity = order_krw / asks[0]['price']
        if len(asks) > 0:
            if possible_order_quantity >= quantity:
                order = bithumb.buy_limit_order(ticker, price, quantity)
                return order
            else:
                log('주문가능 수량보다 더 많은 수량을 주문했습니다.')
                log(f'quantity: {quantity}, possible_order_quantity: {possible_order_quantity} ')
                return None
        else:
            log('주문 호가가 존재하지 않습니다.')


def get_krw_balance() -> tuple:
    """
    보유 원화 금액 조회하기
    :return: 주문 가능 금액
    """
    _balance = bithumb.get_balance('BTC')
    # 총코인, 사용중 코인, 보유중인 총원화, 주문에 사용된 원화
    _coin_quantity, _use_coin_quantity, total_krw, use_krw = _balance
    # print(f'{total_krw:,}')
    return int(total_krw), int(use_krw)


def calc_buy_quantity(ticker: str) -> float:
    """
    매수 가능한 수량 계산(수수료 미고려)
    본인 계좌의 원화 잔고를 조회후 최우선 매도 호가금액을 조회후 매수할수 있는 갯수 계산
    :param ticker: 코인티커
    :return: quantity: 주문 가능한 수량
    """
    active_ticker: list = pybithumb.get_tickers()
    if ticker in active_ticker:
        total_krw, _use_krw = get_krw_balance()
        order_krw = total_krw - _use_krw  # 주문가능금액
        # print(f'보유 원화: {total_krw:,}')
        orderbook: dict = pybithumb.get_orderbook(ticker)
        # 매도 호가
        asks: list = orderbook['asks']
        if len(asks) > 0:
            min_sell_price: float = asks[0]['price']
            # print(min_sell_price)
            quantity: float = order_krw / min_sell_price
            return quantity


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
        return None
    except Exception as e:
        log(f'시장가 매수주문 예외 발생:  {str(e)}')
        traceback.print_exc()


total_krw, use_krw = get_krw_balance()
print('총잔고:', total_krw)
print('주문가능금액: ', total_krw - use_krw)

quantity = calc_buy_quantity('ETH')
print(quantity)

# order_info: tuple = buy_market_price('XLM', 3)
# print(order_info)

order = buy_limit_price('XLM', 200, 3)
print(order)

# order_desc = bithumb.buy_limit_order('XLM', 200, 2)
# print(order_desc)
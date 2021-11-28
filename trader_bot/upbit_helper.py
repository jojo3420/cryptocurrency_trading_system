import time
import traceback
import pyupbit
import os
import constant
from common.utils import log
from db_helper import *
from math_helper import *


class UpbitHelper:
    def __init__(self, path='.env.dev', debug_mode=False):
        root = constant.ROOT_DIR
        os.chdir(root)
        self.debug_mode = debug_mode
        with open(path) as stream:
            keys = {}
            lines = stream.readlines()
            for line in lines:
                _label, key = line.split('=')
                keys[_label] = key.strip()
            # print(keys)
            self.api = pyupbit.Upbit(keys['AccessKey'], keys['SecretKey'])

    def set_debug_mode(self, mode: bool):
        """ 디버그 모드  ON/OFF """
        self.debug_mode = mode

    def buy(self, symbol: str, quantity: float, entry_price: int) -> dict:
        """
        지정가 매수하기
        :param symbol: KRW-BTC : 원화시장에서 BTC 매수
        :param quantity: 수량
        :param entry_price: 매수가(진입가)
        :return:
        """
        quantity = round(quantity, 4)
        if symbol and '-' in symbol and quantity > 0:
            curr_price = pyupbit.get_current_price(symbol)
            minimum_amount = self.get_minimum_order_possible_amount(symbol)  # 최소 주문 가능 수량
            order_total_amount = entry_price * quantity
            if self.debug_mode:
                log(f'최소주문금액: {minimum_amount}, 나의 주문금액: {order_total_amount}')

            if order_total_amount < minimum_amount:
                msg = f'주문금액이 최소주문금액 이하 입니다. => {symbol} 최소주문금액: {minimum_amount:,}'
                log(msg)
                return {'err_msg': msg}

            log(f'{symbol} 현재가: {curr_price:,.0f}')
            # 지정가 매수
            ret = self.api.buy_limit_order(symbol, entry_price, volume=quantity)
            if self.debug_mode:
                log(f'매수 주문결과: {ret}')
                # {'uuid': '13e79a6c-78f7-4759-af47-fb01086d6926', 'side': 'bid', 'ord_type': 'limit', 'price': '995.0', 'state': 'wait', 'market': 'KRW-XRP', 'created_at': '2021-09-13T20:52:51+09:00', 'volume': '10.0', 'remaining_volume': '10.0', 'reserved_fee': '4.975', 'remaining_fee': '4.975', 'paid_fee': '0.0', 'locked': '9954.975', 'executed_volume': '0.0', 'trades_count': 0}

            return ret
        else:
            msg = f'티커명 규칙은 마켓심볼-매수할코인심볼 입니다. {symbol}'
            log(msg)
            return {'err_msg': msg}

    def buy_current_price(self, symbol: str, quantity):
        """
        현재가 매수 (현재시세로 매수) (체결 가능성 높음)
        :param symbol:
        :param quantity:
        :param bid:
        :return:
        """
        entry_price = pyupbit.get_current_price(symbol)
        return self.buy(symbol, quantity, entry_price)

    def buy_ask_price(self, symbol: str, quantity: float):
        """
        현재 최하위 매도호가 가격으로 매수주문 (체결가능성 매수 높음)
        :param symbol:
        :param quantity:
        :return:
        """
        ask, _ = get_lowest_ask_info(symbol)
        if ask:
            self.buy(symbol, quantity, ask)

    def buy_up_tic(self, symbol: str, quantity: float, tic_cnt=1):
        """
        현재가 보다 높게 업틱 올려서 매수준 주문 낸다.
        :param symbol: 심볼
        :param quantity: 수량
        :param tic_cnt: 1
        :return:
        """
        tic = get_krw_market_tic_cap(symbol)
        total_tic = 0
        for n in range(tic_cnt):
            total_tic += tic
        bid, _ = get_highest_bid_info(symbol)
        entry_price = bid + total_tic
        return self.buy(symbol, quantity, entry_price=entry_price)

    def buy_down_tic(self, symbol: str, quantity: float, tic_cnt: int):
        """
           현재가 보다 높게 업틱 올려서 매수준 주문 낸다.
           :param symbol: 심볼
           :param quantity: 수량
           :param tic_cnt: 1
           :return:
           """
        tic = get_krw_market_tic_cap(symbol)
        total_tic = 0
        for n in range(tic_cnt):
            total_tic += tic
        bid, _ = get_highest_bid_info(symbol)
        entry_price = bid - total_tic
        return self.buy(symbol, quantity, entry_price=entry_price)

    def calc_sell_quantity(self, symbol: str) -> float:
        """
        매도 가능 수량(available) 리턴
        :param symbol:
        :return: 매도 주문가능 수량
        """
        if '-' in symbol:
            _, ticker = symbol.split('-')
            _, available, used = self.get_coin_balance(ticker)
            return available

    def sell(self, symbol: str, quantity: float, ask_price: int) -> dict:
        """
        매도 주문(지정가)
        :param symbol:
        :param quantity:
        :param ask_price:
        :return: {'uuid', str, avg_price: int
        """
        if '-' in symbol:
            if ask_price and quantity > 0:
                available_qty = self.calc_sell_quantity(symbol)
                if available_qty >= quantity:
                    my_order_krw = ask_price * quantity
                    order_possible_krw = self.get_minimum_order_possible_amount(symbol)
                    if my_order_krw >= order_possible_krw:
                        ret = self.api.sell_limit_order(symbol, ask_price, quantity)
                        if self.debug_mode:
                            log(ret)
                            # {'uuid': 'e15fa46b-0237-4539-b33b-b00851f72dbb',
                            #  'side': 'ask', 'ord_type': 'limit',
                            #  'price': '2000.0',
                            #  'state': 'wait', 'market': 'KRW-XRP',
                            #  'created_at': '2021-09-23T21:03:44+09:00',
                            #  'volume': '4.0', 'remaining_volume': '4.0',
                            #  'reserved_fee': '0.0', 'remaining_fee': '0.0',
                            #  'paid_fee': '0.0', 'locked': '4.0',
                            #  'executed_volume': '0.0',
                            #  'trades_count': 0
                            #  }
                        # return {
                        #     'uuid': ret.get('uuid', ''),
                        #     'state': ret.get('state', ''),
                        #     # 미체결시 avg_price 는 0
                        #     'avg_price': int(float(ret.get('avg_price', 0))),  # 체결가의 평균가
                        #     'quantity': float(ret.get('executed_volume', 0)),  # 체결 수량
                        #     'fee': float(ret.get('paid_fee', 0)),  # 지불한 수수료
                        # }
                        return ret
                    else:
                        return {
                            'err_msg': f'주문 요청금액({my_order_krw:,})이 작습니다. 최소주문금액({order_possible_krw:,}) 이상으로 주문하세요.'}
                else:
                    return {'err_msg': f'주문 요청수량이({quantity}) 주문가능수량{(available_qty)} 보다 큽니다.'}
            else:
                return {'err_msg': f'매수호가 또는 수량이 유효하지 않습니다. {ask_price} || {quantity}'}

        else:
            return {'err_msg': f'심볼을 확인해주세요 {symbol}'}

    def sell_current_price(self, symbol: str, quantity: float):
        """
        현재가 기준으로 매도 주문
        :param symbol:
        :param quantity:
        :return:
        """
        current_price = pyupbit.get_current_price(symbol)
        return self.sell(symbol, quantity, current_price)

    def sell_bid_price(self, symbol: str, quantity: float):
        """
        매수호가 가격으로 매도 주문실행(체결가능성 매우높음)
        :param symbol:
        :param quantity:
        :return:
        """
        bid, _ = get_highest_bid_info(symbol)
        return self.sell(symbol, quantity, ask_price=bid)

    def sell_up_tic(self, symbol: str, quantity: float, tic_cnt=1):
        """
        매도 호가창 기준으로 업틱으로 매도 주문
        :param symbol: 매도할 심볼
        :param quantity: 수량
        :param tic_cnt: 틱 횟수
        :return:
        """
        tic = get_krw_market_tic_cap(symbol)
        sum_tic = 0
        for n in range(tic_cnt):
            sum_tic += tic
        ask, _ = get_lowest_ask_info(symbol)
        ask_price = ask + sum_tic
        return self.sell(symbol, quantity, ask_price)

    def sell_down_tic(self, symbol: str, quantity: float, tic_cnt=1):
        """
          매도 호가창 기준으로 다운틱으로 매도 주문
          :param symbol: 매도할 심볼
          :param quantity: 수량
          :param tic_cnt: 틱 횟수
          :return:
        """
        tic = get_krw_market_tic_cap(symbol)
        sum_tic = 0
        for n in range(tic_cnt):
            sum_tic += tic
        ask, _ = get_lowest_ask_info(symbol)
        ask_price = ask - sum_tic
        return ask_price
        # return self.sell(symbol, quantity, ask_price)

    def sell_all(self) -> list:
        """
        코인 잔고 모두 청산: 현재가 매도
        1) coin_bought_list 업데이트
        2) coin_transaction_history 매도주문 기록
        :return:
        """
        uuid_list = []
        while True:
            coin_balances = self.get_coin_balance('ALL')
            if len(coin_balances) == 0:
                return uuid_list
            # 청산 로직
            for ticker, available_qty, used in coin_balances:
                symbol = f'KRW-{ticker}'
                log(f'{symbol} 코인 청산 주문!')
                if available_qty > 0:
                    ret: dict = self.sell_current_price(symbol, available_qty)
                    # print(f'sell_all ret: {ret}')
                    err_msg = ret.get('err_msg', '')
                    state = ret.get('state', '')
                    log(f'state: {state}')
                    if err_msg:
                        log(err_msg)
                    else:
                        uuid = ret.get('uuid')
                        uuid_list.append(uuid)
                time.sleep(0.5)
            time.sleep(0.1)

    def order_cancel(self, uuid: str) -> bool:
        """
        주문 취소하기
        :param uuid: 주문번호
        :return: True or False
        """
        ret = self.api.cancel_order(uuid=uuid)
        if self.debug_mode:
            print('주문취소 결과:', ret)
        # 주문취소 결과: {'uuid': 'd02faa13-53ee-4041-aa12-229a4aa08d35', 'side': 'ask', 'ord_type': 'limit',
        # 'price': '2700.0', 'state': 'wait', 'market': 'KRW-XRP',
        # 'created_at': '2021-08-29T20:20:37+09:00', 'volume': '5.0',
        # 'remaining_volume': '5.0', 'reserved_fee': '0.0',
        # 'remaining_fee': '0.0', 'paid_fee': '0.0', 'locked': '5.0',
        # 'executed_volume': '0.0', 'trades_count': 0}

        cancel_order_uuid = ret.get('uuid', '')
        if cancel_order_uuid and 'error' not in ret:
            order_type = ret.get('ord_type', '')
            order_state = ret.get('state', '')
            ask_price = ret.get('price', -1)
            quantity = ret.get('volume', -1)
            if self.debug_mode:
                log(f'주문취소 uuid: {cancel_order_uuid}')
                log(f'주문타입: {order_type}')  # limit: 지정가 매수
                log(f'주문상태: {order_state}, 매도가: {ask_price}, 수량: {quantity}')
            return True
        else:
            error = ret.get('error', '')
            print(error)
            return False

    def get_coin_balance(self, ticker="ALL") -> dict or tuple:
        """
        잔고조회 하기
        :param ticker: 'ALL' 전체잔고, 특정티커: 티커잔고만 조회
        :return: [tuple, tuple, tuple...] OR tuple
        ex) XRP, 10, 5
        """
        try:
            total_balance: list = self.api.get_balances()
            balance_list = []
            for balance in total_balance:
                # print(balance)
                _ticker = balance.get('currency')  # KRW, XRP, BTC ...
                available = balance.get('balance')
                used = balance.get('locked')
                # print(type(balance))
                if self.debug_mode:
                    log(f'_ticker: {_ticker}, available: {float(available):,.2f}, used: {used}')

                if _ticker == 'KRW':
                    available = int(float(available))
                    used = int(float(used))
                else:
                    available = float(available)
                    used = float(used)

                element: tuple = (_ticker, available, used)
                if ticker == 'KRW' and ticker == _ticker:
                    return element
                if ticker != 'ALL' and ticker == _ticker:
                    return element
                elif ticker == 'ALL' and _ticker != 'KRW':
                    balance_list.append(element)
            return balance_list
        except Exception as ex:
            traceback.print_exc()
            msg = f'get_coin_balance() 예외발생 {str(ex)}'
            log(msg)
            # return msg

    def get_cash_balance(self):
        """
        현금 잔고 조회
        :return: 주문가용현금,
        """
        _, available, used = self.get_coin_balance('KRW')
        if self.debug_mode:
            log(f'{_}, available: {available:,}, used: {used:,}')
        return available, used

    def get_transaction_history(self):
        pass

    def get_chance(self, symbol):
        """
         마켓별 주문 가능 정보를 확인.
        :param symbol:
        :return:
        {'bid_fee': '0.0005', 'ask_fee': '0.0005', 'maker_bid_fee': '0.0005',
        'maker_ask_fee': '0.0005', 'market': {'id': 'KRW-XRP', 'name': 'XRP/KRW',
        'order_types': [], 'order_sides': ['ask', 'bid'],
        'bid': {'currency': 'KRW', 'price_unit': None, 'min_total': '5000.0'},
        'ask': {'currency': 'XRP', 'price_unit': None, 'min_total': '5000.0'},
        'max_total': '1000000000.0', 'state': 'active'},
        'bid_account': {'currency': 'KRW', 'balance': '81991.675', 'locked': '18009.0',
        'avg_buy_price': '0', 'avg_buy_price_modified': True, 'unit_currency': 'KRW'},
        'ask_account': {'currency': 'XRP', 'balance': '0.0', 'locked': '0.0',
        'avg_buy_price': '1337.5', 'avg_buy_price_modified': False, 'unit_currency': 'KRW'}
        }
        """
        return self.api.get_chance(symbol)

    def get_minimum_order_possible_amount(self, symbol) -> int:
        """
        최소 매수 가능 금액 조회
        :param symbol:
        :return:
        """
        chance_info = self.get_chance(symbol)
        market = chance_info.get('market')
        return int(float(market.get('bid').get('min_total')))

    def get_fee(self, symbol, position_side):
        """수수료 조회 """
        chance_info = self.get_chance(symbol)
        if position_side == 'bid':
            return chance_info.get('bid_fee')
        elif position_side == 'ask':
            return chance_info.get('ask_fee')

    def check_loss_sell(self, symbol, standard_loss_ratio=-2) -> dict:
        """
        수익률 확인후 -2% 이하일 경우 손절 매도!
        :param symbol:
        :param basic_loss_ratio:
        :return:
        """
        uuid = get_entry_order_uuid(symbol, is_sell=False)
        if uuid:
            _, ticker = symbol.split('-')
            entry_price = self.get_entry_price(uuid)
            curr_price = pyupbit.get_current_price(symbol)
            if entry_price and curr_price:
                yields = calc_yield(entry_price=entry_price, ask_price=curr_price)
                log(f'{symbol} 수익률:  => {yields:.2f}%')
                if yields and yields < standard_loss_ratio:
                    _, available_qty, used = self.get_coin_balance(ticker)
                    log(f'손실발생 -> 매도프로세스 진행 {available_qty}')
                    return uuid, available_qty
                else:
                    return '', 0

    def trailing_stop(self, ticker):
        """
        트레이링 스탑
        :param ticker:
        :return:
        """
        pass

    def get_order_state(self, symbol_or_uuid: str):
        """
        주문(ask, bid) 상태 조회
        :param symbol_or_uuid:
        :return:

        state 상태
        'wait', 'cancel', 'done'

        1) 매수주문
            A. 미체결상태
             {'uuid': '01e6c4f0-4e9c-4616-a6a9-b36437ed64e0', 'side': 'bid',
            'ord_type': 'limit', 'price': '1075.0', 'state': 'wait', 'market': 'KRW-XRP',
            'created_at': '2021-09-24T20:27:22+09:00',
            'volume': '5.0', 'remaining_volume': '5.0', 'reserved_fee': '2.6875',
            'remaining_fee': '2.6875', 'paid_fee': '0.0',
            'locked': '5377.6875', 'executed_volume': '0.0',
            'trades_count': 0, 'trades': []}

            B. 체결상태
            {'uuid': 'c9405bee-0126-42a5-8678-f89540d3b870', 'side': 'bid',
            'ord_type': 'limit', 'price': '1145.0', 'state': 'done', 'market': 'KRW-XRP',
            'created_at': '2021-09-25T20:29:49+09:00', 'volume': '4.6061', 'remaining_volume': '0.0',
            'reserved_fee': '2.63699225', 'remaining_fee': '0.0', 'paid_fee': '2.63699225',
            'locked': '0.0', 'executed_volume': '4.6061',
            'trades_count': 1,
            'trades': [
                {'market': 'KRW-XRP', 'uuid': '1a45abbb-8daf-4810-aefb-99a1c1bfd8db',
                'price': '1145.0', 'volume': '4.6061', '
                funds': '5273.9845', 'created_at': '2021-09-25T20:29:49+09:00',
                'side': 'bid'}
             ]}

        C. 취소
            {'uuid': '01e6c4f0-4e9c-4616-a6a9-b36437ed64e0', 'side': 'bid',
            'ord_type': 'limit', 'price': '1075.0', 'state': 'cancel', 'market': 'KRW-XRP',
            'created_at': '2021-09-24T20:27:22+09:00',
            'volume': '5.0', 'remaining_volume': '5.0',
            'reserved_fee': '2.6875', 'remaining_fee': '2.6875', 'paid_fee': '0.0',
            'locked': '5377.6875', 'executed_volume': '0.0',
            'trades_count': 0, 'trades': []}


        2) 매도주문
         A. 미체결
         {'uuid': '8897d67e-a0b9-44ef-b07e-12549a6abbfa', 'side': 'ask',
         'ord_type': 'limit', 'price': '5000.0', 'state': 'wait',
         'market': 'KRW-XRP', 'created_at': '2021-09-24T20:33:43+09:00',
         'volume': '4.0', 'remaining_volume': '4.0',
         'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '0.0',
         'locked': '4.0', 'executed_volume': '0.0',
         'trades_count': 0, 'trades': []}

        B. 체결
         {'uuid': '196ec126-9b92-4319-af90-d251543f91a2', 'side': 'ask',
          'ord_type': 'limit', 'price': '1150.0', 'state': 'done',
          'market': 'KRW-XRP', 'created_at': '2021-09-26T09:00:04+09:00',
          'volume': '4.6061', 'remaining_volume': '0.0',
          'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '2.6485075',
          'locked': '0.0', 'executed_volume': '4.6061',
          'trades_count': 1, 'trades': [
                {'market': 'KRW-XRP', 'uuid': '1bbbe1ee-e8e6-400d-954c-73ed4f9422ea',
                'price': '1150.0', 'volume': '4.6061', 'funds': '5297.015',
                'created_at': '2021-09-26T09:00:04+09:00', 'side': 'ask'
                }
          ]}

        C. 취소
            {'uuid': '8897d67e-a0b9-44ef-b07e-12549a6abbfa', 'side': 'ask',
            'ord_type': 'limit', 'price': '5000.0', 'state': 'cancel', '
            market': 'KRW-XRP', 'created_at': '2021-09-24T20:33:43+09:00',
            'volume': '4.0', 'remaining_volume': '4.0',
            'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '0.0',
            'locked': '4.0', 'executed_volume': '0.0',
            'trades_count': 0, 'trades': []}
        """
        return self.api.get_order(ticker_or_uuid=symbol_or_uuid)

    def get_entry_price(self, uuid):
        """
        매수한 코인의 진입가격 조회
        :param uuid:
        :return:
        """
        prices = []
        try:
            ret = self.get_order_state(uuid)
            if ret:
                trades = ret.get('trades', [])
                for sub_ret in trades:
                    price = int(float(sub_ret.get('price')))
                    if price:
                        prices.append(price)
            avg_price = sum(prices) / len(prices)
            return avg_price
        except Exception as e:
            log(f'upbit.get_entry_price() 예외 {str(e)}')
            traceback.print_exc()
            return get_entry_price(uuid)


def get_tickers_by(market='KRW', parse=False) -> list:
    """
    매수시장 별 티커 조회하기
    :param fiat: 명목화폐(Fiat Money) KRW, BTC, USDT,
    :param parse market-ticker 에서 market- 제거한 ticker 만 추출하여 리스트로 리턴
    :return: list ['KRW-ETH', 'BTC-ETH', 'USDT-ETH']
    """
    tickers = pyupbit.get_tickers(fiat=market)
    if parse:
        return [symbol.replace(f"{market}-", '') for symbol in tickers]

    return tickers


def get_orderbook(symbol, logging=False):
    """
    호가창 조회
    :param symbol: 마켓-코인티커
    :return:
    """
    orderbook: list = pyupbit.get_orderbook(symbol)
    # print(orderbook)
    bids_asks = orderbook[0]['orderbook_units']
    # print('호가창 갯수: ', len(bids_asks))  # 매수호가 15, 매도호가 15개
    asks = []
    bids = []
    for bid_ask in bids_asks:
        # print(bid_ask)
        ask_price = bid_ask['ask_price']  # 매도호가
        ask_volume = bid_ask['ask_size']  # 매도호가 수량
        asks.append((ask_price, ask_volume))
        bid_price = bid_ask['bid_price']  # 매수호가
        bid_volume = bid_ask['bid_size']  # 매수호가 수량
        bids.append((bid_price, bid_volume))
    if logging is True:
        for i in range(len(asks) - 1, -1, -1):
            # print(i)
            ask, volume = asks[i]
            print(f'매도호가: {ask:,.0f}, volume: {volume}')
        print('-' * 150)
        for bid, volume in bids:
            print(f'매수호가: {bid:,.0f}, volume: {volume}')

    return {'asks': asks, 'bids': bids}


def get_lowest_ask_info(symbol, logging=False):
    """
    호가창 최하단 매도호가 조회
    :param symbol:
    :return: 매도호가, 호가수량
    """
    asks, _ = get_orderbook(symbol, logging=logging).values()
    ask, volume = asks[0]
    return ask, volume


def get_highest_bid_info(symbol, logging=False):
    """
    호가창 최상단 매수호가 조회
    :param symbol:
    :return: 매수호가, 수량
    """
    _, bids = get_orderbook(symbol, logging=logging).values()
    bid, volume = bids[0]
    return bid, volume


def get_krw_market_tic_cap(symbol: str) -> float:
    """
    원화마켓 코인 호가 단위 계산
    :param symbol:
    :return:
    """
    _, bids = get_orderbook(symbol).values()
    diff = 0
    bid_list = []
    for bid, _ in bids:
        bid_list.append(bid)
    if len(bid_list) > 0:
        diff = abs(bid_list[0] - bid_list[1])
    return int(diff)

    # return pyupbit.get_tick_size(price)


def calc_yield(entry_price: int, ask_price: int) -> float:
    """ 수익률 계산 """
    if entry_price > 0 and ask_price > 0:
        coin_yield = (ask_price / entry_price - 1) * 100
        return round(coin_yield, 3)


#
# def after_buy_order_etc(self, ret, entry_qty):
#     uuid = ret.get('uuid')
#     executed_qty = float(ret.get('executed_volume', 0))
#     state = ret.get('state', '')
#     if state == 'wait':
#         time.sleep(3)
#         ret = self.get_order_state(uuid)
#         state = ret.get('state', '')
#     fee = ret.get('paid_fee', 0)
#     avg_price = int(float(ret.get('avg_price', 0)))
#     if uuid and executed_qty > 0:
#         # 주문 성공
#
#         else:
#             # 부분체결로 나머지 수량 재주문!
#             return self.strategy_buy(symbol, remaining_qty, target_price)
#     else:
#         # 매수주문 실패
#         log(f'매수주문 상태: {state}')
#         ret = self.get_order_state(uuid)
#         re_state = ret.get('state', '')
#         if re_state == 'wait':
#             self.order_cancel(uuid)
#             return False

if __name__ == '__main__':
    symbol = 'KRW-ADA'
    # symbol = 'KRW-XRP'
    # symbol = 'KRW-BTC'
    upbit = UpbitHelper()
    # krw_tickers = get_tickers_by('KRW')
    # print(krw_tickers)
    # tickers = get_tickers_by(market='KRW', parse=True)
    # print(tickers)

    # ret = upbit.buy(symbol, 10, 1000)  # 지정가 주문
    # print(ret)
    # {'uuid': '5f3d3191-a50c-4907-8bf0-6ab536ab7593', 'side': 'bid', 'ord_type': 'limit', 'price': '1000.0', 'state': 'wait', 'market': 'KRW-XRP', 'created_at': '2021-09-20T19:07:55+09:00', 'volume': '10.0', 'remaining_volume': '10.0', 'reserved_fee': '5.0', 'remaining_fee': '5.0', 'paid_fee': '0.0', 'locked': '10005.0', 'executed_volume': '0.0', 'trades_count': 0}

    print('cash: ', upbit.get_cash_balance())
    print(upbit.get_coin_balance())
    print(upbit.get_coin_balance('XRP'))
    print(upbit.get_coin_balance('BTC'))
    print('최하위 매도호가: ', get_lowest_ask_info(symbol, logging=False))
    print('최상위 매수호가: ', get_highest_bid_info(symbol))

    # print(calc_krw_market_quote_unit('KRW-ETH'))
    # print(format(calc_krw_market_quote_unit('KRW-XRP')))

    # print(upbit.buy_up_tic(symbol, quantity=10, tic_cnt=1))
    # print(upbit.buy_down_tic(symbol, quantity=5, tic_cnt=10))  # 2틱 아래 가격으로 매수
    # print(upbit.buy_current_price(symbol, 5))  # 현재가 매수

    # upbit.order_cancel('8ff56aad-5695-4519-9331-9869f0de8600')
    # print(f'{symbol} tic-cap: ', get_krw_market_tic_cap(symbol))
    # print(upbit.get_chance(symbol))
    # print(upbit.get_fee(symbol, position_side='bid'))
    # print(upbit.get_fee(symbol, position_side='ask'))
    print('최소주문가능금액: ', upbit.get_minimum_order_possible_amount(symbol))
    print('최소주문가능금액: ', upbit.get_minimum_order_possible_amount('KRW-ETH'))
    print('최소주문가능금액: ', upbit.get_minimum_order_possible_amount('KRW-BTC'))

    # order_result = upbit.order_cancel('5f3d3191-a50c-4907-8bf0-6ab536ab7593')
    # print(order_result)

    # ret: dict = upbit.sell(symbol, 4, 5000)
    # print(ret)
    # {'uuid': '8897d67e-a0b9-44ef-b07e-12549a6abbfa', 'state': 'wait', 'avg_price': 0, 'quantity': 0.0, 'fee': 0.0}

    # r = upbit.order_cancel('49a35336-de6b-4038-8322-e7073255e957')
    # print(r)
    # r = upbit.sell_up_tic(symbol, 5, 10)  # 매도호가창 10틱 위로 매도 주문
    # print(r)
    # r = upbit.sell_down_tic(symbol, 10)  # 매도호가창 1틱 아래 매도주문
    # print(r)

    # print('매수주문 대기 상태: ', upbit.get_order_state('01e6c4f0-4e9c-4616-a6a9-b36437ed64e0'))
    print('매도주문 대기 상태: ', upbit.get_order_state('0cf50e9c-0af3-46b0-bf65-19c70058e302'))
    # print('주문 상태: ', upbit.get_order_state(symbol))
    # df = pyupbit.get_ohlcv(symbol, count=20)
    # print(df)

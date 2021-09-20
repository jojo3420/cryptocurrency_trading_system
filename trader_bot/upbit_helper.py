import pyupbit
from common.utils import log


class UpbitHelper:
    def __init__(self, path='../.env.dev', debug_mode=False):
        self.debug_mode = debug_mode
        with open(path) as stream:
            keys = {}
            lines = stream.readlines()
            for line in lines:
                _label, key = line.split('=')
                keys[_label] = key.strip()
            # print(keys)
            # return keys
            self.api = pyupbit.Upbit(keys['AccessKey'], keys['SecretKey'])

    def set_debug_mode(self, mode: bool):
        """ 디버그 모드  ON/OFF """
        self.debug_mode = mode

    def buy(self, symbol: str, quantity: float, entry_price: int):
        """
        지정가 매수하기
        :param symbol: KRW-BTC : 원화시장에서 BTC 매수
        :param quantity: 수량
        :param entry_price: 매수가(진입가)
        :return:
        """
        if symbol and '-' in symbol:
            curr_price = pyupbit.get_current_price(symbol)
            minimum_amount = self.get_minimum_order_possible_amount(symbol)  # 체크 최소 주문수량
            order_total_amount = entry_price * quantity
            if self.debug_mode:
                log(f'최소주문금액: {minimum_amount}, 나의 주문금액: {order_total_amount}')

            if order_total_amount < minimum_amount:
                msg = f'주문금액이 최소주문금액 이하 입니다. => {symbol} 최소주문금액: {minimum_amount:,}'
                log(msg)
                return msg

            log(f'리플 원화 현재가: {curr_price:,.0f}')
            # 지정가 매수
            ret = self.api.buy_limit_order(symbol, entry_price, volume=quantity)
            if self.debug_mode:
                log('매수 주문결과: ', ret)
                # [2021-09-13 20:52:51.109416] 매수결과:  ({'uuid': '13e79a6c-78f7-4759-af47-fb01086d6926', 'side': 'bid', 'ord_type': 'limit', 'price': '995.0', 'state': 'wait', 'market': 'KRW-XRP', 'created_at': '2021-09-13T20:52:51+09:00', 'volume': '10.0', 'remaining_volume': '10.0', 'reserved_fee': '4.975', 'remaining_fee': '4.975', 'paid_fee': '0.0', 'locked': '9954.975', 'executed_volume': '0.0', 'trades_count': 0},) {}
            return ret
        else:
            log('티커명 규칙은 마켓심볼-매수할코인심볼 입니다.')

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

    def sell(self, symbol: str, quantity: float, ask_price: int):
        """
        매도 주문(지정가)
        :param symbol:
        :param quantity:
        :param ask_price:
        :return:
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
                        return ret
                    else:
                        return f'주문 요청금액({my_order_krw:,})이 작습니다. 최소주문금액({order_possible_krw:,}) 이상으로 주문하세요.'
                else:
                    return f'주문 요청수량이({quantity}) 주문가능수량{(available_qty)} 보다 큽니다. '
            else:
                return f'매수호가 또는 수량이 유효하지 않습니다. {ask_price} || {quantity}'

        else:
            return f'심볼을 확인해주세요 {symbol}'

    def sell_current_price(self, symbol: str, quantity: float):
        """
        현재가 기준으로 매도 주문
        :param symbol:
        :param quantity:
        :return:
        """
        ask_price = pyupbit.get_current_price(symbol)
        return self.sell(symbol, quantity, ask_price)

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

    def calc_sell_quantity(self, symbol: str) -> float:
        """
        매도 가능 수량(available) 리턴
        :param symbol:
        :return: 매도 주문가능 수량
        """
        if '-' in symbol:
            _, ticker = symbol.split('-')
            balance: dict = self.get_balance_by(ticker)
            _, available, used = balance.values()
            return available

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

    def get_balance_by(self, ticker="ALL") -> dict or list:
        """
        잔고조회 하기
        :param ticker: 'ALL' 전체잔고, 특정티커: 티커잔고만 조회
        :return: [dict, dict, dict...] OR dict
        """
        total_balance: list = self.api.get_balances()
        balance_list = []
        for balance in total_balance:
            # print(balance)
            currency = balance.get('currency')
            available = balance.get('balance')
            used = balance.get('locked')
            # print(type(balance))
            if self.debug_mode:
                log(f'currency: {currency}, available: {float(available):,.2f}, locked: {locked}')

            if currency == 'KRW':
                available = int(float(available))
                used = int(float(used))
            else:
                available = float(available)
                used = float(used)

            element = {'ticker': currency, 'available': available, 'used': used}
            if ticker != 'ALL' and ticker == currency:
                return element
            else:
                balance_list.append(element)

        return balance_list

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


if __name__ == '__main__':
    symbol = 'KRW-XRP'
    upbit = UpbitHelper()
    # krw_tickers = get_tickers_by('KRW')
    # print(krw_tickers)
    # tickers = get_tickers_by(market='KRW', parse=True)
    # print(tickers)

    # ret = upbit.buy(symbol, 10, 1000)  # 지정가 주문
    # print(ret)
    # {'uuid': '5f3d3191-a50c-4907-8bf0-6ab536ab7593', 'side': 'bid', 'ord_type': 'limit', 'price': '1000.0', 'state': 'wait', 'market': 'KRW-XRP', 'created_at': '2021-09-20T19:07:55+09:00', 'volume': '10.0', 'remaining_volume': '10.0', 'reserved_fee': '5.0', 'remaining_fee': '5.0', 'paid_fee': '0.0', 'locked': '10005.0', 'executed_volume': '0.0', 'trades_count': 0}

    print(upbit.get_balance_by())
    print(upbit.get_balance_by('XRP'))
    # print('최하위 매도호가: ', get_lowest_ask_info(symbol, logging=False))
    # print('최상위 매수호가: ', get_highest_bid_info(symbol))

    # print(calc_krw_market_quote_unit('KRW-ETH'))
    # print(format(calc_krw_market_quote_unit('KRW-XRP')))

    # print(upbit.buy_up_tic(symbol, quantity=10, tic_cnt=1))
    print(upbit.buy_down_tic(symbol, quantity=5, tic_cnt=2))  # 2틱 아래 가격으로 매수
    # print(upbit.buy_current_price(symbol, 5))  # 현재가 매수

    print(f'{symbol} tic-cap: ', get_krw_market_tic_cap(symbol))
    # print(upbit.get_chance(symbol))
    # print(upbit.get_fee(symbol, position_side='bid'))
    # print(upbit.get_fee(symbol, position_side='ask'))
    print('최소주문가능금액: ', upbit.get_minimum_order_possible_amount(symbol))
    print('최소주문가능금액: ', upbit.get_minimum_order_possible_amount('KRW-ETH'))
    print('최소주문가능금액: ', upbit.get_minimum_order_possible_amount('KRW-BTC'))

    # order_result = upbit.order_cancel('5f3d3191-a50c-4907-8bf0-6ab536ab7593')
    # print(order_result)

    # r = upbit.sell(symbol, 1500, 4)
    # print(r)
    # r = upbit.order_cancel('49a35336-de6b-4038-8322-e7073255e957')
    # print(r)
    # r = upbit.sell_up_tic(symbol, 5, 10)  # 매도호가창 10틱 위로 매도 주문
    # print(r)
    # r = upbit.sell_down_tic(symbol, 10)  # 매도호가창 1틱 아래 매도주문
    # print(r)

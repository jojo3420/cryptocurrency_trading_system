import pyupbit
from common.utils import log


class UpbitHelper:
    def __init__(self, path='../.env.dev'):
        with open(path) as stream:
            keys = {}
            lines = stream.readlines()
            for line in lines:
                _label, key = line.split('=')
                keys[_label] = key.strip()
            # print(keys)
            # return keys
            self.api = pyupbit.Upbit(keys['AccessKey'], keys['SecretKey'])

    def buy(self, ticker: str, quantity: float, bid: float):
        """
        지정가 매수하기
        :param ticker: KRW-BTC : 원화시장-BTC 매수
        :param quantity: 수량
        :param bid: 매수가(진입가)
        :return:
        """
        if '-' in ticker:
            current_krw_xrp_price = pyupbit.get_current_price(ticker)
            log(f'리플 원화 현재가: {current_krw_xrp_price:,.0f}')
            # 지정가 매수
            ret = self.api.buy_limit_order(ticker, bid, volume=quantity)
            log('매수결과: ', ret)
            if ret.get('message', ''):
                return ret.get('message', ''), ret.get('name', '')
                # [2021-09-13 20:52:51.109416] 매수결과:  ({'uuid': '13e79a6c-78f7-4759-af47-fb01086d6926', 'side': 'bid', 'ord_type': 'limit', 'price': '995.0', 'state': 'wait', 'market': 'KRW-XRP', 'created_at': '2021-09-13T20:52:51+09:00', 'volume': '10.0', 'remaining_volume': '10.0', 'reserved_fee': '4.975', 'remaining_fee': '4.975', 'paid_fee': '0.0', 'locked': '9954.975', 'executed_volume': '0.0', 'trades_count': 0},) {}
            return ret
        else:
            log('티커명 규칙은 마켓심볼-매수할코인심볼 입니다.')

    def sell(self, ticker: str, qty: float):
        pass

    def order_cancel(self, uuid: str) -> bool:
        """
        주문 취소하기
        :param uuid: 주문번호
        :return: True or False
        """
        ret = self.api.cancel_order(uuid=uuid)
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
            log(f'주문취소 uuid: {cancel_order_uuid}')
            log(f'주문타입: {order_type}')  # limit: 지정가 매수
            log(f'주문상태: {order_state}, 매도가: {ask_price}, 수량: {quantity}')
            return True
        else:
            error = ret.get('error', '')
            print(error)
            return False

    def get_balance_by(self, ticker="ALL"):
        total_balance: list = self.api.get_balances()
        # 'default' 그룹에 대해서 1분간 1799개, 1초에 29개의 API 호출이 가능함

        for balance in total_balance:
            print(balance)
            currency = balance['currency']
            balance = balance['balance']
            # print(type(balance))
            print(f'currency: {currency}, balance: {float(balance):,.2f}')

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

    def get_minimum_order_amount(self, symbol):
        """
        매수 최소 금액 조회
        :param symbol:
        :return:
        """
        chance_info = self.get_chance(symbol)
        market = chance_info.get('market')
        return market.get('bid').get('min_total')

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


def get_lowest_ask_price(symbol, logging=False):
    """
    호가창 최하단 매도호가 조회
    :param symbol:
    :return: 매도호가, 호가수량
    """
    asks, _ = get_orderbook(symbol, logging=logging).values()
    ask, volume = asks[0]
    return ask, volume


def get_highest_bid_price(symbol, logging=False):
    """
    호가창 최상단 매수호가 조회
    :param symbol:
    :return: 매수호가, 수량
    """
    _, bids = get_orderbook(symbol, logging=logging).values()
    bid, volume = bids[0]
    return bid, volume


def calc_krw_market_tic_size(symbol) -> float:
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


def get_min_order_price(symbol):
    pass


if __name__ == '__main__':
    upbit = UpbitHelper()
    # krw_tickers = upbit.get_tickers_by('KRW')
    # print(krw_tickers)
    # tickers = upbit.get_tickers_by(market='KRW', parse=True)
    # print(tickers)

    upbit.buy('KRW-XRP', 3, 1285)
    # upbit.get_balance_by()
    print(get_lowest_ask_price('KRW-XRP', logging=True))
    print(get_highest_bid_price('KRW-XRP'))
    # print(calc_krw_market_quote_unit('KRW-ETH'))
    # print(format(calc_krw_market_quote_unit('KRW-XRP')))
    curr_price = pyupbit.get_current_price('KRW-XRP')
    print(f'curr_price: {curr_price}')
    print('tic size: ', calc_krw_market_tic_size('KRW-XRP'))
    print(upbit.get_chance('KRW-XRP'))
    print(upbit.get_fee('KRW-XRP', position_side='bid'))
    print(upbit.get_fee('KRW-XRP', position_side='ask'))
    print(upbit.get_minimum_order_amount('KRW-XRP'))
    print(upbit.get_minimum_order_amount('KRW-ETH'))
    print(upbit.get_minimum_order_amount('KRW-BTC'))

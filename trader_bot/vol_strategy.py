import os
import sys

if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
else:
    sys.path.append('/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system')

from common.telegram_bot import system_log, send_coin_bot
from upbit_helper import *
from db_helper import *
from common.utils import log
from math_helper import *
from money_management_system import *


class BreakVolatility:
    def __init__(self, upbit):
        self.upbit = upbit
        self.find_bull_toggle = True
        self.bull_coins = []
        self.tr_history = {}

    def setup(self):
        if self.find_bull_toggle:
            self.find_bull_market_list()

    def find_bull_market_list(self, R=0.5) -> list:
        """
        상승코인 찾기
         1) 현재가격 > EMA3 OR EMA5
         2) 노이즈값 0.55 미만
        :return:
        """
        all_symbol_list = pyupbit.get_tickers(fiat='KRW')
        print(all_symbol_list)
        for symbol in all_symbol_list:
            try:
                curr_price = pyupbit.get_current_price(symbol)
                today_open_price = get_today_open(symbol)
                today_percent = (curr_price / today_open_price - 1) * 100
                target_price = calc_target_price(symbol, R)
                MA3 = calc_ema(symbol, 3)
                # curr_noise = calc_noise_ma_by(symbol, 1)
                if curr_price >= MA3 and curr_price > target_price and today_percent > 5.0:
                    print(f'상승 불코인: {symbol} ')
                    self.bull_coins.append(symbol)

                time.sleep(1)
            except Exception as E:
                print(str(E))

    def check_bid_order(self, uuid: str, target_price, R=0.5):
        """
        체결 상태 확인 => 매수
        :param uuid: 주문pk
        :return:
        """
        if uuid:
            b_ret = self.upbit.get_order_state(uuid)
            print(b_ret)
            b_state = b_ret.get('state', '')
            if b_state == 'wait':
                cancel = self.upbit.order_cancel(uuid)
                log(f'미체결 주문 취소하기: ({cancel}) ')
            elif b_state == 'done':
                trades_count = b_ret.get('trades_count', 0)
                log(f'매수 체결된 주문 있음: {trades_count}건')
                executed_qty = float(b_ret.get('executed_volume', 0))
                trades = b_ret.get('trades')
                paid_fee = b_ret.get('paid_fee')
                remaining_qty = float(b_ret.get('remaining_volume'))  # 주문수량에서 미체결된 수량
                # 1)체결된 거래내역 저장
                for sub_ret in trades:
                    sub_uuid = sub_ret.get('uuid')
                    entry_price = sub_ret.get('price')
                    quantity = float(sub_ret.get('volume', 0.0))
                    funds = sub_ret.get('funds')
                    side = sub_ret.get('side')
                    data_dict = {
                        'position': side, 'symbol': symbol,
                        'uuid': uuid, 'sub_uuid': sub_uuid,
                        'price': entry_price, 'quantity': quantity,
                        'stop_loss_price': self.tr_history[symbol].get('stop_loss_price'),
                        'target_price': target_price, 'R': R,
                        'funds': funds, 'fee': paid_fee,
                    }
                    save_transaction_history(data_dict)
                    send_coin_bot(f'{symbol} 체결됨 => {data_dict}')
                    saved = save_bought_list(uuid, symbol)
                    log(f'save_bought_list => {saved}')
                    if self.tr_history[symbol]:
                        self.tr_history[symbol].update(data_dict)
                if executed_qty == quantity and remaining_qty == 0:
                    log(f'전체 주문 체결 완료 => {b_state}')
                else:
                    # '미체결 수량은 체결창 호가창에 남아 있다.. 추후에 체결될 수 있는데!?
                    # '미체결 주문수량을 취소해야한다. 그대로 놔두면 나중에 체결되어도... DB에 기록할 수 없다.
                    log(f'일부체결 => 미체결수량 {remaining_qty}')
                    log(f'b_ret: {b_ret}')
                    cancel = self.upbit.order_cancel(uuid)
                    print(f'미체결 주문 취소하기: {cancel}')
            else:
                log('*** 주문 상태 확인 필요 ***')
                print(b_ret)

    def buy_coin(self, symbol, R):
        """
        코인 매수하기
        :param upbit: 매수모듈
        :param symbol: 매수할 코인
        :param R: 윌리엄스 k값
        :return:
        """
        available_cash, _ = self.upbit.get_cash_balance()
        allowable_loss_amount = int(available_cash * 0.01)
        # print(f'{symbol} 허용가능한 손실금액: {target_loss_amount}')
        quantity, position_amount, stop_loss_price = calc_position_size_by_loss_percent(symbol, allowable_loss_percent,
                                                                                        target_loss_amount=allowable_loss_amount)
        if quantity > 0:
            # log(f'{symbol} 수량: {quantity}, 진입금액: {position_amount:,.0f} 스탑로스: {stop_loss_price}')
            target_price = calc_target_price(symbol, R)
            curr_price = pyupbit.get_current_price(symbol)
            if target_price and curr_price and curr_price > target_price:
                log(f'변동성 돌파됨 {symbol}')
                ret = self.upbit.buy_current_price(symbol, quantity)
                uuid = ret.get('uuid', None)
                log(f'매수주문 => {uuid}')
                time.sleep(1)
                self.tr_history.setdefault({'target_price': target_price, 'R': R, 'position_amount': position_amount,
                                            'stop_loss_price': stop_loss_price, 'uuid': uuid,
                                            'allowable_loss_amount': allowable_loss_amount,
                                            }, {})
                self.check_bid_order(uuid, target_price, R)
            else:
                log(f'{symbol} 변동성 돌파 실패! (주문X)')
        # else:
        #     log(f'주문가능 수량 없음: {symbol}')

    def sell_after_logic(self, uuid_list: list, sleep_time=1):
        """
        매도 주문후 로직 처리
            - bought_list 업데이트
            - 거래내역 저장 transaction_history
        :param uuid_list:
        :param sleep_time:
        :return:
        """
        for uuid in uuid_list:
            ret = self.upbit.get_order_state(uuid)
            symbol = ret.get('market')
            state = ret.get('state')
            trade_count = ret.get('trade_count', 0)
            log(f'sell_after_logic() 체결수량: {trade_count} ret: {ret}')
            paid_fee = ret.get('paid_fee')
            trades = ret.get('trade_count', [])
            _, ticker = symbol.split('-')
            time.sleep(sleep_time)
            if state == 'done':
                _, qty, used = self.upbit.get_coin_balance(ticker)
                if qty == 0 and used == 0:
                    update_bought_list(symbol)
                for sub_ret in trades:
                    sub_uuid = sub_ret.get('uuid')
                    ask_price = sub_ret.get('price')
                    quantity = sub_ret.get('volume')
                    funds = sub_ret.get('funds')
                    entry_price = get_entry_price(sub_uuid)
                    yields = calc_yield(entry_price=entry_price, ask_price=ask_price)
                    data_dict = {
                        'position': 'ask', 'symbol': symbol,
                        'uuid': uuid, 'sub_uuid': sub_uuid,
                        'price': ask_price, 'quantity': quantity,
                        'yield': yields, 'fee': paid_fee,
                        'funds': funds,
                    }
                    log(data_dict)
                    save_transaction_history(data_dict)
            elif state == 'wait':
                cancel = self.upbit.order_cancel(uuid)
                log(f'{symbol} 주문 미체결로 취소처리: {cancel}')
            time.sleep(0.5)

    def check_stop_loss(self, bought_symbol_list):
        """
        종목별 현재 가격과 손절 가격 비교하여 청산 처리
        :param bought_symbol_list:
        :return:
        """
        # print(bought_symbol_list)
        uuid_li = []
        for sym in bought_symbol_list:
            _uuid = get_entry_order_uuid(sym, is_sell=False)
            entry_price = get_entry_price(_uuid)
            if self.tr_history[sym].get('stop_loss_price'):
                stop_loss_price = self.tr_history[sym].get('stop_loss_price')
            else:
                stop_loss_price = get_stop_loss_price_by(sym, 'bid')
            curr_price = pyupbit.get_current_price(sym)
            _ticker, available_qty, _used = self.upbit.get_coin_balance(sym)
            if curr_price and stop_loss_price and stop_loss_price > curr_price:
                ret = self.upbit.sell_current_price(sym, available_qty)
                log(f'손절매 매도: {sym}')
                log(ret)
                uuid = ret.get('uuid', '')
                uuid_li.append(uuid)
            else:
                if self.tr_history.get(sym):
                    entry_price = self.tr_history.get(sym).get('entry_price')
                    allowable_loss_amount = self.tr_history.get(sym).get('allowable_loss_amount')
                else:
                    available_cash, _ = self.upbit.get_cash_balance()
                    allowable_loss_amount = int(available_cash * 0.01)
                log(f'허용 가능한 손실금액: {allowable_loss_amount:,.0f}원')
                diff = curr_price - entry_price
                log(f'{sym} 손실금액: {(available_qty + _used) * diff:,.1f}원')
                log(f'진입가격: {entry_price:,.0f} 손절가: {stop_loss_price:,.0f}')

            time.sleep(0.5)
        self.sell_after_logic(uuid_li)


if __name__ == '__main__':
    allowable_loss_percent = 0.05
    upbit = UpbitHelper()
    strategy = BreakVolatility(upbit)
    strategy.setup()
    try:
        while True:
            # 메이저 코인 리스트
            coin_buy_wish_list, _, _ = get_buy_wish_list()
            bought_symbol_list = get_bought_list()
            if bought_symbol_list is None:
                log('예외발생 => 매수한 종목 리스트가 배열이 아닙니다.')
                break
            today = datetime.now()
            # 전일 코인자산 청산 시간
            start_sell_tm = today.replace(hour=9, minute=1, second=0, microsecond=0)
            end_sell_tm = today.replace(hour=9, minute=6, second=0, microsecond=0)
            # 트레이딩 시간
            start_trading_tm = today.replace(hour=0, minute=0, second=1, microsecond=0)
            end_trading_tm = today.replace(hour=23, minute=55, second=0, microsecond=0)
            now_tm = datetime.now()

            # 포트폴리오 모두 청산
            if start_sell_tm < now_tm < end_sell_tm:
                log('포트폴리오 모두 청산!')
                uuid_list = upbit.sell_all()
                strategy.sell_after_logic(uuid_list)

            # 손절매: 포지션 정리
            strategy.check_stop_loss(bought_symbol_list)

            # 매수하기 - 변동성 돌파
            if start_trading_tm < now_tm < end_trading_tm:
                for i, symbol in enumerate(coin_buy_wish_list + strategy.bull_coins):
                    if symbol not in bought_symbol_list:
                        strategy.buy_coin(symbol, R=0.5)

            # # 매수 종목 없으면 10초 휴식하기
            if len(coin_buy_wish_list) == 0:
                log('매수할 코인 없음 => 10초 휴식...')
                time.sleep(10)

            # 텔레그램 수익률 보고!
            if now_tm.minute == 0 and now_tm.second <= 7:
                msg = '텔레그램 수익률 보고!'
                send_coin_bot(msg)
                strategy.find_bull_toggle = True
                strategy.find_bull_market_list()

            print('-' * 150)
            time.sleep(1)
    except Exception as e:
        msg = f'가상화폐 시스템 메인 로직 예외 발생. 시스템 종료됨 => {str(e)}'
        log(msg)
        traceback.print_exc()
        system_log(msg)

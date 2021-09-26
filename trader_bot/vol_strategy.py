# import time
# import traceback
import os
import sys
if os.name == 'nt':
    sys.path.append('C:\\source_code\\python\\cryptocurrency_trading_system')
    sys.path.append('C:\\source_code\\cryptocurrency_trading_system')
else:
    sys.path.append('/Users/maegmini/Code/sourcetree-git/python/cryptocurrency_trading_system')

from common.telegram_bot import system_log, send_coin_bot
from datetime import datetime
from upbit_helper import *
from db_helper import *
from common.utils import log
from math_helper import *


def setup():
    print('setup()')


def buy_coin(symbol, R):
    """
    매수로직
      1) 진입 규모 계산: 목표 변동성 타켓(2%) 기준으로 전일 변동성으로 계산하여 2% 내에 손실 발생하도록 진입규모 계산
      전일 변동성이 높을 때: 적은 수량 진입
      전일 변동성이 낮을 때: 많은 수량 진입

      2)

    :param symbol:
    :param R:
    :return:
    """
    available_cash, _ = upbit.get_cash_balance()
    target_price = calc_target_price(symbol, R)
    # minimum_amount = upbit.get_minimum_order_possible_amount(symbol)  # 최소주문금액
    # position_qty = calc_position_sizing(symbol, 5, available_cash, minimum_amount)
    position_qty = calc_position_sizing_target(symbol, coin_buy_wish_list, total_cash=available_cash)
    log(f'{symbol} 진입 수량: {position_qty}')
    if position_qty > 0:
        order_return, uuid = upbit.strategy_buy(symbol, position_qty, target_price)
        if order_return is True and uuid:
            log(f'매수주문 OK {symbol}')
            time.sleep(1)
            b_ret = upbit.get_order_state(uuid)
            b_state = b_ret.get('state', '')
            if b_state == 'wait':
                cancel = upbit.order_cancel(uuid)
                log(f'주문취소하고({cancel}) 다음기회에..')
            elif b_state == 'done':
                trades_count = b_ret.get('trades_count', 0)
                log(f'체결된 주문 있음: {trades_count}건')
                trades = b_ret.get('trades', [])
                fee = b_ret.get('paid_fee')
                executed_qty = float(b_ret.get('executed_volume', 0))
                remaining_qty = float(b_ret.get('remaining_volume'))
                if remaining_qty and trades:
                    # 1)체결된 거래내역 저장
                    for sub_ret in trades:
                        sub_uuid = sub_ret.get('uuid', '')
                        entry_price = sub_ret.get('price')
                        quantity = sub_ret.get('volume')
                        funds = sub_ret.get('funds')
                        data_dict = {
                            'position': 'bid', 'symbol': symbol,
                            'uuid': uuid, 'sub_uuid': sub_uuid,
                            'price': entry_price, 'quantity': quantity,
                            'funds': funds, 'fee': fee,
                            'target_price': target_price, 'R': R,
                        }
                        save_transaction_history(data_dict)
                        send_coin_bot(f'{symbol} 체결 => {data_dict}')

                if executed_qty == position_qty and remaining_qty == 0:
                    log(f'천체 체결 완료 => {b_state}')
                    saved = save_bought_list(uuid, symbol)
                    log(f'save_bought_list => {saved}')
                else:
                    log(f'일부체결 => 미체결수량 {remaining_qty}')
                    log(f'b_ret: {b_ret}')
                    bb_ret = upbit.get_order_state(uuid)
                    log(f'bb_ret: {bb_ret}')
                    log('미체결 수량은 체결창 호가창에 남아 있다.. 추후에 체결될 수 있는데!?  ')
                    log('미체결 주문수량을 취소해야한다. 그대로 놔두면 나중에 체결되어도... DB에 기록할 수 없다.')
            else:
                log(b_ret)
        else:
            log(f'{symbol} 변동성 돌파 실패!(주문X)')
    else:
        log(f'주문수량이 0 이하: {position_qty}')


def sell_logic(uuid_list: list, sleep_time=1):
    for uuid in uuid_list:
        ret = upbit.get_order_state(uuid)
        symbol = ret.get('market')
        state = ret.get('state')
        trade_count = ret.get('trade_count', 0)
        log(f'sell_logic() 체결수량: {trade_count} ret: {ret}')
        fee = ret.get('paid_fee')
        trades = ret.get('trade_count', [])
        _, ticker = symbol.split('-')
        time.sleep(sleep_time)
        if state == 'done':
            _, available, used = upbit.get_coin_balance(ticker)
            if available == 0 and used == 0:
                update_bought_list(symbol)
            for sub_ret in trades:
                #        {'uuid': '196ec126-9b92-4319-af90-d251543f91a2', 'side': 'ask',
                #           'ord_type': 'limit', 'price': '1150.0', 'state': 'done',
                #           'market': 'KRW-XRP', 'created_at': '2021-09-26T09:00:04+09:00',
                #           'volume': '4.6061', 'remaining_volume': '0.0',
                #           'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '2.6485075',
                #           'locked': '0.0', 'executed_volume': '4.6061',
                #           'trades_count': 1, 'trades': [
                #                 {'market': 'KRW-XRP', 'uuid': '1bbbe1ee-e8e6-400d-954c-73ed4f9422ea',
                #                 'price': '1150.0', 'volume': '4.6061', 'funds': '5297.015',
                #                 'created_at': '2021-09-26T09:00:04+09:00', 'side': 'ask'
                #                 }
                #           ]}
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
                    'yield': yields, 'fee': fee,
                    'funds': funds,
                }
                log(data_dict)
                save_transaction_history(data_dict)
        elif state == 'wait':
            cancel = upbit.order_cancel(uuid)
            log(f'{symbol} 주문 미체결로 취소처리: {cancel}')
    time.sleep(0.5)


if __name__ == '__main__':
    upbit = UpbitHelper()
    # FindBullCoinWorker().start()
    try:
        setup()
        basic_loss_ratio = -2.0  # 기본 손절선
        while True:
            # 메이저 코인 리스트
            coin_buy_wish_list, coin_ratio_list, coin_r_list = get_buy_wish_list()
            # balance_list = upbit.get_coin_balance()
            # print(balance_list)
            bought_symbol_list = upbit.get_bought_list()

            # # 급등 코인 리스트
            # bull_coin_list, bull_ratio_list, bull_r_list = get_bull_coin_list()
            # coin_buy_wish_list = coin_buy_wish_list + bull_coin_list
            # coin_ratio_list = coin_ratio_list + bull_ratio_list
            # coin_r_list = coin_r_list + bull_r_list
            # coin_bought_list: list = get_coin_bought_list()
            #
            # krw_balance, used_krw = upbit.get_cash_balance()
            # log(f'가용 원화: {krw_balance:,} 주문에 사용한 금액: {used_krw:,}')

            today = datetime.now()
            # 전일 코인자산 청산 시간
            start_sell_tm = today.replace(hour=9, minute=0, second=0, microsecond=0)
            end_sell_tm = today.replace(hour=9, minute=6, second=0, microsecond=0)
            # 트레이딩 시간
            start_trading_tm = today.replace(hour=0, minute=0, second=1, microsecond=0)
            end_trading_tm = today.replace(hour=23, minute=55, second=0, microsecond=0)
            now_tm = datetime.now()

            if start_sell_tm < now_tm < end_sell_tm:
                log('포트폴리오 모두 청산!')
                while True:
                    balance: list = upbit.get_coin_balance()
                    if len(balance) == 0:
                        end_sell_tm = datetime.now()
                        break
                    uuid_list = upbit.sell_all()
                    sell_logic(uuid_list)

            for symbol in bought_symbol_list:
                ret = upbit.check_loss_sell(symbol, basic_loss_ratio)
                if ret:
                    uuid = ret.get('uuid')
                    order_state = upbit.get_order_state(uuid)
                    state = order_state.get('state')
                    print(f'손절매 결과: {symbol} {state}')
                time.sleep(0.5)
                upbit.trailing_stop(symbol)
                time.sleep(0.1)

            if start_trading_tm < now_tm < end_trading_tm:
                # 매수하기 - 변동성 돌파
                for i, symbol in enumerate(coin_buy_wish_list):
                    # if ticker in daily_profit_list + daily_loss_coin_list:
                    # 당일 수익창출 또는 당일 손절매 코인 당일 재매수 제외
                    # continue
                    if bought_symbol_list is None:
                        break
                    if symbol not in bought_symbol_list:
                        R = coin_r_list[i]  # 0.5
                        buy_coin(symbol, R)
                        time.sleep(0.5)

            # # 10분 마다 수익률 기록
            # if (now_tm.minute == 0 and 0 <= now_tm.second <= 9) \
            #         or (now_tm.minute == 10 and 0 <= now_tm.second <= 9) \
            #         or (now_tm.minute == 20 and 0 <= now_tm.second <= 9) \
            #         or (now_tm.minute == 30 and 0 <= now_tm.second <= 9) \
            #         or (now_tm.minute == 40 and 0 <= now_tm.second <= 9) \
            #         or (now_tm.minute == 50 and 0 <= now_tm.second <= 9):
            #     save_yield_history(get_total_yield(), len(coin_bought_list))
            #
            # # 텔레그램 수익률 보고!
            if now_tm.minute == 0 and 0 <= now_tm.second <= 7:
                # send_coin_bot()
                time.sleep(3)

            # # 매수 종목 없으면 강제 휴식
            if len(coin_buy_wish_list) == 0:
                log('매수할 코인 없음. 휴식 10초')
                time.sleep(10)

            print('-' * 150)
            time.sleep(1)
    except Exception as e:
        msg = f'가상화폐 시스템 메인 로직 예외 발생. 시스템 종료됨 => {str(e)}'
        log(msg)
        traceback.print_exc()
        system_log(msg)

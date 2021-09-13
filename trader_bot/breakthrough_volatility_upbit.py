import traceback

from common.telegram_bot import send_coin_bot, system_log
from math_helper import *
from upbit_helper import *
from datetime import datetime
import time
from common.utils import log

if __name__ == '__main__':
    try:
        # setup()
        # basic_loss_ratio = 2.0  # 기본 손절선
        while True:
            # 메이저 코인 리스트
            # coin_buy_wish_list, coin_ratio_list, coin_r_list = get_buy_wish_list()
            # 급등 코인 리스트
            # bull_coin_list, bull_ratio_list, bull_r_list = get_bull_coin_list()
            # coin_buy_wish_list = coin_buy_wish_list + bull_coin_list
            # coin_ratio_list = coin_ratio_list + bull_ratio_list
            # coin_r_list = coin_r_list + bull_r_list
            # coin_bought_list: list = get_coin_bought_list()

            # total_krw, use_krw = get_krw_balance()
            # log(f'가용 원화: {total_krw:,} 사용한 금액: {use_krw:,}')
            # krw_balance = total_krw - use_krw
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
                # r = sell_all()
                time.sleep(1)
            #     if r is True and len(get_coin_bought_list()) == 0:
            #         end_sell_tm = datetime.now()
            #         start_trading_tm = datetime.now()
            #
            # if start_trading_tm < now_tm < end_trading_tm:
            #     # 매수하기 - 변동성 돌파
            #     for i, ticker in enumerate(coin_buy_wish_list):
            #         # if ticker in daily_profit_list + daily_loss_coin_list:
            #         # 당일 수익창출 또는 당일 손절매 코인 당일 재매수 제외
            #         # continue
            #         if coin_bought_list is None:
            #             break
            #         if ticker not in coin_bought_list:
            #             R = calc_R(ticker, coin_r_list[i])
            #             buy_coin(ticker, coin_ratio_list[i], R)
            #             time.sleep(0.1)
            #
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
            # if now_tm.minute == 0 and 0 <= now_tm.second <= 7:
            #     send_report()
            #     # calc_position_size_by_score()
            #     calc_position_size_by_volatility()
            #     time.sleep(3)
            #
            # if now_tm.hour == 23 and now_tm.minute == 59 and 0 > now_tm.second > 10:
            #     trading_rest_time()
            #     time.sleep(3)
            #
            # # 매수 종목 없으면 강제 휴식
            # if len(coin_buy_wish_list) == 0:
            #     log('매수할 코인 없음. 휴식 10초')
            #     time.sleep(10)

            print('-' * 150)
            time.sleep(1)
    except Exception as e:
        msg = f'가상화폐 시스템 메인 로직 예외 발생. 시스템 종료됨 => {str(e)}'
        log(msg)
        traceback.print_exc()
        system_log(msg)

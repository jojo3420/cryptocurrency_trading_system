from pandas import DataFrame
# from common.date_util import get_today
from datetime import datetime, timedelta
import pyupbit


def calc_position_size_by_volatility(symbol: str, days: int, target_loss_amount=5000):
    """
    목표 손실 금액을 고정하여 포지션 규모 계산
    :param ticker: 코인 심볼 'KRW-ADA' , 'KRW-ETH', 'KRW-BTC', 'KRW-XRP'
    :param days:최고가, 최저가 구할 일수
    :param target_loss_amount: 1최 거래시 최대 허용 손실금액

    :return stock_cnt: 주식수량
    :return position_amount: 투자금액
    :return stop_loss_price: 손절매 가격


    1)가정
    현재가 20$
    20일 최고가: 20$
    20일 최저가: 10$
    1회 투자시 허용할 목표 손실금액: 500$
    손실률 -20%

    3)최고가/최저가를 이용한 투자금액 조절
    (변동성 고려)

    투자 주식수: 손실금액 / (20일최고가 - 20일 최저가)
      ex)500 / (20 - 10)  => 50주

    투자금액: 20$ * 50주 = 1000$

    출처: 인생역전, 투자습관을 바꿔라 -하용현-

    """
    # today = datetime.today()
    df = pyupbit.get_ohlcv(symbol, count=days)
    adj_close = df['close']
    adj_close = adj_close.sort_index(ascending=True)
    # print(adj_close)
    high_price = adj_close.max()
    low_price = adj_close.min()
    print(f'{days}일_최고가: {high_price:,.2f}, {days}일_최저가: {low_price:,.2f}')
    volatility_range = round(high_price - low_price, 2)
    # print(f'변동성 범위: {volatility_range}')
    curr_adj_close = round(adj_close.iloc[-1], 3)
    # print(f'현재가격: {curr_adj_close}')
    stock_cnt = target_loss_amount // volatility_range
    if stock_cnt > 0:
        position_amount = round(curr_adj_close * stock_cnt, 2)
        per_loss = target_loss_amount // stock_cnt
        stop_loss_price = curr_adj_close - per_loss
        return stock_cnt, position_amount, stop_loss_price
    else:
        print(f'{symbol} 수량이 부족합니다. {stock_cnt}')
        return 0, 0, 0


def calc_position_size_by_loss_percent(symbol, loss_percent=0.1, target_loss_amount=5000):
    """
    목표 손실 금액을 고정하여 포지션 규모 계산

    1)가정
    현재가 20$
    20일 최고가: 20$
    20일 최저가: 10$
    1회 투자시 허용할 목표 손실금액: 500$
    손실률 -20%

   2) 손실률에 따른 투자금액 조절
    투자금액: 1회 투자 손실금액 / 손실률(%)

    ex)  500 / 0.2

    """
    days = 20
    df = pyupbit.get_ohlcv(symbol, count=days)
    adj_close = df['close']
    curr_adj_price = round(adj_close[-1], 3)
    # print(f'{symbol} 현재가격: {curr_adj_price}')
    position_amount = round(target_loss_amount / loss_percent, 2)
    stock_cnt = round(position_amount // curr_adj_price, 4)
    if stock_cnt > 0:
        per_loss = target_loss_amount // stock_cnt
        stop_loss_price = curr_adj_price - per_loss
        return stock_cnt, position_amount, stop_loss_price
    else:
        # print(f'{symbol} 수량이 부족. {stock_cnt}')
        return 0, 0, 0


if __name__ == '__main__':
    symbol = 'KRW-ADA'
    days = 20
    cnt, investing_amount, loss_price = calc_position_size_by_volatility(symbol, days, target_loss_amount=5000)
    print(f'{symbol} 변동성 고려한 손실금액 고정한 포지션규모 계산')
    print(f'수량: {cnt}, 투자 금액: {investing_amount:,.0f}')
    print(f'손절가격: {loss_price:,.2f}')
    print('-' * 80)
    print('변동성 고려하지 않는 손실금액 고정 포지션규모 계산')
    cnt, p_amount, loss_price = calc_position_size_by_loss_percent(symbol, target_loss_amount=5000)
    print(f'수량: {cnt}, 투자 규모: {p_amount:,.0f}')
    print(f'손절가격: {loss_price}')

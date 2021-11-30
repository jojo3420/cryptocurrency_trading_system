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
    qty = target_loss_amount // volatility_range
    if qty > 0:
        position_amount = round(curr_adj_close * qty, 2)
        per_loss = target_loss_amount // qty
        stop_loss_price = curr_adj_close - per_loss
        # loss_amount = (curr_adj_close - stop_loss_price) * qty
        return qty, stop_loss_price, position_amount

    return 0, 0, 0


def calc_position_size_by_loss_percent(symbol, loss_percent=0.1, target_loss_amount=5000, entry_price=None):
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

    :return qty: 주식수량
    :return stop_loss_price: 손절매 가격
    :return position_amount: 투자금액
    :return loss_amount: 손실금액

    ex)  500 / 0.2

    """
    days = 20
    df = pyupbit.get_ohlcv(symbol, count=days)
    if df is not None:
        adj_close = df['close']
        curr_adj_price = round(adj_close[-1], 3)
        # print(f'{symbol} 현재가격: {curr_adj_price}')

        position_amount = round(target_loss_amount / loss_percent, 2)
        qty = round(position_amount // curr_adj_price, 4)
        if qty > 0:
            per_loss = target_loss_amount // qty
            if entry_price is None:
                stop_loss_price = curr_adj_price - per_loss
            else:
                stop_loss_price = entry_price - per_loss

            return qty, stop_loss_price, position_amount
    return 0, 0, 0


# def calc_position_size_by_target(symbol: str, portfolio, total_cash, target_volatility=2):
#     """
#     자금 관리: 진입 포지션 규모를 목표한(나의 허용 가능) 변동성과 전일 변동성 기준으로 계산
#     (목표변동성 / 전일변동성) / 코인종목수
#     (2% / 10%) / 5
#     :param target_volatility:
#     :return qty: 수량
#     :return position_amount: 투자 금액
#     :return stop_loss_price: 손절 가격
#     """
#     prev_volatility = calc_prev_volatility(symbol)
#     print(f'이전일 변동성: {prev_volatility}%')
#     size = (target_volatility / prev_volatility) / len(portfolio)
#     position_size = total_cash * size  # 1종목당 사용할 포지션 규모금액
#     curr_price = pyupbit.get_current_price(symbol)
#     qty = round(position_size / curr_price, 4)
#     return qty


# def calc_position_size_turtle(symbol: str, days: int, total_cash: int, minimum_amount: int) -> int:
#     """
#     터틀 트레이딩 자금 방식에 의한 매수(진입) 수량 구하기
#      변동성 ATR 기준으로 수량 계산
#       - 낮은 변동성에는 많은 수량
#       - 높은 변동성에는 낮은 수량
#
#       A: 총 자본에서 감수할 손실금액: 총자본의 1% ~ 2%
#       B: 계약위험: 1N *  거래단위
#       Unit = A / B
#     """
#     ATR = get_current_atr(symbol, days=days)
#     curr_price = pyupbit.get_current_price(symbol)
#     if ATR and curr_price:
#         NN = ATR + ATR
#         transaction_unit = round(minimum_amount / curr_price, 8)  # 최소주문수량
#         # print(f'{symbol} 최소주문수량: {transaction_unit:.8f}')
#         risk_take = total_cash * 0.01  # 총자본에서 허용할 리스크 금액
#         # print(f'리스크 감수 금액: {risk_take:,}')
#         contract_risk = round(ATR * transaction_unit, 1)  # 거래리스크
#         # print(f'거래리스크: {contract_risk:,}')
#         if risk_take and contract_risk:
#             unit = round(risk_take / contract_risk, 4)
#             return unit
#         return 0


if __name__ == '__main__':
    symbol = 'KRW-FLOW'
    symbol = 'KRW-STPT'
    symbol = 'KRW-ADA'
    days = 20
    cnt, loss_price, investing_amount = calc_position_size_by_volatility(symbol, days, target_loss_amount=2000)
    print(f'{symbol} 변동성 고려한 손실금액 고정한 포지션규모 계산')
    print(f'수량: {cnt}, 투자 금액: {investing_amount:,.0f}')
    print(f'손절가격: {loss_price:,.2f}')
    print('-' * 80)
    print('변동성 고려하지 않는 손실금액 고정 포지션규모 계산')
    cnt, loss_price, p_amount = calc_position_size_by_loss_percent(symbol, loss_percent=0.04, target_loss_amount=2000)
    print(f'수량: {cnt}, 투자 규모: {p_amount:,.0f}')
    print(f'손절가격: {loss_price}')

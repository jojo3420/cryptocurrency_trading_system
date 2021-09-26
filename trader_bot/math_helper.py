import time
import traceback

import pyupbit
# from common.utils import calc_williams_R, calc_moving_average_by, calc_fix_moving_average_by
from pandas import DataFrame, Series, concat
import math
import numpy as np
from common.utils import get_today_format


def calc_target_price(symbol: str, R: float = 0.5) -> int:
    """
    래리 윌리엄스 변동성 돌파가격(진입가격) 계산하기
    :param symbol:
    :param R:
    :return: 돌파가격(진입가격)
    """
    # print(f'symbol: {symbol}')
    df = pyupbit.get_ohlcv(symbol, count=2)
    # print(df.tail())
    if len(df) > 0:
        yesterday_s: Series = df.iloc[-2]
        today_s: Series = df.iloc[-1]
        today_open: Series = today_s['open']
        yesterday_high = yesterday_s['high']
        yesterday_low = yesterday_s['low']
        target_price = today_open + ((yesterday_high - yesterday_low) * R)
        if not math.isnan(target_price):
            return int(target_price)


def calc_prev_range(symbol: str) -> float:
    df = pyupbit.get_ohlcv(symbol, count=2)
    # print(df.tail())
    if not df.empty:
        yesterday_s: Series = df.iloc[-2]
        # today_s: Series = df.iloc[-1]
        yesterday_high = yesterday_s['high']
        yesterday_low = yesterday_s['low']
        prev_range = yesterday_high - yesterday_low
        return prev_range


def calc_today_range(symbol: str) -> float:
    df = pyupbit.get_ohlcv(symbol, count=1)
    # print(df.tail())
    if not df.empty:
        today_s: Series = df.iloc[-1]
        high = today_s['high']
        low = today_s['low']
        range = high - low
        return range


def calc_ma_range(symbol: str, days: int) -> float:
    df = pyupbit.get_ohlcv(symbol, count=days)
    # print(df.tail())
    if not df.empty:
        df['range'] = df['high'] - df['low']
        # print(df)
        return df['range'].rolling(window=days).mean().iloc[-1]


def calc_ewm_range(symbol: str, days: int) -> float:
    df = pyupbit.get_ohlcv(symbol, count=days)
    # print(df.tail())
    if not df.empty:
        df['range'] = df['high'] - df['low']
        # print(df)
        return round(df['range'].ewm(days).mean().iloc[-1], 1)


def get_today_open(symbol: str) -> float:
    df = pyupbit.get_ohlcv(symbol, count=1)
    # print(df)
    return df.iloc[-1]['open']


def calc_atr(symbol: str, days: int) -> DataFrame:
    """
        ATR(Average True Range) 구하기 by DataFrame
        1) (당일 고가 - 당일 저가) 차이 절대값
        2) (당일 고가 - 전일 종가) 차이 절대값
        3) (당일 저가 - 전일 종가) 차이 절대값

        1,2,3) 중에 가장 큰값이 당일의 TR
        TR 이동평균 구함 => ATR
        https://www.learnpythonwithrune.org/calculate-the-average-true-range-atr-easy-with-pandas-dataframes/

    """
    # today_str = get_today('%Y%m%d')
    # df = get_ohlc_by(ticker, rows_cnt=days)
    # df = df.sort_index()
    # # print(df)
    # # 당일 시세 데이터 제외
    # # if today_str == str(df.iloc[-1].name):
    # #     df = df.iloc[0: -1]
    # # print(df)
    # # print(len(df))
    # high_low = df['high'] - df['low']
    # high_close = np.abs(df['high'] - df['close'].shift(1))
    # low_close = np.abs(df['low'] - df['close'].shift(1))
    # ranges = pd.concat([high_low, high_close, low_close], axis=1)
    # true_range = np.max(ranges, axis=1)
    true_range = calc_true_range(symbol, days)
    # print(true_range)
    ATR_EMA: Series = true_range.ewm(days).mean()
    return ATR_EMA


def calc_absolute_atr(symbol: str, days: int) -> DataFrame:
    """
    Absolute Average True Range(ATR%) 구하기
    https://www.marketvolume.com/technicalanalysis/absoluteatr.asp
    """

    # true_range = calc_true_range(ticker, days)
    # print(true_range)
    # prev_close = get_prev_stock_close_price(ticker)
    # TR_PERCENT: DataFrame = true_range / prev_close * 100
    # ABS_ATR = TR_PERCENT.rolling(window=days).mean()
    # return ABS_ATR

    # df = get_ohlc_by(symbol, rows_cnt=days+1)
    df = pyupbit.get_ohlcv(symbol, count=days + 1)
    df = df.sort_index()
    # print(df)
    high_low = df['high'] - df['low']
    prev_close = df['close'].shift(1)
    # print(prev_close)
    high_close = np.abs(df['high'] - prev_close)
    low_close = np.abs(df['low'] - prev_close)
    ranges = concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['true_range'] = true_range
    # print(df)
    df['TR%'] = df['true_range'] / prev_close * 100
    df = df.dropna()
    # print(df)
    df['ABS_ATR'] = df['TR%'].rolling(window=days).mean()
    # print(df)
    return df['ABS_ATR'].iloc[-1]


def calc_atr2(symbol: str, days: int) -> DataFrame:
    """
        ATR(Average True Range) 구하기 by DataFrame
        1) (당일 고가 - 당일 저가) 차이 절대값
        2) (당일 고가 - 전일 종가) 차이 절대값
        3) (당일 저가 - 전일 종가) 차이 절대값

        1,2,3) 중에 가장 큰값이 당일의 TR
        TR 이동평균 구함 => ATR

        트레이딩 바이블 책 공식 참조
        1) 당일 가격 데이터 제외
        0 번째 True_Range 제외한 이유는 전일 데이터반영 안되고 당일 고가-저가값 이므로

    """
    today_str = get_today_format('%Y%m%d')
    df = pyupbit.get_ohlcv(symbol, count=days + 3)
    df = df.sort_index()
    # 당일 시세 데이터 제외
    if today_str == str(df.iloc[-1].name):
        # df = df.drop(today_str, axis=1)
        df = df.iloc[0: -2]
    # print(df)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift(1))
    low_close = np.abs(df['low'] - df['close'].shift(1))
    ranges = concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    # print(true_range)
    _TR = true_range[1:-2]
    SMA = _TR.rolling(len(_TR)).mean()
    # print(SMA)
    ATR = (SMA.iloc[-1] * 19 + true_range.iloc[-1] * 2) / (days + 1)
    return ATR


def get_current_atr(symbol: str, days: int) -> float:
    """
     ATR 값
    """
    ATR = calc_atr(symbol, days)
    return round(ATR.iloc[-1], 1)


def calc_true_range(symbol: str, days: int) -> DataFrame:
    """
    True Range 구하기
    """
    df = pyupbit.get_ohlcv(symbol, count=days)
    df = df.sort_index()
    # print(df)
    high_low = df['high'] - df['low']
    prev_close: Series = df['close'].shift(1)
    high_close = np.abs(df['high'] - prev_close)
    low_close = np.abs(df['low'] - prev_close)
    ranges = concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    # print(f'{true_range}')
    return true_range


def calc_position_sizing_target(symbol: str, portfolio, total_cash, target_volatility=2):
    """
    자금 관리: 진입 포지션 규모를 목표한(나의 허용 가능) 변동성과 전일 변동성 기준으로 계산
    (목표변동성 / 전일변동성) / 코인종목수
    (2% / 10%) / 5
    :param target_volatility:
    :return:
    """
    prev_volatility = calc_prev_volatility(symbol)
    print(f'이전일 변동성: {prev_volatility}%')
    size = (target_volatility / prev_volatility) / len(portfolio)
    position_size = total_cash * size  # 1종목당 사용할 포지션 규모금액
    curr_price = pyupbit.get_current_price(symbol)
    qty = round(position_size / curr_price, 4)
    return qty


def calc_prev_volatility(symbol: str) -> float:
    """
    전일 변동성 구하기
    (고가 - 저가) / 시가 * 100
    :param symbol:
    :return:
    """
    prev_range: float = calc_prev_range(symbol)
    open = get_today_open(symbol)
    return round((prev_range / open) * 100, 1)


def calc_ewm_volatility(symbol: str, days: int):
    """
     전일 변동성 구하기 (지수이동평균)
     (고가 - 저가) / 시가 * 100
     :param symbol:
     :return:
     """


def calc_position_sizing(symbol: str, days: int, total_cash: int, minimum_amount: int) -> int:
    """터틀 트레이딩 자금 방식에 의한 매수(진입) 수량 구하기
     변동성 ATR 기준으로 수량 계산
      - 낮은 변동성에는 많은 수량
      - 높은 변동성에는 낮은 수량

      A: 총 자본에서 감수할 손실금액: 총자본의 1% ~ 2%
      B: 계약위험: 1N *  거래단위
      Unit = A / B
    """
    ATR = get_current_atr(symbol, days=days)
    curr_price = pyupbit.get_current_price(symbol)
    if ATR and curr_price:
        # NN = ATR + ATR
        transaction_unit = round(minimum_amount / curr_price, 8)  # 최소주문수량
        # print(f'{symbol} 최소주문수량: {transaction_unit:.8f}')
        risk_take = total_cash * 0.02  # 총자본에서 허용할 리스크 금액
        # print(f'리스크 감수 금액: {risk_take:,}')
        contract_risk = round(ATR * transaction_unit, 1)  # 거래리스크
        # print(f'거래리스크: {contract_risk:,}')
        if risk_take and contract_risk:
            unit = round(risk_take / contract_risk, 4)
            return unit
        return 0


def calc_total_buy_quantity(symbol: str, cash: int) -> float:
    """
    주언진 현금으로 매수 가능 수량 계산
    :param symbol:
    :param cash:
    :return:
    """
    qty = 0
    curr_price = pyupbit.get_current_price(symbol)
    if curr_price:
        qty = round(cash / curr_price, 4)
        return qty
    else:
        return qty


def calc_noise_ma_by(symbol: str, days: int = 20) -> float:
    """
    실시간 이동 평균 노이즈 비율 계산 (당일 가격정보 포함됨)
    추세/비추세 시장상태 판단
    의미: 전체캔들의 길이중 윗꼬리, 아래꼬리가 차지하는 비중 계산

    추세적인 종목(노이즈 비율이 적은 종목만 선택)

    개별 노이즈 공식
        1 - abs(시가 - 종가) / (고가 - 저가)

    의미하는것:  노이즈값은 0~1사이에 값을 가진다. 값이 0에 가까울 수록 시장 노이즈가 적은 즉 방향성이 일정한 것 이며
    노이즈값이 1에 가까울수록 노이즈가 큰 (하락반전) 뜻이다.

    케이스분석
    1) 시가: 1000  종가:1500,  고가:1500, 저가: 1000
    1-(500 / 500)  => 0 노이즈없음
    => 강한추세로 상승만 했음
    당일 시가가 장마감할동안 시가밑으로 떨어지지 않았다는것 그리고 당일종가가 당일 고가와 같으므로
    하락없이 장내내 범위안에서 상승했다는것


    1-2) 시가 1000, 종가 800, 고가 1000, 저가 700
    1 - (200 / 300)  => 0.33
    => 비교적 추세적으로 하락하므로 노이즈가 적다.

    2) 시가: 1000, 종가: 1300, 고가: 1500, 저가: 1000
    1 - (300 / 500) => 0.4

    3) 시가: 1000, 종가 900, 고가 1500, 저가: 700
    1-(100 / 800 =>0.125)  => 0.875  노이즈가 큼 => 비추세적

    4) 시가 1000, 종가 800, 고가: 2000, 저가 500
    1 - (200 / 1500 => 0.133) => 0.867 노이즈 큼 => 비추세적
    :param symbol:
    :param days:
    :return:
    """
    try:
        ohlcv: DataFrame = pyupbit.get_ohlcv(symbol)
        if len(ohlcv) > 0:
            # print(ohlcv.tail())
            # 당일 노이즈 값
            noise: Series = 1 - abs(ohlcv['open'] - ohlcv['close']) / (ohlcv['high'] - ohlcv['low'])
            # print(noise.tail(days))
            # return noise[-1]
            MA_noise = noise.rolling(window=days).mean()
            EMA_noise = noise.ewm(days).mean()
            # print('MA: ', MA_noise[-1])
            # print('EMA', EMA_noise[-1])
            return EMA_noise[-1]
    except Exception as E:
        msg = f'calc_noise_ma_by() 예외 발생. {str(E)}'
        print(msg)
        traceback.print_exc()
        return 0.5


def find_bull_market_list() -> list:
    """
    상승코인 찾기
     1) 현재가격 > EMA3 OR EMA5
     2) 노이즈값 0.55 미만
    :return:
    """
    bull_coins = []
    R = 0.5
    # for symbol in pyupbit.get_tickers(fiat='KRW'):
    #     try:
    #         curr_price = pyupbit.get_current_price(symbol)
    #         target_price = calc_target_price(symbol, R)
    #         # MA3 = calc_fix_moving_average_by(ticker, 3)
    #         # MA5 = calc_fix_moving_average_by(ticker, 5)
    #         # curr_noise = get_current_noise(ticker)
    #         # noise_ma3 = calc_fix_noise_ma_by(ticker, 3)
    #         # noise_ma5 = calc_fix_noise_ma_by(ticker, 5)
    #         # if curr_price > MA3 and curr_price > MA5 \
    #         #         and curr_price > target_price and curr_noise < 0.3 \
    #         #         and noise_ma3 < 0.55 and noise_ma5 < 0.55:
    #         #     print(f'상승 불코인: {ticker}')
    #         # bull_coins.append(symbol)
    # except Exception as E:
    # print(str(E))
    #
# return bull_coins

if __name__ == '__main__':
    symbol = 'KRW-XRP'
    # target_price = calc_target_price(symbol)
    # print(f'{symbol} target_price: {target_price:,}')
    # print(calc_prev_range(symbol))
    # print(calc_today_range(symbol))
    # print(calc_ma_range(symbol, 5))
    # print(calc_ewm_range(symbol, 5))
    # print(get_today_open(symbol))
    # print(calc_prev_volatility(symbol))
    # print('포지션사이징 - 타켓변동성:', calc_position_sizing_target(symbol, [1, 2, 3], 100000))
    # print('포지션사이징 - ATR기준:', calc_position_sizing(symbol, 5, 100000, 5000))

    # true_range = calc_true_range(symbol, 14)
    # atr = calc_atr(symbol, 14)
    # print(atr)
    # print(get_current_atr(symbol, 14))

    for symbol in pyupbit.get_tickers(fiat='KRW'):
        noise = calc_noise_ma_by(symbol, 1)
        if noise <= 0.3:
            print(f'노이즈 적은 종목 => {symbol} {noise}')
        time.sleep(0.2)

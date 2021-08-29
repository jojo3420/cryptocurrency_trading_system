import pybithumb
import numpy as np
from pandas import DataFrame

SYM_BTC = 'BTC'
df = pybithumb.get_ohlcv(SYM_BTC)

# 2018년 데이터만 추출
df_2018 = df['2018']
df_2018.to_excel('2018_bitcoin.xlsx')

df['range'] = (df['high'] - df['low']) * 0.5
df['range_shift_1'] = df['range'].shift(1)  # 현재 range 컬럼 전체를 1행 아래의 데이터 이동
df['target_price'] = df['open'] + df['range_shift_1']
df.to_excel('btc_range.xlsx')

# 전략 검증 백테스트

# 수수료 및 슬리피지 적용 fee
fee = 0.0032
# fee = 0
df['ror'] = np.where(df['high'] > df['target_price'], (df['close'] / df['target_price'] - fee), 1)
print(df.tail())

# 누적 수익률 계산
# 매매	매수가	매도가	수익률 (배)
# 1회차	100	     120	 1.2
# 2회차	120	     120	 1
# 3회차	120	     140	 1.1666
# -      -	       -	 1.4
# 개별 수익률을 각각 곱하면 된다. (복리수익은 곱이라고 기억하고 있다.)
# 1.2 * 1 * 1.1666 = 1.4

#  Series 객체에서 모든 값을 곱해주는 메서드로 cumprod()가 있습니다.
total_ror = df['ror'].cumprod()
print(total_ror)
ror = total_ror[-2]  # cumprod()를 호출하면 Series 객체가 리턴, Series 끝에서 2번째 값( 당일제외 어제 확정값)
print('누적 수익률: ', ror)
# 수수료 적용전  누적 수익률:  61.77
# 수수료 적용후: 누적 수익률:  1.79


df.to_excel('trade.xlsx')

# nympy.where() 용도 확인
#  numpy 모듈의 where() 함수를 사용하면 Pandas DataFrame에서 각 행 단위로 if 문을 적용할 수 있습니다.
data = {'bithumb': [100, 100, 100], 'korbit': [90, 110, 120]}
df2 = DataFrame(data)
df2['최저가'] = np.where(df2['bithumb'] < df2['korbit'], 'bithumb', 'korbit')
df2.to_excel('거래소.xlsx')

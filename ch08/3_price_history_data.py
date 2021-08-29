import pyupbit

# 과거 데이터 조회

df = pyupbit.get_ohlcv('KRW-BTC')
print(df)
# print(df.tail(10))


#interval: 월/주/일/분봉 중 1개  기본값: 일
df2 = pyupbit.get_ohlcv('KRW-ETH', interval='minute1')
print(df2)


# 최근 10일 데이터
df3 = pyupbit.get_ohlcv('KRW-ETH', count=10)
print(df3)

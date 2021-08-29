import pyupbit
print(pyupbit.Upbit)


# 전체 티커 조회
tickers = pyupbit.get_tickers()
for ticker in tickers:
    print(ticker)


# fiat: KRW, BTC, USDT,
# tickers = pyupbit.get_tickers('KRW')
# for ticker in tickers:
#     print(ticker)


#
# tickers = pyupbit.get_tickers('BTC')
# for ticker in tickers:
#     print(ticker)
#
#
#
#
# tickers = pyupbit.get_tickers('USDT')
# for ticker in tickers:
#     print(ticker)
#
#



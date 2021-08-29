import pybithumb

ticker = 'BTC'
btc_rows = pybithumb.get_ohlcv(ticker)
print(btc_rows.tail())


btc_rows.to_excel('btc.xlsx')
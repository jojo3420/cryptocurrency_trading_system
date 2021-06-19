from volatility_breakthrough_trading import *
import pybithumb

if __name__ == '__main__':
    prices: 'DataFrame' = pybithumb.get_candlestick('BTC')
    rows = prices.iloc[-2:]
    for t in rows.itertuples():
        print(t)

    print(calc_williams_R('BTC'))
from common.utils import *
from common.bithumb_api import *
from volatility_breakthrough_trading import *

# price = calc_moving_average_by('ETH')
days = 3
ticker = 'ETH'
prices: DataFrame = pybithumb.get_candlestick(ticker)
print(prices.tail())
close: Series = prices['close']
MA: Series = close.rolling(days).mean()
print(MA.tail())
price = MA[-1]
print(price)

clac_price = (2725000 + 2949000 + 2980000) / 3
print(clac_price)

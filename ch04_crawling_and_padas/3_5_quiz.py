import pandas as pd

"""
1) 3일 동안의 OHLC 정보를 DataFrame 객체로 생성하라.

-	        open    high    low  close
2018-01-01	 737    755	     700   750
2018-01-02	 750    780	     710   770
2018-01-03	 770    770	     750   730

"""
dic = {'open': [737, 750, 770],
       'high': [755, 780, 770],
       'low': [700, 710, 750],
       'close': [750, 770, 730],
       }
index = ['2018-01-01', '2018-01-02', '2018-01-03']
ohlc = pd.DataFrame(dic, index=index)
print(ohlc)

"""
2) DataFrame 객체에 변동폭 (volatility) 을 추가하라. 변독폭은 고가와 저가의 차분값이다.
-	open	high	low	close	volatility
2018-01-01	737	755	700	750	55
2018-01-02	750	780	710	770	70
2018-01-03	770	770	750	730	20
"""

ohlc['volatility'] = ohlc['high'] - ohlc['low']
print(ohlc)


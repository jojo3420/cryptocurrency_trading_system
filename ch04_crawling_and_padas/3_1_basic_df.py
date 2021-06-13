from pandas import DataFrame

dic = {'open': [100, 200, 300], 'close': [110, 210, 310]}
df = DataFrame(dic)
print(df)
print('-' * 100)

#  OHLC (Open/High/Low/Close)
dict2 = {'open': [730, 140], 'high': [440, 120], 'low': [220, 110], 'close': [50, 80]}
index = ['2021-01-01', '2021-01-02']
df2 = DataFrame(dict2, index=index)
print(df2)
print('-' * 100)


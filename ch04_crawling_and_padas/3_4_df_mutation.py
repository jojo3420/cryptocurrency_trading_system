import pandas as pd

dict1 = {'open': [1, 2, 3], 'close': [2, 3, 5]}
index = ['2021-01-02', '2021-01-03', '2021-01-04']
df = pd.DataFrame(dict1, index=index)
# print(df)


# 새로운 컬럼 추가하기
# 사용자정의 인덱스가 설정되어 있다면 => index 설정 중요.
s1 = pd.Series([51, 12, 31], index=index)
print(type(s1))
df['volume'] = s1
print(df)
print('-' * 100)

# row 추가하기
df.loc['2021-01-05'] = (100, 200, 300)
df.loc['2021-01-06'] = [0, 0, 1]
print(df)

print('-' * 100)
# 기존 df 데이터 이용하여 새로운 열(upper) 추가하기
upper: 'Series' = df['open'] * 1.3
# print(upper)
# print(type(upper))  # Series
df['upper'] = upper
print(df)

# 컬럼 시프트
s1 = pd.Series([100, 200, 300])
s2 = s1.shift(1)
print(s1)
print(s2)

# s1
# 0    100
# 1    200
# 2    300
# dtype: int64

# s2
# 0      NaN
# 1    100.0
# 2    200.0
# dtype: float64


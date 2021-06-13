from pandas import Series

values = [100, 200, 300, 400, 500]
s1 = Series(values)
print(type(s1))
print(s1)
print('-' *100)
# index 지정하기
date = ['2020-01-01', '2021-01-01', '2022-01-01', '2023-01-01', '2024-01-01']
xrp_close = [512, 553, 112, 11, 55]
xrp = Series(xrp_close, index=date)
print(xrp)
print('-' *100)
# 정수 인덱스는 디폴트임
print(xrp[0], xrp['2020-01-01'])
print('-' *100)

# 인덱싱 / 슬라이스
values = xrp.values
indexs = xrp.index
print(indexs)
print(type(indexs))
print(values)
print(type(values))
print('-' *100)

# 여러개의 인덱스값 사용
print(xrp[[0, 1, 2]])
print(xrp[['2020-01-01', '2021-01-01']])


print('-' *100)
ll = [1, 2, 3, 4, 5]
print(ll[0: 2])

# 슬라이싱
print(xrp['2020-01-01': '2022-01-01'])
# 리스트와 다르게 인덱싱 할때 끝값도 포함된다. (리스트와 다른점)

print(xrp[1: 3])
# 디폴트 인덱스번호로는 리스트와 같이 끝값 제외


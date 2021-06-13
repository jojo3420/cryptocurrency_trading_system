from pandas import Series

index = ['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04']
close = [100, 110, 220, 50]

s1 = Series(close, index=index)
print(s1)
print('-' * 100)

# 기존값 변경하기
s1['2018-01-02'] = '값 변경'
print(s1)
print('-' * 100)

# 인덱스로 삭제
# print(s1.drop('2018-01-03'))
s1 = s1.drop('2018-01-03')
print(s1)

# 사칙연산 - 기존 리스트
l1 = [1, 2, 3, 4, 5]
new_l1 = [n * 2 for n in l1]  # 나열하여 사칙연산후 새로운 리스트 만들어야함
print(new_l1)

# 시리즈 연산 - 저장된 모든 데이터에 사칙연산 적용됨
s1 = Series(l1)
print(s1 * 10)
print(s1 / 10)
print(s1 // 2)

print(type(s1 * 2))  # series

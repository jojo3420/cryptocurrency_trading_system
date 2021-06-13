import pandas as pd

path = 'BTC_KRW Bithumb 내역.csv'
df = pd.read_csv(path)
print(df)
print('-' * 120)

#  자동 생성된 번호 대신 다른 Column을 index로 지정하기 위해서는 set_index 함수를 사용
df = df.set_index('날짜')
print(df)
print('-' * 120)

# 엑셀로 저장
df.to_excel('ohlc.xlsx')

# 저장된 엑셀파일 읽어오기
df2 = pd.read_excel('ohlc.xlsx')
print(df2)



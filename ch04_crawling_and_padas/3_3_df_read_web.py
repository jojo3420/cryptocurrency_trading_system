import pandas as pd
import requests

# 스크래핑 에러시 확인
# https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context


# LG전자 Naver 금융 - 일별시세
url = 'https://finance.naver.com/item/sise_day.nhn?code=066570'

# 변경되서  헤더 추가 해야함!
response = requests.get(url, headers={"user-agent": "Mozilla"})

df: list = pd.read_html(response.content)
print('df type: ', type(df))  # list
print(type(df[0]))  # pandas.DataFrame
df = df[0].dropna()
df = df.set_index('날짜')
print(df)
print('-' * 100)

# df 인덱싱
# 종가 열(column) 선택후 출력
print(df['종가'])
print('-' * 100)

# 1행(row) 선택후 출력
print(df.iloc[0])  # default index
print('-' * 100)

print(df.loc['2021.06.11'])  # custom index
print('-' * 100)

# 하나 이상의 행 가져오기: [[]] 주의
print(df.iloc[[0, 1, 2]])
print(df.loc[['2021.06.11', '2021.06.10']])



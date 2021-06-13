import requests
from bs4 import BeautifulSoup

url = "https://finance.naver.com/item/main.nhn?code=000660"
response = requests.get(url)
content = response.content
# print(content)

soup = BeautifulSoup(content, 'html5lib')

tags: list = soup.select('#_per')

print(type(tags))  # <class 'bs4.element.ResultSet'>
print(tags[0].text)


def get_per(code) -> float:
    url = "http://finance.naver.com/item/main.nhn?code=" + code
    html = requests.get(url).text

    soup = BeautifulSoup(html, "html5lib")
    tags = soup.select("#_per")
    tag = tags[0]
    return float(tag.text)


def get_dividend(code) -> float:
    url = "http://finance.naver.com/item/main.nhn?code=" + code
    html = requests.get(url).text

    soup = BeautifulSoup(html, "html5lib")
    tags = soup.select("#_dvr")
    tag = tags[0]
    return float(tag.text)


print(get_per("000660"))
print(get_dividend("000660"))

from pybithumb import Bithumb
"""
1) 표 5-1을 참고해서 모든 가상화폐의 24시간 변동률을 출력하세요.

"""

all_currency_prices: dict = Bithumb.get_current_price('ALL')
print(all_currency_prices)
for key, val in all_currency_prices.items():
    print(key, 'change %:',  val['fluctate_rate_24H'])
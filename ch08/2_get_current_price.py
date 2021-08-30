import pyupbit


# 현재가격 조회
krw_btc = pyupbit.get_current_price('KRW-BTC')
print(f'원화 BTC 가격: {krw_btc:,.0f}')

#
# btc_eth = pyupbit.get_current_price('BTC-XRP')
# print(f'BTC의 이더리움 가격: {btc_eth}')
#
# krw_eth = pyupbit.get_current_price('KRW-XRP')
# print(f'krw 이더리움 가격: {krw_eth:,.0f}')

# print(f'1이더리움의 BTC 가격을 원화로 환산: {btc_eth * krw_btc:,.0f}')


prices_dict = pyupbit.get_current_price(['BTC-XRP', 'KRW-XRP', 'USDT-XRP'])
KRW_XRP = prices_dict['KRW-XRP']
BTC_XRP = prices_dict["BTC-XRP"]
USDT_XRP = prices_dict["USDT-XRP"]
print('원화 리플가격:', KRW_XRP)
print('비트코인 리플가격 원화환산:', BTC_XRP * krw_btc)
print(USDT_XRP)

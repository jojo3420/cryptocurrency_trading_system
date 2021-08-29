import pyupbit


# 현재가격 조회
krw_btc = pyupbit.get_current_price('KRW-BTC')
print(f'원화 BTC 가격: {krw_btc:,.0f}')


btc_eth = pyupbit.get_current_price('BTC-ETH')
print(f'BTC의 이더리움 가격: {btc_eth}')

krw_eth = pyupbit.get_current_price('KRW-ETH')
print(f'krw 이더리움 가격: {krw_eth:,.0f}')

print(f'1이더리움의 BTC 가격을 원화로 환산: {btc_eth * krw_btc:,.0f}')


prices_dict = pyupbit.get_current_price(['BTC-XRP', 'KRW-XRP'])
print(f'{prices_dict["BTC-XRP"]:f}', prices_dict['KRW-XRP'])
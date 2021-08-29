import pyupbit


def read_keyfile():
    with open('../.env.dev') as stream:
        keys = {}
        lines = stream.readlines()
        for line in lines:
            _label, key = line.split('=')
            keys[_label] = key.strip()
        # print(keys)
        return keys


keys = read_keyfile()
api = pyupbit.Upbit(keys['AccessKey'], keys['SecretKey'])

ticker = 'KRW-XRP'
current_krw_xrp_price = pyupbit.get_current_price(ticker)
print(f'리플 원화 현재가: {current_krw_xrp_price:,.0f}')

# 지정가 매수
quantity = 1
ret = api.buy_limit_order(ticker, current_krw_xrp_price, volume=quantity)
# print('매수결과: ', ret)
# 매수결과:  {'error': {'message': '최소주문금액 이상으로 주문해주세요', 'name': 'under_min_total_bid'}}
# https://docs.upbit.com/docs/api-%EC%A3%BC%EC%9A%94-%EC%97%90%EB%9F%AC-%EC%BD%94%EB%93%9C-%EB%AA%A9%EB%A1%9D
# => 리플의 현재 최소 주문금액은 5000 krw 임
# 매수결과:  {'uuid': 'ecccd8d2-69a2-4f6a-84ed-29b29c3d020b', 'side': 'bid', 'ord_type': 'limit',
# 'price': '1360.0', 'state': 'wait', 'market': 'KRW-XRP',
# 'created_at': '2021-08-29T19:48:18+09:00', 'volume': '5.0',
# 'remaining_volume': '5.0', 'reserved_fee': '3.4',
# 'remaining_fee': '3.4', 'paid_fee': '0.0', 'locked': '6803.4',
# 'executed_volume': '0.0', 'trades_count': 0}

# 지정가 매도
uuid = ret.get('uuid', '')
if uuid == '' and ret['error']:
    err_msg = ret.get('error', '')
    print(err_msg)
else:
    print(f'uuid: {uuid}')
    position_side = ret.get('side', '')
    order_type = ret.get('order_type', '')
    bought_price = ret.get('price', 0)
    bought_qty = ret.get('volume', 0)



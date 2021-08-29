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

quantity = api.get_balance(ticker)
print(quantity, type(quantity))

ret = api.sell_limit_order(ticker, current_krw_xrp_price * 2, volume=quantity)
# print(ret)
uuid = ret.get('uuid', '')
if uuid and 'error' not in ret:
    # {'uuid': '61f6aa4f-6bdd-4e16-b2f1-9682008dda76',
    # 'side': 'ask', 'ord_type': 'limit', 'price': '2700.0',
    # 'state': 'wait', 'market': 'KRW-XRP', 'created_at': '2021-08-29T20:17:45+09:00',
    # 'volume': '5.0', 'remaining_volume': '5.0',
    # 'reserved_fee': '0.0', 'remaining_fee': '0.0',
    # 'paid_fee': '0.0', 'locked': '5.0', 'executed_volume': '0.0', 'trades_count': 0}
    # 61f6aa4f-6bdd-4e16-b2f1-9682008dda76
    print(uuid)
    order_state = ret.get('state')
    print(order_state)
else:
    err_dict = ret.get('error', '')
    print(err_dict)

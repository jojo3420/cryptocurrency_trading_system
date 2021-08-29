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
uuid = 'e2efa0b2-ae15-41b8-aae6-6adf313dbb96'
ret = api.cancel_order(uuid=uuid)
print('주문취소 결과:',  ret)
# 주문취소 결과: {'uuid': 'd02faa13-53ee-4041-aa12-229a4aa08d35', 'side': 'ask', 'ord_type': 'limit',
# 'price': '2700.0', 'state': 'wait', 'market': 'KRW-XRP',
# 'created_at': '2021-08-29T20:20:37+09:00', 'volume': '5.0',
# 'remaining_volume': '5.0', 'reserved_fee': '0.0',
# 'remaining_fee': '0.0', 'paid_fee': '0.0', 'locked': '5.0',
# 'executed_volume': '0.0', 'trades_count': 0}

cancel_order_uuid = ret.get('uuid', '')
if cancel_order_uuid and 'error' not in ret:
    order_type = ret.get('ord_type', '')
    order_state = ret.get('state', '')
    ask_price = ret.get('price', -1)
    quantity = ret.get('volume', -1)
    print(f'주문취소 uuid: {cancel_order_uuid}')
    print(f'주문상태: {order_state}, 매도가: {ask_price}, 수량: {quantity}')

else:
    error = ret.get('error', '')
    print(error)

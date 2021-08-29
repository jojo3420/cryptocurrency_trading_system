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
total_balance: list = api.get_balances()
# 'default' 그룹에 대해서 1분간 1799개, 1초에 29개의 API 호출이 가능함

for balance in total_balance:
    # print(balance)
    currency = balance['currency']
    balance = balance['balance']
    # print(type(balance))
    print(f'currency: {currency}, balance: {float(balance):,.2f}')

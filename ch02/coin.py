ohlc = {
    'BTC': [100, 200, 300, 400],
    'ETH': [200, 300, 400, 500],
}


def get_open_price(currency: str) -> int:
    return ohlc[currency][0]


def get_close_price(currency: str) -> int:
    return ohlc[currency][3]


if __name__ == '__main__':
    print('BTC open:', get_open_price('BTC'))
    print('ETH close:', get_close_price('ETH'))

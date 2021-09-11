def get_uptic_price(price, tic=1):
    """
    주어진 가격에서 n틱 위의 가격
    :param price:
    :param tic: 1
    :return:
    """
    price = format(price, '.8f')
    if price.find('.') != -1:
        integer_str, decimal_str = price.split('.')
        middle_decimal_str = ''
        for n in decimal_str:
            if n == '0':
                middle_decimal_str += n
        decimal_part = int(float(decimal_str)) + tic
        uptic_price = f'{integer_str}.{middle_decimal_str}{decimal_part}'
        return float(uptic_price)


def get_downtic_price(price, tic=-1):
    """
    주어진 가격에서 n틱 아래의 가격
    기본틱: 1
    :param price:
    :param tic: -1
    :return:
    """
    price = format(price, '.8f')
    if price.find('.') != -1:
        integer_str, decimal_str = price.split('.')
        middle_decimal_str = ''
        for n in decimal_str:
            if n == '0':
                middle_decimal_str += n
            else:
                break

        decimal_part = int(float(decimal_str)) + tic
        if decimal_part == -1:
            integer_part = int(integer_str) + tic
            uptic_price = f'{integer_part}.0'
        else:
            uptic_price = f'{integer_str}.{middle_decimal_str}{decimal_part}'
        return float(uptic_price)


if __name__ == '__main__':
    # price = '123.5123'
    # uptic_price = get_uptic_price(price, 30)
    # downtic_price = get_uptic_price(price, -20)
    # print(uptic_price)
    # print(downtic_price)

    # price = '123.5'
    # uptic_price = get_uptic_price(price, 15)
    # downtic_price = get_downtic_price(price, -15)
    # print(uptic_price)
    # print(downtic_price)

    """
    BTC 마켓에서 COMP 코인 매수하기
[2021-09-06 22:45:35.558979] 매도호가: 0.01069999, 진입가: 0.9272440
    """
    bid_price = 0.00008769
    # tic_price = get_uptic_price(bid_price)
    tic_price = get_downtic_price(bid_price)
    print(format(bid_price, '.8f'), format(tic_price, '.8f'))

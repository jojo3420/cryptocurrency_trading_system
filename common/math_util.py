def get_uptic_price(price, tic=1):
    """
    주어진 가격에서 n틱 위의 가격
    :param price:
    :param tic: 1
    :return:
    """
    if not isinstance(price, str):
        price = str(price)
    if price.find('.') != -1:
        integer_str, decimal_str = price.split('.')
        decimal_part = int(decimal_str) + tic
        uptic_price = f'{integer_str}.{decimal_part}'
        return uptic_price


def get_downtic_price(price, tic=-1):
    """
    주어진 가격에서 n틱 아래의 가격
    기본틱: 1
    :param price:
    :param tic: -1
    :return:
    """
    if tic > 0:
        tic = tic * -1
    if not isinstance(price, str):
        price = str(price)
    if price.find('.') != -1:
        integer_str, decimal_str = price.split('.')
        decimal_part = int(decimal_str) + tic
        if decimal_part < 0:
            # TODO: 마이너스 틱 버그수정
            print(decimal_part)
            print(integer_str, decimal_str, tic)
            integer_part = int(integer_str)
            integer_part -= 1
            decimal_part = int(decimal_str) + tic
        else:
            downtic_price = f'{integer_str}.{decimal_part}'
            return downtic_price


if __name__ == '__main__':
    # price = '123.5123'
    # uptic_price = get_uptic_price(price, 30)
    # downtic_price = get_uptic_price(price, -20)
    # print(uptic_price)
    # print(downtic_price)

    price = '123.5'
    uptic_price = get_uptic_price(price, 15)
    downtic_price = get_downtic_price(price, -15)
    print(uptic_price)
    print(downtic_price)

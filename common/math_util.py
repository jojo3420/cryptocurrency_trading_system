def get_uptic_price(price: float, tic=1):
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
            else:
                break

        decimal_part = int(decimal_str) + tic
        uptic_price = f'{integer_str}.{middle_decimal_str}{decimal_part}'
        return float(uptic_price)


def get_downtic_price(price: float, tic=-1):
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

        decimal_part = int(decimal_str) + tic
        if decimal_part == -1:
            integer_part = int(integer_str) + tic
            uptic_price = f'{integer_part}.0'
        else:
            uptic_price = f'{integer_str}.{middle_decimal_str}{decimal_part}'
        return float(uptic_price)


if __name__ == '__main__':
    # bid_price = 0.00008769
    # bid_price = 0.00005410
    # bid_price = 0.00005413
    # tic_price_0 = get_uptic_price(bid_price, 0)
    # tic_price_1 = get_uptic_price(bid_price, 1)
    # tic_price_2 = get_uptic_price(bid_price, 2)
    # tic_price_3 = get_uptic_price(bid_price, 3)
    # print(format(bid_price, '.8f'), format(tic_price_0, '.8f'))
    # print(format(bid_price, '.8f'), format(tic_price_1, '.8f'))
    # print(format(bid_price, '.8f'), format(tic_price_2, '.8f'))
    # print(format(bid_price, '.8f'), format(tic_price_3, '.8f'))

    ask_price = 5.96900
    downtic_price = get_downtic_price(ask_price, -1)
    print(f'{ask_price:,.8f}, {downtic_price:,.8f}')
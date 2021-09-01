from volatility_breakthrough_trading import *
# import pybithumb


if __name__ == '__main__':
    print(get_my_coin_balance())
    # print(get_coin_bought_list())
    all_balance = bithumb.get_balance('ALL')
    print(all_balance)

    xlm_balance = bithumb.get_balance('XLM')
    total_coin, used_coin = get_my_coin_balance('XLM')
    print(xlm_balance)
    print(total_coin, used_coin)
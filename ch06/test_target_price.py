from volatility_breakthrough_trading import *
import pandas as pd
import pybithumb

if __name__ == '__main__':
    # buy_wish_list, _coin_ratio_list, _coin_r_list = get_buy_wish_list()
    # for i, sym in enumerate(buy_wish_list):
    #     R = calc_R(sym, _coin_r_list[i])
    #     print(f'R: {R}')
    #     target_price = calc_williams_R(sym, R)
    #     print(f'{sym} target: {target_price}')

    # row 생략 없이 출력
    pd.set_option('display.max_rows', None)
    # col 생략 없이 출력
    pd.set_option('display.max_columns', None)

    coins = ['BTC', 'XRP', 'ETH', 'EOS', 'XLM', 'ADA', 'LTC', 'BCH']
    sym = 'BTC'
    # for i in range(0, 20):
    #     # R = calc_R(sym, 0.5)
    #     # print(f'R: {R}')
    #     target_price = calc_williams_R(sym, 0.5)
    #     print(f'{sym} target_price: {target_price:,}')
    #     print('-'*100)
    #     time.sleep(10)

    # R = calc_R('BTC', 0.5)
    # print(f'R: {R}')
    # target_price = calc_williams_R('BTC', R)
    # print(target_price)

    ticker = 'BTC'
    prices = pybithumb.get_candlestick(ticker)
    print(prices.tail(10))

    open = 39434000
    high = 41680000
    low = 39000000
    R = 0.5
    target_price_1 = open + ((high - low) * R)
    print(target_price_1)

    print(calc_williams_R(ticker, R))

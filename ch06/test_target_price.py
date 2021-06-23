from volatility_breakthrough_trading import *
import pybithumb

if __name__ == '__main__':
    # buy_wish_list, _coin_ratio_list, _coin_r_list = get_buy_wish_list()
    # for i, sym in enumerate(buy_wish_list):
    #     R = calc_R(sym, _coin_r_list[i])
    #     print(f'R: {R}')
    #     target_price = calc_williams_R(sym, R)
    #     print(f'{sym} target: {target_price}')

    # coins = ['BTC', 'XRP', 'ETH', 'EOS', 'XLM', 'ADA', 'LTC', 'BCH']
    # for i, sym in enumerate(coins):
    #     R = calc_R(sym, 0.5)
    #     print(f'R: {R}')
    #     target_price = calc_williams_R(sym, R)
    #     print(f'{sym} target: {target_price:,}')
    #     print('-'*100)


    print('LTC 매수가: ', get_bought_price('LTC'))
    print('BCH 매수가: ', get_bought_price('BCH'))
    print('BTC 매수가: ', get_bought_price('BTC'))

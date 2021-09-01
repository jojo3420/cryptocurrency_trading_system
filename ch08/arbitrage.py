import time
import pyupbit

"""
코인마켓 매수 호가창 기준으로 
"""


target_list = []
btc_tickers = pyupbit.get_tickers(fiat='BTC')
btc_order_books = pyupbit.get_orderbook(btc_tickers)
# print(order_books)
for order_book in btc_order_books:
    # print(order_book)
    # {'market': 'BTC-ETH', 'timestamp': 1630421732690, 'total_ask_size': 39.68671099,
    # 'total_bid_size': 9.34726369,
    # 'orderbook_units': [
    # {'ask_price': 0.0718423, 'bid_price': 0.0713729, 'ask_size': 0.0121526, 'bid_size': 0.00734924},
    # {'ask_price': 0.07184524, 'bid_price': 0.07137, 'ask_size': 0.21, 'bid_size': 0.0619509},
    # {'ask_price': 0.07189508, 'bid_price': 0.07124, 'ask_size': 10.0, 'bid_size': 0.09787348},
    # {'ask_price': 0.07191876, 'bid_price': 0.0712325, 'ask_size': 0.7, 'bid_size': 0.60875447},
    # {'ask_price': 0.07196898, 'bid_price': 0.07123249, 'ask_size': 0.7, 'bid_size': 0.14441508},
    # {'ask_price': 0.072, 'bid_price': 0.07118196, 'ask_size': 23.20227555, 'bid_size': 0.7024251},
    # {'ask_price': 0.07202, 'bid_price': 0.07111, 'ask_size': 0.09773014, 'bid_size': 0.09754017},
    # {'ask_price': 0.0721, 'bid_price': 0.07098285, 'ask_size': 1.0, 'bid_size': 0.03691425},
    # {'ask_price': 0.072119, 'bid_price': 0.07098, 'ask_size': 0.05634084, 'bid_size': 0.09773014},
    # {'ask_price': 0.07212, 'bid_price': 0.07064329, 'ask_size': 0.3, 'bid_size': 1.0},
    # {'ask_price': 0.07215, 'bid_price': 0.07024, 'ask_size': 0.09751789, 'bid_size': 0.71006992},
    # {'ask_price': 0.07221682, 'bid_price': 0.07005469, 'ask_size': 0.4341931, 'bid_size': 0.07209045},
    # {'ask_price': 0.07224073, 'bid_price': 0.07, 'ask_size': 0.27864517, 'bid_size': 5.59563576},
    # {'ask_price': 0.07228, 'bid_price': 0.0697882, 'ask_size': 0.0978557, 'bid_size': 0.01339356},
    # {'ask_price': 0.0724, 'bid_price': 0.06977777, 'ask_size': 2.5, 'bid_size': 0.10112117}
    # ]}
    coin_market_symbol = order_book.get('market')
    ticker = coin_market_symbol.split('-')[1]
    print(ticker)
    coin_order_book_units = order_book.get('orderbook_units', [])
    if coin_order_book_units:
        low_ask_price = coin_order_book_units[0].get('ask_price', 0)
        print(f'BTC 기준 매도가: {format(low_ask_price, "f")}')
        curr_krw_btc_price = pyupbit.get_current_price(f'KRW-BTC')
        # print(f'비트코인 원화가격: {curr_krw_btc_price:,.0f}')
        coin_converted_krw_price = low_ask_price * curr_krw_btc_price
        print(f'비트코인 원화시세 기준 현재 매도가: {coin_converted_krw_price:,.0f}')
        krw_order_book = pyupbit.get_orderbook(f'KRW-{ticker}')
        if isinstance(krw_order_book, list):
            # print(krw_order_book)
            # [{'market': 'KRW-ETH', 'timestamp': 1630422175403, 'total_ask_size': 108.24908619,
            # 'total_bid_size': 201.77310278,
            # 'orderbook_units': [
            # {'ask_price': 3963000.0, 'bid_price': 3962000.0, 'ask_size': 18.99821452, 'bid_size': 12.53959125},
            # {'ask_price': 3964000.0, 'bid_price': 3961000.0, 'ask_size': 3.89873859, 'bid_size': 4.56883907},
            # {'ask_price': 3965000.0, 'bid_price': 3960000.0, 'ask_size': 0.78184111, 'bid_size': 3.62887362},
            # {'ask_price': 3966000.0, 'bid_price': 3959000.0, 'ask_size': 5.51413915, 'bid_size': 8.39771156},
            # {'ask_price': 3967000.0, 'bid_price': 3957000.0, 'ask_size': 26.65577002, 'bid_size': 1.30814517},
            # {'ask_price': 3968000.0, 'bid_price': 3956000.0, 'ask_size': 10.37357453, 'bid_size': 1.49143194}, {'ask_price': 3969000.0, 'bid_price': 3955000.0, 'ask_size': 6.77253356, 'bid_size': 122.52484254}, {'ask_price': 3970000.0, 'bid_price': 3954000.0, 'ask_size': 2.43605981, 'bid_size': 12.92693195}, {'ask_price': 3971000.0, 'bid_price': 3953000.0, 'ask_size': 15.54692088, 'bid_size': 0.26696178}, {'ask_price': 3972000.0, 'bid_price': 3952000.0, 'ask_size': 0.05469013, 'bid_size': 0.3}, {'ask_price': 3973000.0, 'bid_price': 3951000.0, 'ask_size': 7.46087116, 'bid_size': 0.50678907}, {'ask_price': 3974000.0, 'bid_price': 3950000.0, 'ask_size': 2.40872644, 'bid_size': 7.88643247}, {'ask_price': 3975000.0, 'bid_price': 3949000.0, 'ask_size': 6.04943099, 'bid_size': 20.47059308}, {'ask_price': 3976000.0, 'bid_price': 3948000.0, 'ask_size': 0.0621355, 'bid_size': 3.203}, {'ask_price': 3977000.0, 'bid_price': 3947000.0, 'ask_size': 1.2354398, 'bid_size': 1.75295928}]
            # }]
            krw_order_book = krw_order_book[0]
            krw_market = krw_order_book.get('market', '')
            krw_order_book_units = krw_order_book.get('orderbook_units', [])
            krw_bid_price = krw_order_book_units[0].get('bid_price')
            print(f'원화 매수호가: {krw_bid_price:,.0f}')
            yields = (krw_bid_price / coin_converted_krw_price - 1) * 100
            print(f'yields: {yields:.2f}')
            if abs(yields) > 5.0:
                target_list.append((ticker, yields))
    print('-' * 70)
    time.sleep(0.4)

print(target_list)

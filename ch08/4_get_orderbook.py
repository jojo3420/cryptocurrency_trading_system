import pyupbit

# 'KRW-BTC'
ticker = 'KRW-XRP'

orderbook: list = pyupbit.get_orderbook(ticker)
# print(orderbook)
bids_asks = orderbook[0]['orderbook_units']
print('호가창 갯수: ', len(bids_asks))  # 매수호가 15, 매도호가 15개
for bid_ask in bids_asks:
    # print(bid_ask)
    ask_price = bid_ask['ask_price']  # 매도호가
    ask_size = bid_ask['ask_size']    # 매도호가 수량
    bid_price = bid_ask['bid_price']  # 매수호가
    bid_size = bid_ask['bid_size']   # 매수호가 수량
    print(f'매수호가: {bid_price:,.0f} 매도호가: {ask_price:,.0f}')
    print(f'매수수량: {bid_size}, 매도수량: {ask_size}')
    print('-'*50)

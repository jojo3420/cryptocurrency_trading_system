import pyupbit

# 'KRW-BTC'
ticker = 'KRW-XRP'

orderbook: list = pyupbit.get_orderbook(ticker)
# print(orderbook)
bids_asks = orderbook[0]['orderbook_units']
print('호가창 갯수: ', len(bids_asks))  # 매수호가 15, 매도호가 15개
asks = []
bids = []
for bid_ask in bids_asks:
    # print(bid_ask)
    ask_price = bid_ask['ask_price']  # 매도호가
    ask_volume = bid_ask['ask_size']  # 매도호가 수량
    asks.append((ask_price, ask_volume))
    bid_price = bid_ask['bid_price']  # 매수호가
    bid_volume = bid_ask['bid_size']  # 매수호가 수량
    bids.append((bid_price, bid_volume))

for i in range(len(asks) - 1, -1, -1):
    # print(i)
    ask, volume = asks[i]
    print(f'매도호가: {ask:,.0f}, volume: {volume}')
print('-' * 150)
for bid, volume in bids:
    print(f'매수호가: {bid:,.0f}, volume: {volume}')

# print(asks)
# print(bids)
# return {'asks': asks, 'bids': bids}

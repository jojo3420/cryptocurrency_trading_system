from volatility_breakthrough_trading import *

"""
        1) 정상매도
        sell() => XRP 2.0개
        매도 주문 요청, order_desc: ('ask', 'XRP', 'C0106000000241177536', 'KRW')


        2) 매도실패 - 보유수랑 없음
        매도 주문 요청,  order_desc: {'status': '5500', 'message': 'Invalid Parameter'}
        체결된 주문 내역 조회 실패 => 'NoneType' object is not subscriptable
        sell() 예외발생! e =>cannot unpack non-iterable NoneType object
"""
ticker = 'KLAY'
total_qty, used_qty = get_coin_quantity(ticker)
sell(ticker, total_qty-used_qty)


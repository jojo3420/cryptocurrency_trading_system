from common.utils import *
from common.bithumb_api import *

# 매도
bit_keys: dict = read_bithumb_key('.env.local')
secretKey, connectKey = tuple(bit_keys.values())
bithumb = pybithumb.Bithumb(connectKey, secretKey)




# total_coin_q, sell_use = get_balance_coin('XLM')
# sell_limit_price('XLM', 400, total_coin_q - sell_use)

order_info = sell_market_price('XLM', 5)
print(order_info)
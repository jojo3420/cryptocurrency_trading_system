
from common.utils import *
from common.bithumb_api import *

print(bithumb.get_balance('DOGE'))

quantity = get_balance_coin('DOGE')
print(quantity)
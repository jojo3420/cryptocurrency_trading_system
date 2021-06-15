
from common.utils import *
from common.bithumb_api import *

print(bithumb.get_balance('DOGE'))

quantity = get_coin_quantity('DOGE')
print(quantity)
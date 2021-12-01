import time
import unittest
from upbit_helper import UpbitHelper
import pyupbit


class CancelTest(unittest.TestCase):
    def setUp(self, api=None) -> None:
        self.api = UpbitHelper()
        self.ticker = 'KRW-XRP'
        self.qty = 10
        _, balance, locked = self.api.get_cash_balance()
        print(f'balance: {balance:,.0f}원')
        self.assertTrue(balance > 0)

    def testCancel(self):
        current_price = pyupbit.get_current_price(self.ticker)
        # print(current_price)
        entry_price = current_price // 2
        ret = self.api.buy(self.ticker, self.qty, entry_price)
        # print(ret)
        self.assertIsNotNone(ret)
        time.sleep(1)
        self.assertTrue(self.api.order_cancel(ret.get('uuid')))


if __name__ == '__main__':
    unittest.main()

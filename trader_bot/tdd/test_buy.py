import unittest

import pyupbit

from upbit_helper import UpbitHelper


class BuyTest(unittest.TestCase):
    def setUp(self, api=None) -> None:
        self.api = UpbitHelper(tdd_mode=True)
        self.ticker = 'KRW-ADA'
        self.qty = 10
        _, balance, locked = self.api.get_cash_balance()
        # print(f'balance: {balance:,.0f}원')
        self.assertTrue(balance > 5000)

    def testBuy(self):
        curr_price = pyupbit.get_current_price(self.ticker)
        entry_price = curr_price - int(curr_price // 2)
        ret = self.api.buy(self.ticker, self.qty, entry_price)
        self.assertIsNotNone(ret)
        # print(ret)
        self.assertTrue(self.api.order_cancel(ret.get('uuid')))

    def testCurrentPriceBuy(self):
        curr_price = pyupbit.get_current_price(self.ticker)
        entry_order_price = self.api.buy_current_price(self.ticker, self.qty)
        self.assertEqual(curr_price, entry_order_price)


if __name__ == '__main__':
    unittest.main()

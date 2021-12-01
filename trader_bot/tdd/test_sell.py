import unittest
from upbit_helper import UpbitHelper


class SellTest(unittest.TestCase):
    def setUp(self, api=None) -> None:
        self.api = UpbitHelper()
        self.ticker = 'KRW-ADA'

    def testSell(self):
        pass

    def testSellIoc(self):
        _, qty, locked = self.api.get_coin_balance(self.ticker)
        self.assertTrue(qty > 0)
        # self.api.sell_ioc(self.ticker, qty)

    def testSaveSellHistory(self):
        pass
        # self.api.sell

    def testSellAll(self):
        pass


if __name__ == '__main__':
    unittest.main()

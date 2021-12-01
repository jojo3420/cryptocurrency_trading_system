import unittest
from upbit_helper import UpbitHelper


class GetBalanceTest(unittest.TestCase):
    def setUp(self, api=None) -> None:
        # self.api = api
        self.api = UpbitHelper()

    def testGetCashBalance(self):
        balance = self.api.get_cash_balance()
        self.assertTrue(isinstance(balance, tuple))
        ticker, qty, locked_qty = balance
        print(balance)
        self.assertTrue(isinstance(ticker, str))
        self.assertTrue(isinstance(qty, int))
        self.assertTrue(isinstance(locked_qty, int))

    def testGetCoinBalance(self):
        balance = self.api.get_coin_balance('ADA')
        self.assertTrue(isinstance(balance, tuple))
        ticker, qty, locked_qty = balance
        print(balance)
        self.assertTrue(isinstance(ticker, str))
        self.assertTrue(isinstance(qty, float))
        self.assertTrue(isinstance(locked_qty, float))

    def testGetCoinBalances(self):
        balance_list = self.api.get_coin_balances()
        self.assertTrue(isinstance(balance_list, list))
        for balance in balance_list:
            self.assertTrue(isinstance(balance, tuple))


if __name__ == '__main__':
    unittest.main()

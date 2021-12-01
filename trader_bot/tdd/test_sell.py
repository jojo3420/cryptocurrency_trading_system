import unittest
from upbit_helper import UpbitHelper


class SellTest(unittest.TestCase):
    def setUp(self, api=None) -> None:
        self.api = UpbitHelper()

    def testSell(self):
        pass

    def testSaveSellHistory(self):
        pass


if __name__ == '__main__':
    unittest.main()

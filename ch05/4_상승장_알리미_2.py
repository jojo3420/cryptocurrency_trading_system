import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from pybithumb import Bithumb
from pandas import DataFrame

form_class = uic.loadUiType("bull.ui")[0]


class MyWindow(QMainWindow, form_class):
    tickers = ["BTC", "ETH", "BCH", "ETC"]

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('상승장 알리미')

        timer = QTimer(self)
        timer.start(5000)  # 5second
        timer.timeout.connect(self.handle_timeout)

    def moving_average_by(self, ticker: str, days: int = 5) -> DataFrame:
        """ 특정 이동평균 구해진 DataFrame 리턴

        6-13일 MA3: 11, 12, 13일 close
        ( 2724000.0 + 2811000.0 + 2840000.0 ) / 3

        2021-06-09 00:00:00, close: 2840000.0, MA3: 2941000.0
        2021-06-10 00:00:00, close: 2919000.0, MA3: 2842666.6666666665
        2021-06-11 00:00:00, close: 2840000.0, MA3: 2866333.3333333335
        2021-06-12 00:00:00, close: 2811000.0, MA3: 2856666.6666666665
        2021-06-13 16:00:00, close: 2724000.0, MA3: 2791666.6666666665
        """

        prices: DataFrame = Bithumb.get_candlestick(ticker)
        close = prices['close']
        MA = close.rolling(days).mean()
        prices[f'MA{days}'] = MA
        prices = prices.dropna()
        return prices

    def market_info(self, ticker: str, days: int = 5) -> tuple:
        is_bull = '하락장'
        df = self.moving_average_by(ticker, days)
        MA = df['close'].rolling(window=days).mean()
        current_price = Bithumb.get_current_price(ticker)
        prev_ma = MA[-2]
        if current_price > prev_ma:
            is_bull = '상승장'

        return current_price, prev_ma, is_bull

    def handle_timeout(self):
        # print('5초 인터벌')
        for i, ticker in enumerate(self.tickers):
            ticker_item = QTableWidgetItem(ticker)

            _price, MA3, is_bull_3 = self.market_info(ticker, 3)
            price, MA5, is_bull_5 = self.market_info(ticker, 5)

            price_item = QTableWidgetItem(f'{int(price):,}')
            ma3_item = QTableWidgetItem(f'{int(MA3):,}')
            is_bull_3_item = QTableWidgetItem(is_bull_3)
            ma5_item = QTableWidgetItem(f'{int(MA5):,}')
            is_bull_5_item = QTableWidgetItem(is_bull_5)

            self.tableWidget.setItem(i, 0, ticker_item)
            self.tableWidget.setItem(i, 1, price_item)
            self.tableWidget.setItem(i, 2, ma3_item)
            self.tableWidget.setItem(i, 3, is_bull_3_item)
            self.tableWidget.setItem(i, 4, ma5_item)
            self.tableWidget.setItem(i, 5, is_bull_5_item)





app = QApplication(sys.argv)
win = MyWindow()
win.show()
app.exec_()

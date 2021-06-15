import sys
import traceback

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from pybithumb import Bithumb
from pandas import DataFrame

tickers = ["BTC", "ETH", "BCH", "ETC"]


def get_market_info(ticker: str, days: int = 5) -> tuple:
    try:
        is_bull = '하락장'
        df = moving_average_by(ticker, days)
        MA = df['close'].rolling(window=days).mean()
        current_price = Bithumb.get_current_price(ticker)
        prev_ma = MA[-2]
        if current_price > prev_ma:
            is_bull = '상승장'

        return current_price, prev_ma, is_bull
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        return None, None, None


def moving_average_by(ticker: str, days: int = 5) -> DataFrame:
    """ 이돌평균 구하기 """
    try:
        prices: DataFrame = Bithumb.get_candlestick(ticker)
        close = prices['close']
        MA = close.rolling(days).mean()
        prices[f'MA{days}'] = MA
        prices = prices.dropna()
        return prices
    except Exception as e:
        print(str(e))
        traceback.print_exc()


# 사용자 정의 쓰레드 class
class Worker(QThread):
    # 사용자 정의 시그널 정의
    fetch_finished = pyqtSignal(dict)

    # 오버라이딩
    def run(self):
        while True:
            data = {}
            for ticker in tickers:
                ma3_data: set = get_market_info(ticker, 3)
                ma5_data: set = get_market_info(ticker, 5)
                # print(ma5_data)
                data[ticker] = ma3_data + ma5_data[1:]

            # print(data)
            self.fetch_finished.emit(data)  # emit(event) 발생
            self.msleep(500)  # 0.5초


form_class = uic.loadUiType("bull.ui")[0]


class MyWindow(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('상승장 알리미')

        self.worker = Worker()
        self.worker.fetch_finished.connect(self.update_table_widget)
        self.worker.start()

    @pyqtSlot(dict)
    def update_table_widget(self, data: dict):
        print('refresh')
        try:
            for i, ticker in enumerate(tickers):

                # get data
                price, ma3, is_bull_3, ma5, is_bull_5 = data[ticker]

                # create widget item
                ticker_item = QTableWidgetItem(ticker)
                price_item = QTableWidgetItem(f'{int(price):,}')
                ma3_item = QTableWidgetItem(f'{int(ma3):,}')
                bull_item_3 = QTableWidgetItem(is_bull_3)
                ma5_item = QTableWidgetItem(f'{int(ma5):,}')
                bull_item_5 = QTableWidgetItem(is_bull_5)

                # set(행, 열, item)
                self.tableWidget.setItem(i, 0, ticker_item)
                self.tableWidget.setItem(i, 1, price_item)
                self.tableWidget.setItem(i, 2, ma3_item)
                self.tableWidget.setItem(i, 3, bull_item_3)
                self.tableWidget.setItem(i, 4, ma5_item)
                self.tableWidget.setItem(i, 5, bull_item_5)

        except Exception as e:
            print(str(e))
            traceback.print_exc()


app = QApplication(sys.argv)
win = MyWindow()
win.show()
app.exec_()

import sys
import time
import traceback
import pybithumb
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from ch06.volatility_breakthrough_trading import calc_moving_average_by, calc_williams_R, find_bull_market_list


def get_bithumb_market_info(ticker: str, days: int = 5) -> tuple:
    try:
        is_bull = '하락장'
        volatility = ''
        MA = calc_moving_average_by(ticker, days)
        current_price = pybithumb.get_current_price(ticker)
        if current_price > MA:
            is_bull = '상승장'

        target_price = calc_williams_R(ticker, 0.2)
        if current_price > target_price:
            volatility = '돌파'
        return current_price, MA, is_bull, target_price, volatility
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        return None, None, None, None, None


# 사용자 정의 쓰레드 class
class Worker(QThread):
    # 사용자 정의 시그널 정의
    fetch_finished = pyqtSignal(dict)

    # 오버라이딩
    def run(self):
        while True:
            data = {}
            for ticker in bull_tickers:
                ma3_data: set = get_bithumb_market_info(ticker, 3)
                ma5_data: set = get_bithumb_market_info(ticker, 5)
                # (current_price, prev_ma, is_bull,  target_price, volatility)
                data[ticker] = ma3_data[0: -2] + ma5_data[1:]
            # print(data)
            self.fetch_finished.emit(data)  # emit(event) 발생
            self.msleep(500)  # 0.5초


form_class = uic.loadUiType('bull.ui')[0]


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
        # print('refresh')
        try:
            for i, ticker in enumerate(bull_tickers):
                # get data
                price, ma3, is_bull_3, ma5, is_bull_5, target_price, volatility = data[ticker]

                # create widget item
                ticker_item = QTableWidgetItem(ticker)
                price_item = QTableWidgetItem(f'{int(price):,}')
                ma3_item = QTableWidgetItem(f'{int(ma3):,}')
                bull_item_3 = QTableWidgetItem(is_bull_3)
                ma5_item = QTableWidgetItem(f'{int(ma5):,}')
                bull_item_5 = QTableWidgetItem(is_bull_5)
                target_price_item = QTableWidgetItem(f'{int(target_price):,}')
                volatility_item = QTableWidgetItem(volatility)

                # set(행, 열, item)
                self.tableWidget.setItem(i, 0, ticker_item)
                self.tableWidget.setItem(i, 1, price_item)
                self.tableWidget.setItem(i, 2, ma3_item)
                self.tableWidget.setItem(i, 3, bull_item_3)
                self.tableWidget.setItem(i, 4, ma5_item)
                self.tableWidget.setItem(i, 5, bull_item_5)
                self.tableWidget.setItem(i, 6, target_price_item)
                self.tableWidget.setItem(i, 7, volatility_item)

        except Exception as e:
            print(str(e))
            traceback.print_exc()


if __name__ == '__main__':
    bull_tickers = find_bull_market_list()
    # print(bull_tickers)
    # 현재 상승장인 코인 목록 저장하기
    # update_coin_buy_wish_list()

    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    app.exec_()

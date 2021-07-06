import sys
import time
import traceback
import pybithumb
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from pandas import DataFrame
import threading
from ch06.volatility_breakthrough_trading import calc_moving_average_by, calc_williams_R, calc_R, \
    calc_fix_moving_average_by, calc_fix_noise_ma_by, get_current_noise, calc_prev_ma_volume, calc_fix_noise_ma_by

# tickers = ["BTC", "ETH", "BCH", "ETC", 'XRP', 'BNB', 'DOGE', 'KLAY']
from common.bithumb_api import save_bull_coin


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


def find_bull_market_list() -> list:
    _list = []
    for ticker in pybithumb.get_tickers():
        try:
            curr_price = pybithumb.get_current_price(ticker)
            R = calc_R(ticker, 0.5)
            target_price = calc_williams_R(ticker, R)
            MA3 = calc_fix_moving_average_by(ticker, 3)
            MA5 = calc_fix_moving_average_by(ticker, 5)
            curr_noise = get_current_noise(ticker)
            noise_ma3 = calc_fix_noise_ma_by(ticker, 3)
            noise_ma5 = calc_fix_noise_ma_by(ticker, 5)
            # volume = calc_prev_ma_volume()
            if curr_price > MA3 and curr_price > MA5 \
                    and curr_price > target_price and curr_noise <= 0.4 \
                    and noise_ma3 < 0.6 and noise_ma5 < 0.6:
                print(f'이동평균 3,5 상승 변동성 돌파 및 노이즈 필터링 통과 =>  상승코인: {ticker}')
                _list.append(ticker)
        except Exception as E:
            print(str(E))
            pass

    return _list


class FindBullCoinWorker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        while True:
            _bull_tickers = find_bull_market_list()
            print(_bull_tickers)
            save_bull_coin(_bull_tickers)
            time.sleep(1 * 60 * 60)


if __name__ == '__main__':
    FindBullCoinWorker().start()

    bull_tickers = find_bull_market_list()
    print(bull_tickers)
    # 현재 상승장인 코인 목록 저장하기
    # update_coin_buy_wish_list()

    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    app.exec_()

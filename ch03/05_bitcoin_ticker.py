import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pykorbit


form_class = uic.loadUiType("mainwindow_bitcon.ui")[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('코빗 시세 조회 알림미')
        self.pushButton.clicked.connect(self.handle_btc_curr_price)

        self.timer = QTimer(self)
        self.timer.start(5000) # inveral: 1 초
        self.timer.timeout.connect(self.handle_timer)

    def handle_btc_curr_price(self):
        price = pykorbit.get_current_price('BTC')
        self.lineEdit.setText(str(price))


    def handle_timer(self):
        cur_time = QTime.currentTime()
        str_time = cur_time.toString('hh:mm:ss')
        self.statusBar().showMessage(str_time)

        self.handle_btc_curr_price()

app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()

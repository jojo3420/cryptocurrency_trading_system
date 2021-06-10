import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MyClickSignal(QObject):
    click_signal = pyqtSignal()  # 클래스 변수

    def run(self):
        self.click_signal.emit()  # 시그널(이벤트) 발생


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        my_click_signal = MyClickSignal()
        my_click_signal.click_signal.connect(self.handle_click)
        my_click_signal.run()

    @pyqtSlot()
    def handle_click(self):
        print('custom click signal')


app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()
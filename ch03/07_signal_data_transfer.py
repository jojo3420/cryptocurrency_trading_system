import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MySignal(QObject):
    signal1 = pyqtSignal()
    signal2 = pyqtSignal(int, int)

    def run(self):
        self.signal1.emit()  # send no data to MyWindow
        self.signal2.emit(1, 2)  # send data to MyWindow


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        mysignal = MySignal()
        # 시그널(이벤트) 발생!
        mysignal.signal1.connect(self.signal1_emitted)
        mysignal.signal2.connect(self.signal2_emitted)
        mysignal.run()

    @pyqtSlot()
    def signal1_emitted(self):
        print('signal1 emitted!')

    @pyqtSlot(int, int)
    def signal2_emitted(self, val1, val2):
        print('signal2 emitted!', val1, val2)


app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()

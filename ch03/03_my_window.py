import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 200, 300, 500)
        self.setWindowTitle('PyQt')
        self.setWindowIcon(QIcon('icon.png'))

        btn1 = QPushButton('버튼1', self)
        btn1.move(10, 10)
        btn1.clicked.connect(self.btn_cliekced_1)

        btn2 = QPushButton('버튼2', self)
        btn2.move(10, 40)
        btn2.clicked.connect(self.btn_cliekced_2)

    def btn_cliekced_1(self):
        print('버튼1 클릭')

    def btn_cliekced_2(self): 
        print('버튼2 클릭')


app = QApplication(sys.argv)
window = MyWindow()
window.show()

app.exec_()

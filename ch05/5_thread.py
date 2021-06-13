from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys


class Worker(QThread):
    def run(self):
        while True:
            print('hi?')
            self.sleep(1)  # 1 second



class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.worker = Worker()
        self.worker.run()






app = QApplication(sys.argv)
mywindow = MyWindow()
mywindow.show()


app.exec_()


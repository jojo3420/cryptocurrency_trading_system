import sys
from PyQt5.QtWidgets import *

app = QApplication(sys.argv)
label = QLabel('Hello')
label.show()

# 이벤트 루프 실행!
app.exec_()

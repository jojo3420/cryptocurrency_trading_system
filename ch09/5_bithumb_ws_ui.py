import json
import websockets
import asyncio
import multiprocessing as mp
import sys
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


async def bithumb_ws_client(que):
    uri = "wss://pubwss.bithumb.com/pub/ws"

    async with websockets.connect(uri, ping_interval=None) as socket:
        subscribe_format = {
            'type': 'ticker',
            'symbols': ['BTC_KRW'],
            'tickTypes': ['1H']
        }
        param = json.dumps(subscribe_format)
        await socket.send(param)

        while True:
            raw: 'json' = await socket.recv()  # receive from ws
            data: dict = json.loads(raw)
            # print('소켓에서 받은 데이터', data)
            que.put(data)  # 큐에 데이터 바인딩


async def main(que):
    await bithumb_ws_client(que)


def fetch_producer(que):
    asyncio.run(main(que))


class DataFetchThread(QThread):
    """
    메인윈도우(UI) 에서 데이터 fetch 전용 쓰레드
    다른 프로세스(fetch_producer)가 websocket 통신을 통해 빗썸 서버에서
    실시간 거래 시세 데이터 구독

    queue 통해 데이터 가져오기
    """
    poped = pyqtSignal(dict)  # signal

    def __init__(self, que):
        super().__init__()
        self.que = que

    def run(self):
        while True:
            if not self.que.empty():
                data = self.que.get()  # 큐에서 데이터 pop
                # print('Fetch Thread:', data)
                self.poped.emit(data)  # 시그널 emit: 메인Window 전달!


class MyWindow(QMainWindow):
    def __init__(self, que):
        super().__init__()
        self.setGeometry(200, 200, 400, 200)
        self.setWindowTitle('Bithumb Websocket with PyQT')

        # Sub Thread(data fetch)
        self.data_fetch_t1 = DataFetchThread(que)
        self.data_fetch_t1.poped.connect(self.print_data)  # 시그널 연결
        self.data_fetch_t1.start()

        # widget
        self.label = QLabel('Bitcoin ', self)
        self.label.move(10, 10)

        # QLineEdit
        self.line_edit = QLineEdit(' ', self)
        self.line_edit.resize(150, 30)
        self.line_edit.move(100, 10)

    @pyqtSlot(dict)
    def print_data(self, data):
        content: dict = data.get('content')
        if content:
            current_price = int(content.get('closePrice'))
            self.line_edit.setText(format(current_price, ',d'))

        now_tm = datetime.now()
        str_now = now_tm.strftime('%Y-%m-%d %H:%m:%S')
        self.statusBar().showMessage(str_now)


if __name__ == '__main__':
    # Sub Process(Data Fetch)
    q = mp.Queue()  # 프로세스 간의 데이터 주고받음 자료구조
    sub_process = mp.Process(name="fetch_producer", target=fetch_producer, args=(q,), daemon=True)
    sub_process.start()

    # Main process
    app = QApplication(sys.argv)
    my_window = MyWindow(que=q)
    my_window.show()
    app.exec_()

import threading
import time


class Worker(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name  # thread 이름 지정
        self.daemon = True

    def run(self):
        print("sub thread start ", threading.currentThread().getName())
        self.hi()
        time.sleep(3)
        print("sub thread end ", threading.currentThread().getName())

    def hi(self):
        print('hi')


if __name__ == '__main__':
    """
    참조: https://wikidocs.net/82581
    """
    print('main thread start')
    t1 = Worker('t1')
    # t1.daemon = True  # 데몬 스레드로 생성
    t1.start()  # 스레드 run()메서드 실행

    # for i in range(10):
    i = 0
    while i < 10:
        print(i)
        # time.sleep(1)
        i += 1

    print('main thread end')

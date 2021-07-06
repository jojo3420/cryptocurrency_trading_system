import time
from multiprocessing import Process, Queue


def worker(id, start, end, result):
    total = 0
    for i in range(start, end):
        print(f'{id}: {i} ')
        total += i
        time.sleep(0.1)
    result.put(total)
    return


def process_1(name, start, end):
    for i in range(start, end):
        print(f'{name} {i}')
        time.sleep(0.1)




if __name__ == "__main__":
    # START, END = 0, 1000
    # result = Queue()
    # t1 = Process(target=worker, args=('t1', START, END // 2, result))
    # t2 = Process(target=worker, args=('t2', END // 2, END, result))
    #
    # t1.start()
    # t2.start()
    # t1.join()  # 자식 프로세스(쓰레드) 종료전까지 메인쓰레드는 기달린다.
    # t2.join()
    # result.put('STOP')
    # total = 0
    # while True:
    #     tmp = result.get()
    #     if tmp == 'STOP':
    #         break
    #     else:
    #         print(f'main: {tmp}')
    #         total += tmp
    #
    # print(f'Result: {total}')



    start, end, i = 0, 1000, 0
    p1 = Process(target=process_1, args=('p1', start, end // 2))
    p2 = Process(target=process_1, args=('p2', end // 2, end))
    p1.start()
    p2.start()
    while i < 1000:
        print(f'main: {i}')
        i += 1
        time.sleep(0.1)

import multiprocessing as mp
import time


def worker():
    proc = mp.current_process()
    print(proc.name)
    print(proc.pid)
    for i in range(0, 5):
        print(i)
        time.sleep(1)
    print('SubProcess End')


if __name__ == '__main__':
    proc = mp.current_process()
    print(proc.name)
    print(proc.pid)

    # 서브 프로세스 생성(스포닝)
    sub_proc = mp.Process(name="subProcess", target=worker)
    sub_proc.start()

    print('Main Process End')

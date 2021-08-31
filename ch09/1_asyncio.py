import asyncio


# 동기적 함수
def sync_func1():
    print('hello')


def sync_func2():
    print('world')


sync_func1()
sync_func2()


async def async_func1():
    print('hi?')


# async_func1()  #  비동기 함수는 이벤트 루프가 호출하여 처리하게 해야함

# 코루틴(비동기함수)의 실행에는 항상 이벤트 루프가 필요하다는 점 기억!
# asyncio.run(async_func1())  # 고수준 이벤트 함수

# 이벤트 루프 직접 생성
event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(async_func1())
event_loop.close()

import asyncio


async def grind_coffee_beans(beans):
    print('원두 갈기 시작', beans)
    await asyncio.sleep(3)


async def make_americano():
    print('Americano 제조 시작')
    await grind_coffee_beans(3)
    await asyncio.sleep(3)
    print('Americano 제조 완료')
    return '아메리카노'


async def make_latte():
    print('커피라떼 만들기')
    await grind_coffee_beans(2)
    await asyncio.sleep(3)
    print('우유 마무리')
    await asyncio.sleep(2)
    print('라떼 완성')
    return '카페라떼'


async def main():
    coro1 = make_americano()
    coro2 = make_latte()
    coffees = await asyncio.gather(coro1, coro2)
    print(coffees)

print('Main start')
asyncio.run(main())
print('Main End')
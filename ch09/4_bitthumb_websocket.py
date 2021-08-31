import websockets
import asyncio
import json


async def bithumb_ws_client():
    uri = 'wss://pubwss.bithumb.com/pub/ws'
    async with websockets.connect(uri, ping_interval=None) as socket:
        response = await socket.recv()
        print(response)

        subscribe_fmt = {
            'type': 'ticker',
            'symbols': ['BTC_KRW', 'ETH_KRW'],
            'tickTypes': ['30M']
        }
        subscribe_json = json.dumps(subscribe_fmt)
        await socket.send(subscribe_json)

        while True:
            raw_data: 'json' = await socket.recv()
            # print(raw_data)
            data: dict = json.loads(raw_data)
            # print(isinstance(data, dict))
            print(data)


async def main():
    await bithumb_ws_client()


asyncio.run(main())
# asyncio.run(bithumb_ws_client())

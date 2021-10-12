import asyncio
from threading import Thread, Lock
import aioredis
import async_timeout


redis = aioredis.from_url("redis://localhost")
pubsub = redis.pubsub()

async def event_stream():
    print("Running Event Stream")
    count = 0
    while True:
        count += 1
        await asyncio.sleep(1)
        try:
            async with async_timeout.timeout(0.1):
                print(f'pub: {count}')
                await redis.publish('channel:1', f'{count}')
        except asyncio.TimeoutError:
            print('TIMEOUT on publish event')
            pass 

def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()

def start():
    loop1 = asyncio.new_event_loop()
    t1 = Thread(target=start_background_loop, args=(loop1,))
    t1.start()

    asyncio.run_coroutine_threadsafe(event_stream(), loop1)

    loop1.stop()


if __name__ == '__main__':
    start()
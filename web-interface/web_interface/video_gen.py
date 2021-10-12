from imutils.video import VideoStream
import cv2
import asyncio
from threading import Thread, Lock
import aioredis
import async_timeout


vs = VideoStream(src=0).start()
redis = aioredis.from_url("redis://localhost")
pubsub = redis.pubsub()

async def event_stream():
    print("Running Event Stream")
    count = 0
    while True:
        count += 1
        await asyncio.sleep(0.05)
        try:
            async with async_timeout.timeout(0.1):
                print(f'pub: {count}')
                await redis.publish('channel:1', count)
        except asyncio.TimeoutError:
            print('TIMEOUT on publish event')
            pass 

async def video_stream():
    while True:
        frame = vs.read()
        r, jpg = cv2.imencode('.jpg', frame)
        await redis.set('video', jpg.tobytes())

def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()

def start():
    loop = asyncio.get_event_loop()
    loop.create_task(video_stream())
    loop.create_task(event_stream())
    loop.run_forever()

if __name__ == '__main__':
    start()
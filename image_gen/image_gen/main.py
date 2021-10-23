from imutils.video import VideoStream
import cv2
import asyncio
from threading import Thread, Lock
import aioredis
import async_timeout
import aioamqp
import signal
import functools

vs = VideoStream(src=0).start()
redis = aioredis.from_url("redis://localhost")
pubsub = redis.pubsub()

async def callback(ch, body, envelope, properties):
    print(f"recv: {body}")
    await redis.publish('channel:1', body)

async def event_stream():
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()
    await channel.basic_consume(callback, queue_name="state", no_ack=True)

async def video_stream():
    while True:
        frame = vs.read()
        r, jpg = cv2.imencode('.jpg', frame)
        await redis.set('video', jpg.tobytes())

def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()

def stopper(signame, loop):
    print(f'got {signame}, stopping..')
    loop.stop()

def start():
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), functools.partial(stopper, signame, loop))
    loop.create_task(video_stream())
    loop.create_task(event_stream())
    loop.run_forever()

if __name__ == '__main__':
    start()

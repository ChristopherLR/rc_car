from imutils.video import VideoStream
import cv2
import asyncio
from threading import Thread, Lock
import aioredis
import async_timeout
import aioamqp
import signal
import functools
import numpy as np
import json
import time

vs = VideoStream(src=0).start()
redis = aioredis.from_url("redis://localhost")
pubsub = redis.pubsub()
global target
target = None

async def callback(ch, body, envelope, properties):
    print(f"recv: {body}")
    await redis.publish('channel:1', body)

async def event_stream():
    print('starting event stream')
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()
    await channel.basic_consume(callback, queue_name="state", no_ack=True)

async def target_stream():
    global target
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()
    while True:
        if target != None:
            await channel.basic_publish(
                    payload=json.dumps(target),
                    exchange_name='amq.topic',
                    routing_key='target.position'
            )
            x, y = target
            await redis.publish('channel:1', f'Target Position {x}, {y}')
            print(f'pub {target}')
        else:
            await channel.basic_publish(
                    payload=json.dumps((-1, -1)),
                    exchange_name='amq.topic',
                    routing_key='target.position'
            )

        await asyncio.sleep(0.5)

async def video_stream():
    lowerBound=np.array([33,80,40])
    upperBound=np.array([102,255,255])
    print('starting video stream')
    while True:
        frame = vs.read()
        frame=cv2.resize(frame,(340,220))
        imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(imgHSV, lowerBound, upperBound)
        kernelOpen = np.ones((5,5))
        kernelClose = np.ones((20,20))
        maskOpen = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
        maskClose = cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
        maskFinal=maskClose
        conts,h=cv2.findContours(maskFinal,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        if len(conts) > 0:
            M = cv2.moments(conts[0])
            global target
            target = (round(M['m10'] / M['m00']), round(M['m01'] / M['m00']))
            cv2.circle(frame, target, 5, (0, 255, 0), -1)
        else:
            target = None
        cv2.drawContours(frame,conts,-1,(255,0,0),3)

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
    loop.create_task(target_stream())
    loop.run_forever()

if __name__ == '__main__':
    start()

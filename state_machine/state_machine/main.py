#!/usr/bin/env python
import sys, os
from dataclasses import dataclass
from enum import Enum
import aioamqp
import asyncio
import functools
import signal
import json
import time

class Direction(Enum):
    forward = 'forward'
    reverse = 'reverse'
    left = 'left'
    stop = 'stop'
    right = 'right'

@dataclass
class MotorState:
    direction: Direction
    throttle: float
    autonomous: bool = False

MOTOR_STATE = MotorState(Direction.stop, 0, False)

async def setup_queues():
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()
    await channel.queue_declare(queue_name='motor_state', durable=True)
    await channel.queue_bind(exchange_name="amq.topic", queue_name="motor_state", routing_key="motor.state")
    await channel.queue_declare(queue_name='state', durable=True)
    await channel.queue_bind(exchange_name="amq.topic", queue_name="state", routing_key="*.state")
    await channel.queue_declare(queue_name='target', durable=True)
    await channel.queue_bind(exchange_name="amq.topic", queue_name="target", routing_key="target.*")

async def ui_cb(ch, body, envelope, properties):
    print("Received %r" % body)
    msg = json.loads(body)
    if msg['direction'] == 'auto_on': MOTOR_STATE.autonomous = True
    if msg['direction'] == 'auto_off': MOTOR_STATE.autonomous = False
    if MOTOR_STATE.autonomous == False or msg['direction'] == "stop":
        await ch.basic_publish(
            payload=body,
            exchange_name='amq.topic',
            routing_key='motor.state'
        )

async def target_cb(ch, body, envelope, properties):
    print("Received %r" % body)
    target = json.loads(body)
    [x, y] = target
    if MOTOR_STATE.autonomous:
        msg = None
        if x < 0:
            msg = {'direction': 'stop', 'throttle': 0, 'ts': int(time.time()) }
        elif x < 100:
            print('l')
            msg = {'direction': 'left', 'throttle': 50, 'ts': int(time.time()) }
        elif x > 200:
            print('r')
            msg = {'direction': 'right', 'throttle': 50, 'ts': int(time.time()) }
        else:
            print('s')
            msg = {'direction': 'forward', 'throttle': 30, 'ts': int(time.time()) }
        await ch.basic_publish(
            payload=json.dumps(msg),
            exchange_name='amq.topic',
            routing_key='motor.state'
        )

async def ui_stream():
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()
    await channel.queue_declare(queue_name='ui_commands')
    print('UI Stream Started')
    await channel.basic_consume(ui_cb, queue_name="ui_commands", no_ack=True)

async def target_stream():
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()
    print('Target Stream Started')
    await channel.basic_consume(target_cb, queue_name="target", no_ack=True)

async def state_publish():
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()
    print('State Publish Started')
    while True:
        await channel.basic_consume(ui_cb, queue_name="ui_commands", no_ack=False)

def stopper(signame, loop):
    print("Got %s, stopping..." % signame)
    loop.stop()

def start():
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), functools.partial(stopper, signame, loop))

    loop.create_task(setup_queues())
    loop.create_task(ui_stream())
    loop.create_task(target_stream())
    loop.run_forever()

if __name__ == '__main__':
    start()

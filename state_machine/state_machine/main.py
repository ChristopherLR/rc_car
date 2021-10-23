#!/usr/bin/env python
import sys, os
from dataclasses import dataclass
from enum import Enum
import aioamqp
import asyncio
import functools
import signal

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

MOTOR_STATE = MotorState(Direction.stop, 0)

async def setup_queues():
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()
    await channel.queue_declare(queue_name='motor_state', durable=True)
    await channel.queue_bind(exchange_name="amq.topic", queue_name="motor_state", routing_key="motor.state")
    await channel.queue_declare(queue_name='state', durable=True)
    await channel.queue_bind(exchange_name="amq.topic", queue_name="state", routing_key="*.state")

async def ui_cb(ch, body, envelope, properties):
    print("Received %r" % body)
    await ch.basic_publish(
        payload=body,
        exchange_name='amq.topic',
        routing_key='motor.state'
    )

async def ui_stream():
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()
    await channel.queue_declare(queue_name='ui_commands')
    print('UI Stream Started')
    await channel.basic_consume(ui_cb, queue_name="ui_commands", no_ack=True)

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
    loop.run_forever()

if __name__ == '__main__':
    start()

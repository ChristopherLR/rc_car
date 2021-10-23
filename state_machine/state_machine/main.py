#!/usr/bin/env python
import pika, sys, os
from dataclasses import dataclass
from enum import Enum

@dataclass
class MotorState:
    direction: Enum
    throttle: float


def main():
    ui_queue = 'ui_commands'
    motor_queue = 'motor_state'
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=ui_queue)
    channel.queue_declare(queue=motor_queue)

    def callback(ch, method, properties, body):
        print("Received %r" % body)

    channel.basic_consume(queue=ui_queue, on_message_callback=callback, auto_ack=True)

    print('State Machine Started')
    channel.start_consuming()

def start():
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == '__main__':
    start()

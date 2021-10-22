#!/usr/bin/env python
import pika, sys, os

def main():
    ui_queue = 'ui_commands'
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    ui_channel = connection.channel()

    ui_channel.queue_declare(queue=ui_queue)

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    ui_channel.basic_consume(queue=ui_queue, on_message_callback=callback, auto_ack=True)

    print('State Machine Started')
    ui_channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

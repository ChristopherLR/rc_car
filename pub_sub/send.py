#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

while True:
    x = str(input("type something: "))
    print(f"Daniel likes to send '{x}'")
    channel.basic_publish(exchange='', routing_key='hello', body=x)
connection.close()

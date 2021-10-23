#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

while True:
    x = str(input("type something: "))
    print(f"Chris likes to send '{x}'")
    channel.basic_publish(exchange='', routing_key='hello', body=x)
connection.close()
(web-interface-l2fkojDu-py3.7) pi@raspberrypi:~/test/servo $ ls
send.py  servo.py
(web-interface-l2fkojDu-py3.7) pi@raspberrypi:~/test/servo $ cat servo.py
import RPi.GPIO as GPIO
import time
import pika, sys, os

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(6.5) # Initialization

def remap(oldValue):
   oldMax = 100
   oldMin = -100
   newMax = 10
   newMin = 2.5
   newValue = (((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin
   return newValue

def changeServo(value):
   x = remap(value)
   GPIO.output(servoPIN, True)
   p.ChangeDutyCycle(x)
   time.sleep(1)
   GPIO.output(servoPIN, False)
   p.ChangeDutyCycle(0)


def main():
   connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
   channel = connection.channel()

   channel.queue_declare(queue='hello')

   def callback(ch, method, properties, body):
      print(" [x] Received %r" % body)
      changeServo(int(body))
      print("I got It!")

   channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

   print(' [*] Waiting for messages. To exit press CTRL+C')
   channel.start_consuming()

if __name__ == '__main__':
   try:
      main()
   except KeyboardInterrupt:
      print('Interrupted')
      try:
         sys.exit(0)
      except SystemExit:
         os._exit(0)

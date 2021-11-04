import RPi.GPIO as GPIO
import time
import asyncio
import aioamqp
import json
import functools
import signal

motor_a_1 = 14
motor_a_2 = 15
motor_a_pwm = 18

motor_b_1 = 5
motor_b_2 = 6
motor_b_pwm = 13

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motor_a_pwm, GPIO.OUT)
    GPIO.setup(motor_a_1, GPIO.OUT)
    GPIO.setup(motor_a_2, GPIO.OUT)
    GPIO.output(motor_a_1, GPIO.LOW)
    GPIO.output(motor_a_2, GPIO.LOW)

    GPIO.setup(motor_b_pwm, GPIO.OUT)
    GPIO.setup(motor_b_1, GPIO.OUT)
    GPIO.setup(motor_b_2, GPIO.OUT)
    GPIO.output(motor_b_1, GPIO.LOW)
    GPIO.output(motor_b_2, GPIO.LOW)

    global pwm_a
    pwm_a = GPIO.PWM(motor_a_pwm, 1000)
    pwm_a.start(0)

    global pwm_b
    pwm_b = GPIO.PWM(motor_b_pwm, 1000)
    pwm_b.start(0)

def straight(power):
    print("straight: ", power)
    GPIO.output(motor_a_1, GPIO.LOW)
    GPIO.output(motor_a_2, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(power)

    GPIO.output(motor_b_1, GPIO.LOW)
    GPIO.output(motor_b_2, GPIO.HIGH)
    pwm_b.ChangeDutyCycle(power)

def reverse(power):
    print("reverse: ", power)
    GPIO.output(motor_a_1, GPIO.HIGH)
    GPIO.output(motor_a_2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(power)

    GPIO.output(motor_b_1, GPIO.HIGH)
    GPIO.output(motor_b_2, GPIO.LOW)
    pwm_b.ChangeDutyCycle(power)

def left(power):
    print("left: ", power)
    GPIO.output(motor_a_1, GPIO.LOW)
    GPIO.output(motor_a_2, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(power)

    GPIO.output(motor_b_1, GPIO.HIGH)
    GPIO.output(motor_b_2, GPIO.LOW)
    pwm_b.ChangeDutyCycle(power)

def right(power):
    print("right: ", power)
    GPIO.output(motor_a_1, GPIO.HIGH)
    GPIO.output(motor_a_2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(power)

    GPIO.output(motor_b_1, GPIO.LOW)
    GPIO.output(motor_b_2, GPIO.HIGH)
    pwm_b.ChangeDutyCycle(power)

def stop():
    GPIO.output(motor_a_1, GPIO.LOW)
    GPIO.output(motor_a_2, GPIO.LOW)
    GPIO.output(motor_b_1, GPIO.LOW)
    GPIO.output(motor_b_2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(0)
    pwm_b.ChangeDutyCycle(0)



async def motor_state_cb(ch, body, envelope, properties):
    data = json.loads(body)
    print(data)
    if data['direction'] == 'forward': straight(data['throttle'])
    if data['direction'] == 'back': reverse(data['throttle'])
    if data['direction'] == 'left': left(data['throttle'])
    if data['direction'] == 'right': right(data['throttle'])
    if data['direction'] == 'stop': stop()

async def receive_motor_state():
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()
    print('consuming motor state')
    await channel.basic_consume(motor_state_cb, queue_name='motor_state', no_ack=True)

def destroy():
    pwm_a.stop()
    GPIO.output(motor_a_1, GPIO.LOW)
    GPIO.output(motor_a_2, GPIO.LOW)
    pwm_b.stop()
    GPIO.output(motor_b_1, GPIO.LOW)
    GPIO.output(motor_b_2, GPIO.LOW)
    GPIO.cleanup()

def stopper(signame, loop):
    print(f'got {signame}, stopping...')
    destroy()
    loop.stop()

def start():
    setup()
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), functools.partial(stopper, signame, loop))

    loop.create_task(receive_motor_state())
    loop.run_forever()

if __name__ == '__main__':
    start()

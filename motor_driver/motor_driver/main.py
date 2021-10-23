import RPi.GPIO as GPIO
import time

motor_a_1 = 14
motor_a_2 = 15
motor_a_pwm = 18

motor_b_1 = 5
motor_b_2 = 6
motor_b_pwm = 13

def setup():
    global pwm_a
    global pwm_b
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

    pwm_a = GPIO.PWM(motor_a_pwm, 1000)
    pwm_a.start(0)
    pwm_a.ChangeDutyCycle(20.0)

    pwm_b = GPIO.PWM(motor_b_pwm, 1000)
    pwm_b.start(0)
    pwm_b.ChangeDutyCycle(20.0)

def straight(power):
    print("straight: ", power)
    GPIO.output(motor_a_1, GPIO.LOW)
    GPIO.output(motor_a_2, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(power)

    GPIO.output(motor_b_1, GPIO.HIGH)
    GPIO.output(motor_b_2, GPIO.LOW)
    pwm_b.ChangeDutyCycle(power)

def reverse(power):
    print("reverse: ", power)
    GPIO.output(motor_a_1, GPIO.HIGH)
    GPIO.output(motor_a_2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(power)

    GPIO.output(motor_b_1, GPIO.LOW)
    GPIO.output(motor_b_2, GPIO.HIGH)
    pwm_b.ChangeDutyCycle(power)

def right(power):
    print("right: ", power)
    GPIO.output(motor_a_1, GPIO.LOW)
    GPIO.output(motor_a_2, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(power)

    GPIO.output(motor_b_1, GPIO.LOW)
    GPIO.output(motor_b_2, GPIO.HIGH)
    pwm_b.ChangeDutyCycle(power)

def left(power):
    print("left: ", power)
    GPIO.output(motor_a_1, GPIO.HIGH)
    GPIO.output(motor_a_2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(power)

    GPIO.output(motor_b_1, GPIO.LOW)
    GPIO.output(motor_b_2, GPIO.HIGH)
    pwm_b.ChangeDutyCycle(power)

def loop():
    while True:
        right(20.0)
        time.sleep(2)
        left(20.0)
        time.sleep(2)
        straight(20.0)
        time.sleep(2)

def destroy():
    pwm_a.stop()
    GPIO.output(motor_a_1, GPIO.LOW)
    GPIO.output(motor_a_2, GPIO.LOW)
    pwm_b.stop()
    GPIO.output(motor_b_1, GPIO.LOW)
    GPIO.output(motor_b_2, GPIO.LOW)
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()

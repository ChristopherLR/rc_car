import RPi.GPIO as GPIO
import time

stepper = 17
dc = 50.0

def setup():
    global stepper_pwm
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(stepper, GPIO.OUT)
    stepper_pwm = GPIO.PWM(stepper, 50)
    stepper_pwm.start(0)


def loop():
    while True:
        dc = int(input("dc"))
        print(dc)
        stepper_pwm.ChangeDutyCycle(dc)

def destroy():
    stepper_pwm.stop()
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()

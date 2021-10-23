import RPi.GPIO as GPIO
import time

#pins = [i for i in range(27)]
pins = [2]

def setup():
    GPIO.setmode(GPIO.BCM)
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

def on(pin):
    GPIO.output(pin, GPIO.HIGH)

def off(pin):
    GPIO.output(pin, GPIO.LOW)

def loop():
    while True:
        for pin in pins:
            print(pin)
            on(pin)
            time.sleep(2)
            off(pin)
            time.sleep(2)

def destroy():
    for pin in pins:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()

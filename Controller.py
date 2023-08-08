import RPi.GPIO as GPIO
import time
import Params

ON = GPIO.HIGH
OFF = GPIO.LOW


def warm_fan(status):
    GPIO.output(Params.WARM_FAN, status)


def cool_fan(status):
    GPIO.output(Params.COOL_FAN, status)


def controller_fan(status):
    GPIO.output(Params.COOL_FAN, status)


def sun_lamp(status):
    GPIO.output(Params.SUN_LAMP, status)


def night_lamp(status):
    GPIO.output(Params.NIGHT_LAMP, status)


def uv_lamp(status):
    GPIO.output(Params.UV_LAMP, status)


def humidifier(status):
    GPIO.output(Params.HUMIDIFIER, status)


if __name__ == "__main__":
    print(f'lamp 1 on')
    sun_lamp(ON)
    time.sleep(8)
    sun_lamp(OFF)

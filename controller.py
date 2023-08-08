import RPi.GPIO as GPIO
import time
import params

ON = GPIO.HIGH
OFF = GPIO.LOW


def warm_fan(status):
    GPIO.output(params.WARM_FAN, status)


def cool_fan(status):
    GPIO.output(params.COOL_FAN, status)


def controller_fan(status):
    GPIO.output(params.COOL_FAN, status)


def sun_lamp(status):
    GPIO.output(params.SUN_LAMP, status)


def night_lamp(status):
    GPIO.output(params.NIGHT_LAMP, status)


def uv_lamp(status):
    GPIO.output(params.UV_LAMP, status)


def humidifier(status):
    GPIO.output(params.HUMIDIFIER, status)


if __name__ == "__main__":
    print(f'lamp 1 on')
    sun_lamp(ON)
    time.sleep(8)
    sun_lamp(OFF)

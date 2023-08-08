import RPi.GPIO as GPIO
from time import sleep
import params

ON = GPIO.HIGH
OFF = GPIO.LOW


def warm_fan(status):
    print(f"warm  fan {params.WARM_FAN}")
    GPIO.output(params.WARM_FAN, status)


def cool_fan(status):
    print(f"cool fan {params.COOL_FAN}")
    GPIO.output(params.COOL_FAN, status)


def controller_fan(status):
    print(f"controller fan {params.CONTROLLER_FAN}")
    GPIO.output(params.CONTROLLER_FAN, status)


def sun_lamp(status):
    print(f'sun lamp {params.SUN_LAMP}')
    GPIO.output(params.SUN_LAMP, status)


def night_lamp(status):
    print(f'night lamp {params.NIGHT_LAMP}')
    GPIO.output(params.NIGHT_LAMP, status)


def uv_lamp(status):
    print(f'uv lamp {params.UV_LAMP}')
    GPIO.output(params.UV_LAMP, status)


def humidifier(status):
    GPIO.output(params.HUMIDIFIER, status)


if __name__ == "__main__":
    
    warm_fan(ON)
    sleep(1)
    cool_fan(ON)
    sleep(1)
    controller_fan(ON)
    sleep(1)
    night_lamp(ON)
    sleep(1)
    sun_lamp(ON)
    sleep(1)
    uv_lamp(ON)
    sleep(1)
    sleep(8)
    uv_lamp(OFF)
    sleep(1)
    sun_lamp(OFF)
    sleep(1)
    night_lamp(OFF)
    sleep(1)
    controller_fan(OFF)
    sleep(1)
    cool_fan(OFF)
    sleep(1)
    warm_fan(OFF)
    

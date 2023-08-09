import RPi.GPIO as GPIO
import time
# Set GPIO mode to use board nr 1-40
GPIO.setmode(GPIO.BCM)

# Gobalparameter
TERMO_L = 26
TERMO_M = 4
TERMO_R = 17
TERMO_F = 22
TERMO_CL = 10
WARM_FAN = 11
COOL_FAN = 5
CONTROLLER_FAN = 13
NIGHT_LAMP = 14
SUN_LAMP = 23
UV_LAMP = 8
HUMIDIFIER = 12

pin_input = [TERMO_L, TERMO_M, TERMO_R, TERMO_F, TERMO_CL]
pin_output = [WARM_FAN, COOL_FAN, CONTROLLER_FAN, NIGHT_LAMP, SUN_LAMP, UV_LAMP, HUMIDIFIER]

time.sleep(1)
# Initialize input pins
for i in pin_input:
    GPIO.setup(i, GPIO.IN)
    time.sleep(0.1)
time.sleep(1)

# Initialize output pins
for i in pin_output:
    GPIO.setup(i, GPIO.OUT)
    time.sleep(0.1)




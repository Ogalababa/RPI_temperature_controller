import RPi.GPIO as GPIO
import time
# Set GPIO mode to use board nr 1-40
GPIO.setmode(GPIO.BOARD)

# Gobalparameter
TERMO_L = 3
TERMO_M = 7
TERMO_R = 11
TERMO_F = 15
TERMO_CL = 19
WARM_FAN = 23
COOL_FAN = 29
CONTROLLER_FAN = 33
NIGHT_LAMP = 8
SUN_LAMP = 16
UV_LAMP = 24
HUMIDIFIER = 32

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




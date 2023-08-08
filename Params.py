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
FAN_WARM_UP = 23
FAN_COOL_DOWN = 29
FAN_CONTROLLER = 33
CERAMIC_LAMP = 8
SUN_LAMP = 16
UV_LAMP = 24
HUMIDIFIER = 32

pin_input = [TERMO_L, TERMO_M, TERMO_R, TERMO_F, TERMO_CL]
pin_output = [FAN_WARM_UP, FAN_COOL_DOWN, FAN_CONTROLLER, CERAMIC_LAMP, SUN_LAMP, UV_LAMP, HUMIDIFIER]

time.sleep(1)
# Initialize input pins
for i in pin_input:
    GPIO.setup(i, GPIO.IN)
    print(f'input pins: {i}')
    time.sleep(0.1)
time.sleep(1)
# Initialize output pins
for i in pin_output:
    GPIO.setup(i, GPIO.OUT)
    print(f'output pins: {i}')
    time.sleep(0.1)




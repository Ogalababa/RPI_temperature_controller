import RPi.GPIO as GPIO
import time
import Params

def lamp_1_on():
    GPIO.output(Params.SUN_LAMP, GPIO.HIGH)

def lamp_1_off():
    GPIO.output(Params.SUN_LAMP, GPIO.LOW)

if __name__ == "__main__":
    print(f'lamp 1 on')
    lamp_1_on()
    time.sleep(8)
    lamp_1_off()


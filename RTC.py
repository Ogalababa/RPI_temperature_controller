import RPi.GPIO as GPIO
import time
import Adafruit_DHT as DHT


class RTC:

    def __init__(self):
        # Set GPIO mode to use board nr 1-40
        GPIO.setmode(GPIO.BCM)
        # Parameterizable
        self.TERMO_L = 26
        self.TERMO_M = 4
        self.TERMO_R = 17
        self.TERMO_F = 22
        self.TERMO_CL = 10
        self.WARM_FAN = 11
        self.COOL_FAN = 5
        self.CONTROLLER_FAN = 13
        self.NIGHT_LAMP = 14
        self.SUN_LAMP = 23
        self.UV_LAMP = 8
        self.HUMIDIFIER = 12

        pin_input = [self.TERMO_L, self.TERMO_M, self.TERMO_R, self.TERMO_F, self.TERMO_CL]
        pin_output = [self.WARM_FAN, self.COOL_FAN, self.CONTROLLER_FAN, self.NIGHT_LAMP,
                      self.SUN_LAMP, self.UV_LAMP, self.HUMIDIFIER]

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

        # temp sensor
        self.TEMP_SENSOR = DHT.DHT11
        self.temp = None
        self.hum = None
        self.control_temp = None
        self.control_hum = None

        # status
        self.ON = GPIO.HIGH
        self.OFF = GPIO.LOW

    def get_room_temp(self):
        temp_list = []
        hum_list = []
        termo_list = [self.TERMO_L, self.TERMO_R, self.TERMO_M, self.TERMO_F]

        for i in termo_list:
            temp_1, hum_1 = DHT.read_retry(self.TEMP_SENSOR, i)
            temp_list.append(temp_1)
            hum_list.append(hum_1)

        temp_list = [i for i in temp_list if i is not None]
        hum_list = [i for i in hum_list if i is not None]

        temp = sum(temp_list) / len(temp_list)
        hum = sum(hum_list) / len(hum_list)
        self.temp = round(temp, 2)
        self.hum = round(hum, 2)

    def get_control_temp(self):
        temp_list = []
        hum_list = []

        for i in range(4):
            temp, hum = DHT.read_retry(self.TEMP_SENSOR, self.TERMO_CL)
            if temp is not None and hum is not None:
                temp_list.append(temp)
                hum_list.append(hum)
            else:
                time.sleep(5)
            time.sleep(2)

        temp_final = sum(temp_list) / len(temp_list)
        hum_final = sum(hum_list) / len(temp_list)
        self.control_temp = round(temp_final, 2)
        self.control_hum = round(hum_final, 2)

    def controller(self, equipment, status):
        GPIO.output(equipment, status)
        if status == self.ON:
            return "ON"
        elif status == self.OFF:
            return "OFF"

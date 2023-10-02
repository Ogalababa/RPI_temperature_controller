import json
import RPi.GPIO as GPIO
import time
import Adafruit_DHT as DHT


class RTC:
    # Class Constants
    ON = GPIO.HIGH
    OFF = GPIO.LOW
    NUM_RETRIES = 4

    # Initialization
    def __init__(self):
        # Set GPIO mode to use board nr 1-40
        GPIO.setmode(GPIO.BCM)

        # Parameterizable
        self.set_pin_numbers()

        self.initialize_pins(self.pin_input, GPIO.IN)
        self.initialize_pins(self.pin_output, GPIO.OUT)

        # temp sensor
        self.TEMP_SENSOR = DHT.DHT11
        self.temp = None
        self.hum = None
        self.control_temp = None
        self.control_hum = None

        # status
        self.init_status()

        # initialization status set to off
        for pin in self.pin_output:
            self.controller(pin, self.OFF)

    def set_pin_numbers(self):
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

        self.pin_input = [self.TERMO_L, self.TERMO_M, self.TERMO_R, self.TERMO_F, self.TERMO_CL]
        self.pin_output = [self.WARM_FAN, self.COOL_FAN, self.CONTROLLER_FAN, self.NIGHT_LAMP,
                           self.SUN_LAMP, self.UV_LAMP, self.HUMIDIFIER]

    def init_status(self):
        self.warm_fan_status = None
        self.cool_fan_status = None
        self.controller_fan_status = "N/A"
        self.night_lamp_status = None
        self.sun_lamp_status = None
        self.uv_lamp_status = None
        self.humidifier_status = "N/A"

    def initialize_pins(self, pins, mode):
        for pin in pins:
            GPIO.setup(pin, mode)
            time.sleep(0.1)

    def get_room_temp(self):
        temp_list = []
        hum_list = []
        termo_list = [self.TERMO_L, self.TERMO_R, self.TERMO_M, self.TERMO_F]

        for i in termo_list:
            temp_1, hum_1 = DHT.read_retry(self.TEMP_SENSOR, i)
            if temp_1 is not None and hum_1 is not None:
                temp_list.append(temp_1)
                hum_list.append(hum_1)

        if temp_list and hum_list:
            temp = sum(temp_list) / len(temp_list)
            hum = sum(hum_list) / len(hum_list)
            self.temp = round(temp, 2)
            self.hum = round(hum, 2)
        else:
            print("Failed to read temperature and humidity")

    def get_control_temp(self):
        temp_list = []
        hum_list = []

        for i in range(self.NUM_RETRIES):
            temp, hum = DHT.read_retry(self.TEMP_SENSOR, self.TERMO_CL)
            if temp is not None and hum is not None:
                temp_list.append(temp)
                hum_list.append(hum)
            else:
                time.sleep(5)
            time.sleep(2)

        if temp_list and hum_list:
            temp_final = sum(temp_list) / len(temp_list)
            hum_final = sum(hum_list) / len(temp_list)
            self.control_temp = round(temp_final, 2)
            self.control_hum = round(hum_final, 2)
        else:
            print("Failed to read control temperature and humidity")

    def controller(self, equipment, status, ):
        GPIO.output(equipment, status)
        set_dict = {self.ON: "ON", self.OFF: "OFF"}
        status_str = set_dict.get(status)
        if equipment == self.WARM_FAN:
            self.warm_fan_status = status_str
        elif equipment == self.COOL_FAN:
            self.cool_fan_status = status_str
        elif equipment == self.CONTROLLER_FAN:
            self.controller_fan_status = status_str
        elif equipment == self.NIGHT_LAMP:
            self.night_lamp_status = status_str
        elif equipment == self.SUN_LAMP:
            self.sun_lamp_status = status_str
        elif equipment == self.UV_LAMP:
            self.uv_lamp_status = status_str
        elif equipment == self.HUMIDIFIER:
            self.humidifier_status = status_str

    def save_to_json(self):
        data = {
            'temp': self.temp,
            'hum': self.hum,
            'control_temp': self.control_temp,
            'control_hum': self.control_hum,
            'warm_fan_status': self.warm_fan_status,
            'cool_fan_status': self.cool_fan_status,
            'controller_fan_status': self.controller_fan_status,
            'night_lamp_status': self.night_lamp_status,
            'sun_lamp_status': self.sun_lamp_status,
            'uv_lamp_status': self.uv_lamp_status,
            'humidifier_status': self.humidifier_status
        }
        with open("status.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

    def cleanup(self):
        GPIO.cleanup()



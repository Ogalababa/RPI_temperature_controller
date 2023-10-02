import time
import json
import RPi.GPIO as GPIO
import Adafruit_DHT as DHT


class RTC:
    # Class Constants
    ON = "ON"
    OFF = "OFF"
    NUM_RETRIES = 4

    # Pin numbers
    PINS = {
        "TERMO_L": 26, "TERMO_M": 4, "TERMO_R": 17, "TERMO_F": 22, "TERMO_CL": 10,
        "WARM_FAN": 11, "COOL_FAN": 5, "CONTROLLER_FAN": 13, "NIGHT_LAMP": 14,
        "SUN_LAMP": 23, "UV_LAMP": 8, "HUMIDIFIER": 12
    }

    # Initialization
    def __init__(self):

        self.GPIO = GPIO
        self.DHT = DHT
        self.time = time

        # Set GPIO mode to use board nr 1-40
        self.GPIO.setmode(self.GPIO.BCM)

        self.initialize_pins()

        # Temp sensor
        self.TEMP_SENSOR = self.DHT.DHT11
        self.temp = None
        self.hum = None
        self.control_temp = None
        self.control_hum = None

        # Status
        self.status = {key: None for key in self.PINS.keys()}
        self.status["CONTROLLER_FAN"] = "N/A"
        self.status["HUMIDIFIER"] = "N/A"

        # Initialization status set to off
        for pin in self.PINS.values():
            self.controller(pin, self.OFF)

    def initialize_pins(self):
        for pin in self.PINS.values():
            self.GPIO.setup(pin,
                            self.GPIO.OUT if "FAN" in pin or "LAMP" in pin or "HUMIDIFIER" in pin else self.GPIO.IN)
            self.time.sleep(0.1)

    def get_room_temp(self):
        temp_list = []
        hum_list = []
        for _ in range(self.NUM_RETRIES):
            hum, temp = self.DHT.read(self.TEMP_SENSOR, self.PINS["TERMO_L"])
            if hum is not None and temp is not None:
                temp_list.append(temp)
                hum_list.append(hum)
            else:
                self.time.sleep(5)
            self.time.sleep(2)

        if temp_list and hum_list:
            self.control_temp = round(sum(temp_list) / len(temp_list), 2)
            self.control_hum = round(sum(hum_list) / len(temp_list), 2)
        else:
            print("Failed to read control temperature and humidity")

    def controller(self, equipment, status):

        if status == "ON":
            setTo = GPIO.HIGH
        else:
            setTo = GPIO.LOW

        self.GPIO.output(self.PINS[equipment], setTo)
        self.status[equipment] = status

    def save_to_json(self):

        data = self.status.copy()
        data.update({
            'temp': self.temp,
            'hum': self.hum,
            'control_temp': self.control_temp,
            'control_hum': self.control_hum,
        })
        with open("status.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

    def cleanup(self):
        self.GPIO.cleanup()

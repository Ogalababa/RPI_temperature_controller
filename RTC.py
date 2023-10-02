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
        termo_list = [self.PINS.get("TERMO_L"), self.PINS.get("TERMO_R"),
                      self.PINS.get("TERMO_M"), self.PINS.get("TERMO_F")]

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
            temp, hum = DHT.read_retry(self.TEMP_SENSOR, self.PINS.get("TERMO_CL"))
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

        if status == "ON":
            setTo = GPIO.HIGH
        else:
            setTo = GPIO.LOW

        self.GPIO.output(self.PINS[equipment], setTo)
        self.status[equipment] = status

    def save_to_json(self):

        data = self.status.copy()
        data.update({
            'temp': f"{self.temp} ℃",
            'hum': f"{self.hum} %",
            'control_temp': f"{self.control_temp} ℃",
            'control_hum': f"{self.control_hum} %",
        })
        with open("status.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

    def cleanup(self):
        self.GPIO.cleanup()

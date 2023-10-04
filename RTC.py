import os
import time
import json
import RPi.GPIO as GPIO
import Adafruit_DHT as DHT
from pathlib import Path
import pandas as pd
import sqlite3
import datetime
import pytz



def cleanup():
    GPIO.cleanup()


class RTC:
    # Class Constants
    ON = "ON"
    OFF = "OFF"
    NUM_RETRIES = 4

    # Pins
    PINS = {
        "INPUT": {"TERMO_L": 26, "TERMO_M": 4, "TERMO_R": 17, "TERMO_F": 22, "TERMO_CL": 10},
        "OUTPUT": {"加温风扇": 11, "降温风扇": 5, "控制室风扇": 13, "陶瓷灯": 14,
                   "日光灯": 23, "UV 灯": 8, "加湿器": 12}
    }

    # Initialization
    def __init__(self):

        # Set GPIO mode to use board nr 1-40
        GPIO.setmode(GPIO.BCM)

        self.initialize_pins()

        # Temp sensor
        self.TEMP_SENSOR = DHT.DHT11
        self.temp = 0
        self.hum = 0
        self.control_temp = 0
        self.control_hum = 0

        # Status

        self.status = {key: None for key in self.PINS["OUTPUT"].keys()}
        self.status["控制室风扇"] = "N/A"
        self.status["加湿器"] = "N/A"

        # # Database
        # current_dir = Path(__file__).parent
        # self.conn = sqlite3.connect(os.path.join(current_dir, 'status.db'))

        # Initialization status set to off
        for equipment in self.PINS["OUTPUT"].keys():
            self.controller(equipment, self.OFF)

    def initialize_pins(self):
        for pin_type, pins in self.PINS.items():
            mode = GPIO.IN if pin_type == "INPUT" else GPIO.OUT
            for pin in pins.values():
                GPIO.setup(pin, mode)
                time.sleep(0.1)

    def get_room_temp(self):

        temp_list = []
        hum_list = []
        termo_list = [i for i in self.PINS["INPUT"].values() if i != self.PINS["INPUT"]["TERMO_CL"]]

        for i in termo_list:
            print(i)
            hum_1, temp_1 = DHT.read_retry(self.TEMP_SENSOR, i)
            print(temp_1)

            if temp_1 is not None and hum_1 is not None:
                temp_list.append(temp_1)
                hum_list.append(hum_1)

        if temp_list and hum_list:
            self.temp = round(sum(temp_list) / len(temp_list), 1)
            self.hum = round(sum(hum_list) / len(hum_list), 1)

    def get_control_temp(self):
        temp_list = []
        hum_list = []

        for i in range(self.NUM_RETRIES):

            hum, temp = DHT.read_retry(self.TEMP_SENSOR, self.PINS["INPUT"]["TERMO_CL"])
            if temp is not None and hum is not None:
                temp_list.append(temp)
                hum_list.append(hum)
            else:
                print("sensor field")
                self.control_temp = 0
                self.control_hum = 0
                time.sleep(5)
            time.sleep(3)

        temp_final = sum(temp_list) / len(temp_list)
        hum_final = sum(hum_list) / len(temp_list)
        self.control_temp = round(temp_final, 1)
        self.control_hum = round(hum_final, 1)

    def controller(self, equipment, status):

        set_to = GPIO.LOW if status == self.ON else GPIO.HIGH
        # set_to = GPIO.HIGH if status == self.ON else GPIO.LOW
        print(f"{equipment} {status}")
        GPIO.output(self.PINS["OUTPUT"][equipment], set_to)
        self.status[equipment] = status

    def save_to_json(self):

        # data = self.status.copy()
        data = {
            # '温度': f"{self.temp} ℃",
            # '湿度': f"{self.hum} %",
            # '控制室温度': f"{self.control_temp} ℃",
            # '控制室湿度': f"{self.control_hum} %",
            '温度': f"{self.control_temp} ℃",
            '湿度': f"{self.control_hum} %",
            '陶瓷灯': self.status.get("陶瓷灯")
        }
        current_dir = Path(__file__).parent
        with open(os.path.join(current_dir, "status.json"), "w") as json_file:
            json.dump(data, json_file, indent=4)

        # db_data = data.copy()
        # db_data.update(self.status)
        # df = pd.DataFrame(db_data)
        #
        # now_utc = datetime.datetime.now(pytz.utc)
        # # 将UTC日期和时间转换为阿姆斯特丹时区
        # amsterdam_tz = pytz.timezone('Europe/Amsterdam')
        # now_amsterdam = now_utc.astimezone(amsterdam_tz)
        # # 将阿姆斯特丹的日期和时间添加到DataFrame中
        # df['时间'] = [now_amsterdam]
        # df.to_sql('status', self.conn, if_exists='append', index=True)
        # self.conn.close()

# ！/usr/bin/python3
# coding:utf-8
# sys

import time
from datetime import datetime
from run.RTC import RTC


class Schedule:
    def __init__(self):
        self.rtc = RTC()
        self.target_day = 32
        self.target_night = 30
        self.target_temp = 28
        self.temp_range = 2
        self.is_night = True
        self.temp_status = 'good'
        self.equipment_mapping = {
            '加温风扇': self.rtc.OFF,
            '降温风扇': self.rtc.OFF,
            'UV 灯': self.rtc.OFF,
            '日光灯': self.rtc.OFF,
            '陶瓷灯': self.rtc.OFF,
        }
        self.lock = {
            '加温风扇': False,
            '降温风扇': False,
            'UV 灯': False,
            '日光灯': False,
            '陶瓷灯': False
        }

    def day_night(self):
        hour = datetime.now().hour
        if hour >= 20:
            self.is_night = False
        else:
            self.is_night = True

    def check_temp(self):
        if self.is_night:
            self.target_temp = self.target_night
        else:
            self.target_temp = self.target_temp
        current_temp = self.rtc.get_control_temp()
        print(current_temp)
        print(type(current_temp))
        if current_temp < self.target_temp - self.temp_range:
            self.temp_status = 'cold'
        elif self.target_temp <= current_temp < self.target_temp + self.temp_range:
            self.temp_status = 'good'
        elif self.target_temp >= self.target_temp + self.temp_range:
            self.temp_status = 'hot'
        else:
            self.temp_status = 'error'
        print(self.temp_status)

    def change_mapping_status(self, equipment, status):
        status_dict = {'lock': True, 'unlock': False, 'ON': self.rtc.ON, 'OFF': self.rtc.OFF}
        if status in status_dict:
            if equipment in self.equipment_mapping and status in ('ON', "OFF") and self.lock.get(
                    equipment) is False:
                self.equipment_mapping[equipment] = status_dict.get(status)
            if equipment in self.lock and status in ('lock', 'unlock'):
                self.lock[equipment] = status_dict.get(status)
        else:
            print(f"无效的状态: {status}")

    def equipment_action(self, equipment, desired_status):
        current_status = self.rtc.status.get(equipment, self.rtc.OFF)

        if current_status != desired_status:
            self.rtc.controller(equipment, desired_status)

    def equipment_actions(self):
        for equipment, status in self.equipment_mapping.items():
            self.equipment_action(equipment, status)

    def uv_lamp(self):
        hour = datetime.now().hour
        if 14 <= hour < 20:
            self.change_mapping_status('UV 灯', "ON")
        else:
            self.change_mapping_status('UV 灯', "OFF")

    def sun_lamp(self):
        if self.is_night is False:
            self.change_mapping_status('日光灯', "ON")
        else:
            self.change_mapping_status('日光灯', "OFF")

    def night_lamp(self):
        if self.is_night and self.temp_status == "cold":
            self.change_mapping_status('陶瓷灯', "ON")
        else:
            self.change_mapping_status("陶瓷灯", "OFF")

    def cooling_fan(self):
        if self.temp_status == "hot":
            self.change_mapping_status('降温风扇', "ON")
        else:
            self.change_mapping_status('降温风扇', "OFF")

    def controller(self):
        while True:
            self.day_night()
            self.check_temp()
            self.uv_lamp()
            self.sun_lamp()
            self.night_lamp()
            self.rtc.save_to_json(self.target_temp)
            self.equipment_actions()
            time.sleep(54)
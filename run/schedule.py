#!/usr/bin/python3
# coding:utf-8
import os.path
import time
from datetime import datetime
from run.RTC import RTC
from run.ToDB import ConnectToDB


class Schedule:
    def __init__(self):
        self.rtc = RTC()
        self.db = ConnectToDB('Status', os.path.join('/', 'home', 'jiawei', 'RPI_temperature_controller', 'data'))
        self.target_day = 28
        self.target_night = 29
        self.target_temp = 27
        self.temp_range = 2
        self.uv_time = 14
        self.sun_time = 20
        self.is_night = True
        self.is_uv = False
        self.temp_status = 'good'
        button_df = self.db.read_from_sql("button")
        self.equipment_mapping = {
            '加温风扇': self.rtc.ON if button_df['加温风扇'][0] else self.rtc.OFF,
            '降温风扇': self.rtc.ON if button_df['降温风扇'][0] else self.rtc.OFF,
            'UV 灯': self.rtc.ON if button_df['UV 灯'][0] else self.rtc.OFF,
            '日光灯': self.rtc.ON if button_df['日光灯'][0] else self.rtc.OFF,
            '陶瓷灯': self.rtc.ON if button_df['陶瓷灯'][0] else self.rtc.OFF,
        }
        for key, value in self.equipment_mapping.items():
            print("原始状态")
            print(key+' : ' + value)

        lock_df = self.db.read_from_sql('lock')
        self.lock = {
            '加温风扇': lock_df['加温风扇'][0],
            '降温风扇': lock_df['降温风扇'][0],
            'UV 灯': lock_df['UV 灯'][0],
            '日光灯': lock_df['日光灯'][0],
            '陶瓷灯': lock_df['陶瓷灯'][0]
        }

    def get_target_temp(self):
        temp_df = self.db.read_from_sql(table_name="target_temp")
        self.target_day = temp_df['日间温度'][0]
        self.target_night = temp_df['夜间温度'][0]
        self.uv_time = temp_df['UV时间'][0]
        self.sun_time = temp_df['日光时间'][0]

    def day_night(self):
        hour = datetime.now().hour
        if hour >= self.sun_time:
            self.is_night = False
        else:
            self.is_night = True
        if self.uv_time <= hour < self.sun_time:
            self.is_uv = True
        else:
            self.is_uv = False

    def check_temp(self):
        if self.is_night:
            self.target_temp = self.target_night
        else:
            self.target_temp = self.target_day

        current_temp = self.rtc.get_control_temp()
        print(f"Current Temp: {current_temp}°C")
        print(f"Target Temp: {self.target_temp}°C")
        if current_temp < self.target_temp:
            self.temp_status = 'cold'
        elif self.target_temp <= current_temp < self.target_temp + self.temp_range:
            self.temp_status = 'good'
        elif current_temp >= self.target_temp + self.temp_range:
            self.temp_status = 'hot'
        else:
            self.temp_status = 'error'
        print(f"Temperature Status: {self.temp_status}")

    def change_mapping_status(self, equipment, status):
        status_dict = {'lock': True, 'unlock': False, 'ON': self.rtc.ON, 'OFF': self.rtc.OFF}
        if status in status_dict:
            if equipment in self.equipment_mapping and status in ('ON', "OFF") and not self.lock.get(
                    equipment, False):
                self.equipment_mapping[equipment] = status_dict.get(status)
            if equipment in self.lock and status in ('lock', 'unlock'):
                self.lock[equipment] = status_dict.get(status)
        else:
            print(f"Invalid status: {status}")

    def equipment_action(self, equipment, desired_status):
        current_status = self.rtc.status.get(equipment, self.rtc.OFF)

        if current_status != desired_status:
            self.rtc.controller(equipment, desired_status)

    def equipment_actions(self):
        for equipment, status in self.equipment_mapping.items():
            self.equipment_action(equipment, status)
        inverse_equipment_mapping = {
            key: True if value == self.rtc.ON else False for key, value in self.equipment_mapping.items()
        }
        self.db.set_target_temp("button", inverse_equipment_mapping)

    def uv_lamp(self):
        if self.is_uv:
            self.change_mapping_status('UV 灯', "ON")
            self.change_mapping_status('加温风扇', "ON")
        else:
            self.change_mapping_status('UV 灯', "OFF")
            self.change_mapping_status('加温风扇', "OFF")

    def sun_lamp(self):
        if not self.is_night:
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
        try:
            while True:
                self.get_target_temp()
                self.day_night()
                self.check_temp()
                self.uv_lamp()
                self.sun_lamp()
                self.night_lamp()
                self.cooling_fan()
                self.equipment_actions()
                self.rtc.save_to_json(self.target_temp)
                time.sleep(54)
        except KeyboardInterrupt:
            print("Controller stopped by user.")


if __name__ == "__main__":
    schedule = Schedule()
    schedule.controller()

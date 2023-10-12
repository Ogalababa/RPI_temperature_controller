# ！/usr/bin/python3
# coding:utf-8
# sys
import time
from datetime import datetime
from RTC import RTC


class TC:

    def __init__(self, target_day=32, target_night=30, temp_range=2, ):
        self.rtc = RTC()
        self.target_day = target_day
        self.target_night = target_night
        self.ranges = temp_range
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

    def change_mapping_status(self, equipment, status):
        status_dict = {'lock': True, 'unlock': False, 'ON': self.rtc.ON, 'OFF': self.rtc.OFF}
        if status in status_dict:
            if equipment in self.equipment_mapping and status in ('ON', "OFF") and self.lock.get(equipment) is False:
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

    def update_uv_equipment(self):
        current_hour = datetime.now().hour
        if 10 <= current_hour < 16:
            self.change_mapping_status('UV 灯', 'ON')
            self.change_mapping_status('加温风扇', 'ON')

        else:
            self.change_mapping_status('UV 灯', 'OFF')
            self.change_mapping_status('加温风扇', 'OFF')

    def update_day_equipment(self, current_temp):
        print('in day')
        self.change_mapping_status('陶瓷灯', 'OFF')
        self.update_uv_equipment()
        print('end uv')

        if current_temp is not None:
            print('temp is not none')
            print(current_temp)
            print(self.target_day)
            print(current_temp < (self.target_day - self.ranges))
            print(f'too cold night: {current_temp < (self.target_day - self.ranges)}')
            print(f'good night: {self.target_day < current_temp < (self.target_day + self.ranges)}')
            print(f'too hot night: {current_temp > (self.target_day + self.ranges)}')

            if current_temp < (self.target_day - self.ranges):  # 冷
                print('too cold day')
                self.change_mapping_status('日光灯', 'ON')
                self.change_mapping_status('加温风扇', 'ON')

            elif self.target_day < current_temp < (self.target_day + self.ranges):  # 目标温度
                print('good day')
                self.change_mapping_status('日光灯', 'OFF')
                self.change_mapping_status('加温风扇', 'OFF')

            elif current_temp > (self.target_day + self.ranges):  # 热
                print('too hot day')
                self.change_mapping_status('降温风扇', 'ON')
                self.change_mapping_status('日光灯', 'OFF')
                self.change_mapping_status('加温风扇', 'OFF')
        else:
            print('temp is none')
            current_temp = self.rtc.get_control_temp()
            self.update_day_equipment(current_temp)
        print('end day')

    def update_night_equipment(self, current_temp):
        print('in night')
        self.change_mapping_status('日光灯', 'OFF')
        self.update_uv_equipment()

        if current_temp is not None:
            print(current_temp)
            print(self.target_night)
            print(f'too cold night: {current_temp < (self.target_night - self.ranges)}')
            print(f'good night: {self.target_night <= current_temp <= (self.target_night + self.ranges)}')
            print(f'too hot night: {current_temp > (self.target_night + self.ranges)}')

            if current_temp < (self.target_night - self.ranges):  # 冷
                self.change_mapping_status('陶瓷灯', 'ON')
                self.change_mapping_status('加温风扇', 'ON')

            elif self.target_night < current_temp < (self.target_night + self.ranges):
                self.change_mapping_status('陶瓷灯', 'OFF')
                self.change_mapping_status('加温风扇', 'OFF')

            elif current_temp > (self.target_night + self.ranges):
                self.change_mapping_status('陶瓷灯', 'OFF')
                self.change_mapping_status('加温风扇', 'OFF')
                self.change_mapping_status('降温风扇', 'ON')
        else:
            print('current_temp is none')
            current_temp = self.rtc.get_control_temp()
            self.update_night_equipment(current_temp)

    def temperature_controller(self):
        while True:
            current_temp = self.rtc.get_control_temp()
            print(current_temp)
            current_hour = datetime.now().hour
            print(f"time: {current_hour}")
            if 20 <= current_hour:
                self.change_mapping_status('日光灯', 'ON')
                self.change_mapping_status('降温风扇', 'ON')
                self.change_mapping_status('加温风扇', 'OFF')
                self.change_mapping_status('日光灯', 'lock')
                self.change_mapping_status('降温风扇', 'lock')
                self.change_mapping_status('加温风扇', 'lock')
            else:
                self.change_mapping_status('日光灯', 'unlock')
                self.change_mapping_status('降温风扇', 'unlock')
                self.change_mapping_status('加温风扇', 'unlock')
                self.change_mapping_status('日光灯', 'OFF')
                self.change_mapping_status('降温风扇', 'OFF')

            if 0 <= current_hour < 20:
                self.update_night_equipment(current_temp)
            else:
                self.update_day_equipment(current_temp)

            self.rtc.save_to_json()
            self.equipment_actions()
            time.sleep(54)


if __name__ == '__main__':
    temp_controller = TC(target_day=32, target_night=30, temp_range=2)
    temp_controller.temperature_controller()

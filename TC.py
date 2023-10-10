# ！/usr/bin/python3
# coding:utf-8
# sys
import time
from RTC import RTC
from datetime import datetime


class TC:

    def __init__(self, target_day=32, target_night=30, temp_range=2, ):
        self.rtc = RTC()
        self.target_day = target_day
        self.target_night = target_night
        self.range = temp_range
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
    def change_mapping_status(self,equipment, status):
        lock = self.lock[equipment] = True
        unlock = self.lock[equipment] = False
        on = self.equipment_mapping[equipment] = self.rtc.ON
        off = self.equipment_mapping[equipment] = self.rtc.OFF
        status_dict = {'lock': lock, 'unlock': unlock, 'ON': on, 'OFF': off}
        if self.lock.get(equipment) is False or status == 'unlock':
            status_dict.get(status)


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
        self.change_mapping_status('陶瓷灯', 'ON')
        current_hour = datetime.now().hour
        if 16 <= current_hour <= 18:
            self.change_mapping_status('降温风扇', 'ON')
        else:
            self.change_mapping_status('降温风扇', 'OFF')

        if current_temp is not None:
            if current_temp < self.target_day - self.range:  # 冷
                self.change_mapping_status('日光灯', 'ON')
                self.change_mapping_status('加温风扇', 'ON')

            elif self.target_day <= current_temp <= self.target_day + self.range:  # 目标温度
                self.change_mapping_status('日光灯', 'OFF')
                self.change_mapping_status('加温风扇', 'OFF')

            else:  # 热
                self.change_mapping_status('降温风扇', 'ON')
                self.change_mapping_status('日光灯', 'OFF')
                self.change_mapping_status('加温风扇', 'OFF')
        else:
            current_temp = self.rtc.get_control_temp()
            self.update_day_equipment(current_temp)
        self.update_uv_equipment()

    def update_night_equipment(self, current_temp):
        self.change_mapping_status('日光灯', 'OFF')

        if current_temp is not None:
            if current_temp < self.target_night - self.range:  # 冷
                self.change_mapping_status('陶瓷灯', 'ON')
                self.change_mapping_status('加温风扇', 'ON')

            elif self.target_night <= current_temp <= self.target_night + self.range:
                self.change_mapping_status('陶瓷灯', 'OFF')
                self.change_mapping_status('加温风扇', 'OFF')

            else:
                self.change_mapping_status('陶瓷灯', 'OFF')
                self.change_mapping_status('加温风扇', 'OFF')
                self.change_mapping_status('降温风扇', 'ON')

        else:
            current_temp = self.rtc.get_control_temp()
            self.update_night_equipment(current_temp)
        self.update_uv_equipment()

    def temperature_controller(self):
        while True:
            current_temp = self.rtc.get_control_temp()
            print(current_temp)
            current_hour = datetime.now().hour
            if 20 <= current_hour < 22:
                self.change_mapping_status('日光灯', 'ON')
                self.change_mapping_status('降温风扇', 'ON')
                self.change_mapping_status('日光灯', 'lock')
                self.change_mapping_status('降温风扇', 'lock')
            else:
                self.change_mapping_status('日光灯', 'unlock')
                self.change_mapping_status('降温风扇', 'unlock')

            if 0 <= current_hour < 16:
                self.update_night_equipment(current_temp)
            else:
                self.update_day_equipment(current_temp)

            self.rtc.save_to_json()
            self.equipment_actions()
            time.sleep(54)


if __name__ == '__main__':
    temp_controller = TC(target_day=32, target_night=30, temp_range=2)
    temp_controller.temperature_controller()

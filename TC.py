# ！/usr/bin/python3
# coding:utf-8
# sys
import time
from RTC import RTC
from datetime import datetime


class TC:

    def __init__(self, target_day=32, target_night=30, temp_range=2, ):
        self.datetime = datetime.now()
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
        self.hourly_functions = [
            (10, 16, self.update_day_equipment),
            (16, 24, self.update_night_equipment)

        ]

    def equipment_action(self, equipment, desired_status):
        current_status = self.rtc.status.get(equipment, self.rtc.OFF)
        if current_status != desired_status:
            self.rtc.controller(equipment, desired_status)

    def equipment_actions(self):
        for equipment, status in self.equipment_mapping.items():
            self.equipment_action(equipment, status)

    def get_current_hour(self):
        self.datetime = datetime.now().hour
        return datetime.now().hour

    def update_uv_equipment(self):
        if 10 <= self.get_current_hour() < 16:
            self.equipment_mapping['UV 灯'] = self.rtc.ON
            self.equipment_mapping['降温风扇'] = self.rtc.ON
        else:
            self.equipment_mapping['UV 灯'] = self.rtc.OFF
            self.equipment_mapping['降温风扇'] = self.rtc.OFF

    def update_day_equipment(self, current_temp):
        self.equipment_mapping['陶瓷灯'] = self.rtc.OFF
        self.update_uv_equipment()

        if current_temp is not None:
            if current_temp < self.target_day - self.range:  # 冷
                self.equipment_mapping['日光灯'] = self.rtc.ON
                self.equipment_mapping['加温风扇'] = self.rtc.ON
            elif self.target_day <= current_temp <= self.target_day + self.range:  # 目标温度
                self.equipment_mapping['日光灯'] = self.rtc.OFF
                self.equipment_mapping['加温风扇'] = self.rtc.OFF
            else:  # 热
                self.equipment_mapping['降温风扇'] = self.rtc.ON
                self.equipment_mapping['日光灯'] = self.rtc.OFF
        else:
            current_temp = self.rtc.get_control_temp()
            self.update_day_equipment(current_temp)

    def update_night_equipment(self, current_temp):
        self.equipment_mapping['日光灯'] = self.rtc.OFF
        self.update_uv_equipment()

        if current_temp is not None:
            if current_temp < self.target_night - self.range:  # 冷
                self.equipment_mapping['陶瓷灯'] = self.rtc.ON
                self.equipment_mapping['加温风扇'] = self.rtc.ON
            elif self.target_night <= current_temp <= self.target_night + self.range:
                self.equipment_mapping['陶瓷灯'] = self.rtc.OFF
                self.equipment_mapping['加温风扇'] = self.rtc.OFF
            else:
                self.equipment_mapping['陶瓷灯'] = self.rtc.OFF
                self.equipment_mapping['加温风扇'] = self.rtc.OFF
                self.equipment_mapping['降温风扇'] = self.rtc.ON

        else:
            current_temp = self.rtc.get_control_temp()
            self.update_night_equipment(current_temp)

    def temperature_controller(self):
        while True:
            current_temp = self.rtc.get_control_temp()
            current_hour = self.get_current_hour()
            for start_hour, end_hour, equipment_function in self.hourly_functions:
                # 在这里使用start_hour、end_hour和equipment_function
                if start_hour <= current_hour < end_hour:
                    print(start_hour)
                    equipment_function(current_temp)
            print('save to json')
            self.rtc.save_to_json()
            self.equipment_actions()
            time.sleep(54)


if __name__ == '__main__':
    temp_controller = TC(target_day=32, target_night=30, temp_range=2)
    temp_controller.temperature_controller()


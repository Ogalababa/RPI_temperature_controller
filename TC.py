import os.path
import time
from RTC import RTC
from datetime import datetime

from __init__ import *


class TC:
    def __init__(self, target_day=32, targe_night=30, temp_range=2, ):
        self.datetime = datetime.now()
        self.rtc = RTC()
        self.target_day = target_day
        self.targe_night = targe_night
        self.range = temp_range
        self.equipment_mapping = {
            '加温风扇': self.rtc.OFF,
            '降温风扇': self.rtc.OFF,
            'UV 灯': self.rtc.OFF,
            '日光灯': self.rtc.OFF,
            '陶瓷灯': self.rtc.OFF,
        }
        self.hourly_functions = {
            (10, 16): {"cold": {self.equipment_mapping}}
        }

    def update_equipment_status(self, equipment, desired_status):
        current_status = self.rtc.status.get(equipment, self.rtc.OFF)
        if current_status != desired_status:
            self.rtc.controller(equipment, desired_status)

    def update_all_equipment_status(self):
        for eq, status in self.equipment_mapping.items():
            self.update_equipment_status(eq, status)

    def get_current_hour(self):
        self.datetime = self.datetime.now().hour
        return self.datetime.now().hour


    def temperature_controller(self):
        while True:
            current_temp = self.rtc.get_control_temp()
            current_hour = self.get_current_hour()



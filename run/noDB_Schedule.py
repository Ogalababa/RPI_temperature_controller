#!/usr/bin/python3
# coding:utf-8
import time
from datetime import datetime
from run.RTC import RTC
import logging


# 设置logging基础配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])  # 输出到控制台
logger = logging.getLogger(__name__)


class Schedule:
    def __init__(self, day_time=8, uv_start_time=12, night_time=22, day_temp=30,  night_temp=28, target_temp=27):
        self.rtc = RTC()
        self.day_time = day_time
        self.night_time = night_time
        self.day_temp = day_temp
        self.uv_start_time = uv_start_time
        self.night_temp = night_temp
        self.target_temp = target_temp
        self.is_day = False
        self.is_uv = False
        self.temp_status = 'good'
        self.equipment_mapping = {
            '降温风扇': self.rtc.OFF,
            '陶瓷灯': self.rtc.OFF,
            'UV 灯': self.rtc.OFF,
            '日光灯': self.rtc.OFF,
        }

    def update_day_night_status(self):
        hour = datetime.now().hour
        self.is_day = self.day_time <= hour < self.uv_start_time
        self.is_uv = self.uv_start_time <= hour < self.night_time
        logger.info("Day time activate" if self.is_day else "Night time activate")
        logger.info("UV time activate" if self.is_uv else "UV time deactivate")

    def check_temp(self):
        current_temp = self.rtc.get_control_temp()
        logger.info(f"Current Temp: {current_temp}°C")
        if self.is_day:
            self.target_temp = self.day_temp
        else:
            self.target_temp = self.night_temp
        logger.info(f"Target Temp: {self.target_temp}°C")

        if current_temp - self.target_temp >= 2:
            self.temp_status = 'hot'
        elif current_temp - self.target_temp <= -2:
            self.temp_status = 'cold'
        else:
            self.temp_status = 'good'
        logger.info(f"Temperature Status: {self.temp_status}")

    def change_mapping_status(self, equipment, status):
        if equipment in self.equipment_mapping:
            self.equipment_mapping[equipment] = status

    def equipment_action(self, equipment, desired_status):
        current_status = self.rtc.status.get(equipment, self.rtc.OFF)
        if current_status != desired_status:
            self.rtc.controller(equipment, desired_status)

    def equipment_actions(self):
        for equipment, status in self.equipment_mapping.items():
            self.equipment_action(equipment, status)

    def control_lamps(self):
        if self.is_day:
            self.change_mapping_status('日光灯', self.rtc.ON)
        else:
            self.change_mapping_status('日光灯', self.rtc.OFF)
        if self.is_uv:
            self.change_mapping_status('UV 灯', self.rtc.ON)
        else:
            self.change_mapping_status('UV 灯', self.rtc.OFF)

    def control_fans_and_heaters(self):
        if self.temp_status == 'hot':
            self.change_mapping_status('降温风扇', self.rtc.ON)
            self.change_mapping_status('陶瓷灯', self.rtc.OFF)
        elif self.temp_status == 'cold':
            self.change_mapping_status('降温风扇', self.rtc.OFF)
            self.change_mapping_status('陶瓷灯', self.rtc.ON)
        else:
            self.change_mapping_status('降温风扇', self.rtc.OFF)
            self.change_mapping_status('陶瓷灯', self.rtc.OFF)

    def controller(self):
        try:
            while True:
                start_time = time.time()
                self.update_day_night_status()
                self.check_temp()
                self.control_lamps()
                self.control_fans_and_heaters()
                self.equipment_actions()
                self.rtc.save_to_json(self.target_temp)

                time.sleep(10)  # 确保每分钟执行一次
        except KeyboardInterrupt:
            logger.info("Controller stopped by user.")


if __name__ == "__main__":
    schedule = Schedule(day_time=8, uv_start_time=12, night_time=22, day_temp=30,  night_temp=28, target_temp=27)
    schedule.controller()

#!/usr/bin/python3
# coding:utf-8
import time
from datetime import datetime, timedelta
from threading import Thread
import sys

print(sys.executable)
print(sys.version)
from flask import Flask, request, jsonify
import logging
from run.RTC import RTC

# 设置logging基础配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])  # 输出到控制台
logger = logging.getLogger(__name__)

app = Flask(__name__)


class Schedule:
    def __init__(self, day_time=8, uv_start_time=12, night_time=22, day_temp=30, night_temp=28, target_temp=27):
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
        self.current_temp = 0
        self.equipment_mapping = {
            '降温风扇': self.rtc.OFF,
            '陶瓷灯': self.rtc.OFF,
            'UV 灯': self.rtc.OFF,
            '日光灯': self.rtc.OFF,
        }
        self.last_control_time = {
            '降温风扇': datetime.min,
            '陶瓷灯': datetime.min,
            'UV 灯': datetime.min,
            '日光灯': datetime.min,
        }

    def update_day_night_status(self):
        hour = datetime.now().hour
        self.is_day = self.day_time <= hour < self.uv_start_time
        self.is_uv = self.uv_start_time <= hour < self.night_time
        logger.info("Day time activate" if self.is_day else "Night time activate")
        logger.info("UV time activate" if self.is_uv else "UV time deactivate")

    def check_temp(self):
        self.current_temp = self.rtc.get_control_temp()
        logger.info(f"Current Temp: {self.current_temp}°C")
        if self.is_day:
            self.target_temp = self.day_temp
        else:
            self.target_temp = self.night_temp
        logger.info(f"Target Temp: {self.target_temp}°C")

        if self.current_temp - self.target_temp >= 2:
            self.temp_status = 'hot'
        elif self.current_temp - self.target_temp <= -2:
            self.temp_status = 'cold'
        else:
            self.temp_status = 'good'
        logger.info(f"Temperature Status: {self.temp_status}")

    def change_mapping_status(self, equipment, status, source='scheduler'):
        if equipment in self.equipment_mapping:
            self.equipment_mapping[equipment] = status
            if source == 'api':
                self.last_control_time[equipment] = datetime.now()

    def equipment_action(self, equipment, desired_status):
        current_status = self.rtc.status.get(equipment, self.rtc.OFF)
        if current_status != desired_status:
            self.rtc.controller(equipment, desired_status)

    def equipment_actions(self):
        for equipment, status in self.equipment_mapping.items():
            self.equipment_action(equipment, status)

    def control_lamps(self):
        current_time = datetime.now()
        if self.is_day and (current_time - self.last_control_time['日光灯']) > timedelta(minutes=1):
            self.change_mapping_status('日光灯', self.rtc.ON)
        elif not self.is_day and (current_time - self.last_control_time['日光灯']) > timedelta(minutes=1):
            self.change_mapping_status('日光灯', self.rtc.OFF)

        if self.is_uv and (current_time - self.last_control_time['UV 灯']) > timedelta(minutes=1):
            self.change_mapping_status('UV 灯', self.rtc.ON)
        elif not self.is_uv and (current_time - self.last_control_time['UV 灯']) > timedelta(minutes=1):
            self.change_mapping_status('UV 灯', self.rtc.OFF)

    def control_fans_and_heaters(self):
        current_time = datetime.now()
        if self.temp_status == 'hot' and (current_time - self.last_control_time['降温风扇']) > timedelta(minutes=1):
            self.change_mapping_status('降温风扇', self.rtc.ON)
            self.change_mapping_status('陶瓷灯', self.rtc.OFF)
        elif self.temp_status == 'cold' and (current_time - self.last_control_time['陶瓷灯']) > timedelta(minutes=1):
            self.change_mapping_status('降温风扇', self.rtc.OFF)
            self.change_mapping_status('陶瓷灯', self.rtc.ON)
        else:
            if self.rtc.status.get('降温风扇',
                                   self.rtc.OFF) == self.rtc.ON and self.current_temp <= self.target_temp and (
                    current_time - self.last_control_time['降温风扇']) > timedelta(minutes=1):
                self.change_mapping_status('降温风扇', self.rtc.OFF)
            self.change_mapping_status('陶瓷灯', self.rtc.OFF)

    def controller(self, sec):
        try:
            while True:
                self.update_day_night_status()
                self.check_temp()
                self.control_lamps()
                self.control_fans_and_heaters()
                self.equipment_actions()
                self.rtc.save_to_json(self.target_temp)
                time.sleep(sec)  # 确保每分钟执行一次
        except KeyboardInterrupt:
            logger.info("Controller stopped by user.")


schedule = Schedule(day_time=8, uv_start_time=12, night_time=22, day_temp=30, night_temp=28, target_temp=27)


@app.route('/control', methods=['POST'])
def control():
    data = request.json
    equipment = data.get('equipment')
    action = data.get('action')
    if equipment not in schedule.equipment_mapping:
        return jsonify({"error": "Invalid equipment name"}), 400
    if action not in [schedule.rtc.ON, schedule.rtc.OFF]:
        return jsonify({"error": "Invalid action"}), 400

    schedule.change_mapping_status(equipment, action, source='api')
    schedule.equipment_action(equipment, action)
    return jsonify({"message": "Success"}), 200


def run_controller():
    schedule.controller(30)


def run_server():
    app.run(host='0.0.0.0', port=5000)


def main():
    controller_thread = Thread(target=run_controller)
    server_thread = Thread(target=run_server)

    controller_thread.start()
    server_thread.start()

    controller_thread.join()
    server_thread.join()


if __name__ == "__main__":
    main()

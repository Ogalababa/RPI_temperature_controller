#!/usr/bin/python3
# coding:utf-8
# /main.py
import argparse
import time
from datetime import datetime
from run.RTC import RTC
import logging
import threading
from flask import Flask, request, jsonify, render_template

# 设置logging基础配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])  # 输出到控制台
logger = logging.getLogger(__name__)


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
            if self.rtc.status.get('降温风扇', self.rtc.OFF) == self.rtc.ON and self.current_temp <= self.target_temp:
                self.change_mapping_status('降温风扇', self.rtc.OFF)
            self.change_mapping_status('陶瓷灯', self.rtc.OFF)

    def controller(self, sec):
        try:
            while True:
                start_time = time.time()
                self.update_day_night_status()
                self.check_temp()
                self.control_lamps()
                self.control_fans_and_heaters()
                self.equipment_actions()
                self.rtc.save_to_json(self.target_temp)

                time.sleep(sec)  # 确保每分钟执行一次
        except KeyboardInterrupt:
            logger.info("Controller stopped by user.")


# Flask API 部分
app = Flask(__name__)
schedule = Schedule(day_time=10, uv_start_time=16, night_time=22, day_temp=30, night_temp=28, target_temp=29)

# 全局锁用于线程同步
lock = threading.Lock()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status', methods=['GET'])
def get_status():
    with lock:
        status = {
            'equipment': schedule.equipment_mapping,
            'current_temp': schedule.current_temp,
            'target_temp': schedule.target_temp,
            'temp_status': schedule.temp_status,
            'is_day': schedule.is_day,
            'is_uv': schedule.is_uv
        }
    return jsonify(status)


@app.route('/control', methods=['POST'])
def control_equipment():
    with lock:
        data = request.json
        equipment = data.get('equipment')
        action = data.get('action')
        if equipment in schedule.equipment_mapping and action in [schedule.rtc.ON, schedule.rtc.OFF]:
            schedule.change_mapping_status(equipment, action)
            schedule.equipment_action(equipment, action)
            return jsonify({'message': 'Success', 'equipment': equipment, 'action': action}), 200
        else:
            return jsonify({'message': 'Invalid equipment or action'}), 400


def run_controller():
    schedule.controller(30)


def main():
    # 创建ArgumentParser对象
    parser = argparse.ArgumentParser(description="Schedule Controller")

    # 添加参数
    parser.add_argument('--day_time', type=int, default=10, help='Day time')
    parser.add_argument('--uv_start_time', type=int, default=16, help='UV start time')
    parser.add_argument('--night_time', type=int, default=22, help='Night time')
    parser.add_argument('--day_temp', type=int, default=30, help='Day temperature')
    parser.add_argument('--night_temp', type=int, default=28, help='Night temperature')
    parser.add_argument('--target_temp', type=int, default=29, help='Target temperature')
    parser.add_argument('--sleep', type=int, default=300, help='Parameter for controller method')

    # 解析命令行参数
    args = parser.parse_args()

    # 更新 Schedule 对象的参数
    schedule.day_time = args.day_time
    schedule.uv_start_time = args.uv_start_time
    schedule.night_time = args.night_time
    schedule.day_temp = args.day_temp
    schedule.night_temp = args.night_temp
    schedule.target_temp = args.target_temp

    # 启动控制器线程
    controller_thread = threading.Thread(target=run_controller)
    controller_thread.daemon = True
    controller_thread.start()

    # 启动 Flask 应用
    app.run(host='0.0.0.0', port=5000)


if __name__ == "__main__":
    main()

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
from flask_socketio import SocketIO, emit

# 设置logging基础配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])  # 输出到控制台
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app)
schedule = None


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
        self.last_update = None
        self.manual_control = {
            '降温风扇': False,
            '陶瓷灯': False,
            'UV 灯': False,
            '日光灯': False,
        }
        self.equipment_mapping = {
            '降温风扇': self.rtc.OFF,
            '陶瓷灯': self.rtc.OFF,
            'UV 灯': self.rtc.OFF,
            '日光灯': self.rtc.OFF,
        }

    def reset_manual_control(self):
        for equipment in self.manual_control:
            self.manual_control[equipment] = False

    def update_day_night_status(self):
        hour = datetime.now().hour
        if hour == 0:
            self.reset_manual_control()
        self.is_day = self.day_time <= hour < self.uv_start_time
        self.is_uv = self.uv_start_time <= hour < self.night_time
        logger.info("Day time activate" if self.is_day else "Night time activate")
        logger.info("UV time activate" if self.is_uv else "UV time deactivate")

    def check_temp(self):
        self.last_update = datetime.now()
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

    def change_mapping_status(self, equipment, status, manual=False):
        if equipment in self.equipment_mapping:
            if manual:
                self.manual_control[equipment] = True
            self.equipment_mapping[equipment] = status

    def equipment_action(self, equipment, desired_status):
        current_status = self.rtc.status.get(equipment, self.rtc.OFF)
        if current_status != desired_status:
            self.rtc.controller(equipment, desired_status)

    def equipment_actions(self):
        for equipment, status in self.equipment_mapping.items():
            if not self.manual_control[equipment]:
                self.equipment_action(equipment, status)

    def control_lamps(self):
        if not self.manual_control['日光灯']:
            if self.is_day:
                self.change_mapping_status('日光灯', self.rtc.ON)
            else:
                self.change_mapping_status('日光灯', self.rtc.OFF)
        if not self.manual_control['UV 灯']:
            if self.is_uv:
                self.change_mapping_status('UV 灯', self.rtc.ON)
            else:
                self.change_mapping_status('UV 灯', self.rtc.OFF)

    def control_fans_and_heaters(self):
        if not self.manual_control['降温风扇'] and not self.manual_control['陶瓷灯']:
            if self.temp_status == 'hot':
                self.change_mapping_status('降温风扇', self.rtc.ON)
                self.change_mapping_status('陶瓷灯', self.rtc.OFF)
            elif self.temp_status == 'cold':
                self.change_mapping_status('降温风扇', self.rtc.OFF)
                self.change_mapping_status('陶瓷灯', self.rtc.ON)
            else:
                if self.rtc.status.get('降温风扇',
                                       self.rtc.OFF) == self.rtc.ON and self.current_temp <= self.target_temp:
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

                socketio.emit('status_update', self.get_status_data())  # 发送更新状态到客户端

                time.sleep(sec)  # 确保每分钟执行一次
        except KeyboardInterrupt:
            logger.info("Controller stopped by user.")

    def get_status_data(self):
        return {
            'equipment': self.equipment_mapping,
            'manual_control': self.manual_control,
            'current_temp': self.current_temp,
            'target_temp': self.target_temp,
            'temp_status': self.temp_status,
            'is_day': self.is_day,
            'last_update': self.last_update
        }


# Flask API 部分
app = Flask(__name__)
socketio = SocketIO(app)

# 全局锁用于线程同步
lock = threading.Lock()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status', methods=['GET'])
def get_status():
    with lock:
        status = schedule.get_status_data()
    return jsonify(status)


@app.route('/control', methods=['POST'])
def control_equipment():
    with lock:
        data = request.json
        equipment = data.get('equipment')
        action = data.get('action')
        mode = data.get('mode', 'auto')  # 默认为自动模式
        if equipment in schedule.equipment_mapping and action in [schedule.rtc.ON, schedule.rtc.OFF]:
            manual = mode == 'manual'
            if manual:
                schedule.manual_control[equipment] = True
                schedule.change_mapping_status(equipment, action, manual=True)
            else:
                schedule.manual_control[equipment] = False
            schedule.equipment_action(equipment, action)
            socketio.emit('status_update', schedule.get_status_data())  # 发送更新状态到客户端
            return jsonify({'message': 'Success', 'equipment': equipment, 'action': action, 'mode': mode}), 200
        else:
            return jsonify({'message': 'Invalid equipment or action'}), 400


def run_controller():
    schedule.controller(0)


def main():
    global schedule
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
    schedule = Schedule(day_time=args.day_time, uv_start_time=args.uv_start_time, night_time=args.night_time,
                        day_temp=args.day_temp, night_temp=args.night_temp, target_temp=args.target_temp)

    # 启动控制器线程
    controller_thread = threading.Thread(target=run_controller)
    controller_thread.daemon = True
    controller_thread.start()

    # 启动 Flask-SocketIO 应用
    socketio.run(app, host='0.0.0.0', port=520)


if __name__ == "__main__":
    main()

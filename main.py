import argparse
import time
import logging
import threading
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from run.RTC import RTC  # 假设RTC模块在同一目录下

# Flask and SocketIO setup
app = Flask(__name__)
socketio = SocketIO(app)

# Logging configuration
log_filename = "app_logs.txt"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(),  # Output to console
                              logging.FileHandler(log_filename)])  # Output to file
logger = logging.getLogger(__name__)

class SocketIOHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        with app.app_context():
            socketio.emit('log_message', {'message': log_entry})

# Add the SocketIO handler to logger
socketio_handler = SocketIOHandler()
socketio_handler.setLevel(logging.INFO)
socketio_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(socketio_handler)

# Global schedule object
schedule = None

class Schedule:
    def __init__(self, day_time=9, uv_start_time=16, night_time=22, target_temp=25):
        self.rtc = RTC()
        self.day_time = day_time
        self.night_time = night_time
        self.uv_start_time = uv_start_time
        self.target_temp = float(target_temp)
        self.day_temp = float(target_temp)
        self.night_temp = float(target_temp) - 4
        self.is_day = False
        self.is_uv = False
        self.temp_status = 'good'
        self.current_temp = 0.0
        self.current_hum = 0.0
        self.control_temp = 0.0
        self.control_hum = 0.0
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
        try:
            self.current_temp, self.current_hum = self.rtc.get_room_temp()
            self.control_temp, self.control_hum = self.rtc.get_control_temp()
            logger.info(f"Current Temp: {self.current_temp}°C")
            logger.info(f"Current Hum: {self.current_hum}%")
            logger.info(f"Control Room Temp: {self.control_temp}°C")
            logger.info(f"Control Room Hum: {self.control_hum}%")
        except Exception as e:
            logger.error(f"Error getting control temp: {e}")
            return

        if self.is_day or self.is_uv:
            self.target_temp = self.day_temp
        else:
            self.target_temp = self.night_temp
        logger.info(f"Target Temp: {self.target_temp}°C")

        temp_diff = float(self.current_temp) - float(self.target_temp)
        if temp_diff >= 2:
            self.temp_status = 'hot'
        elif temp_diff <= -2:
            self.temp_status = 'cold'
        else:
            self.temp_status = 'good'
        logger.info(f"Temperature Status: {self.temp_status}")

    def change_mapping_status(self, equipment, status, manual=False):
        if equipment in self.equipment_mapping:
            if manual:
                self.manual_control[equipment] = True
            self.equipment_mapping[equipment] = status

    def set_equipment_status(self, equipment, status):
        if equipment in self.equipment_mapping:
            self.equipment_mapping[equipment] = status
            logger.info(f"Set {equipment} to {'ON' if status == self.rtc.ON else 'OFF'}")

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
            self.set_equipment_status('日光灯', self.rtc.ON if self.is_day else self.rtc.OFF)
        if not self.manual_control['UV 灯']:
            self.set_equipment_status('UV 灯', self.rtc.ON if self.is_uv else self.rtc.OFF)

    def control_fans_and_heaters(self):
        if not self.manual_control['降温风扇'] and not self.manual_control['陶瓷灯']:
            if self.temp_status == 'hot':
                if self.current_temp >= self.day_temp:
                    self.set_equipment_status('降温风扇', self.rtc.ON)
                else:
                    self.set_equipment_status('降温风扇', self.rtc.OFF)
                self.set_equipment_status('陶瓷灯', self.rtc.OFF)

            elif self.temp_status == 'cold':
                self.set_equipment_status('降温风扇', self.rtc.OFF)
                if self.current_temp <= self.night_temp:
                    self.set_equipment_status('陶瓷灯', self.rtc.ON)
                else:
                    self.set_equipment_status('陶瓷灯', self.rtc.OFF)
            else:
                if self.rtc.status.get('降温风扇', self.rtc.OFF) == self.rtc.ON and self.current_temp <= self.target_temp:
                    self.set_equipment_status('降温风扇', self.rtc.OFF)
                self.set_equipment_status('陶瓷灯', self.rtc.OFF)

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

                with app.app_context():
                    data = self.get_status_data()
                    socketio.emit('status_update', data)  # 发送更新状态到客户端

                time.sleep(sec)  # 确保每分钟执行一次
        except KeyboardInterrupt:
            logger.info("Controller stopped by user.")

    def get_status_data(self):
        return {
            'equipment': self.equipment_mapping,
            'manual_control': self.manual_control,
            'current_temp': self.current_temp,
            'current_hum': self.current_hum,
            'control_temp': self.control_temp,
            'control_hum': self.control_hum,
            'target_temp': self.target_temp,
            'day_temp': self.day_temp,
            'night_temp': self.night_temp,
            'temp_status': self.temp_status,
            'is_day': self.is_day,
            'is_uv': self.is_uv,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }

# Flask API 部分
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def get_status():
    status = schedule.get_status_data()
    return jsonify(status)

@app.route('/logs', methods=['GET'])
def get_logs():
    with open(log_filename, 'r') as file:
        logs = file.readlines()
    last_10_logs = logs[-10:]  # 获取最后10条日志
    return jsonify({'logs': ''.join(last_10_logs)})


@app.route('/control', methods=['POST'])
def control_equipment():
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
        socketio.emit('status_update', schedule.get_status_data())
        return jsonify({'message': 'Success', 'equipment': equipment, 'action': action, 'mode': mode}), 200
    else:
        return jsonify({'message': 'Invalid equipment or action'}), 400

@socketio.on('set_target_temperature')
def handle_set_target_temperature(data):
    target_temp = data.get('target_temp')
    if target_temp is not None:
        schedule.target_temp = float(target_temp)
        schedule.day_temp = float(target_temp)
        schedule.night_temp = float(target_temp) - 4
        socketio.emit('status_update', schedule.get_status_data())
        emit('temperature_set', {'message': 'Temperature set successfully', 'target_temp': target_temp})
    else:
        emit('temperature_set', {'message': 'Invalid temperature value'}, status=400)

def run_controller():
    schedule.controller(0)

def main():
    global schedule
    parser = argparse.ArgumentParser(description="Schedule Controller")
    parser.add_argument('--day_time', type=int, default=10, help='Day time')
    parser.add_argument('--uv_start_time', type=int, default=16, help='UV start time')
    parser.add_argument('--night_time', type=int, default=22, help='Night time')
    parser.add_argument('--target_temp', type=float, default=27, help='Target temperature')
    parser.add_argument('--sleep', type=int, default=0, help='Parameter for controller method')
    args = parser.parse_args()

    schedule = Schedule(day_time=args.day_time, uv_start_time=args.uv_start_time, night_time=args.night_time,
                        target_temp=args.target_temp)

    controller_thread = threading.Thread(target=run_controller)
    controller_thread.daemon = True
    controller_thread.start()

    socketio.run(app, host='0.0.0.0', port=520, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()

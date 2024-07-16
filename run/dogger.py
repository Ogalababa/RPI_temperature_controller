#!/usr/bin/python3
# coding:utf-8
import json
import os
from datetime import datetime, timedelta
import time
import subprocess
import logging

# 配置日志记录
logging.basicConfig(filename='/home/jiawei/RPI_temperature_controller/dogger.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')


def restart_raspberry_pi():
    try:
        logging.info("Restarting Raspberry Pi due to time discrepancy in database records")
        subprocess.run(["sudo", "reboot"])
    except Exception as e:
        logging.error(f"Error occurred while restarting Raspberry Pi: {e}")


def check_last_record_time(minutes: int):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    try:
        with open(os.path.join(parent_dir, "status.json"), "r") as json_file:
            data = json.load(json_file)

        last_record_time = datetime.fromisoformat(data['最后更新'])
        current_time = datetime.now()

        if current_time - last_record_time > timedelta(minutes=minutes):
            return True
    except Exception as e:
        logging.error(f"Error while checking last record in status.json: {e}")

    return False


def main():
    logging.info("Database monitoring script started")
    time.sleep(300)
    while True:
        time.sleep(240)  # 等待5分钟
        if check_last_record_time(10):
            restart_raspberry_pi()


if __name__ == "__main__":
    main()

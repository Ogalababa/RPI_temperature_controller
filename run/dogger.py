#!/usr/bin/python3
# coding:utf-8
import pandas as pd
import os
from sqlalchemy import create_engine
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


def check_last_record_time():
    try:
        conn = create_engine(
            f'sqlite:///{os.path.join("/", "home", "jiawei", "RPI_temperature_controller", "data", "Status.db")}').connect()

        last_record = pd.read_sql_query("SELECT * FROM Status ORDER BY 时间 DESC LIMIT 1", conn)
        conn.close()

        if not last_record.empty:
            last_record_time = pd.to_datetime(last_record['时间'].iloc[0])
            current_time = datetime.now()

            if current_time - last_record_time > timedelta(minutes=5):
                return True
    except Exception as e:
        logging.error(f"Error while checking last record in database: {e}")
    return False


def main():
    logging.info("Database monitoring script started")
    time.sleep(300)
    while True:
        time.sleep(300)  # 等待5分钟
        if check_last_record_time():
            restart_raspberry_pi()


if __name__ == "__main__":
    main()

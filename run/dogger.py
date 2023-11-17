#!/usr/bin/python3
# coding:utf-8
import pandas as pd
import os
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import time
import subprocess


def restart_raspberry_pi():
    # 使用 subprocess 来重启树莓派
    subprocess.run(["sudo", "reboot"])


def check_last_record_time():
    conn = create_engine(
        f'sqlite:///{os.path.join("/", "home", "jiawei", "RPI_temperature_controller", "data", "Status.db")}').connect()

    # 读取最后一条记录
    last_record = pd.read_sql_query("SELECT * FROM Status ORDER BY 时间 DESC LIMIT 1", conn)
    conn.close()

    # 检查记录的时间
    if not last_record.empty:
        last_record_time = pd.to_datetime(last_record['时间'].iloc[0])
        current_time = datetime.now()

        # 检查时间差
        if current_time - last_record_time > timedelta(minutes=10):
            return True
    return False


def main():
    while True:
        if check_last_record_time():
            restart_raspberry_pi()
        time.sleep(300)  # 等待5分钟


if __name__ == "__main__":
    main()

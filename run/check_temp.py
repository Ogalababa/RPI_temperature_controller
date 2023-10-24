#!/usr/bin/python3
# coding:utf-8
import time
from objects import rtc_instance
from objects import db_instance as db

if __name__ == "__main__":
    while True:
        current_temp = rtc_instance.get_control_temp()
        current_hum = rtc_instance.control_hum
        db.set_target_temp("current status", {'current temp': current_temp, "current hum": current_hum})
        print(f'Current temperature: {current_temp} C')
        print(f'Current humility: {current_hum}%')
        time.sleep(5)

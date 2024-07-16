# ！/usr/bin/python3
# coding:utf-8
# sys
from run.noDB_Schedule import Schedule

temp_controller = Schedule(day_time=10, uv_start_time=16, night_time=22, day_temp=30,  night_temp=28, target_temp=29)
temp_controller.controller()

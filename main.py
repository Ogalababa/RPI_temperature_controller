# ！/usr/bin/python3
# coding:utf-8
# sys
from run.TC import TC

temp_controller = TC(target_day=32, target_night=30, temp_range=2)
temp_controller.temperature_controller()

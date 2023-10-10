# ！/usr/bin/python3
# coding:utf-8
# sys
import time

from RTC import RTC
from RTC import cleanup

if __name__ == "__main__":
    print("Initialization Status")
    rtc = RTC()
    time.sleep(5)
    for equipment in rtc.PINS["OUTPUT"].keys():
        rtc.controller(equipment, rtc.ON)

        time.sleep(1)
    for equipment in rtc.PINS["OUTPUT"].keys():
        rtc.controller(equipment, rtc.OFF)
        time.sleep(1)
    # rtc.get_room_temp()
    # print(rtc.temp)
    # print(rtc.hum)
    # rtc.get_control_temp()
    # print(rtc.control_temp)
    # print(rtc.control_hum)
    time.sleep(1)
    rtc.controller("降温风扇", rtc.ON)
    time.sleep(60)
    rtc.controller("降温风扇", rtc.OFF)

    cleanup()
    exit()

from RTC import RTC
from RTC import cleanup
import time

if __name__ == "__main__":
    rtc = RTC()
    for equipment in rtc.PINS["OUTPUT"].keys():
        rtc.controller(equipment, rtc.ON)
        print(f"{equipment} ON")
        time.sleep(1)
    for equipment in rtc.PINS["OUTPUT"].keys():
        rtc.controller(equipment, rtc.OFF)
        print(f"{equipment} OFF")
        time.sleep(1)
    cleanup()
    exit()
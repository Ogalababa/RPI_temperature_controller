from RTC import RTC
from RTC import cleanup
import time

if __name__ == "__main__":
    print("Initialization Status")
    rtc = RTC()
    time.sleep(5)
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
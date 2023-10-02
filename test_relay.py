from RTC import RTC
from RTC import cleanup
import time

if __name__ == "__main__":
    rtc = RTC()
    time.sleep(10)
    cleanup()
    exit()
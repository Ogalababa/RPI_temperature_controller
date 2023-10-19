from objects import rtc_instance as rtc
from objects import db_instance as db
import time

if __name__ == '__main__':
    while True:
        temp = rtc.get_control_temp()
        hum = rtc.control_hum
        data_dict = {
            '温度': temp,
            '湿度': hum
        }
        db.set_target_temp('actual_temp', data_dict)
        time.sleep(10)

import os.path
import time
import pytz
import logging
from RTC import RTC
from __init__ import current_dir


def setup_logging():
    logging.basicConfig(filename=os.path.join(current_dir, 'temperature_controller.log'),
                        level=logging.INFO,
                        format='%(asctime)s - %(message)s')
    return logging.getLogger()


class TemperatureController:

    def __init__(self, target_temp_day=32, target_temp_night=31, temp_range=2, timezone='Europe/Amsterdam'):
        self.datetime = None
        self.rtc = RTC()
        self.target_temp_day = target_temp_day
        self.target_temp_night = target_temp_night
        self.temp_range = temp_range
        self.timezone = pytz.timezone(timezone)
        self.logger = setup_logging()
        self.equipment_mapping = {
            '加温风扇': self.rtc.ON,
            'UV 灯': self.rtc.OFF,
            '日光灯': self.rtc.OFF,
            '陶瓷灯': self.rtc.OFF,
            '降温风扇': self.rtc.OFF
        }
        self.hourly_functions = {
            (10, 16): self.update_daytime_equipment,
            (16, 24): self.update_nighttime_equipment
        }

    def update_equipment_status(self, equipment, desired_status):
        current_status = self.rtc.status.get(equipment, self.rtc.OFF)
        if current_status != desired_status:
            self.rtc.controller(equipment, desired_status)

    def control_temperature(self):
        while True:
            current_temp = self.rtc.get_control_temp()
            current_hour = self.get_current_hour()
            self.update_equipment_status('加温风扇', self.rtc.ON)

            for (start_hour, end_hour), equipment_function in self.hourly_functions.items():
                if start_hour <= current_hour < end_hour:
                    equipment_function(current_temp)

            self.rtc.save_to_json()
            self.log_temperature_status(current_temp)
            time.sleep(54)  # Adjust this value as per your requirement

    def get_current_hour(self):
        return self.datetime.now(self.timezone).hour

    def update_daytime_equipment(self, current_temp):
        self.equipment_mapping['日光灯'] = self.rtc.OFF
        self.equipment_mapping['UV 灯'] = self.rtc.ON

        if current_temp < self.target_temp_day - self.temp_range:
            self.equipment_mapping['日光灯'] = self.rtc.ON
            self.equipment_mapping['降温风扇'] = self.rtc.OFF

        elif self.target_temp_day <= current_temp <= self.target_temp_day + self.temp_range:
            self.equipment_mapping['降温风扇'] = self.rtc.OFF

        elif current_temp > self.target_temp_day + self.temp_range:
            self.equipment_mapping['加温风扇'] = self.rtc.OFF
            self.equipment_mapping['降温风扇'] = self.rtc.ON

        self.update_equipment_statuses()

    def update_nighttime_equipment(self, current_temp):
        self.equipment_mapping['日光灯'] = self.rtc.OFF

        if current_temp < self.target_temp_night - self.temp_range:
            self.equipment_mapping['陶瓷灯'] = self.rtc.ON
            self.equipment_mapping['加温风扇'] = self.rtc.ON
            self.equipment_mapping['降温风扇'] = self.rtc.OFF

        elif self.target_temp_night <= current_temp <= self.target_temp_night + self.temp_range:
            self.equipment_mapping['陶瓷灯'] = self.rtc.OFF
            self.equipment_mapping['加温风扇'] = self.rtc.OFF

        elif current_temp > self.target_temp_night + self.temp_range:
            self.equipment_mapping['降温风扇'] = self.rtc.ON

        self.update_equipment_statuses()

    def update_equipment_statuses(self):
        for equipment, status in self.equipment_mapping.items():
            self.update_equipment_status(equipment, status)

    def log_temperature_status(self, current_temp):
        self.logger.info(f"Temperature: {current_temp}, Status: {self.rtc.status}")


if __name__ == '__main__':
    temp_controller = TemperatureController(target_temp_day=32, target_temp_night=30, temp_range=2, 
                                            timezone='Europe/Amsterdam')
    temp_controller.control_temperature()

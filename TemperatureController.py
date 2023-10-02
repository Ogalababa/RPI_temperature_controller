import time
from datetime import datetime
import pytz
from RTC import RTC

class TemperatureController:

    def __init__(self):
        self.rtc = RTC()
        self.target_temp = 30
        self.amsterdam = pytz.timezone('Europe/Amsterdam')
        self.temp_range = 5

    def update_equipment_status(self, equipment, desired_status):
        current_status = getattr(self.rtc, f'{equipment}_status')
        if current_status != desired_status:
            self.rtc.controller(getattr(self.rtc, equipment), getattr(self.rtc, desired_status))

    def control_temperature(self):
        while True:
            self.rtc.get_room_temp()
            current_temp = self.rtc.temp
            current_hour = datetime.now(self.amsterdam).hour

            if 10 <= current_hour < 24:
                # check night lamp status:
                self.update_equipment_status('night_lamp', 'OFF')

                if current_temp < self.target_temp - self.temp_range:  # It's too cold
                    self.update_equipment_status('sun_lamp', 'ON')
                    self.update_equipment_status('warm_fan', 'ON')
                    self.update_equipment_status('cool_fan', 'OFF')

                elif self.target_temp - 3 <= current_temp <= self.target_temp + 3:  # It's good temp
                    self.update_equipment_status('sun_lamp', 'OFF')
                    self.update_equipment_status('warm_fan', 'OFF')
                    self.update_equipment_status('cool_fan', 'OFF')

                elif current_temp >= self.target_temp + self.temp_range:  # It's too hot
                    self.update_equipment_status('sun_lamp', 'OFF')
                    self.update_equipment_status('warm_fan', 'OFF')
                    self.update_equipment_status('cool_fan', 'ON')

            else:
                self.update_equipment_status('sun_lamp', 'OFF')

            time.sleep(60)  # Adjust this value as per your requirement

if __name__ == "__main__":
    temp_controller = TemperatureController()
    temp_controller.control_temperature()

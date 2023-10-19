from ToDB import ConnectToDB
from RTC import RTC
import os

rtc_instance = RTC()
db_instance = ConnectToDB('Status', os.path.join('/', 'jiawei', 'RPI_temperature_controller', 'data'))


from rpi_lcd import LCD
from time import sleep
import json


DEGREE_SIGN = u'\xb0' #degree sign
TEM_SIGN = f"{DEGREE_SIGN}C"

lcd = LCD()


def status_to_str(status):
    if status is Ture:
        return "ON"
    else:
        return "OFF"


def show_lamp_status():
    with open('status.json', 'r') as file:
        status = json.load(file)
    lcd.text(f"Ni:{status_to_str(status.get('night_lamp_status'))} "
             f"Su:{status_to_str(status.get('sun_lamp_status'))} "
             f"UV:{status_to_str(status.get('uv_lamp_status'))} ", 1)

    lcd.text(f"WF:{status_to_str(status.get('warm_fan_status'))} "
             f"CF:{status_to_str(status.get('cool_fan_status'))} "
             f"CL:{status_to_str(status.get('controller_fan_status'))} ", 2)
    temp, humi = get_room_temp()
    ldc.text(f'Temp: {temp} {TEM_SIGN}', 3)
    ldc.text(f'Humi: {humi} %', 4)


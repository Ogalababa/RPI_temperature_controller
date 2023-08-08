from Params import *
import Adafruit_DHT as DHT
import time

TEMP_SENSOR = DHT.DHT11

def get_room_temp():
    
    temp_list = []
    hum_list = []
    termo_list = [TERMO_L, TERMO_R, TERMO_M, TERMO_F]

    for i in termo_list:
        temp_1, hum_1 = DHT.read_retry(TEMP_SENSOR, i)
        temp_list.append(temp_1)
        hum_list.append(hum_1)
    
    temp_list = [i for i in temp_list if i is not None]
    hum_list = [i for i in hum_list if i is not None]
    
    temp = sum(temp_list) / len(temp_list)
    hum = sum(hum_list) / len(hum_list)

    return round(temp, 2), round(hum, 2)

def get_control_temp():
    
    temp_list = []
    hum_list = []
    
    for i in range(4):
        temp, hum = DHT.read_retry(TEMP_SENSOR, TERMO_CL)
        if temp is not None and hum is not None:
            temp_list.append(temp)
            hum_list.append(hum)
        else:
            time.sleep(5)
        time.sleep(1)
    
    temp_final = sum(temp_list)/len(temp_list)
    hum_final = sum(hum_list)/len(temp_list)
    return round(temp_final, 2), round(hum_final, 2)


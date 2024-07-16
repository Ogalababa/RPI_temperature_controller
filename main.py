# ！/usr/bin/python3
# coding:utf-8
# sys
import argparse
# from run.noDB_Schedule import Schedule
from run.flask_Schedule import Schedule
from threading import Thread
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.post('/control')
def control(control: EquipmentControl):
    equipment = control.equipment
    action = control.action
    if equipment not in schedule.equipment_mapping:
        raise HTTPException(status_code=400, detail="Invalid equipment name")
    if action not in [schedule.rtc.ON, schedule.rtc.OFF]:
        raise HTTPException(status_code=400, detail="Invalid action")

    schedule.change_mapping_status(equipment, action, source='api')
    schedule.equipment_action(equipment, action)
    return {"message": "Success"}

class EquipmentControl(BaseModel):
    equipment: str
    action: str
def main():
    # 创建ArgumentParser对象
    parser = argparse.ArgumentParser(description="Schedule Controller")

    # 添加参数
    parser.add_argument('--day_time', type=int, default=10, help='Day time')
    parser.add_argument('--uv_start_time', type=int, default=16, help='UV start time')
    parser.add_argument('--night_time', type=int, default=22, help='Night time')
    parser.add_argument('--day_temp', type=int, default=30, help='Day temperature')
    parser.add_argument('--night_temp', type=int, default=28, help='Night temperature')
    parser.add_argument('--target_temp', type=int, default=29, help='Target temperature')
    parser.add_argument('--sleep', type=int, default=300, help='Parameter for controller method')

    # 解析命令行参数
    args = parser.parse_args()

    # 创建Schedule对象
    temp_controller = Schedule(
        day_time=args.day_time,
        uv_start_time=args.uv_start_time,
        night_time=args.night_time,
        day_temp=args.day_temp,
        night_temp=args.night_temp,
        target_temp=args.target_temp
    )

    # 调用controller方法
    # temp_controller.controller(args.sleep)
    controller_thread = Thread(target=temp_controller.controller, args=(args.sleep,))
    controller_thread.start()

    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)

    controller_thread.join()


if __name__ == "__main__":
    main()

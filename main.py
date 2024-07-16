# ！/usr/bin/python3
# coding:utf-8
# sys
import argparse
from run.noDB_Schedule import Schedule


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
    temp_controller.controller(args.sleep)


if __name__ == "__main__":
    main()

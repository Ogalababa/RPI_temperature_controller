# ！/usr/bin/python3
# coding:utf-8
# sys
import json
import os
import time
from pathlib import Path

from PIL import ImageFont
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106


def read_status():
    current_dir = Path(__file__).parent
    try:
        with open(os.path.join(current_dir, "status.json"), "r") as file:
            data = json.load(file)
        return data
    except:
        return {"读取错误": "Error", "jiawei@rasp.local": "SSH"}


def display_on_oled():
    serial = i2c(port=1, address=0x3C)
    device = sh1106(serial, rotate=0)

    font_path = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    font = ImageFont.truetype(font_path, size=14)  # 使用相同的字体大小

    while True:
        data = read_status()  # 每分钟刷新数据
        with canvas(device) as draw:
            y_position = 0  # 初始化y轴位置
            for key, value in data.items():
                text_line = f"{key}: {value}"
                draw.text((0, y_position), text_line, fill="white", font=font)
                y_position += 20  # 更新y轴位置以便下一行文本
        time.sleep(10)  # 每分钟刷新一次显示内容


def main():
    display_on_oled()


if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            pass

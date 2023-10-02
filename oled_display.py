from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import time

def main():
    # 初始化OLED设备
    serial = i2c(port=1, address=0x3C)
    device = sh1106(serial)

    # 使用canvas绘制简单的文本
    with canvas(device) as draw:
        draw.text((10, 10), "Hello, World!", fill="white")
        draw.text((10, 30), "This is SH1106!", fill="white")

    # 保持内容显示5秒
    time.sleep(5)

if __name__ == "__main__":
    main()

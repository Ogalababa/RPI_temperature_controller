import os.path
import time
import json
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont


def read_status():
    with open(os.path.join("/","home","jiawei","RPI_temperature_controller","status.json"), "r") as file:
        data = json.load(file)
    return data


def display_on_oled():
    serial = i2c(port=1, address=0x3C)
    device = sh1106(serial, rotate=0)

    font_path_small = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    font_path_large = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"

    font_small = ImageFont.truetype(font_path_small, size=20)
    font_large = ImageFont.truetype(font_path_large, size=40)

    while True:
        data = read_status()  # Refresh the data every minute
        start_time = time.time()

        while time.time() - start_time < 60:  # Keep displaying for 1 minute
            for key, value in data.items():
                with canvas(device) as draw:
                    draw.text((0, 0), key, fill="white", font=font_small)
                    draw.text((0, 14), str(value), fill="white", font=font_large)
                time.sleep(2)  # Display each key-value pair for 2 seconds


def main():
    display_on_oled()


if __name__ == "__main__":
    main()

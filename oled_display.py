import time
import json
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont


def read_status():
    with open("status.json", "r") as file:
        data = json.load(file)
    return data


def display_on_oled():
    serial = i2c(port=1, address=0x3C)
    device = sh1106(serial, rotate=0)

    font_path_small = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    font_path_large = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"

    font_small = ImageFont.truetype(font_path_small, size=12)
    font_large = ImageFont.truetype(font_path_large, size=24)

    screen_width = device.width
    screen_height = device.height

    while True:
        data = read_status()  # Refresh the data every minute
        start_time = time.time()

        while time.time() - start_time < 60:  # Keep displaying for 1 minute
            for key, value in data.items():
                with canvas(device) as draw:
                    value_width, value_height = draw.textsize(str(value), font=font_large)

                    key_position = (0, 0)
                    value_position = (
                    (screen_width - value_width) // 2, (screen_height + value_height) // 2 - value_height)

                    draw.text(key_position, key, fill="white", font=font_small)
                    draw.text(value_position, str(value), fill="white", font=font_large)
                time.sleep(2)  # Display each key-value pair for 2 seconds


def main():
    display_on_oled()


if __name__ == "__main__":
    main()

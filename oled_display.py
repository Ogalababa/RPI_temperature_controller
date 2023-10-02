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


def display_on_oled(data):
    serial = i2c(port=1, address=0x3C)
    device = sh1106(serial, rotate=0)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, size=12)

    with canvas(device) as draw:
        y = 0
        for key, value in data.items():
            text = f"{key}: {value}"
            draw.text((0, y), text, fill="white", font=font)
            y += 14  # Adjust depending on your font size


def main():
    while True:
        data = read_status()
        display_on_oled(data)
        time.sleep(60)  # Wait for 1 minute before updating again


if __name__ == "__main__":
    main()

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

    total_height = len(data) * 14  # Assuming each line is 14 pixels high
    start_y = 0

    while True:
        with canvas(device) as draw:
            y = start_y
            for key, value in data.items():
                text = f"{key}: {value}"
                draw.text((0, y), text, fill="white", font=font)
                y += 14

        start_y -= 1  # Move the text up by 1 pixel
        if -start_y > total_height:
            start_y = 64  # Reset to the bottom once all the text has moved off the top
        time.sleep(0.05)  # Adjust speed as necessary


def main():
    data = read_status()
    display_on_oled(data)


if __name__ == "__main__":
    main()

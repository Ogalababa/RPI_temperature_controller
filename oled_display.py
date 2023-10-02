import time
import json
import socket
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont

# Function to get the IP address of the Raspberry Pi
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This command will not send anything outside of your local network
        s.connect(('10.255.255.255', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

class OLED_Display:

    def __init__(self):
        # Initialize OLED display
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_bus=1, gpio=1)  # If necessary, adjust these parameters
        self.disp.begin()
        self.disp.clear()
        self.disp.display()

        # Create a blank image for drawing.
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Load a font
        self.font = ImageFont.load_default()

    def display_data(self):
        while True:
            # Read data from status.json
            with open('status.json', 'r') as file:
                data = json.load(file)
            ip_address = get_ip_address()

            # Clear the display
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

            # Draw the IP Address
            y_position = 0
            self.draw.text((0, y_position), f"IP Address: {ip_address}", font=self.font, fill=255)
            y_position += 10

            # Draw the data from status.json
            for key, value in data.items():
                text = f"{key}: {value}"
                self.draw.text((0, y_position), text, font=self.font, fill=255)
                y_position += 10

            # Display the drawn image
            self.disp.image(self.image)
            self.disp.display()

            time.sleep(60)


if __name__ == '__main__':
    display = OLED_Display()
    display.display_data()

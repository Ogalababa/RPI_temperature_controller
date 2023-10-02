import time
import json
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont

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

            # Clear the display
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

            # Draw the data (modify this part as per your requirement)
            y_position = 0
            for key, value in data.items():
                text = f"{key}: {value}"
                self.draw.text((0, y_position), text, font=self.font, fill=255)
                y_position += 8  # Adjust this as per your text size

            # Display the drawn image
            self.disp.image(self.image)
            self.disp.display()

            time.sleep(60)

display = OLED_Display()
display.display_data()

from luma.core.interface.serial import spi
from luma.lcd.device import st7789
from PIL import Image, ImageDraw, ImageFont

class DisplayManager:
    def __init__(self):
        self.serial = spi(port=0, device=0, gpio_DC=8, gpio_RST=25, bus_speed_hz=40000000)
        self.disp = st7789(self.serial, width=240, height=240)
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)

    def display_text(self, text):
        width, height = self.disp.width, self.disp.height
        image = Image.new('RGB', (width, height), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)
        text_width, text_height = draw.textsize(text, font=self.font)
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, font=self.font, fill=(255, 255, 255))
        self.disp.display(image)

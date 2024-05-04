from leaphymicropython.actuators.ssd1306 import SSD1306I2C
from machine import Pin, SoftI2C

i2c = SoftI2C(scl=Pin(5), sda=Pin(4))

oled_WIDTH = 128
oled_HEIGHT = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.text("Hello, World 1!", 0, 0)
oled.text("Hello, World 2!", 0, 10)
oled.text("Hello, World 3!", 0, 20)

oled.show()

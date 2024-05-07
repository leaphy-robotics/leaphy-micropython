from machine import Pin, SoftI2C

from leaphymicropython.actuators import ssd1306

i2c = SoftI2C(scl=Pin(5), sda=Pin(4))

OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = ssd1306.SSD1306SPI(OLED_WIDTH, OLED_HEIGHT, i2c)

oled.text("Hello, World 1!", 0, 0)
oled.text("Hello, World 2!", 0, 10)
oled.text("Hello, World 3!", 0, 20)

oled.show()

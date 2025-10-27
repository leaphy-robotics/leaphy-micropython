"""Lets the rgb-led blink"""

from time import sleep
from leaphymicropython.actuators.rgbled import RGBLed

led = RGBLed("D1", "D2", "D4")
while True:
    led.set_color(255, 0, 0)
    sleep(1)
    led.set_color(0, 0, 0)
    sleep(1)

"""Lets the rgb-led blink"""
from leaphymicropython.actuators.rgbled import RGBLed
from time import sleep

led = RGBLed(1, 2, 4)
while True:
    led.set_color(255, 0, 0)
    sleep(1)
    led.set_color(0, 0, 0)
    sleep(1)
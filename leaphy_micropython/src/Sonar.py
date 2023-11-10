from .boards_config import pinToGPIO
from machine import Pin
import utime

def read_distance(trigPin: int, echoPin):
    """Reads distance from object"""
    trigger = pinToGPIO(trigPin)
    echo = pinToGPIO(echoPin)
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(5)
    trigger.low()
    while echo.value() == 0:
        signaloff = utime.ticks_us()
    while echo.value() == 1:
        signalon = utime.ticks_us()
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
    return distance
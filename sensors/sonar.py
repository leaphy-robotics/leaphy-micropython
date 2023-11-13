from leaphymicropython.utils.boards_config import pin_to_gpio
from machine import Pin
import utime


def read_distance(trigPin: int, echoPin: int):
    """Reads distance from object"""
    trigger_pin = pin_to_gpio(trigPin)
    echo_pin = pin_to_gpio(echoPin)
    trigger = Pin(trigger_pin, Pin.OUT)
    echo = Pin(echo_pin, Pin.IN)
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(5)
    trigger.low()
    signal_on: int
    signal_off: int
    while echo.value() == 0:
        signal_off = utime.ticks_us()
    while echo.value() == 1:
        signal_on = utime.ticks_us()
    time_passed = signal_on - signal_off
    return (time_passed * 0.0343) / 2
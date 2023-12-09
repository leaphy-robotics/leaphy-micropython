import utime
from machine import Pin

from leaphymicropython.utils.boards_config import pin_to_gpio


def read_distance(trig_pin: int, echo_pin: int) -> float:
    """Reads distance from object
    :param trig_pin: Trigger pin
    :param echo_pin: Echo pin
    :return: The distance
    """
    trigger_pin = pin_to_gpio(trig_pin)
    echo_pin = pin_to_gpio(echo_pin)
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

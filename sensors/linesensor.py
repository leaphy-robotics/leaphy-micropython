"""A module for the new leaphy line sensor"""
from machine import Pin
from leaphymicropython.utils.boards_config import pin_to_gpio


def read_line_sensor(pin: int) -> int:
    """
    Sets a pin
    :param pin: int, the pin to set
    :return: sensor_state: gives a value from the module
    """
    pin = pin_to_gpio(pin)
    pin = Pin(pin, Pin.IN)
    sensor_state = pin.value()
    return sensor_state

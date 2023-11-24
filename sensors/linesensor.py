"""A module for the new leaphy line sensor"""
from machine import Pin
from leaphymicropython.utils.pins import read_pin


def read_line_sensor(pin: int) -> bool:
    """
    Sets a pin
    :param pin: int, the pin to set
    :return: sensor_state: gives a value from the module
    """
    return read_pin(pin)
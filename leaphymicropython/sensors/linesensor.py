"""A module for the new leaphy line sensor"""
from leaphymicropython.utils.pins import read_pin
from leaphymicropython.utils.pins import read_analog


def read_line_sensor(pin: int) -> bool:
    """
    Sets a pin
    :param pin: int, the pin to set
    :return: sensor_state: gives a value from the module
    """
    return read_pin(pin)


def calibrate_analog_line_sensor(
    pin: int, below_white: int, above_black: int, test="yes"
):
    """
    Maps analog line sensor output to white | black | unclear

    :param pin: int, the pin to set
    :param below_white: int, below this value, the color is white
    :param above_black: int, above this value, the color is black
    :param test: str, if set to 'yes', the value and the mapped value are shown in the shell

    :return: color: white | black | unclear
    """
    value = read_analog(pin)
    color = "unclear"
    if value < below_white:
        color = "white"
    elif value > above_black:
        color = "black"

    if test == "yes":
        print(value, color)
    return color

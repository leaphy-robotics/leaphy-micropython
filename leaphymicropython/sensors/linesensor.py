"""A module for the new leaphy line sensor"""

from leaphymicropython.utils.pins import read_pin, read_analog, init_analog_pin


class AnalogIR:
    """
    A class to control the analog ir sensor
    """

    def __init__(self, pin_name, above_black=4000):
        """
        Initializes the AnalogIR object.

        Args:
            pin_name: The pin connect to the A0 pin of the IR sensor
            everything you provide to machine.Pin, you can provide here.
            above_black
            above_black (int, optional): the analog value is represented
            as a 16-bit unsigned integer ranging from 0 to 65535.
            Practically speaking, a reading of 0 means purely white is picked up
            a value of 65535 means that the sensor only picks up black.
            With this parameter, you can determine the threshold between a black
            and a white line. From experience, above 4000 usually indicates
            a black line, but obviously you can change this.
        """
        self.pin = init_analog_pin(pin_name)
        self.above_black = above_black

    def get_analog_value(self):
        """
        :return: the analog value
        """
        return self.pin.read_u16()

    def black_or_white(self):
        """
        :return: black or white
        Black is returned if the analog value is >= self.above_black
        """
        if self.get_analog_value() >= self.above_black:
            return "black"
        return "white"


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

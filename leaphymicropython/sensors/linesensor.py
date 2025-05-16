"""A module for the new leaphy line sensor"""

from leaphymicropython.utils.pins import get_analog_pin


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
        self.pin = get_analog_pin(pin_name)
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

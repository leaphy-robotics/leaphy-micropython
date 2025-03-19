"""This module provides time-of-flight related calculations."""  # Single-line docstring

from machine import I2C, Pin
from leaphymicropython.sensors.vl53l0x import VL53L0X
from leaphymicropython.utils.i2c_helper import select_channel


class TimeOfFlight:
    """
    Initializes the TimeOfFlight object.

    Args:
        channel (int, optional): The I2C multiplexer channel to select.
        Defaults to 255, indicating no multiplexer is used.
        sda_gpio_pin (int, optional): The GPIO pin connected to the SDA line. Defaults to 12.
        scl_gpio_pin (int, optional): The GPIO pin connected to the SCL line. Defaults to 13.
    """

    MULTIPLEXER_ADDRESS = 0x70

    def __init__(self, channel=255, sda_gpio_pin=12, scl_gpio_pin=13):
        """
        Initializes the TimeOfFlight object.

        Args:
            channel (int, optional): The I2C multiplexer channel to select.
            Defaults to 255, indicating no multiplexer is used.
            sda_gpio_pin (int, optional): The GPIO pin connected to the SDA line. Defaults to 12.
            scl_gpio_pin (int, optional): The GPIO pin connected to the SCL line. Defaults to 13.
        """
        self.channel = channel
        self.i2c = I2C(id=0, scl=Pin(scl_gpio_pin), sda=Pin(sda_gpio_pin))
        select_channel(self.i2c, self.MULTIPLEXER_ADDRESS, self.channel)
        self.tof = self.initialize_tof()
        self.reinitialize = False

    def initialize_tof(self):
        """
        initialize external library
        """
        return VL53L0X(self.i2c)

    def get_distance(self):
        """
        Retrieves the distance measurement from the VL53L0X sensor.

        If a multiplexer channel is specified (channel != 255),
        it selects the appropriate channel before reading from the sensor.

        Returns:
            int: The measured distance in millimeters.
        """
        select_channel(self.i2c, self.MULTIPLEXER_ADDRESS, self.channel)
        if self.reinitialize:
            try:
                self.__init__()
                self.reinitialize = False
            except Exception as e:
                if e.errno == 5:
                    value = None

        if self.reinitialize == False:
            try:
                value = self.tof.ping()
                self.reinitialize = False
            except Exception as e:
                if e.errno == 5:
                    self.reinitialize = True
                    value = None

        return value

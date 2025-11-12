"""This module provides OLED SSH1106 methods"""

from leaphymicropython.actuators.sh1106 import SH1106_I2C
from leaphymicropython.utils.i2c_helper import I2CDevice
from leaphymicropython.utils.i2c_helper import handle_i2c_errors


class OLEDSH1106(I2CDevice):
    """
    Initializes the OLED screen using the SSH1106 driver.

    Args:
        channel (int, optional): The I2C multiplexer channel to select.
        Defaults to 255, indicating no multiplexer is used.
        sda_gpio_pin (int, optional): The GPIO pin connected to the SDA line. Defaults to 12.
        scl_gpio_pin (int, optional): The GPIO pin connected to the SCL line. Defaults to 13.
        bus_id (int, optional): identifies a particular I2C peripheral, for example bus 0 or 1.
        show_warnings (bool,optional): if True, show warnings
    """

    # the following attribute is used by decorator handle_i2c_errors
    ADDRESS = 0x3C

    def __init__(
        self,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=0,
        show_warnings=True,
    ):
        """
        Initializes the OLED screen using the SSH1106 driver.

        Args:
            channel (int, optional): The I2C multiplexer channel to select.
            Options are: 0-7 and 255
            sda_gpio_pin (int, optional): The GPIO pin connected to the SDA line. Defaults to 12.
            scl_gpio_pin (int, optional): The GPIO pin connected to the SCL line. Defaults to 13.
            bus_id (int, optional): identifies a particular I2C peripheral, for example bus 0 or 1.
            show_warnings (bool, optional): if True, show warning about device address not found
        """
        super().__init__(channel, sda_gpio_pin, scl_gpio_pin, bus_id, show_warnings)
        self.tof = None
        self.find_device(show_warnings=self.show_warnings)

    def initialize_device(self):
        """
        initialize external library
        """
        raise NotImplementedError

    def fill(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def text(self):
        raise NotImplementedError

"""This module provides OLED SSH1106 methods"""

from leaphymicropython.actuators.sh1106 import SH1106_I2C
from leaphymicropython.utils.i2c_helper import I2CDevice
from leaphymicropython.utils.i2c_helper import handle_i2c_errors


class OLEDSH1106(I2CDevice):

    # the following attribute is used by decorator handle_i2c_errors.
    ADDRESS = 0x3C

    def __init__(
        self,
        height=64,
        width=128,
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
        self.screen = None
        self.height = height
        self.width = width

    def initialize_device(self):
        """
        initialize external library
        """
        super().initialize_device()
        self.screen = SH1106_I2C(self.width, self.height, self.i2c, addr=self.ADDRESS)

    @handle_i2c_errors
    def fill(self, color):
        self.screen.sleep(False)
        self.screen.fill(color)

    @handle_i2c_errors
    def text(self, text, x=0, y=0, color=1):
        self.screen.sleep(False)
        self.screen.text(text, x, y, color)

    @handle_i2c_errors
    def show(self):
        self.screen.sleep(False)
        self.screen.show()

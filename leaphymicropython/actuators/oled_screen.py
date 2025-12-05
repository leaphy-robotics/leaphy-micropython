"""This module provides OLED SSH1106 methods"""

from leaphymicropython.actuators.sh1106 import SH1106_I2C
from leaphymicropython.utils.i2c_helper import I2CDevice
from leaphymicropython.utils.i2c_helper import handle_i2c_errors


class OLEDSH1106(I2CDevice):
    """
    Initializes the TimeOfFlight object.

    Tests:
    1. channel=255, no multiplexer, oled screen connected
    If you disconnect the actuator,
    you should see None (if show_warnings is True, you should see a warning)
    Once you reconnect, you should see valid readings again.

    2. channel=255, no multiplexer, oled_screen not connected
    you should see None (if show_warnings is True, you should see a warning)

    3. channel=between 0 and 7, with multiplexer, oled screen connected
    If you disconnect the actuator,
    you should see None (if show_warnings is True, you should see a warning)
    Once you reconnect, you should see valid readings again.

    4. channel=between 0 and 7, with multiplexer, oled screen not connected
    you should see None (if show_warnings is True, you should see a warning)

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
        height=64,
        width=128,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=0,
        show_warnings=True,
    ):  # pylint: disable=too-many-positional-arguments
        """
        Initializes the OLED screen using the SSH1106 driver.
        """
        super().__init__(channel, sda_gpio_pin, scl_gpio_pin, bus_id, show_warnings)
        self.screen = None
        self.height = height
        self.width = width

    def initialize_device(self):
        """
        Initializes the external SH1106 library and creates the display object.

        This method first calls the parent `I2CDevice.initialize_device()` to
        prepare the I2C bus, then instantiates the `SH1106_I2C` driver with the
        correct screen dimensions and I2C address.
        """
        super().initialize_device()
        self.screen = SH1106_I2C(self.width, self.height, self.i2c, addr=self.ADDRESS)

    @handle_i2c_errors
    def fill(self, color):
        """
        Fills the entire OLED display with the given color.

        Args:
            color (int): Pixel color (usually 0 for black or 1 for white).
        """
        self.screen.sleep(False)
        self.screen.fill(color)

    @handle_i2c_errors
    def text(self, text, x=0, y=0, color=1):
        """
        Draws a text string onto the OLED display.

        Args:
            text (str): The text to display.
            x (int, optional): X-coordinate of the text. Defaults to 0.
            y (int, optional): Y-coordinate of the text. Defaults to 0.
            color (int, optional): Text color (0 = black, 1 = white). Defaults to 1.
        """
        self.screen.sleep(False)
        self.screen.text(text, x, y, color)

    @handle_i2c_errors
    def show(self):
        """
        Updates the OLED display and renders all pending drawing operations.
        """
        self.screen.sleep(False)
        self.screen.show()

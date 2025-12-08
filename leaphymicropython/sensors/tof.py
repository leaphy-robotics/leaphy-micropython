"""This module provides time-of-flight related calculations."""

from leaphymicropython.sensors.vl53l0x import VL53L0X
from leaphymicropython.utils.i2c_helper import I2CDevice
from leaphymicropython.utils.i2c_helper import handle_i2c_errors


class TimeOfFlight(I2CDevice):
    """
    Initializes the TimeOfFlight object.

    Tests:
    1. channel=255, no multiplexer, tof sensor connected
    If you disconnect the sensor,
    you should see None (if show_warnings is True, you should see a warning)
    Once you reconnect, you should see valid readings again.

    2. channel=255, no multiplexer, tof sensor not connected
    you should see None (if show_warnings is True, you should see a warning)

    3. channel=between 0 and 7, with multiplexer, tof sensor connected
    If you disconnect the sensor,
    you should see None (if show_warnings is True, you should see a warning)
    Once you reconnect, you should see valid readings again.

    4. channel=between 0 and 7, with multiplexer, tof sensor not connected
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
    ADDRESS = 0x29

    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=0,
        show_warnings=True,
    ):
        """
        Initializes the TimeOfFlight object.

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
        super().initialize_device()
        self.tof = VL53L0X(self.i2c)

    @handle_i2c_errors
    def get_distance(self):
        """
        Retrieves the distance measurement from the VL53L0X sensor.

        If a multiplexer channel is specified,
        it selects the appropriate channel before reading from the sensor.

        Returns:
            int: The measured distance in millimeters.
        """
        return self.tof.ping()

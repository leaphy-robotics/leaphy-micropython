"""This module provides time-of-flight related calculations."""  # Single-line docstring

from machine import I2C, Pin  # pylint: disable=import-error
from leaphymicropython.sensors.vl53l0x import VL53L0X  # pylint: disable=import-error
from leaphymicropython.utils.i2c_helper import (  # pylint: disable=import-error
    select_channel,
)
from leaphymicropython.utils.i2c_address_finder import (  # pylint: disable=import-error
    is_device_address_visible,
)
from leaphymicropython.utils.i2c_helper import (  # pylint: disable=import-error
    i2c_is_it_used_and_alive,
)


class TimeOfFlight:  # pylint: disable=too-many-instance-attributes
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

    # the following attributes are used by
    # decorator i2c_is_it_used_and_alive
    MULTIPLEXER_ADDRESS = 0x70
    TOF_ADDRESS = 0x29

    def __init__(
        self,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=0,
        show_warnings=True,
    ):  # pylint: disable=too-many-arguments
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
        # the following attributes are used by
        # decorator i2c_is_it_used_and_alive
        self.reinitialize = True
        self.mugs_used = None
        self.i2c = None
        self.channel = channel
        # end of attributes used by decorator
        self.sda_gpio_pin = sda_gpio_pin
        self.scl_gpio_pin = scl_gpio_pin
        self.bus_id = bus_id
        self.show_warnings = show_warnings
        self.tof = None

    def initialize(self):
        """
        initialize external library
        """
        self.i2c = I2C(
            id=self.bus_id, scl=Pin(self.scl_gpio_pin), sda=Pin(self.sda_gpio_pin)
        )
        self.mugs_used = is_device_address_visible(
            i2c=self.i2c, target_address=self.MULTIPLEXER_ADDRESS
        )
        if self.mugs_used:
            select_channel(self.i2c, self.MULTIPLEXER_ADDRESS, self.channel)
        sensor_visible = is_device_address_visible(
            i2c=self.i2c, target_address=self.TOF_ADDRESS
        )
        if not sensor_visible:
            if self.show_warnings:
                print(
                    f"can not find tof sensor (address should be {hex(self.TOF_ADDRESS)})"
                )
        self.tof = VL53L0X(self.i2c)

    @i2c_is_it_used_and_alive
    def get_distance(self):
        """
        Retrieves the distance measurement from the VL53L0X sensor.

        If a multiplexer channel is specified,
        it selects the appropriate channel before reading from the sensor.

        Returns:
            int: The measured distance in millimeters.
        """
        return self.tof.ping()

"""This module provides time-of-flight related calculations."""  # Single-line docstring

from machine import I2C, Pin  # pylint: disable=E0401
from leaphymicropython.sensors.vl53l0x import VL53L0X  # pylint: disable=E0401
from leaphymicropython.utils.i2c_helper import select_channel  # pylint: disable=E0401
from leaphymicropython.utils.i2c_address_finder import (  # pylint: disable=E0401
    is_device_address_visible,
)


class TimeOfFlight:  # pylint: disable=R0902
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

    MULTIPLEXER_ADDRESS = 0x70

    def __init__(
        self,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=0,
        show_warnings=True,
    ):  # pylint: disable=R0913
        """
        Initializes the TimeOfFlight object.

        Args:
            channel (int, optional): The I2C multiplexer channel to select.
            Defaults to 255, indicating no multiplexer is used.
            sda_gpio_pin (int, optional): The GPIO pin connected to the SDA line. Defaults to 12.
            scl_gpio_pin (int, optional): The GPIO pin connected to the SCL line. Defaults to 13.
            bus_id (int, optional): identifies a particular I2C peripheral, for example bus 0 or 1.
        """
        self.channel = channel
        self.sda_gpio_pin = sda_gpio_pin
        self.scl_gpio_pin = scl_gpio_pin
        self.bus_id = bus_id
        self.reinitialize = True
        self.tof_address = 0x29
        self.show_warnings = show_warnings

    def initialize_tof(self):
        """
        initialize external library
        """
        self.i2c = I2C(  # # pylint: disable=W0201
            id=self.bus_id, scl=Pin(self.scl_gpio_pin), sda=Pin(self.sda_gpio_pin)
        )
        if self.channel >= 0 and self.channel <= 7:
            select_channel(self.i2c, self.MULTIPLEXER_ADDRESS, self.channel)
        sensor_visible = is_device_address_visible(
            i2c=self.i2c, target_address=self.tof_address
        )
        if not sensor_visible:
            if self.show_warnings:
                print(
                    f"can not find tof sensor (address should be {hex(self.tof_address)})"
                )
        return VL53L0X(self.i2c)

    def get_distance(self):
        """
        Retrieves the distance measurement from the VL53L0X sensor.

        If a multiplexer channel is specified (channel != 255),
        it selects the appropriate channel before reading from the sensor.

        Returns:
            int: The measured distance in millimeters.
        """
        if self.reinitialize:
            try:
                self.tof = self.initialize_tof()  # pylint: disable=W0201
                self.reinitialize = False
            except Exception as e:  # pylint: disable=W0718,C0103
                if e.errno == 5:  # pylint: disable=E1101
                    value = None
                else:
                    raise e

        if self.reinitialize is False:
            try:
                value = self.tof.ping()
                self.reinitialize = False
            except Exception as e:  # pylint: disable=W0718,C0103
                if e.errno == 5:  # pylint: disable=E1101
                    self.reinitialize = True
                    value = None

        return value

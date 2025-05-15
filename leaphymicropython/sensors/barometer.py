"""
This module provides barometric pressure sensor (BMP280) related measurements.
"""

from leaphymicropython.utils.i2c_helper import I2CDevice, handle_i2c_errors
from leaphymicropython.sensors.bmp280 import BMP280


class BarometricPressure(I2CDevice):
    """
    Initializes the BarometricPressure object for BMP280 sensor.

    Tests:
    1. channel=255, no multiplexer, baro sensor connected
    2. channel=255, no multiplexer, baro sensor not connected
    3. channel=0–7, with multiplexer, baro sensor connected
    4. channel=0–7, with multiplexer, baro sensor not connected

    If the sensor is disconnected, you should see None.
    If show_warnings is True, a warning will be printed.
    Reconnecting should result in valid readings again.

    Args:
        channel (int, optional): I2C multiplexer channel. Default 255 (no mux).
        sda_gpio_pin (int, optional): SDA GPIO pin. Default 12.
        scl_gpio_pin (int, optional): SCL GPIO pin. Default 13.
        bus_id (int, optional): I2C bus number. Default 0.
        show_warnings (bool, optional): Show warnings if device not found. Default True.
    """

    ADDRESS = 0x76  # or 0x77, depending on your setup

    def __init__(
        self,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=0,
        show_warnings=True,
    ):
        super().__init__(channel, sda_gpio_pin, scl_gpio_pin, bus_id, show_warnings)
        self.bmp = None
        self.find_device(show_warnings=self.show_warnings)

    def initialize_device(self):
        """
        Initializes the external BMP280 driver.
        """
        super().initialize_device()
        self.bmp = BMP280(self.i2c)
        self.bmp.use_case(self.bmp.BMP280_CASE_INDOOR)

    @handle_i2c_errors
    def get_temperature(self):
        """
        Retrieves the temperature in degrees Celsius.

        Returns:
            float: Temperature in °C, or None if sensor not found.
        """
        return self.bmp.temperature

    @handle_i2c_errors
    def get_pressure(self):
        """
        Retrieves the barometric pressure in Pascals.

        Returns:
            float: Pressure in Pa, or None if sensor not found.
        """
        return self.bmp.pressure
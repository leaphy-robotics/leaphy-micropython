"""This module provides helper functions for i2c."""

import struct
from machine import Pin, I2C
from leaphymicropython.utils.i2c_address_finder import is_device_address_visible


def handle_i2c_errors(func):
    """
    Decorator to handle I2C errors.

    This decorator wraps a function that interacts with I2C devices.
    It checks if the I2C connection is alive and attempts to reinitialize
    the connection if necessary. It also handles specific OSError exceptions
    that may occur during I2C communication.

    Args:
        func: The function to be wrapped.

    Returns:
        The wrapped function.
    """

    def wrapper(*args, **kwargs):
        instance = args[0]
        # check if the class instance is a subclass of I2CDevice
        if not isinstance(instance, I2CDevice):
            return func(*args, **kwargs)
        # if i2c is used, check if connection is alive
        result = None
        if instance.reinitialize:
            try:
                instance.initialize_i2c()
                instance.find_device(show_warnings=instance.show_warnings)
                instance.initialize_device()
                instance.reinitialize = False
            except RuntimeError:
                if instance.show_warnings == True:
                    print("RuntimeError trying to initialize device")
            except OSError as ex:
                if ex.errno == 5:
                    result = None
                else:
                    raise ex

        if not instance.reinitialize:
            try:
                instance.select_channel()
                result = func(*args, **kwargs)
                instance.reinitialize = False
            except OSError as ex:
                if ex.errno == 5:
                    instance.reinitialize = True
                    result = None
                else:
                    raise ex
        return result

    return wrapper


def select_channel(i2c, multiplexer_address, channel_number) -> None:
    """
    Selects a channel on an I2C multiplexer.

    This function writes to the specified I2C multiplexer to select a given channel.
    It supports channels 0-7 and a special value (255)
    for disabling all channels (or a similar function depending on the multiplexer).

    Args:
        i2c: The I2C bus object.
        multiplexer_address: The I2C address of the multiplexer.
        channel_number: The channel number to select (0-7) or 255 for a special function.

    Raises:
        ValueError: If the channel_number is outside the valid range.

    """
    if 0 <= channel_number <= 7:
        i2c.writeto(multiplexer_address, bytes([1 << channel_number]))
    elif channel_number == 255:
        i2c.writeto(multiplexer_address, bytes([channel_number]))
    else:
        print("Invalid channel number. Please select a channel between 0 and 7 or 255.")


class I2CDevice:  # pylint: disable=too-many-instance-attributes
    """
    Base class for I2C sensors and actuators.

    This class provides a common interface and functionality for interacting with
    I2C devices. It includes methods for initializing the I2C bus, finding the
    device on the bus, and selecting a channel on an I2C multiplexer if one is used.
    """

    MULTIPLEXER_ADDRESS = 0x70
    ADDRESS = None

    def __init__(
        self,
        channel: int = 255,
        sda_gpio_pin: int = 12,
        scl_gpio_pin: int = 13,
        bus_id: int = 0,
        show_warnings: bool = True,
    ):
        self.reinitialize: bool = True
        self.i2c = None
        self.channel: int = channel
        self.bus_id: int = bus_id
        self.scl_gpio_pin: int = scl_gpio_pin
        self.sda_gpio_pin: int = sda_gpio_pin
        self.show_warnings: bool = show_warnings
        self._mux_used = None
        self.initialize_i2c()

    def initialize_i2c(self) -> None:
        """
        Initializes the I2C bus.

        This method sets up the I2C bus with the specified ID, SCL pin, and SDA pin.
        It is called during the initialization of the I2C device.
        """
        self.i2c = I2C(
            id=self.bus_id, scl=Pin(self.scl_gpio_pin), sda=Pin(self.sda_gpio_pin)
        )
        self._mux_used = None

    def initialize_device(self) -> None:
        """
        Abstract method. Initializes the I2C device attached to the bus.
        """

    def find_device(self, show_warnings=True) -> None:
        """Finds the I2C device on the bus.

        This method checks if the device is visible on the I2C bus.
        If a multiplexer is used, it selects the appropriate channel before
        checking for the device. If the device is not found, it prints a warning
        message if show_warnings is True.

        Args:
            show_warnings (bool, optional): If True, show a warning if the device is not found.
            Defaults to True.
        """
        if self.is_mux_used():
            select_channel(self.i2c, self.MULTIPLEXER_ADDRESS, self.channel)
        device_visible = is_device_address_visible(
            i2c=self.i2c, target_address=self.ADDRESS
        )
        if not device_visible and show_warnings:
            print(f"can not find device (address should be {hex(self.ADDRESS)})")

    def is_mux_used(self) -> bool:
        """
        Checks if a multiplexer is used.

        This method checks (once!) if a multiplexer is used by checking if its address is visible on the I2C bus.
        """
        if self._mux_used is None:
            self._mux_used = is_device_address_visible(
                i2c=self.i2c, target_address=self.MULTIPLEXER_ADDRESS
            )
        return self._mux_used

    def select_channel(self) -> None:
        """
        Selects the appropriate channel on the I2C multiplexer.

        If a multiplexer is used, this method selects the specified channel.
        """
        if self.is_mux_used():
            select_channel(self.i2c, self.MULTIPLEXER_ADDRESS, self.channel)


class CBits:
    """
    Changes bits from a byte register
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        num_bits: int,
        register_address: int,
        start_bit: int,
        register_width=1,
        lsb_first=True,
    ) -> None:
        self.bit_mask = ((1 << num_bits) - 1) << start_bit
        self.register = register_address
        self.star_bit = start_bit
        self.lenght = register_width
        self.lsb_first = lsb_first

    def __get__(
        self,
        obj,
        objtype=None,
    ) -> int:
        mem_value = obj.i2c.readfrom_mem(obj.address, self.register, self.lenght)

        reg = 0
        order = range(len(mem_value) - 1, -1, -1)
        if not self.lsb_first:
            order = reversed(order)
        for i in order:
            reg = (reg << 8) | mem_value[i]

        reg = (reg & self.bit_mask) >> self.star_bit

        return reg

    def __set__(self, obj, value: int) -> None:
        memory_value = obj.i2c.readfrom_mem(obj.address, self.register, self.lenght)

        reg = 0
        order = range(len(memory_value) - 1, -1, -1)
        if not self.lsb_first:
            order = range(0, len(memory_value))
        for i in order:
            reg = (reg << 8) | memory_value[i]
        reg &= ~self.bit_mask

        value <<= self.star_bit
        reg |= value
        reg = reg.to_bytes(self.lenght, "big")

        obj.i2c.writeto_mem(obj.address, self.register, reg)


class RegisterStruct:
    """
    Register Struct
    """

    def __init__(self, register_address: int, form: str) -> None:
        self.format = form
        self.register = register_address
        self.lenght = struct.calcsize(form)

    def __get__(
        self,
        obj,
        objtype=None,
    ):
        if self.lenght <= 2:
            value = struct.unpack(
                self.format,
                memoryview(
                    obj.i2c.readfrom_mem(obj.address, self.register, self.lenght)
                ),
            )[0]
        else:
            value = struct.unpack(
                self.format,
                memoryview(
                    obj.i2c.readfrom_mem(obj.address, self.register, self.lenght)
                ),
            )
        return value

    def __set__(self, obj, value):
        mem_value = value.to_bytes(self.lenght, "big")
        obj.i2c.writeto_mem(obj.address, self.register, mem_value)

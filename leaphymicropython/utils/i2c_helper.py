"""This module provides helper functions for i2c."""

import struct
from machine import Pin, I2C
from leaphymicropython.utils.i2c_address_finder import is_device_address_visible

i2c_bus_instances = {}

# Recoverable I2C errno values. 110 (ETIMEDOUT) also covers VL53L0X timeouts
# (see VL53L0XTimeoutError in sensors/vl53l0x.py).
_I2C_ERROR_CODES = {5, 9, 110, 116}


def _is_recoverable_os_error(ex):
    """Check if an OSError has a known recoverable I2C error code."""
    return ex.errno in _I2C_ERROR_CODES


def _handle_error(instance, ex, set_reinitialize=False):
    """Handle a caught I2C error: log warning and optionally flag for reinitialization."""
    if instance.show_warnings:
        print(f"{type(ex).__name__} on channel {instance.channel}: {ex}")
    if set_reinitialize:
        instance.reinitialize = True


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
        if not isinstance(instance, I2CDevice):
            return func(*args, **kwargs)

        result = None
        try:
            if instance.reinitialize:
                instance.initialize_i2c()
                instance.find_device(show_warnings=instance.show_warnings)
                instance.initialize_device()
                instance.reinitialize = False

            if not instance.reinitialize:
                instance.select_channel()
                result = func(*args, **kwargs)
        except RuntimeError as ex:
            _handle_error(instance, ex, set_reinitialize=True)
            result = instance.on_i2c_error(ex)
        except OSError as ex:
            if _is_recoverable_os_error(ex):
                _handle_error(instance, ex, set_reinitialize=True)
                result = instance.on_i2c_error(ex)
            else:
                raise
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


# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-instance-attributes
class I2CDevice:
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
        freq: int = 400_000,
        show_warnings: bool = True,
    ):
        self.reinitialize: bool = True
        self.i2c = None
        self.channel: int = channel
        self.bus_id: int = bus_id
        self.scl_gpio_pin: int = scl_gpio_pin
        self.sda_gpio_pin: int = sda_gpio_pin
        self.freq: int = freq
        self.show_warnings: bool = show_warnings
        self._mux_used = None

    def initialize_i2c(self) -> None:
        """
        Initializes the I2C bus.

        This method sets up the I2C bus with the specified ID, SCL pin, and SDA pin.
        It is called during the initialization of the I2C device.
        """

        if self.bus_id in i2c_bus_instances:
            self.i2c = i2c_bus_instances[self.bus_id]
        else:
            self.i2c = I2C(
                id=self.bus_id,
                scl=Pin(self.scl_gpio_pin),
                sda=Pin(self.sda_gpio_pin),
                freq=self.freq,
            )
            i2c_bus_instances[self.bus_id] = self.i2c

    def initialize_device(self) -> None:
        """
        Abstract method. Initializes the I2C device attached to the bus.
        """

    def on_i2c_error(self, ex):  # pylint: disable=unused-argument
        """Value returned by an @handle_i2c_errors method when a recoverable
        I2C error is caught.

        Defaults to None; subclasses override to surface an error sentinel
        instead of None.
        """
        return None

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


class I2CRegisterDevice(I2CDevice):
    """
    Base class for I2C devices, with additional features to read/write on-device
    memory and registers.
    """

    def __init__(
        self,
        register_width: int = 1,
        addrsize: int = 8,
        big_endian: bool = True,
        channel: int = 255,
        sda_gpio_pin: int = 12,
        scl_gpio_pin: int = 13,
        bus_id: int = 0,
        freq: int = 400_000,
        show_warnings: bool = True,
    ):
        super().__init__(
            channel, sda_gpio_pin, scl_gpio_pin, bus_id, freq, show_warnings
        )
        self.register_width = register_width
        self.addrsize = addrsize
        value_mask = 0x00
        for _ in range(register_width):
            value_mask = value_mask << 8
            value_mask = value_mask | 0xFF
        self.value_mask = value_mask
        if register_width == 1:
            self.value_format = "B"
        elif register_width == 2:
            self.value_format = "H"
        elif register_width == 4:
            self.value_format = "I"
        else:
            self.value_format = None
            return
        if big_endian:
            self.value_format = ">" + self.value_format
        else:
            self.value_format = "<" + self.value_format

    @handle_i2c_errors
    def register_read(self, register) -> int | bytes:
        """
        Read the current value in a register. Since this goes over the I2C line,
        errors may occur.

        Args:
            register: The register to read.

        Returns:
            int: The value read from the register, formatted as a single unsigned number.
            bytes: The value read from the register, formatted as a series of raw bytes.
                Fallback in case no format is specified.
        """
        byte_buffer = self.i2c.readfrom_mem(self.ADDRESS, register, self.register_width)
        if self.value_format is not None:
            return struct.unpack(self.value_format, byte_buffer)[0]
        return byte_buffer

    @handle_i2c_errors
    def register_write(self, register, value):
        """
        Set a register to a value. Since this goes over the I2C line, errors may
        occur.

        Args:
            register: The address of the register to set.
            value: The value that the register will be set to.
        """
        value_buffer = None
        if self.value_format is not None:
            value_buffer = struct.pack(self.value_format, value)
        else:
            value_buffer = bytes([value])
        self.i2c.writeto_mem(self.ADDRESS, register, value_buffer)

    def register_update(self, register, to_set, to_clear) -> int:
        """
        Attempt to set/clear the bits held in a register, quitting early if no operation.
        Since this goes over the I2C line, errors may occur.

        Args:
            register: The address of the register to update.
            to_set: A bitmask of all the bits in the destination register that need to be on.
            to_clear: A bitmask of all the bits in the destination register that need to be off.

        Returns:
            int: The new value in the register, or `None` if no change was written out.
        """
        # If nothing has to change, no point in checking.
        if to_set == 0 and to_clear == 0:
            return None
        # If all the bits that need to be set *are* set, and all the bits that need
        # to be cleared *are* cleared, no point in writing any changes through.
        original_value = self.register_read(register)
        if original_value & to_set == to_set and original_value & to_clear == 0:
            return None
        # Calculate the intended value for the register, then write all at once.
        new_value = original_value | to_set
        new_value = new_value & (self.value_mask ^ to_clear)
        self.register_write(register, new_value)
        return new_value


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

"""This module provides helper functions for i2c."""  # Single-line docstring

import struct


def i2c_is_it_used_and_alive(func):
    """check if i2c connection is used and if so, if it is alive before using it"""

    def wrapper(*args, **kwargs):
        instance = args[0]
        # check if i2c is used
        i2c_used = hasattr(instance, "i2c")
        if not i2c_used:
            result = func(*args, **kwargs)
        else:
            # if i2c is used, check if connection is alive
            if instance.reinitialize:
                try:
                    instance.initialize()  # each class has to have this method
                    instance.reinitialize = False
                except OSError as ex:
                    if ex.errno == 5:
                        result = None
                    else:
                        raise ex

            if instance.reinitialize is False:
                try:
                    if instance.mugs_used:
                        select_channel(
                            instance.i2c, instance.MULTIPLEXER_ADDRESS, instance.channel
                        )
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


def select_channel(i2c, multiplexer_address, channel_number):
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

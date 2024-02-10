import struct
from time import sleep
from micropython import const

_REGISTER_WHOAMI = const(0x0D)
_REGISTER_SET_RESET = const(0x0B)
_REGISTER_OPERATION_MODE = const(0x09)
_REGISTER_STATUS = const(0x06)

OVERSAMPLE_64 = const(0b11)
OVERSAMPLE_128 = const(0b10)
OVERSAMPLE_256 = const(0b01)
OVERSAMPLE_512 = const(0b00)

FIELD_RANGE_2G = const(0b00)
FIELD_RANGE_8G = const(0b01)


OUTPUT_DATA_RATE_10 = const(0b00)
OUTPUT_DATA_RATE_50 = const(0b01)
OUTPUT_DATA_RATE_100 = const(0b10)
OUTPUT_DATA_RATE_200 = const(0b11)

MODE_STANDBY = const(0b00)
MODE_CONTINUOUS = const(0b01)

RESET_VALUE = const(0b01)


class ChangeBitsToBytes:
    """
    Changes bits from a byte register
    """

    def __init__(
        self,
        num_bits: int,
        register_address: int,
        start_bit_position: int,
        register_width: int = 1,
        is_lsb_first: bool = True,
    ) -> None:
        """
        :param num_bits: int, the number of bits in the register
        :param register_address: int, the address of the register
        :param start_bit_position: int, the position of the starting bit
        :param register_width: int, the width of the register (default is 1)
        :param is_lsb_first: bool, indicates whether the least significant bit is first (default is True)
        """
        self.bit_mask = ((1 << num_bits) - 1) << start_bit_position
        self.register_address = register_address
        self.start_bit_position = start_bit_position
        self.register_width = register_width
        self.is_lsb_first = is_lsb_first

    def get_register_value(self, obj) -> int:
        """
        Reads a value from the specified register.
        :param obj: The object representing the device to read from.
        :return: The value read from the register.
        """
        memory_value = obj.i2c.readfrom_mem(
            obj.address, self.register_address, self.register_width
        )
        register_value = 0
        byte_order = range(len(memory_value) - 1, -1, -1)
        if not self.is_lsb_first:
            byte_order = reversed(byte_order)
        for i in byte_order:
            register_value = (register_value << 8) | memory_value[i]
        register_value = (register_value & self.bit_mask) >> self.start_bit_position
        return register_value

    def __set__(self, obj, value: int) -> None:
        """
        Sets the value to the specified register.
        :param obj: The object representing the device to write to.
        :param value: The value to set in the register.
        """
        memory_value = obj.i2c.readfrom_mem(
            obj.address, self.register_address, self.register_width
        )

        register_value = 0
        byte_order = range(len(memory_value) - 1, -1, -1)
        if not self.is_lsb_first:
            byte_order = range(len(memory_value))
        for i in byte_order:
            register_value = (register_value << 8) | memory_value[i]
        register_value &= ~self.bit_mask

        value <<= self.start_bit_position
        register_value |= value
        register_value = register_value.to_bytes(self.register_width, "big")
        obj.i2c.writeto_mem(obj.address, self.register_address, register_value)


class RegisterStruct:
    """
    Represents a structure for handling register data.
    """

    def __init__(self, register_address: int, format_string: str) -> None:
        """
        Initializes the RegisterStruct with the given register address and format string.

        :param register_address: int, the address of the register
        :param format_string: str, the format string specifying the data structure
        """
        self.format = format_string
        self.register = register_address
        self.length = struct.calcsize(format_string)

    def __get__(self, obj, obj_type=None):
        """
        Gets the value of the register.

        :param obj: The object representing the device.
        :param obj_type: The type of the object.
        :return: The value of the register.
        """
        mem_value = obj.i2c.readfrom_mem(obj.address, self.register, self.length)
        if self.length <= 2:
            value = struct.unpack(self.format, mem_value)[0]
        else:
            value = struct.unpack(self.format, mem_value)
        return value

    def __set__(self, obj, value):
        """
        Sets the value of the register.

        :param obj: The object representing the device.
        :param value: The value to set.
        """
        mem_value = struct.pack(self.format, value)
        obj.i2c.writeto_mem(obj.address, self.register, mem_value)

import struct
from time import sleep
from micropython import const

# Constants for register addresses
_REGISTER_WHOAMI = const(0x0D)
_REGISTER_SET_RESET = const(0x0B)
_REGISTER_OPERATION_MODE = const(0x09)
_REGISTER_STATUS = const(0x06)

# Constants for sensor configurations
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
    Class to handle manipulation of bits within a byte register.
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
        Initialize ChangeBitsToBytes object.

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
        Read a value from the specified register.

        :param obj: The object representing the device to read from.
        :return: The value read from the register.
        """
        memory_value = obj._i2c.readfrom_mem(  # pylint: disable=protected-access
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
        Set the value to the specified register.

        :param obj: The object representing the device to write to.
        :param value: The value to set in the register.
        """
        memory_value = obj._i2c.readfrom_mem(
            obj.address, self.register_address, self.register_width
        )  # pylint: disable=protected-access

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
        obj._i2c.writeto_mem(
            obj.address, self.register_address, register_value
        )  # pylint: disable=protected-access


class RegisterStruct:
    """
    Class representing a structure for handling register data.
    """

    def __init__(self, register_address: int, format_string: str) -> None:
        """
        Initialize RegisterStruct object with given register address and format string.

        :param register_address: int, the address of the register
        :param format_string: str, the format string specifying the data structure
        """
        self.format = format_string
        self.register = register_address
        self.length = struct.calcsize(format_string)

    def __get__(self, obj, obj_type=None) -> tuple:
        """
        Get the value of the register.

        :param obj: The object representing the device.
        :param obj_type: The type of the object.
        :return: The value of the register.
        """
        mem_value = obj._i2c.readfrom_mem(
            obj.address, self.register, self.length
        )  # pylint: disable=protected-access
        if self.length <= 2:
            value = struct.unpack(self.format, mem_value)[0]
        else:
            value = struct.unpack(self.format, mem_value)
        return value

    def __set__(self, obj, value):
        """
        Set the value of the register.

        :param obj: The object representing the device.
        :param value: The value to set.
        """
        mem_value = struct.pack(self.format, value)
        obj._i2c.writeto_mem(
            obj.address, self.register, mem_value
        )  # pylint: disable=protected-access


# pylint: disable=too-many-instance-attributes
class Compass:
    """
    Class representing a compass sensor.
    """

    _device_id = RegisterStruct(_REGISTER_WHOAMI, "H")
    _reset = RegisterStruct(_REGISTER_SET_RESET, "H")
    _conf_reg = RegisterStruct(_REGISTER_OPERATION_MODE, "H")
    _oversample = ChangeBitsToBytes(2, _REGISTER_OPERATION_MODE, 6)
    _field_range = ChangeBitsToBytes(2, _REGISTER_OPERATION_MODE, 4)
    _output_data_rate = ChangeBitsToBytes(2, _REGISTER_OPERATION_MODE, 2)
    _mode_control = ChangeBitsToBytes(2, _REGISTER_OPERATION_MODE, 0)
    _data_ready_register = ChangeBitsToBytes(1, _REGISTER_STATUS, 2)
    _measures = RegisterStruct(0x00, "<hhhBh")

    def __init__(self, i2c, address: int = 0xD) -> None:
        """
        Initialize Compass object.

        :param i2c: The I2C bus object.
        :param address: int, the address of the compass sensor (default is 0xD)
        """
        self._i2c = i2c
        self._address = address

        if self._device_id != 0xFF:
            raise RuntimeError("Failed to find the QMC5883L!")
        self._reset = 0x01

        self.oversample = OVERSAMPLE_128
        self.field_range = FIELD_RANGE_2G
        self.output_data_rate = OUTPUT_DATA_RATE_200
        self.mode_control = MODE_CONTINUOUS

    @property
    def oversample(self) -> int:
        """
        Get the oversample setting.
        :return: int, the oversample setting.
        """
        oversample_values = (
            OVERSAMPLE_512,
            OVERSAMPLE_256,
            OVERSAMPLE_128,
            OVERSAMPLE_64,
        )
        return oversample_values[self.oversample]

    @oversample.setter
    def oversample(self, value: int) -> None:
        """
        Set the oversample setting.
        :param value: int, the value to set as oversample.
        """
        if value not in (OVERSAMPLE_512, OVERSAMPLE_256, OVERSAMPLE_128, OVERSAMPLE_64):
            raise ValueError("Value must be a valid oversample setting")
        self._oversample = value

    @property
    def field_range(self) -> int:
        """
        Get the field range setting.
        :return: int, the field range setting.
        """
        field_range_values = (FIELD_RANGE_2G, FIELD_RANGE_8G)
        return field_range_values[self.field_range]

    @field_range.setter
    def field_range(self, value: int) -> None:
        """
        Set the field range setting.
        :param value: int, the value to set as field range.
        """
        if value not in (FIELD_RANGE_2G, FIELD_RANGE_8G):
            raise ValueError("Value must be a valid field range setting")

        if value == 1:
            self.resolution = 3000
        else:
            self.resolution = 12000

        self._field_range = value

    @property
    def output_data_rate(self) -> int:
        """
        Get the output data rate setting.
        :return: int, the output data rate setting.
        """
        data_rate_values = (
            OUTPUT_DATA_RATE_10,
            OUTPUT_DATA_RATE_50,
            OUTPUT_DATA_RATE_100,
            OUTPUT_DATA_RATE_200,
            50,
        )
        return data_rate_values[self.output_data_rate]

    @output_data_rate.setter
    def output_data_rate(self, value: int) -> None:
        """
        Set the output data rate setting.
        :param value: int, the value to set as output data rate.
        """
        if value not in (
            OUTPUT_DATA_RATE_10,
            OUTPUT_DATA_RATE_50,
            OUTPUT_DATA_RATE_100,
            OUTPUT_DATA_RATE_200,
        ):
            raise ValueError("Value must be a valid data rate setting")
        self._output_data_rate = value

    @property
    def mode_control(self) -> int:
        """
        Get the mode control setting.

        :return: int, the mode control setting.
        """
        mode_values = (MODE_STANDBY, MODE_CONTINUOUS)
        return mode_values[self.mode_control]

    @mode_control.setter
    def mode_control(self, value: int) -> None:
        """
        Set the mode control setting.

        :param value: int, the value to set as mode control.
        """
        if value not in (MODE_STANDBY, MODE_CONTINUOUS):
            raise ValueError("Value must be a valid mode setting")
        self._mode_control = value

    @property
    def magnetic(self):
        """
        Get the magnetic property.

        :return: tuple, the magnetic property.
        """
        while self._data_ready_register != 1:
            sleep(0.001)
        x, y, z, _, _ = self._measures  # pylint: disable=unpacking-non-sequence

        return x / self.resolution, y / self.resolution, z / self.resolution

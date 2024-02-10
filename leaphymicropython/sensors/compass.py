import struct
from micropython import const
from time import sleep


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

    def get_register_value(self, obj, obj_type=None) -> int:
        """
        Reads a value from the specified register.
        :param obj: The object representing the device to read from.
        :param obj_type: Optional parameter specifying the type of the object.
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
        "#big indicates that the most significant digit should come first"
        obj.i2c.writeto_mem(obj.address, self.register_address, register_value)

# pylint: disable=too-many-positional-arguments
import struct


class CBits:
    """
    Changes bits from a byte register
    """

    def __init__(
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

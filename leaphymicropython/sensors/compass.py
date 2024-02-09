import math
from time import sleep
from machine import I2C, Pin


class Compass:
    """A class to connect and read a compass sensor"""

    ADDR = 0x0D

    def __init__(self):
        self.i2c = I2C(0, freq=400000)
        self._write_reg(0x0B, 0x01)
        self.set_mode(0x01, 0x0C, 0x10, 0x00)

    def _write_reg(self, r: int, v: int) -> None:
        self.i2c.writeto(self.ADDR, bytes([r, v]))

    def set_mode(self, mode: int, odr: int, rng: int, osr: int) -> None:
        self._write_reg(9, mode | odr | rng | osr)

    def read_compass(self) -> tuple[int, int, int]:
        self.i2c.writeto(self.ADDR, bytes(0))
        sleep(0.01)
        buffer: bytes = self.i2c.readfrom(self.ADDR, 6, False)
        x: int = buffer[1] << 8 | buffer[0]
        y: int = buffer[3] << 8 | buffer[2]
        z: int = buffer[5] << 8 | buffer[4]
        return x, y, z

    @staticmethod
    def get_azimuth(x, y) -> int:
        heading: float = math.atan2(y, x) * 180.0 / math.pi
        return int(heading % 360)

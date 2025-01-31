from machine import I2C, Pin
from leaphymicropython.utils.i2c_helper import select_channel
from vl53l0x import VL53L0X


class TimeOfFlight:
    MULTIPLEXER_ADDRESS = 0x70

    def __init__(self, channel=255, sda_gpio_pin=12, scl_gpio_pin=13):
        self.channel = channel
        self.i2c = I2C(id=0, scl=Pin(scl_gpio_pin), sda=Pin(sda_gpio_pin))
        self.tof = VL53L0X(self.i2c)

    def get_distance(self):
        select_channel(self.i2c, self.MULTIPLEXER_ADDRESS, self.channel)
        return self.tof.ping()

from micropython import const
from utime import sleep_ms
from leaphymicropython.utils.i2c_helper import handle_i2c_errors, I2CRegisterDevice

_RESULT_ADDRESS = const(0x00)
_CONFIG_ADDRESS = const(0x01)
_CONFIG_BASE_VALUE = const(0xC180)
_CONFIG_READY_STATUS = const(0x8000)
_CONFIG_CHANNEL_OFFSET = const(12)
_LOWTRESH_ADDRESS = const(0x02)
_LOWTRESH_DEFAULT = const(0x0000)
_HITRESH_ADDRESS = const(0x03)
_HITRESH_DEFAULT = const(0x8000)


class Adc1115(I2CRegisterDevice):
    def __init__(
        self,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=72,
        freq=400_000,
        show_warnings=True,
    ):
        __super__(
            register_width=2,
            addrsize=8,
            big_endian=True,
            channel=channel,
            sda_gpio_pin=sda_gpio_pin,
            scl_gpio_pin=scl_gpio_pin,
            bus_id=bus_id,
            freq=freq,
            show_warnings=show_warnings,
        )

    def readADC_single_ended(self, channel: int) -> int:
        # startADCReading
        if channel < 0 or channel > 3:
            raise ValueError("Channel needs to be between 0 and 3, was " + str(channel))
        config = _CONFIG_BASE_VALUE | (channel << _CONFIG_CHANNEL_OFFSET)
        self.register_write(_CONFIG_ADDRESS, config)
        self.register_write(_HITRESH_ADDRESS, _HITRESH_DEFAULT)
        self.register_write(_LOWTRESH_ADDRESS, _LOWTRESH_DEFAULT)
        # conversionComplete
        while (self.register_read(_CONFIG_ADDRESS) & _CONFIG_READY_STATUS) == 0:
            pass
        # getLastConversionResult
        result = self.register_read(_RESULT_ADDRESS)
        # Result is signed, `register_read()` returns unsigned values.
        if (result & const(0x8000)) != 0:
            return result - const(0x10000)
        return result

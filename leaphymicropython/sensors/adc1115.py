from micropython import const
from leaphymicropython.utils.i2c_helper import I2CRegisterDevice

# pylint: disable=too-many-positional-arguments

_RESULT_ADDRESS = const(0x00)
_CONFIG_ADDRESS = const(0x01)
# Start single conversion, compare against GND,
# FSR setting of 2.048v, single-shot, data-rate of 128SPS,
# traditional comparator, active low, nonlatching,
# disable-and-ignore-ALERT
_CONFIG_SINGLE_SHOT_BASE = const(0b1_100_010_1_100_0_0_0_11)
# Do not start, compare against GND,
# FSR setting of 2.048v, continuous, data-rate of 128SPS,
# traditional comparator, active low, nonlatching,
# disable-and-ignore-ALERT
_CONFIG_CONTINUOUS_BASE =  const(0b0_100_010_0_100_0_0_0_11)
_CONFIG_READY_STATUS = const(0x8000)
_CONFIG_CHANNEL_OFFSET = const(12)
_LOWTRESH_ADDRESS = const(0x02)
_LOWTRESH_DEFAULT = const(0x0000)
_HITRESH_ADDRESS = const(0x03)
_HITRESH_DEFAULT = const(0x8000)




class Adc1115(I2CRegisterDevice):
    """
    An ADC1115 analog-to-digital converter, capable of reading out up to 4 channels
    as 16-bit integer levels.
    """
    def __init__(
        self,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=72,
        freq=400_000,
        show_warnings=True,
    ):
        super().__init__(
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
        self.continuous = False

    def readadc_single_ended(self, channel: int) -> int:
        """
        Perform a single reading of the given channel.
        Args:
            channel: Which of the four channels 0 through 3 to read.
        Returns:
            int: A 16-bit signed value indicating the voltage on the channel.
        Raises:
            ValueError: an invalid channel-number was supplied.
        """
        # startADCReading
        if channel < 0 or channel > 3:
            raise ValueError("Channel needs to be between 0 and 3, was " + str(channel))
        config = _CONFIG_SINGLE_SHOT_BASE | (channel << _CONFIG_CHANNEL_OFFSET)
        self.register_write(_CONFIG_ADDRESS, config)
        self.register_write(_HITRESH_ADDRESS, _HITRESH_DEFAULT)
        self.register_write(_LOWTRESH_ADDRESS, _LOWTRESH_DEFAULT)
        self.continuous = False
        # conversionComplete
        while (self.register_read(_CONFIG_ADDRESS) & _CONFIG_READY_STATUS) == 0:
            pass
        # getLastConversionResult
        result = self.register_read(_RESULT_ADDRESS)
        # Result is signed, `register_read()` returns unsigned values.
        if (result & const(0x8000)) != 0:
            return result - const(0x10000)
        return result

    def start_continuous_read(self, channel:int):
        """
        Starts continuously reading from the given channel.
        Args:
            channel: Which of the four channels 0 through 3 to read.
        Raises:
            ValueError: an invalid channel-number was supplied.
        """
        if channel < 0 or channel > 3:
            raise ValueError("Channel needs to be between 0 and 3,  was "+str(channel))
        config = _CONFIG_CONTINUOUS_BASE | (channel << _CONFIG_CHANNEL_OFFSET)
        self.register_write(_CONFIG_ADDRESS,config)
        self.register_write(_HITRESH_ADDRESS,_HITRESH_DEFAULT)
        self.register_write(_LOWTRESH_ADDRESS,_LOWTRESH_DEFAULT)
        self.continuous = True

    def latest_read(self) -> int:
        """
        Fetch the latest value from the sensor, or busy-wait until a value
        is available.

        Returns:
            int: The most recent value available from the sensor.
        Raises:
            RuntimeError: If this function was called before `start_continuous_read()`.
        """
        if not self.continuous:
            raise RuntimeError("ADC was not in continuous mode.")

        while (self.register_read(_CONFIG_ADDRESS) & _CONFIG_READY_STATUS) == 0:
            pass
        result = self.register_read(_RESULT_ADDRESS)
        # Result is signed, `register_read()` returns unsigned values.
        if (result & const(0x8000)) != 0:
            return result - const(0x10000)
        return result

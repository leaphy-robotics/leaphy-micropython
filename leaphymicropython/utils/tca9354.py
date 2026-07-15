from micropython import const
from utime import sleep_ms
from leaphymicropython.utils.i2c_helper import handle_i2c_errors, I2CRegisterDevice

# This file is in "utils" since the device is capable of both
# sending a value out (making it an actuator) and receiving
# values that the processor can interpret (making it a sensor.)

TCA9354_REG_INPUT = const(0x00)
TCA9354_REG_OUTPUT = const(0x01)
TCA9354_REG_CONFIG = const(0x03)

TCA9354_CONFIG_IN = const(1)
TCA9354_CONFIG_OUT = const(0)


class Tca9354(I2CRegisterDevice):
    """
    A TCA9354 digital signal multiplexer that can have each of
    its 8 channels configured as input or output at runtime.
    """

    def __init__(
        self,
        io_config=0xFF,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=32,
        freq=400_000,
        show_warnings=True,
    ):
        """
        Initialize the TCA9354 multiplexer.

        Args:
            io_config: 8-bit bitfield describing the input/output configuration. 0 configures a pin as input, 1 configures a pin as output.
        """

        super().__init__(
            register_width=1,
            addrsize=8,
            channel=channel,
            sda_gpio_pin=sda_gpio_pin,
            scl_gpio_pin=scl_gpio_pin,
            bus_id=bus_id,
            freq=freq,
            show_warnings=show_warnings,
        )

        self.io_config = io_config

    def begin(self):
        """
        Configure the multiplexer to its expected settings.
        Call this before requesting or sending data for the
        first time.
        """
        self.register_write(TCA9354_REG_CONFIG, self.io_config)

    def configure_pin(self, pin, direction):
        """
        Configure one pin of the multiplexer as input/output.

        Args:
            pin: The number of the pin to be configured. Values outside the range [0..7] will be quietly ignored.
            direction: One of TCA9354_CONFIG_IN or TCA9354_CONFIG_OUT, indicating if the pin should be configured as input/output.
        """
        if pin < 0 or pin > 7:
            return

        if direction == TCA9354_CONFIG_IN:
            self.register_update(TCA9354_REG_CONFIG, (1 << pin), 0)
            self.io_config |= 1 << pin
        if direction == TCA9354_CONFIG_OUT:
            self.register_update(TCA9354_REG_CONFIG, 0, (1 << pin))
            self.io_config &= const(0xFF) ^ (1 << pin)

    def read(self) -> int:
        """
        Read the current output value. Note that pins configured as output
        always read as 0.
        """
        return self.register_read(TCA9354_REG_INPUT) & const(0xFF)

    def read_pin(self, pin) -> bool:
        """
        Read the specified pin. Pins outside the range [0..7] will always read as `False`.

        Args:
            pin: The number of the pin to read.
        """
        if pin < 0 or pin > 7:
            return False
        current_output = self.read()
        return current_output & (1 << pin) != 0

    def write(self, value):
        """
        Write a value to the output register. Note that only pins configured as output
        will update.

        Args:
            value: The 8-bit value to write.
        """
        self.register_write(TCA9354_REG_OUTPUT, value & 0xFF)

    def write_pin(self, pin, value):
        """
        Read the current state of the output, then update it to set one output pin high/low.

        Args:
            pin: The number of the pin to update. Values outside the range [0..7] result in no operation taking place.
            value: Whether the pin should be set high (True) or low (False).
        """
        if pin < 0 or pin > 7:
            return
        if value:
            self.register_update(TCA9354_REG_OUTPUT, (1 << pin), 0)
        else:
            self.register_update(TCA9354_REG_OUTPUT, 0, (1 << pin))

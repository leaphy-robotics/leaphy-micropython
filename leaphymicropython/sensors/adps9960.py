from micropython import const
import ustruct
from utime import sleep_ms
from leaphymicropython.utils.i2c_helper import handle_i2c_errors, I2CDevice

_I2C_ADDRESS = const(0x39)

_REG_ENABLE = const(0x80)
_REG_ATIME = const(0x81)
_REG_WTIME = const(0x83)
_REG_PPULSE = const(0x8E)
_REG_CONTROL = const(0x8F)
_REG_STATUS = const(0x93)
_REG_CDATAL = const(0x94)
_REG_GCONF2 = const(0xA3)
_REG_GCONF4 = const(0xAB)
_REG_GFLVL = const(0xAE)
_REG_GSTATUS = const(0xAF)
_REG_GFIFO_U = const(0xFC)

_ENABLE_ALL_OFF = const(0x00)
_ENABLE_MASK_PON = const(0x01)  # General power-enable
_ENABLE_MASK_AEN = const(0x02)  # Ambient light detection mode.
_ENABLE_MASK_WEN = const(0x08)  # Wait-enable mode.
_ENABLE_MASK_GEN = const(0x40)  # Gesture detection mode.
_ENABLE_WAIT_POW_ON = (
    _ENABLE_MASK_PON | _ENABLE_MASK_WEN
)  # Default settings on startup.
_ATIME_11_12MS = const(0xFC)  # Smallest wait-time greater than 10ms.
_WTIME_1_PERIOD = const(0xFF)
_PPULSE_8US_64PULSE = const(0x8F)
_CONTROL_16X_GAIN = const(0x02)
_STATUS_COLOR_AV = const(0x01)
_GCONF2_ALL_MAX = const(0x8F)  # gesture gain x8, led current 12.5mA, wait time 39.2ms
_GCONF4_MASK_GMODE_INT = const(0x03)
_GSTATUS_MASK_GVALID = const(0x01)

_MASK_NONE = const(0x00)
_COLOR_DATA_LEN = const(
    8
)  # red, green, blue color channels, clear "color" channel, 2 bytes each.
_GESTURE_DATA_LEN = const(4)  # up, down, left, right, One byte each.

GESTURE_NONE = const(-1)
GESTURE_UP = const(0)
GESTURE_DOWN = const(1)
GESTURE_LEFT = const(2)
GESTURE_RIGHT = const(3)


class Adps9960(I2CDevice):
    """
    An ADPS 9960 gesture and ambient light sensor.
    """

    ADDRESS = _I2C_ADDRESS

    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        gesture_sensitivity=20,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=0,
        show_warnings=True,
    ):
        """
        Initialize the ADPS 9960 sensor.

        Args:
            gesture_sensitivity: Minimum amount of movement that is recognised as a gesture-movement.
        """
        super().__init__(channel, sda_gpio_pin, scl_gpio_pin, bus_id, show_warnings)
        self._last_gesture = GESTURE_NONE
        self._gesture_sensitivity = gesture_sensitivity
        self._gesture_in = False
        self._gesture_direction_x = 0
        self._gesture_direction_y = 0
        self._gesture_dir_in_x = 0
        self._gesture_dir_in_y = 0

    @handle_i2c_errors
    def begin(self):
        """
        Configure the sensor to its default operating settings.
        Call this before requesting data from the sensor.
        """
        self._register_write(_REG_ENABLE, _ENABLE_ALL_OFF)
        self._register_write(_REG_WTIME, _WTIME_1_PERIOD)
        self._register_write(_REG_PPULSE, _PPULSE_8US_64PULSE)
        self._register_write(_REG_GCONF2, _GCONF2_ALL_MAX)
        self._register_update(_REG_GCONF4, _GCONF4_MASK_GMODE_INT, _MASK_NONE)
        self._register_write(_REG_ENABLE, _ENABLE_WAIT_POW_ON)
        self._register_write(_REG_ATIME, _ATIME_11_12MS)
        self._register_write(_REG_CONTROL, _CONTROL_16X_GAIN)
        sleep_ms(10)
        self._register_update(_REG_ENABLE, _ENABLE_MASK_PON, _MASK_NONE)

    @handle_i2c_errors
    def color_available(self) -> bool:
        """
        Check if the sensor has a color-level reading available.

        Returns:
            bool: True if RGB levels are available, False otherwise.
        """
        self._register_update(_REG_ENABLE, _ENABLE_MASK_AEN, _MASK_NONE)
        return (self._register_read(_REG_STATUS) & _STATUS_COLOR_AV) != 0

    @handle_i2c_errors
    def read_color(self) -> tuple[int, int, int, int]:
        """
        Read the latest color-levels from the sensor.

        Returns:
            tuple[int,int,int,int]: A tuple of the red, green, blue and "clear"
            light-levels, expressed as 16-bit unsigned integers.
        """
        raw_data = self._memory_read(_REG_CDATAL, _COLOR_DATA_LEN)
        clear, red, green, blue = ustruct.unpack(">HHHH", raw_data)
        self._register_update(_REG_ENABLE, _MASK_NONE, _ENABLE_MASK_AEN)
        return red, green, blue, clear

    @handle_i2c_errors
    def gesture_available(self, gesture_threshold=30):
        """
        Set the sensor to gesture-reading mode if necessary and, if the data is available,
        fetch the latest gesture-data from the sensor.

        Args:
            gesture_threshold: Gesture maximum threshold.

        Returns:
            bool: True if a gesture was detected, False otherwise.
        """
        self._register_update(_REG_ENABLE, _ENABLE_MASK_GEN, _MASK_NONE)
        if (self._register_read(_REG_GSTATUS) & _GSTATUS_MASK_GVALID) == 0:
            # No gesture data in the queue.
            return False
        retval = False
        data_waiting = self._register_read(_REG_GFLVL)
        gesture_data = self._memory_read(_REG_GFIFO_U, data_waiting * _GESTURE_DATA_LEN)
        for offset in range(len(gesture_data) // _GESTURE_DATA_LEN):
            slice_start = offset * _GESTURE_DATA_LEN
            if all(
                x < gesture_threshold
                for x in gesture_data[slice_start : slice_start + 4]
            ):
                self._gesture_in = True
                if self._gesture_dir_in_x != 0 or self._gesture_dir_in_y != 0:
                    total_x = self._gesture_dir_in_x - self._gesture_direction_x
                    total_y = self._gesture_dir_in_y - self._gesture_direction_y
                    if total_x < -self._gesture_sensitivity:
                        self._last_gesture = GESTURE_LEFT
                    if total_x > self._gesture_sensitivity:
                        self._last_gesture = GESTURE_RIGHT
                    if total_y < -self._gesture_sensitivity:
                        self._last_gesture = GESTURE_DOWN
                    if total_y > self._gesture_sensitivity:
                        self._last_gesture = GESTURE_UP
                    retval = self._last_gesture != GESTURE_NONE
                    self._gesture_direction_x = 0
                    self._gesture_direction_y = 0
                    self._gesture_dir_in_x = 0
                    self._gesture_dir_in_y = 0
                continue

            up, down, left, right = gesture_data[slice_start : slice_start + 4]
            self._gesture_direction_x = right - left
            self._gesture_direction_y = up - down
            if self._gesture_in:
                self._gesture_in = False
                self._gesture_dir_in_x = self._gesture_direction_x
                self._gesture_dir_in_y = self._gesture_direction_y
        return retval

    @handle_i2c_errors
    def read_gesture(self) -> int:
        """
        Fetches the latest gesture-direction detected, then puts the sensor
        into color-detection mode.
        Note that this function will return `GESTURE_NONE` until a call to
        `gesture_available()` has returned True.

        Returns:
            int: One of `GESTURE_NONE`, `GESTURE_UP`, `GESTURE_RIGHT`, `GESTURE_DOWN` or `GESTURE_LEFT`.
        """
        return_value = self._last_gesture
        self._last_gesture = GESTURE_NONE
        self._register_update(_REG_ENABLE, _MASK_NONE, _ENABLE_MASK_GEN)
        return return_value

    def _register_read(self, register) -> int:
        byte_buffer = self.i2c.readfrom_mem(self.ADDRESS, register, 1)
        # print("read register",hex(register),"value",byte_buffer[0])
        return byte_buffer[0]

    def _register_write(self, register, value):
        # print("write register",hex(register),"value",bin(value))
        value_buffer = bytes([value])
        self.i2c.writeto_mem(self.ADDRESS, register, value_buffer)

    def _register_update(self, register, to_set, to_clear):
        if to_set == 0 and to_clear == 0:
            return
        original_value = self._register_read(register)
        # print(bin(original_value),"set",bin(to_set),"clear",bin(to_clear))
        if original_value & to_set == to_set and original_value & to_clear == 0:
            return
        self._register_write(register, (original_value | to_set) & (0xFF ^ to_clear))

    def _memory_read(self, start, length):
        if length <= 0 or start < 0 or start > 0xFF:
            return None
        return self.i2c.readfrom_mem(self.ADDRESS, start, length)

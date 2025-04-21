import time

from micropython import const

from leaphymicropython.utils.i2c_helper import CBits, RegisterStruct

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/MicroPython_QMC5883L.git"

_REG_WHOAMI = const(0x0D)
_REG_SET_RESET = const(0x0B)
_REG_OPERATION_MODE = const(0x09)
_REG_STATUS = const(0x06)

OVERSAMPLE_64 = const(0b11)
OVERSAMPLE_128 = const(0b10)
OVERSAMPLE_256 = const(0b01)
OVERSAMPLE_512 = const(0b00)
oversample_values = (OVERSAMPLE_64, OVERSAMPLE_128, OVERSAMPLE_256, OVERSAMPLE_512)

FIELDRANGE_2G = const(0b00)
FIELDRANGE_8G = const(0b01)
field_range_values = (FIELDRANGE_2G, FIELDRANGE_8G)

OUTPUT_DATA_RATE_10 = const(0b00)
OUTPUT_DATA_RATE_50 = const(0b01)
OUTPUT_DATA_RATE_100 = const(0b10)
OUTPUT_DATA_RATE_200 = const(0b11)
data_rate_values = (
    OUTPUT_DATA_RATE_10,
    OUTPUT_DATA_RATE_50,
    OUTPUT_DATA_RATE_100,
    OUTPUT_DATA_RATE_200,
)

MODE_STANDBY = const(0b00)
MODE_CONTINUOUS = const(0b01)
mode_values = (MODE_STANDBY, MODE_CONTINUOUS)

RESET_VALUE = const(0b01)


class QMC5883L:
    # pylint: disable=too-many-instance-attributes
    """
    The class to make the compass operational
    """
    _device_id = RegisterStruct(_REG_WHOAMI, "H")
    _reset = RegisterStruct(_REG_SET_RESET, "H")
    _conf_reg = RegisterStruct(_REG_OPERATION_MODE, "H")
    _oversample = CBits(2, _REG_OPERATION_MODE, 6)
    _field_range = CBits(2, _REG_OPERATION_MODE, 4)
    _output_data_rate = CBits(2, _REG_OPERATION_MODE, 2)
    _mode_control = CBits(2, _REG_OPERATION_MODE, 0)
    _data_ready_register = CBits(1, _REG_STATUS, 2)
    _measures = RegisterStruct(0x00, "<hhhBh")

    def __init__(self, i2c, address: int = 0xD) -> None:
        self.i2c = i2c
        self.address = address

        if self._device_id != 0xFF:
            raise RuntimeError("Failed to find the QMC5883L!")
        self._reset = 0x01

        self.oversample = OVERSAMPLE_128
        self.field_range = FIELDRANGE_2G
        self.output_data_rate = OUTPUT_DATA_RATE_200
        self.mode_control = MODE_CONTINUOUS

    @property
    def oversample(self) -> int:
        """
        Oversample
        """

        oversamples = (
            "OVERSAMPLE_512",
            "OVERSAMPLE_256",
            "OVERSAMPLE_128",
            "OVERSAMPLE_64",
        )

        return oversamples[self._oversample]

    @oversample.setter
    def oversample(self, value: int) -> None:
        if value not in oversample_values:
            raise ValueError("Value must be a valid oversample setting")

        self._oversample = value

    @property
    def field_range(self) -> int:
        """
        Field range
        """

        ranges = ("FIELDRANGE_2G", "FIELDRANGE_8G")

        return ranges[self._field_range]

    @field_range.setter
    def field_range(self, value: int) -> None:
        """
        Field range setter
        """
        if value not in field_range_values:
            raise ValueError("Value must be a valid field range setting")

        if value == 1:
            self.resolution = 3000
        else:
            self.resolution = 12000

        self._field_range = value

    @property
    def output_data_rate(self) -> int:
        """
        output data rate
        """

        rates = (
            "OUTPUT_DATA_RATE_10",
            "OUTPUT_DATA_RATE_50",
            "OUTPUT_DATA_RATE_100",
            "OUTPUT_DATA_RATE_200",
        )

        return rates[self._output_data_rate]

    @output_data_rate.setter
    def output_data_rate(self, value: int) -> None:
        if value not in data_rate_values:
            raise ValueError("Value must be a valid data rate setting")

        self._output_data_rate = value

    @property
    def mode_control(self) -> int:
        """
        Mode control
        """

        modes = ("MODE_STANDBY", "MODE_CONTINUOUS")

        return modes[self._mode_control]

    @mode_control.setter
    def mode_control(self, value: int) -> None:
        if value not in mode_values:
            raise ValueError("Value must be a valid mode setting")
        self._mode_control = value

    @property
    def magnetic(self):
        """Magnetic property"""
        while self._data_ready_register != 1:
            time.sleep(0.001)
        x, y, z, _, _ = self._measures

        return x / self.resolution, y / self.resolution, z / self.resolution

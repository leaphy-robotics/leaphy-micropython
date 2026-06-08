"""
VL53L0X time-of-flight ranging sensor driver.
Originates from https://github.com/kevinmcaleer/vl53l0x
"""

from micropython import const
import ustruct
import utime

# Polling loops use this many 1 ms iterations as their watchdog.
# Effective wall-clock budget: ~_IO_TIMEOUT_MS milliseconds per polled call.
_IO_TIMEOUT_MS = 1000

# Register addresses actually referenced by this driver.
_SYSRANGE_START = const(0x00)
_SYSTEM_SEQUENCE = const(0x01)
_MEASURE_PERIOD = const(0x04)
_INTERRUPT_GPIO = const(0x0A)
_INTERRUPT_CLEAR = const(0x0B)
_RESULT_INTERRUPT_STATUS = const(0x13)
_RESULT_RANGE_STATUS = const(0x14)
_PRE_RANGE_TIMEOUT_MACROP_HI = const(0x51)
_MSRC_CONFIG_TIMEOUT_MACROP = const(0x46)
_PRE_RANGE_VCSEL_PERIOD = const(0x50)
_FINAL_RANGE_VCSEL_PERIOD = const(0x70)
_FINAL_RANGE_TIMEOUT_MACROP_HI = const(0x71)
_SPAD_REF_START = const(0x4F)
_SPAD_ENABLES = const(0xB0)
_REF_EN_START_SELECT = const(0xB6)
_SPAD_NUM_REQUESTED = const(0x4E)
_GPIO_MUX_ACTIVE_HIGH = const(0x84)
_OSC_CALIBRATE = const(0xF8)
_EXTSUP_HV = const(0x89)
_MSRC_CONFIG = const(0x60)
_FINAL_RATE_RTN_LIMIT = const(0x44)

# Bus settle time after I2C peripheral comes up, before issuing the first
# transaction to the chip. Empirically required on RP2 / ESP32 ports.
_I2C_BOOT_DELAY_MS = 100


# errno that handle_i2c_errors treats as a recoverable I2C fault (see
# _I2C_ERROR_CODES in utils/i2c_helper.py). 110 == ETIMEDOUT.
_ETIMEDOUT = 110


class VL53L0XTimeoutError(OSError):
    """Raised when an I2C operation to the VL53L0X times out.

    Carries errno ETIMEDOUT so handle_i2c_errors classifies it as a recoverable
    I2C fault: get_distance() returns the I2C error code 9000 + errno (9110 for
    this ETIMEDOUT) and the sensor reinitializes on the next call, instead of
    the exception propagating to user code.
    """

    def __init__(self, message="VL53L0X I2C operation timed out"):
        super().__init__(_ETIMEDOUT, message)


class VL53L0X:
    """
    VL53L0X Time-of-Flight distance sensor driver.

    This class provides initialization and distance reading for the VL53L0X
    sensor over I2C. It supports continuous and single-shot modes.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, i2c, address=0x29, debug=False, timing_budget_us=33000):
        """
        Initializes the VL53L0X sensor.

        Args:
            i2c: An initialized I2C object.
            address (int, optional): The I2C address of the sensor. Defaults to 0x29.
            debug (bool, optional): Enables debug print statements. Defaults to False.
            timing_budget_us (int, optional): Measurement timing budget in microseconds. Defaults to 33000.
        """
        self.debug = debug
        self._dbg(f"[VL53L0X] __init__ address=0x{address:02X}")
        self.i2c = i2c
        self.address = address
        self._started = False
        self.last_range_status = 0
        self.enables = {"tcc": 0, "dss": 0, "msrc": 0, "pre_range": 0, "final_range": 0}
        self.timeouts = {
            "pre_range_vcsel_period_pclks": 0,
            "msrc_dss_tcc_mclks": 0,
            "msrc_dss_tcc_us": 0,
            "pre_range_mclks": 0,
            "pre_range_us": 0,
            "final_range_vcsel_period_pclks": 0,
            "final_range_mclks": 0,
            "final_range_us": 0,
        }
        self.vcsel_period_type = ["VcselPeriodPreRange", "VcselPeriodFinalRange"]
        self.measurement_timing_budget_us = timing_budget_us

        utime.sleep_ms(_I2C_BOOT_DELAY_MS)
        self.init()

    def _dbg(self, msg):
        if self.debug:
            print(msg)

    def ping(self):
        """
        Performs a single-shot measurement or reads the current value if in continuous mode.

        Returns:
            int: The measured distance in millimeters.
        """
        self._dbg(f"[VL53L0X] ping() started={self._started}")
        if self._started:
            # Already in continuous mode; sample without disturbing state.
            distance = self.read()
        else:
            self.start()
            distance = self.read()
            self.stop()
        self._dbg(f"[VL53L0X] ping() -> {distance} mm")
        return distance

    def _registers(self, register, values=None, struct="B"):
        if values is None:
            size = ustruct.calcsize(struct)
            for attempt in range(3):
                try:
                    data = self.i2c.readfrom_mem(self.address, register, size)
                    break
                except OSError:
                    if attempt == 2:
                        raise
                    utime.sleep_ms(1)
            values = ustruct.unpack(struct, data)
            self._dbg(
                f"  [I2C] READ  reg=0x{register:02X} struct={struct!r} -> {values}"
            )
            return values
        self._dbg(
            f"  [I2C] WRITE reg=0x{register:02X} struct={struct!r} values={values}"
        )
        data = ustruct.pack(struct, *values)
        for attempt in range(3):
            try:
                self.i2c.writeto_mem(self.address, register, data)
                return None
            except OSError:
                if attempt == 2:
                    raise
                utime.sleep_ms(1)
        return None

    def _register(self, register, value=None, struct="B"):
        if value is None:
            return self._registers(register, struct=struct)[0]
        self._registers(register, (value,), struct=struct)
        return None

    def _flag(self, register=0x00, bit=0, value=None):
        self._dbg(f"[VL53L0X] _flag reg=0x{register:02X} bit={bit} value={value}")
        data = self._register(register)
        mask = 1 << bit
        if value is None:
            return bool(data & mask)
        if value:
            data |= mask
        else:
            data &= ~mask
        self._register(register, data)
        return None

    def _config(self, *config):
        self._dbg(f"[VL53L0X] _config ({len(config)} register writes)")
        for register, value in config:
            self._register(register, value)

    def init(self, power2v8=True):
        """
        Executes the complex initialization sequence required by the VL53L0X.

        Args:
            power2v8 (bool, optional): Set to True if operating at 2.8V. Defaults to True.
        """
        self._dbg(f"[VL53L0X] init(power2v8={power2v8})")
        self._flag(_EXTSUP_HV, 0, power2v8)

        # I2C standard mode
        self._config(
            (0x88, 0x00),
            (0x80, 0x01),
            (0xFF, 0x01),
            (0x00, 0x00),
        )
        self._stop_variable = self._register(0x91)
        self._config(
            (0x00, 0x01),
            (0xFF, 0x00),
            (0x80, 0x00),
        )

        # disable signal_rate_msrc and signal_rate_pre_range limit checks
        self._flag(_MSRC_CONFIG, 1, True)
        self._flag(_MSRC_CONFIG, 4, True)

        # rate_limit = 0.25
        self._register(_FINAL_RATE_RTN_LIMIT, int(0.25 * (1 << 7)), struct=">H")

        self._register(_SYSTEM_SEQUENCE, 0xFF)

        spad_count, is_aperture = self._spad_info()
        spad_map = bytearray(self._registers(_SPAD_ENABLES, struct="6B"))

        # set reference spads
        self._config(
            (0xFF, 0x01),
            (_SPAD_REF_START, 0x00),
            (_SPAD_NUM_REQUESTED, 0x2C),
            (0xFF, 0x00),
            (_REF_EN_START_SELECT, 0xB4),
        )

        spads_enabled = 0
        for i in range(48):
            if i < 12 and is_aperture or spads_enabled >= spad_count:
                spad_map[i // 8] &= ~(1 << (i >> 2))
            elif spad_map[i // 8] & (1 << (i >> 2)):
                spads_enabled += 1

        self._registers(_SPAD_ENABLES, spad_map, struct="6B")

        self._config(
            (0xFF, 0x01),
            (0x00, 0x00),
            (0xFF, 0x00),
            (0x09, 0x00),
            (0x10, 0x00),
            (0x11, 0x00),
            (0x24, 0x01),
            (0x25, 0xFF),
            (0x75, 0x00),
            (0xFF, 0x01),
            (0x4E, 0x2C),
            (0x48, 0x00),
            (0x30, 0x20),
            (0xFF, 0x00),
            (0x30, 0x09),
            (0x54, 0x00),
            (0x31, 0x04),
            (0x32, 0x03),
            (0x40, 0x83),
            (0x46, 0x25),
            (0x60, 0x00),
            (0x27, 0x00),
            (0x50, 0x06),
            (0x51, 0x00),
            (0x52, 0x96),
            (0x56, 0x08),
            (0x57, 0x30),
            (0x61, 0x00),
            (0x62, 0x00),
            (0x64, 0x00),
            (0x65, 0x00),
            (0x66, 0xA0),
            (0xFF, 0x01),
            (0x22, 0x32),
            (0x47, 0x14),
            (0x49, 0xFF),
            (0x4A, 0x00),
            (0xFF, 0x00),
            (0x7A, 0x0A),
            (0x7B, 0x00),
            (0x78, 0x21),
            (0xFF, 0x01),
            (0x23, 0x34),
            (0x42, 0x00),
            (0x44, 0xFF),
            (0x45, 0x26),
            (0x46, 0x05),
            (0x40, 0x40),
            (0x0E, 0x06),
            (0x20, 0x1A),
            (0x43, 0x40),
            (0xFF, 0x00),
            (0x34, 0x03),
            (0x35, 0x44),
            (0xFF, 0x01),
            (0x31, 0x04),
            (0x4B, 0x09),
            (0x4C, 0x05),
            (0x4D, 0x04),
            (0xFF, 0x00),
            (0x44, 0x00),
            (0x45, 0x20),
            (0x47, 0x08),
            (0x48, 0x28),
            (0x67, 0x00),
            (0x70, 0x04),
            (0x71, 0x01),
            (0x72, 0xFE),
            (0x76, 0x00),
            (0x77, 0x00),
            (0xFF, 0x01),
            (0x0D, 0x01),
            (0xFF, 0x00),
            (0x80, 0x01),
            (0x01, 0xF8),
            (0xFF, 0x01),
            (0x8E, 0x01),
            (0x00, 0x01),
            (0xFF, 0x00),
            (0x80, 0x00),
        )

        self._register(_INTERRUPT_GPIO, 0x04)
        self._flag(_GPIO_MUX_ACTIVE_HIGH, 4, False)
        self._register(_INTERRUPT_CLEAR, 0x01)

        self._register(_SYSTEM_SEQUENCE, 0xE8)
        self.set_measurement_timing_budget(self.measurement_timing_budget_us)

        self._register(_SYSTEM_SEQUENCE, 0x01)
        self._calibrate(0x40)
        self._register(_SYSTEM_SEQUENCE, 0x02)
        self._calibrate(0x00)

        self._register(_SYSTEM_SEQUENCE, 0xE8)

    def _spad_info(self):
        self._dbg("[VL53L0X] _spad_info()")
        self._config(
            (0x80, 0x01),
            (0xFF, 0x01),
            (0x00, 0x00),
            (0xFF, 0x06),
        )
        self._flag(0x83, 3, True)
        self._config(
            (0xFF, 0x07),
            (0x81, 0x01),
            (0x80, 0x01),
            (0x94, 0x6B),
            (0x83, 0x00),
        )
        for _ in range(_IO_TIMEOUT_MS):
            if self._register(0x83):
                break
            utime.sleep_ms(1)
        else:
            raise VL53L0XTimeoutError()
        self._config(
            (0x83, 0x01),
        )
        value = self._register(0x92)
        self._config(
            (0x81, 0x00),
            (0xFF, 0x06),
        )
        self._flag(0x83, 3, False)
        self._config(
            (0xFF, 0x01),
            (0x00, 0x01),
            (0xFF, 0x00),
            (0x80, 0x00),
        )
        count = value & 0x7F
        is_aperture = bool(value & 0b10000000)
        self._dbg(f"[VL53L0X] _spad_info() -> count={count} is_aperture={is_aperture}")
        return count, is_aperture

    def _calibrate(self, vhv_init_byte):
        self._dbg(f"[VL53L0X] _calibrate(vhv_init_byte=0x{vhv_init_byte:02X})")
        self._register(_SYSRANGE_START, 0x01 | vhv_init_byte)
        for _ in range(_IO_TIMEOUT_MS):
            if self._register(_RESULT_INTERRUPT_STATUS) & 0x07:
                break
            utime.sleep_ms(1)
        else:
            raise VL53L0XTimeoutError()
        self._register(_INTERRUPT_CLEAR, 0x01)
        self._register(_SYSRANGE_START, 0x00)

    def start(self, period=0):
        """
        Starts the sensor measurement process.

        Args:
            period (int, optional): Inter-measurement period in milliseconds.
                                    If 0, continuous mode is not used. Defaults to 0.
        """
        self._dbg(f"[VL53L0X] start(period={period})")
        self._config(
            (0x80, 0x01),
            (0xFF, 0x01),
            (0x00, 0x00),
            (0x91, self._stop_variable),
            (0x00, 0x01),
            (0xFF, 0x00),
            (0x80, 0x00),
        )
        if period:
            oscilator = self._register(_OSC_CALIBRATE, struct=">H")
            if oscilator:
                period *= oscilator
            self._register(_MEASURE_PERIOD, period, struct=">I")
            self._register(_SYSRANGE_START, 0x04)
        else:
            self._register(_SYSRANGE_START, 0x02)
        self._started = True

    def stop(self):
        """Stops continuous measurement mode and puts the sensor in standby."""
        self._dbg("[VL53L0X] stop()")
        self._register(_SYSRANGE_START, 0x01)
        self._config(
            (0xFF, 0x01),
            (0x00, 0x00),
            (0x91, self._stop_variable),
            (0x00, 0x01),
            (0xFF, 0x00),
        )
        self._started = False

    def read(self):
        """
        Reads a distance measurement from the sensor.

        If not already started, it initiates a single measurement.

        Returns:
            int: The distance measurement in millimeters.
        """
        self._dbg(f"[VL53L0X] read() started={self._started}")
        if not self._started:
            self._config(
                (0x80, 0x01),
                (0xFF, 0x01),
                (0x00, 0x00),
                (0x91, self._stop_variable),
                (0x00, 0x01),
                (0xFF, 0x00),
                (0x80, 0x00),
                (_SYSRANGE_START, 0x01),
            )
            for _ in range(_IO_TIMEOUT_MS):
                if not self._register(_SYSRANGE_START) & 0x01:
                    break
                utime.sleep_ms(1)
            else:
                raise VL53L0XTimeoutError()
        for _ in range(_IO_TIMEOUT_MS):
            if self._register(_RESULT_INTERRUPT_STATUS) & 0x07:
                break
            utime.sleep_ms(1)
        else:
            raise VL53L0XTimeoutError()
        status = self._register(_RESULT_RANGE_STATUS)
        self.last_range_status = (status >> 3) & 0x0F
        value = self._register(_RESULT_RANGE_STATUS + 10, struct=">H")
        self._register(_INTERRUPT_CLEAR, 0x01)
        self._dbg(
            f"[VL53L0X] read() -> {value} mm (range_status={self.last_range_status})"
        )
        return value

    def decode_vcsel_period(self, reg_val):
        """Decodes the VCSEL period from the register value."""
        return ((reg_val) + 1) << 1

    def get_sequence_step_enables(self):
        """Retrieves the current sequence step enables from the system sequence register."""
        self._dbg("[VL53L0X] get_sequence_step_enables()")
        sequence_config = self._register(_SYSTEM_SEQUENCE)

        self.enables["tcc"] = (sequence_config >> 4) & 0x1
        self.enables["dss"] = (sequence_config >> 3) & 0x1
        self.enables["msrc"] = (sequence_config >> 2) & 0x1
        self.enables["pre_range"] = (sequence_config >> 6) & 0x1
        self.enables["final_range"] = (sequence_config >> 7) & 0x1

    def get_vcsel_pulse_period(self, period_type):
        """Retrieves the VCSEL pulse period for the given period type."""
        if period_type == self.vcsel_period_type[0]:
            return self.decode_vcsel_period(self._register(_PRE_RANGE_VCSEL_PERIOD))
        if period_type == self.vcsel_period_type[1]:
            return self.decode_vcsel_period(self._register(_FINAL_RANGE_VCSEL_PERIOD))
        return 255

    def get_sequence_step_timeouts(self):
        """Calculates the sequence step timeouts based on current sensor settings."""
        self._dbg("[VL53L0X] get_sequence_step_timeouts()")
        self.timeouts["pre_range_vcsel_period_pclks"] = self.get_vcsel_pulse_period(
            self.vcsel_period_type[0]
        )
        self.timeouts["msrc_dss_tcc_mclks"] = (
            int(self._register(_MSRC_CONFIG_TIMEOUT_MACROP)) + 1
        )
        self.timeouts["msrc_dss_tcc_us"] = self.timeout_mclks_to_microseconds(
            self.timeouts["msrc_dss_tcc_mclks"],
            self.timeouts["pre_range_vcsel_period_pclks"],
        )
        self.timeouts["pre_range_mclks"] = self.decode_timeout(
            self._register(_PRE_RANGE_TIMEOUT_MACROP_HI, struct=">H")
        )
        self.timeouts["pre_range_us"] = self.timeout_mclks_to_microseconds(
            self.timeouts["pre_range_mclks"],
            self.timeouts["pre_range_vcsel_period_pclks"],
        )
        self.timeouts["final_range_vcsel_period_pclks"] = self.get_vcsel_pulse_period(
            self.vcsel_period_type[1]
        )
        self.timeouts["final_range_mclks"] = self.decode_timeout(
            self._register(_FINAL_RANGE_TIMEOUT_MACROP_HI, struct=">H")
        )

        if self.enables["pre_range"]:
            self.timeouts["final_range_mclks"] -= self.timeouts["pre_range_mclks"]
        self.timeouts["final_range_us"] = self.timeout_mclks_to_microseconds(
            self.timeouts["final_range_mclks"],
            self.timeouts["final_range_vcsel_period_pclks"],
        )

    def timeout_mclks_to_microseconds(self, timeout_period_mclks, vcsel_period_pclks):
        """Converts a timeout period in macro clocks to microseconds."""
        macro_period_ns = self.calc_macro_period(vcsel_period_pclks)
        return ((timeout_period_mclks * macro_period_ns) + (macro_period_ns / 2)) / 1000

    def timeout_microseconds_to_mclks(self, timeout_period_us, vcsel_period_pclks):
        """Converts a timeout period in microseconds to macro clocks."""
        macro_period_ns = self.calc_macro_period(vcsel_period_pclks)
        return ((timeout_period_us * 1000) + (macro_period_ns / 2)) / macro_period_ns

    def calc_macro_period(self, vcsel_period_pclks):
        """Calculates the macro period in nanoseconds."""
        return ((2304 * (vcsel_period_pclks) * 1655) + 500) / 1000

    def decode_timeout(self, reg_val):
        """Decodes a timeout value from the given register format."""
        return ((reg_val & 0x00FF) << ((reg_val & 0xFF00) >> 8)) + 1

    def encode_timeout(self, timeout_mclks):
        """Encodes a timeout value in macro clocks into the register format."""
        timeout_mclks = int(timeout_mclks)
        ls_byte = 0
        ms_byte = 0

        if timeout_mclks > 0:
            ls_byte = timeout_mclks - 1

            while (ls_byte & 0xFFFFFF00) > 0:
                ls_byte >>= 1
                ms_byte += 1
            return (ms_byte << 8) | (ls_byte & 0xFF)
        return 0

    def set_measurement_timing_budget(self, budget_us):
        """
        Sets the measurement timing budget.

        Longer timing budgets improve measurement accuracy but reduce the measurement rate.
        The minimum timing budget is 20000 microseconds.

        Args:
            budget_us (int): Timing budget in microseconds.

        Returns:
            bool: True if the timing budget was applied successfully, False if the
                  budget is below the minimum or cannot be fulfilled.
        """
        self._dbg(f"[VL53L0X] set_measurement_timing_budget(budget_us={budget_us})")
        start_overhead = 1320
        end_overhead = 960
        msrc_overhead = 660
        tcc_overhead = 590
        dss_overhead = 690
        pre_range_overhead = 660
        final_range_overhead = 550

        min_timing_budget = 20000

        if budget_us < min_timing_budget:
            return False
        used_budget_us = start_overhead + end_overhead

        self.get_sequence_step_enables()
        self.get_sequence_step_timeouts()

        if self.enables["tcc"]:
            used_budget_us += self.timeouts["msrc_dss_tcc_us"] + tcc_overhead
        if self.enables["dss"]:
            used_budget_us += 2 * self.timeouts["msrc_dss_tcc_us"] + dss_overhead
        if self.enables["msrc"]:
            used_budget_us += self.timeouts["msrc_dss_tcc_us"] + msrc_overhead
        if self.enables["pre_range"]:
            used_budget_us += self.timeouts["pre_range_us"] + pre_range_overhead
        if self.enables["final_range"]:
            used_budget_us += final_range_overhead

            if used_budget_us > budget_us:
                return False
            final_range_timeout_us = budget_us - used_budget_us
            final_range_timeout_mclks = self.timeout_microseconds_to_mclks(
                final_range_timeout_us, self.timeouts["final_range_vcsel_period_pclks"]
            )

            if self.enables["pre_range"]:
                final_range_timeout_mclks += self.timeouts["pre_range_mclks"]
            self._register(
                _FINAL_RANGE_TIMEOUT_MACROP_HI,
                self.encode_timeout(final_range_timeout_mclks),
                struct=">H",
            )
            self.measurement_timing_budget_us = budget_us
        return True

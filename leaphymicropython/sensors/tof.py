"""This module provides time-of-flight related calculations."""

from leaphymicropython.sensors.vl53l0x import VL53L0X
from leaphymicropython.utils.i2c_helper import I2CDevice
from leaphymicropython.utils.i2c_helper import handle_i2c_errors


class TimeOfFlight(I2CDevice):
    """
    VL53L0X time-of-flight sensor wrapper with multiplexer support.

    The sensor runs in continuous-timed mode: it measures autonomously at
    `period_ms` intervals, and each get_distance() reads the latest sample
    instead of re-triggering. This gives near-chip-rate throughput when
    multiple sensors share a TCA9548A-style I2C multiplexer.

    Return semantics for get_distance(): every result is a non-negative int,
    and every non-distance result is a sentinel above 8090 (the practical max
    distance) so callers can treat "value > 8090" as "not a valid reading":
      * 0..~8090 - valid distance in millimeters
      * TimeOfFlight.OUT_OF_RANGE (8191) - sensor responded but the target is
                                    out of range: too far / no target (or
                                    saturation at maximum distance), or too
                                    close (below ~50 mm, where the chip clamps
                                    to ~0 and readings are unreliable)
      * 9000 + errno - I2C communication failed (e.g. 9005, 9009, 9110, 9116).
                       Decode the errno as value - 9000. The next
                       get_distance() will attempt reinitialization.
      * TimeOfFlight.UNKNOWN_ERROR (9999) - error without an errno.

    Tests:
    1. channel=255, no multiplexer, sensor connected
       Disconnect -> 9000 + errno (e.g. 9110, with warning if show_warnings).
       Reconnect  -> valid readings resume.
    2. channel=255, no multiplexer, sensor not connected -> 9000 + errno.
    3. channel=0..7, with multiplexer, sensor connected
       Same disconnect/reconnect behavior.
    4. channel=0..7, with multiplexer, sensor not connected -> 9000 + errno.
    """

    # the following attribute is used by decorator handle_i2c_errors
    ADDRESS = 0x29

    # Sentinels returned by get_distance() in place of a distance. All are
    # above 8090 (the practical max distance) so callers can branch on
    # `value > 8090` to detect any non-distance result.
    OUT_OF_RANGE = 8191  # sensor responded but reports no valid target
    I2C_ERROR_BASE = 9000  # recoverable I2C fault -> code = 9000 + errno
    UNKNOWN_ERROR = 9999  # error without an errno (e.g. a bare RuntimeError)

    # Distance at/above which a reading is treated as out-of-range saturation.
    # NB: this cutoff (8000 mm) assumes the sensor is in its default range
    # configuration. A long-range preset would push the legitimate maximum
    # higher and this constant would need to follow.
    _OUT_OF_RANGE_MM = 8000

    # Distance below which a reading is treated as out-of-range. The VL53L0X
    # clamps to ~0 and is unreliable below a few cm, so values under this floor
    # (notably the impossible 0) are rejected as "too close".
    _MIN_VALID_MM = 50

    # VL53L0X device range status that indicates a valid measurement. Any other
    # status (sigma/phase/signal-rate failure, etc.) means the reported distance
    # is unreliable and should be treated as out-of-range.
    _VALID_RANGE_STATUS = 11

    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        channel=255,
        sda_gpio_pin=12,
        scl_gpio_pin=13,
        bus_id=0,
        freq=400_000,
        show_warnings=True,
        timing_budget_us=33000,
        debug=False,
    ):
        """
        Initializes the TimeOfFlight object.

        Args:
            channel (int, optional): The I2C multiplexer channel to select.
            Options are: 0-7 and 255
            sda_gpio_pin (int, optional): The GPIO pin connected to the SDA line. Defaults to 12.
            scl_gpio_pin (int, optional): The GPIO pin connected to the SCL line. Defaults to 13.
            bus_id (int, optional): identifies a particular I2C peripheral, for example bus 0 or 1.
            freq (int, optional): I2C bus frequency in Hz. Defaults to 400000.
            show_warnings (bool, optional): if True, show warning about device address not found
            timing_budget_us (int, optional): VL53L0X measurement timing budget in microseconds.
                Longer = more accurate/stable but slower. Must be >= 20000.
            debug (bool, optional): if True, emit VL53L0X trace prints.
        """
        super().__init__(
            channel, sda_gpio_pin, scl_gpio_pin, bus_id, freq, show_warnings
        )
        self.tof = None
        self.timing_budget_us = timing_budget_us
        self.debug = debug

    @property
    def last_status(self):
        """Internal range status (0-15) of the most recent read, or None."""
        if self.tof is None:
            return None
        return self.tof.last_range_status

    def on_i2c_error(self, ex):
        """Map a recoverable I2C error to a get_distance() sentinel above 8090.

        Returns 9000 + errno so the caller can see which I2C fault occurred,
        or UNKNOWN_ERROR (9999) for an error that carries no errno.
        """
        errno = getattr(ex, "errno", None)
        if errno is None:
            return self.UNKNOWN_ERROR
        return self.I2C_ERROR_BASE + errno

    def initialize_device(self):
        """
        Initialize the underlying VL53L0X driver and start continuous mode.

        If a previous sensor object exists (reinit path after a bus error),
        attempt to stop it first so the chip transitions cleanly out of
        whatever mode it was left in.
        """
        super().initialize_device()
        if self.tof is not None:
            try:
                self.tof.stop()
            except OSError:
                pass
        self.tof = VL53L0X(
            self.i2c, debug=self.debug, timing_budget_us=self.timing_budget_us
        )
        # Inter-measurement period in ms; must exceed the timing budget.
        # 10 ms headroom over (budget_us/1000) is the chip's recommended slack.
        period_ms = max(50, self.timing_budget_us // 1000 + 10)
        self.tof.start(period=period_ms)

    @handle_i2c_errors
    def get_distance(self):
        """
        Retrieves the distance measurement from the VL53L0X sensor.

        If a multiplexer channel is specified, it selects the appropriate
        channel before reading from the sensor.

        Returns:
            int: distance in mm (0..~8090) for a valid reading.
            TimeOfFlight.OUT_OF_RANGE (8191) if the sensor responded but the
            measurement was invalid (bad range status), no target was detected,
            the target was too far, or the target was too close (below ~50 mm).
            9000 + errno if I2C communication failed (decode errno as
            value - 9000), or TimeOfFlight.UNKNOWN_ERROR (9999) for an error
            without an errno.
        """
        distance = self.tof.read()
        if self.tof.last_range_status != self._VALID_RANGE_STATUS:
            return self.OUT_OF_RANGE
        if distance < self._MIN_VALID_MM or distance >= self._OUT_OF_RANGE_MM:
            return self.OUT_OF_RANGE
        return distance

    def deinit(self):
        """
        Stops the sensor's continuous-measurement mode.

        Safe to call even if the sensor was never started or is no longer
        reachable. A subsequent get_distance() will trigger a full
        reinitialization.
        """
        if self.tof is None or self.reinitialize:
            return
        try:
            if self.is_mux_used():
                self.select_channel()
            self.tof.stop()
        except OSError:
            pass

    def __del__(self):
        # Best-effort cleanup; __del__ must never raise.
        try:
            self.deinit()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

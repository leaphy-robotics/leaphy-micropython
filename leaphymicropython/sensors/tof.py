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

    Return semantics for get_distance():
      * int  - valid distance in millimeters
      * TimeOfFlight.OUT_OF_RANGE - sensor responded but reports no target
                                    (or saturation at maximum distance)
      * None - I2C communication failed; sensor is unreachable.
               The next get_distance() will attempt reinitialization.

    Tests:
    1. channel=255, no multiplexer, sensor connected
       Disconnect -> None (with warning if show_warnings).
       Reconnect  -> valid readings resume.
    2. channel=255, no multiplexer, sensor not connected -> None.
    3. channel=0..7, with multiplexer, sensor connected
       Same disconnect/reconnect behavior.
    4. channel=0..7, with multiplexer, sensor not connected -> None.
    """

    # the following attribute is used by decorator handle_i2c_errors
    ADDRESS = 0x29

    # Sentinel returned by get_distance() when the sensor responded but no
    # valid target was detected. Negative so callers can branch on `< 0`.
    # NB: this cutoff (8000 mm) assumes the sensor is in its default range
    # configuration. A long-range preset would push the legitimate maximum
    # higher and this constant would need to follow.
    OUT_OF_RANGE = -1
    _OUT_OF_RANGE_MM = 8000

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
            int: distance in mm for a valid reading.
            TimeOfFlight.OUT_OF_RANGE (-1) if the sensor responded but no
            target was detected.
            None if I2C communication failed.
        """
        distance = self.tof.read()
        if distance >= self._OUT_OF_RANGE_MM:
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

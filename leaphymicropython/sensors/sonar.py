import time

import machine
from machine import Pin


def read_distance(trig_pin: str, echo_pin: str) -> float:
    """Reads distance from object
    :param trig_pin: Trigger pin
    :param echo_pin: Echo pin
    :return: The distance
    """
    trigger = Pin(trig_pin, Pin.OUT)
    echo = Pin(echo_pin, Pin.IN)
    pulse_time = _send_pulse_and_wait(trigger, echo)
    if pulse_time < 0:
        # Timeout
        return 1313.0

    # To calculate the distance we get the pulse_time and divide it by 2
    # (the pulse walk the distance twice) and by 29.1 because
    # the sound speed on air (343.2 m/s), that It's equivalent to
    # 0.034320 cm/us that is 1cm each 29.1us
    cms = (pulse_time / 2) / 29.1
    return cms


# echo_timeout_us is based in chip range limit (400cm)
def _send_pulse_and_wait(
    trigger: Pin, echo: Pin, echo_timeout_us=500 * 2 * 30
) -> float:
    """
    Send the pulse to trigger and listen on echo pin.
    We use the method `machine.time_pulse_us()` to get the microseconds until the echo is received.
    """
    trigger.value(0)  # Stabilize the sensor
    time.sleep_us(5)  # pylint: disable=no-member
    trigger.value(1)
    # Send a 10us pulse.
    time.sleep_us(10)  # pylint: disable=no-member
    trigger.value(0)
    return machine.time_pulse_us(echo, 1, echo_timeout_us)

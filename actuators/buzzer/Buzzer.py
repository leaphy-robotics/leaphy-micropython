from machine import Pin, PWM
from PWM import set_pwm


def set_buzzer(pin: int, freq: int):
    """
    Sets the buzzer
    :param pin: int, the pin of the buzzer
    :param freq: int, the frequency of the buzzer
    """
    if freq < 0 or freq > 255:
        raise ValueError("Buzzer values must be in between 0 and 255")
    set_pwm(pin, freq, 255)

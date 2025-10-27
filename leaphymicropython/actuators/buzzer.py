from leaphymicropython.utils.pins import set_pwm


def set_buzzer(pin: str, value: int, freq: int):
    """
    Sets the buzzer
    :param pin: str, the pin of the buzzer
    :param value: int, the value of the buzzer
    :param freq: int, the frequency of the buzzer
    """
    if freq < 0 or freq > 255:
        raise ValueError(
            "Buzzer values must be up to and including 0 and 255, your freq is {freq}"
        )
    set_pwm(pin, value, freq)

from machine import Pin, PWM, ADC
from leaphymicropython.utils.boards_config import pin_to_gpio


def get_analog_pin(pin_name: str) -> ADC:
    """
    Initializes an analog pin using ADC
    :param pin_name: the pin to check
    :return: ADC object if the pin is analog, ValueError otherwise
    """
    try:
        pin = ADC(pin_name)
        return pin
    except ValueError as ex:
        # ValueError has an attribute 'value', contrary to the belief of pylint
        if ex.value == "Pin doesn't have ADC capabilities":  # pylint: disable=no-member
            print(f"It is not possible to use pin {pin_name} in an analog way")
            print(
                "Please use a pin that has a label that starts with A, for example A0, A1, etc."
            )
        raise ex


def set_pwm(pin: int, value: int, freq: int = 50):
    """Sets a pwm pin
    :param pin: int, the pin to set
    :param value: int, the value to set the pin to
    :param freq: int, the frequency of the pwm
    """
    pin = pin_to_gpio(pin)
    if value < 0 or value > 255:
        raise ValueError("PWM value must be between 0 and 255")
    pwm = PWM(Pin(pin))
    pwm.freq(freq)
    pwm.duty_u16(value * 257)


def read_pwm(pin: int):
    """
    Reads a pwm pin
    :param pin: int, the pin to read
    :return: int, the value of the pin
    """
    pin = pin_to_gpio(pin)
    pwm = PWM(Pin(pin))
    return round(pwm.duty_u16() / 257)


def set_pin(pin: int, value: int):
    """
    Sets a pin
    :param pin: int, the pin to set
    :param value: int, the value to set the pin to
    """
    pin = pin_to_gpio(pin)
    pin = Pin(pin, Pin.OUT)
    if value < 0 or value > 1:
        raise ValueError("Pin values must be in between 0 and 1")
    pin.value(value)


def read_pin(pin: int) -> int:
    """
    Reads a pin
    :param pin: int, the pin to read
    :return: int, the value of the pin
    """
    pin = pin_to_gpio(pin)
    pin = Pin(pin, Pin.IN)
    return pin.value()


def read_analog(pin: int) -> int:
    """
    reads an analog pin
    :param pin: the pin to read
    :return: returns the value
    """
    pin = pin_to_gpio(pin)
    adcpin = ADC(Pin(pin))
    return adcpin.read_u16()

from machine import Pin,PWM
from .boards_config import pinToGPIO


def setPWM(pin: int, value: int):
    """ Set PWM,\n
        pin: int, value: int\n
        value must be between 0 and 255\n
    """
    pin = pinToGPIO(pin)
    if not value > -1 and not value < 256: raise ValueError("PWM value must be between 0 and 255")
    pwm = PWM(Pin(pin))
    pwm.freq(1000)
    pwm.duty_u16(value * 257)


def readPWM(pin: int):
    """ Read PWM,\n
        pin: int\n
        returns a value between 0 and 1"""
    pin = pinToGPIO(pin)
    pwm = PWM(Pin(pin))
    return pwm.duty_u16() / 257



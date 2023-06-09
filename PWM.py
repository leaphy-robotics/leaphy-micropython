from machine import Pin,PWM

def setPWM(pin: int, value: int):
    if not value > -1 and not value < 256: raise ValueError("PWM value must be between 0 and 255")
    pwm = PWM(Pin(pin))
    pwm.freq(1000)
    pwm.duty_u16(value * 257)


def readPWM(pin: int):
    pwm = PWM(Pin(pin))
    return pwm.duty_u16() / 257



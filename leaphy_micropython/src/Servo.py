from time import sleep
from .boards_config import pinToGPIO
from machine import Pin, PWM

def convertAngleToU16180(degrees):
    """ Convert angle to u16,\n
        graden: int\n
        graden must be between 0 and 180\n
        returns a value between 2000 and 9000"""
    if degrees < 0 or degrees > 180: raise ValueError("Angle must be between 0 and 180")
    u16PerDegree: float = (9000-2000)/180
    return round((9000 - (degrees * u16PerDegree)))

def servoMoveTo180(pin: int, angle: int):
    """ Move servo to angle,\n
        pin: int, angle: int\n
        angle must be between 0 and 180\n
    """
    pin = pinToGPIO(pin)
    if angle < 0 or angle > 180: raise ValueError("Angle must be between 0 and 180")
    pwm = PWM(Pin(pin))
    pwm.freq(50)
    oldPos: int = pwm.duty_u16()
    anglesU16: int = convertAngleToU16180(angle)
    for pos in range(oldPos, anglesU16, 50 if oldPos < anglesU16 else -50):
        pwm.duty_u16(pos)
        sleep(0.01)





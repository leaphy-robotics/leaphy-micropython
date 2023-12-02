from time import sleep

from leaphymicropython.utils.boards_config import pin_to_gpio
from machine import Pin, PWM


def servo_angle(pin: int, angle: int):
    """Puts the servo on a angle"""
    pin = pin_to_gpio(pin)
    pwm = PWM(Pin(pin))
    pwm.freq(50)
    degrees_in_u16 = (9000 - 2000) / 180
    u_16 = round(9000 - (angle * degrees_in_u16))
    if not angle > -1 and not angle < 181:
        raise ValueError("The angle must be in between 0 and 180")
    current_pos = pwm.duty_u16()
    for pos in range(current_pos, u_16, 50 if current_pos < u_16 else -50):
        pwm.duty_u16(pos)
        sleep(0.01)

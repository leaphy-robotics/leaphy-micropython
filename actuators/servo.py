from leaphymicropython.utils.boards_config import pin_to_gpio
from machine import Pin, PWM


def servo_angle(pin: int, angle: int) -> None:
    """
    Puts the servo on an angle
    :param pin: The pin number to which the servo motor is connected
    :param angle: The angle to set the servo motor to
    """
    pin = pin_to_gpio(pin)
    pwm = PWM(Pin(pin))
    pwm.freq(50)
    degrees_in_u16 = (9000 - 2000) / 180
    duty_cycle = round(9000 - (angle * degrees_in_u16))
    if not angle > -1 or not angle < 361:
        raise ValueError("The angle must be in between 0 and 180")
    pwm.duty_u16(duty_cycle)

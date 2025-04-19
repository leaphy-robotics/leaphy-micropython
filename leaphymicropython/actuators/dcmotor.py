"""
Module for controlling DC motors.
"""

from time import sleep
from machine import Pin, PWM  # pylint: disable=import-error


class DCMotors:  # pylint: disable=too-few-public-methods
    """
    A class to control multiple DC motors
    """

    def __init__(
        self,
        dir_pin_motor_a="D2",
        dir_pin_motor_b="D4",
        pwn_pin_motor_a="D3",
        pwn_pin_motor_b="D11",
    ):
        self.motor_a = DCMotor(direction_pin=dir_pin_motor_a, pwn_pin=pwn_pin_motor_a)
        self.motor_b = DCMotor(direction_pin=dir_pin_motor_b, pwn_pin=pwn_pin_motor_b)


class DCMotor:
    """
    A class to control a DC motor
    """

    MAX_U16 = 65535

    def __init__(self, direction_pin, pwn_pin, freq=20000):
        """
        Creates a DC motor
        :param direction_pin: the pin used to indicate the direction of the motor
        :param pwn_pin: the pin used to determine the pwm signal of the motor
        :param freq: the frequency of the pwm signal, defaults to 2.000
        """
        self.direction = Pin(direction_pin, Pin.OUT)
        self.pwm = PWM(pwn_pin)
        self.pwm.freq(freq)

    def forward(self, speed: int):
        """
        Sets the DC motor to forward
        :param speed: int, the speed of the motor
        """
        self.direction.value(1)
        self.validate_speed(speed)
        speed_u16 = self.convert_speed_to_duty_u16(speed)
        self.pwm.duty_u16(speed_u16)

    def backward(self, speed: int):
        """
        Sets the DC motor to backward
        :param speed: int, the speed of the motor
        """
        self.direction.value(0)
        self.validate_speed(speed)
        speed_u16 = self.convert_speed_to_duty_u16(speed)
        self.pwm.duty_u16(speed_u16)

    def stop(self):
        """
        Stops the DC motor
        """
        self.pwm.duty_u16(0)

    def test(self):
        """
        Tests the DC motor
        """
        self.forward(100)
        sleep(1)
        self.backward(100)
        sleep(1)
        self.stop()
        sleep(1)

    def validate_speed(self, speed):
        """
        Validates the speed of the motor
        :param speed: int, the speed of the motor
        """
        assert 0 <= speed <= 100, "Speed must be between 0 and 100"

    def convert_speed_to_duty_u16(self, speed: int):
        """
        Converts the speed to a u16 cycle
        :param speed: int, the speed of the motor

        :return: int, the u16 cycle of the speed
        """
        u16 = speed * (self.MAX_U16 / 100)
        u16 = int(u16)
        return u16

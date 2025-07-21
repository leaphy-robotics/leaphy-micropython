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

    def steer(self, direction: str, speed: int, steering_intensity: float):
        """
        Steers the vehicle right with adjustable intensity.

        We're assuming that:
        - motor_a is the left motor
        - motor_b is the right motor

        :param direction: left, right, forward or backward
        :param speed: The base speed of the motors.
        :param steering_intensity: A value between 0 (straight) and 1 (fully turning), ignored when using forward or backward direction
        """
        self.motor_b.validate_speed(speed)
        if steering_intensity < 0 or steering_intensity > 1:
            raise ValueError("Steering intensity must be between 0 and 1")
        if direction not in ["left", "right", "forward", "backward"]:
            raise ValueError("Steering direction should be left, right, forward or backward")

        speed_left = speed
        speed_right = speed

        if direction == "left":
            speed_left = int(speed * (1 - 2 * steering_intensity))
        elif direction == "right":
            speed_right = int(speed * (1 - 2 * steering_intensity))
        elif direction == "forward":
            # Default values are good
            pass
        elif direction == "backward":
            speed_left = -speed
            speed_right = -speed

        if speed_left >= 0:
            self.motor_a.forward(speed_left)
        else:
            self.motor_a.backward(-speed_left)
        
        if speed_right >= 0:
            self.motor_b.forward(speed_right)
        else:
            self.motor_b.backward(-speed_right)

    def stop(self):
        """
        Stops the DC motors
        """
        self.motor_a.stop()
        self.motor_b.stop()

    def test(self):
        """
        Tests the DC motors
        """
        self.motor_a.test()
        self.motor_b.test()


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
        :param freq: the frequency of the pwm signal, defaults to 20.000
        """
        self.direction = Pin(direction_pin, Pin.OUT)
        self.pwm = PWM(pwn_pin)
        self.pwm.freq(freq)

    def forward(self, speed: int):
        """
        Sets the DC motor to forward
        :param speed: int, the speed of the motor
        """
        self.validate_speed(speed)
        self.direction.value(1)
        speed_u16 = self.convert_speed_to_duty_u16(speed)
        self.pwm.duty_u16(speed_u16)

    def backward(self, speed: int):
        """
        Sets the DC motor to backward
        :param speed: int, the speed of the motor
        """
        self.validate_speed(speed)
        self.direction.value(0)
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
        self.forward(255)
        sleep(1)
        self.backward(255)
        sleep(1)
        self.stop()
        sleep(1)

    def validate_speed(self, speed):
        """
        Validates the speed of the motor
        :param speed: int, the speed of the motor
        """
        if not 0 <= speed <= 255:
            raise ValueError(f"Speed must be between 0 and 255, your speed is {speed}")

    def convert_speed_to_duty_u16(self, speed: int):
        """
        Converts the speed to a u16 cycle
        :param speed: int, the speed of the motor

        :return: int, the u16 cycle of the speed
        """
        u16 = speed * (self.MAX_U16 / 255)
        u16 = int(u16)
        return u16

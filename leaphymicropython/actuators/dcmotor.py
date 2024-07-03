from leaphymicropython.utils.boards_config import pin_to_gpio
from leaphymicropython.utils.pins import set_pwm, set_pin


class DCMotor:
    """
    This class represents a DCMotor object
    """

    def __init__(
        self, motor_a: int = 2, motor_b: int = 4, enable_a: int = 3, enable_b: int = 11
    ):
        """
        Constructs all the necessary attributes for the DC Motor object.

        :param motor_a: GPIO pin number for motor A. Default is 2.
        :param motor_b: GPIO pin number for motor B. Default is 4.
        :param enable_a: GPIO pin number to enable motor A. Default is 3.
        :param enable_b: GPIO pin number to enable motor B. Default is 11.
        """
        self.value_speed_cw = None
        self.value_speed_ccw = None
        self.motor_a = pin_to_gpio(motor_a)
        self.motor_b = pin_to_gpio(motor_b)
        self.enable_a = pin_to_gpio(enable_a)
        self.enable_b = pin_to_gpio(enable_b)

    def convert_cw(self, speed: int) -> float:
        """
        Converts speed to a value suitable for clockwise rotation.

        :param speed: The speed value to convert.
        :return: The converted speed value for clockwise rotation.
        """
        self.value_speed_cw = (127.5 / 255) * speed
        return self.value_speed_cw

    def convert_ccw(self, speed: int) -> float:
        """
        Converts speed to a value suitable for counterclockwise rotation.

        :param speed: The speed value to convert.
        :return: The converted speed value for counterclockwise rotation.
        """
        self.value_speed_ccw = (127.5 / 255) * speed + 127.5
        return self.value_speed_ccw

    def forward(self, speed: int):
        """
        Moves the motor forward at the specified speed.

        :param speed: The speed value for forward motion.
        """
        self.convert_ccw(speed)
        set_pwm(self.motor_a, self.value_speed_cw, 20000)
        set_pwm(self.motor_b, self.value_speed_cw, 20000)
        set_pin(self.enable_a, True)
        set_pin(self.enable_b, True)

    def backward(self, speed: int):
        """
        Moves the motor backward at the specified speed.

        :param speed: The speed value for backward motion.
        """
        self.convert_ccw(speed)
        set_pwm(self.motor_a, self.value_speed_ccw, 20000)
        set_pwm(self.motor_b, self.value_speed_ccw, 20000)
        set_pin(self.enable_a, True)
        set_pin(self.enable_b, True)

    def left(self, speed: int, direction: int):
        """
        Turns the motor left at the specified speed and direction.

        :param speed: The speed value for turning.
        :param direction: The direction for turning (1 for CW, 0 for CCW).
        """
        if direction == 1:
            self.convert_cw(speed)
            set_pwm(self.motor_a, self.value_speed_cw, 20000)
            set_pwm(self.motor_a, self.value_speed_cw / 8, 20000)
            set_pin(self.enable_a, True)
            set_pin(self.enable_b, True)
        elif direction == 0:
            self.convert_ccw(speed)
            set_pwm(self.motor_a, self.value_speed_cw, 20000)
            set_pwm(self.motor_a, self.value_speed_cw / 8, 20000)
            set_pin(self.enable_a, True)
            set_pin(self.enable_b, True)

    def right(self, speed: int, direction: int):
        """
        Turns the motor right at the specified speed and direction.

        :param speed: The speed value for turning.
        :param direction: The direction for turning (1 for CW, 0 for CCW).
        """
        if direction == 1:
            self.convert_cw(speed)
            set_pwm(self.motor_a, self.value_speed_cw / 8, 20000)
            set_pwm(self.motor_a, self.value_speed_cw, 20000)
            set_pin(self.enable_a, True)
            set_pin(self.enable_b, True)
        elif direction == 0:
            self.convert_ccw(speed)
            set_pwm(self.motor_a, self.value_speed_cw / 8, 20000)
            set_pwm(self.motor_a, self.value_speed_cw, 20000)
            set_pin(self.enable_a, True)
            set_pin(self.enable_b, True)

    def stop(self):
        """
        Stops the motor
        """
        set_pin(self.enable_a, False)
        set_pin(self.enable_b, False)

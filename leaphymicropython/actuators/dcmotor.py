from leaphymicropython.utils.boards_config import pin_to_gpio
from leaphymicropython.utils.pins import set_pwm, set_pin
import time


class DCMotor:
    """
    This class controls a DC motor shield with 2 PWM and 2 enable pins.
    It includes advanced features such as steering control, soft start/stop,
    motor calibration, and debug functionality.
    """

    def __init__(
        self,
        motor_a: int = 2,
        motor_b: int = 4,
        enable_a: int = 3,
        enable_b: int = 11,
        motor_balance: float = 1.0,
        debug: bool = False
    ):
        """
        Initializes the DC motor with specified GPIO pins and optional configurations.

        :param motor_a: GPIO pin number for motor A. Default is 2.
        :param motor_b: GPIO pin number for motor B. Default is 4.
        :param enable_a: GPIO pin number to enable motor A. Default is 3.
        :param enable_b: GPIO pin number to enable motor B. Default is 11.
        :param motor_balance: Calibration factor for balancing motor speeds. Default is 1.0.
        :param debug: Enable debug mode for logging PWM values and states. Default is False.
        """
        self.value_speed_cw = None
        self.value_speed_ccw = None
        self.motor_a = pin_to_gpio(motor_a)
        self.motor_b = pin_to_gpio(motor_b)
        self.enable_a = pin_to_gpio(enable_a)
        self.enable_b = pin_to_gpio(enable_b)
        self.motor_balance = motor_balance
        self.debug = debug

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

    def steer(self, speed: int, steering_intensity: float):
        """
        Steers the vehicle left or right with adjustable intensity.

        :param speed: The base speed of the motors.
        :param steering_intensity: A value between -1 (max left) and 1 (max right).
        """
        steering_intensity = max(min(steering_intensity, 1), -1)

        if steering_intensity > 0:
            left_motor_speed = speed
            right_motor_speed = speed * (1 - steering_intensity)
        elif steering_intensity < 0:
            left_motor_speed = speed * (1 + steering_intensity)
            right_motor_speed = speed
        else:
            left_motor_speed = speed
            right_motor_speed = speed

        left_pwm = self.convert_ccw(left_motor_speed)
        right_pwm = self.convert_ccw(right_motor_speed)

        set_pwm(self.motor_a, left_pwm, 20000)
        set_pwm(self.motor_b, right_pwm, 20000)
        set_pin(self.enable_a, True)
        set_pin(self.enable_b, True)

    def soft_start(self, target_speed: int, duration: float):
        """
        Gradually increases the motor speed to the target value.

        :param target_speed: The desired final speed.
        :param duration: The time over which to increase the speed (in seconds).
        """
        steps = 50
        step_delay = duration / steps
        for speed in range(0, target_speed + 1, target_speed // steps):
            self.forward(speed)
            time.sleep(step_delay)

    def stop(self):
        """
        Stops the motor.
        """
        set_pin(self.enable_a, False)
        set_pin(self.enable_b, False)

    def reset(self):
        """
        Resets all pins to a safe state.
        """
        set_pin(self.enable_a, False)
        set_pin(self.enable_b, False)
        set_pwm(self.motor_a, 0, 20000)
        set_pwm(self.motor_b, 0, 20000)

    def test_motors(self):
        """
        Tests the motors by activating them sequentially.
        """
        print("Testing Motor A Forward")
        self.forward(100)
        time.sleep(1)
        self.stop()

        print("Testing Motor B Backward")
        self.backward(100)
        time.sleep(1)
        self.stop()

        print("Testing Steering Left")
        self.steer(100, -1)
        time.sleep(1)
        self.stop()

        print("Testing Steering Right")
        self.steer(100, 1)
        time.sleep(1)
        self.stop()

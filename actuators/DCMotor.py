from leaphymicropython.utils.boards_config import pin_to_gpio
from machine import Pin


class DCMotor:
    """DC Motor class"""

    def __init__(
        self, in_1: int, in_2: int, in_3: int, in_4: int, en_a: int, en_b: int
    ):
        """
        Creates a DC motor
        :param in_1: int, the pin of the in1
        :param in_2: int, the pin of the in2
        :param in_3: int, the pin of the in3
        :param in_4: int, the pin of the in4
        :param en_a: int, the pin of the enable pin a
        :param en_b: int, the pin of the enable pin b
        """
        in_1 = pin_to_gpio(in_1)
        in_2 = pin_to_gpio(in_2)
        en_a = pin_to_gpio(en_a)
        in_3 = pin_to_gpio(in_3)
        in_4 = pin_to_gpio(in_4)
        en_b = pin_to_gpio(en_b)
        self.In1 = Pin(in_1, Pin.OUT)
        self.In2 = Pin(in_2, Pin.OUT)
        self.EN_A = Pin(en_a, Pin.OUT)
        self.In3 = Pin(in_3, Pin.OUT)
        self.In4 = Pin(in_4, Pin.OUT)
        self.EN_B = Pin(en_b, Pin.OUT)

    def set_pins(
        self, in_1: int, in_2: int, in_3: int, in_4: int, en_a: int, en_b: int
    ):
        """
        Sets the pins of the DC motor
        :param in_1: int, the pin of the in1
        :param in_2: int, the pin of the in2
        :param in_3: int, the pin of the in3
        :param in_4: int, the pin of the in4
        :param en_a: int, the pin of the enable pin a
        :param en_b: int, the pin of the enable pin b
        """
        self.In1 = Pin(in_1, Pin.OUT)
        self.In2 = Pin(in_2, Pin.OUT)
        self.EN_A = Pin(en_a, Pin.OUT)
        self.In3 = Pin(in_3, Pin.OUT)
        self.In4 = Pin(in_4, Pin.OUT)
        self.EN_B = Pin(en_b, Pin.OUT)

    def move_forward(self):
        """
        Moves the DC motor forward
        """
        self.in_1.high()
        self.in_2.low()
        self.in_3.high()
        self.in_4.low()

    def move_backward(self):
        """
        Moves the DC motor backward
        """
        self.in_1.low()
        self.in_2.high()
        self.in_3.low()
        self.in_4.high()

    def turn_right(self):
        """
        Moves the DC motor to the right
        """
        self.in_1.low()
        self.in_2.low()
        self.in_3.low()
        self.in_4.high()

    def turn_left(self):
        """
        Moves the DC motor to the left
        """
        self.in_1.low()
        self.in_2.high()
        self.in_3.low()
        self.in_4.low()

    def stop(self):
        """
        Stops the DC motor
        """
        self.in_1.low()
        self.in_2.low()
        self.in_3.low()
        self.in_4.low()

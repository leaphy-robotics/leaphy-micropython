from machine import Pin


class DCMotor:
    """DC Motor class"""
    In1: Pin
    In2: Pin
    EN_A: Pin
    In3: Pin
    In4: Pin
    EN_B: Pin

    def __init__(self, in1: int, in2: int, in3: int, in4: int, en_a: int, en_b: int):
        """
        Creates a DC motor
        :param in1: int, the pin of the in1
        :param in2: int, the pin of the in2
        :param in3: int, the pin of the in3
        :param in4: int, the pin of the in4
        :param en_a: int, the pin of the enable pin a
        :param en_b: int, the pin of the enable pin b
        """
        self.In1 = Pin(in1,Pin.OUT)
        self.In2 = Pin(in2,Pin.OUT)
        self.EN_A = Pin(en_a,Pin.OUT)
        self.In3 = Pin(in3,Pin.OUT)
        self.In4 = Pin(in4,Pin.OUT)
        self.EN_B = Pin(en_b,Pin.OUT)
        
    def set_pins(self, in1: int, in2: int, in3: int, in4: int, en_a: int, en_b: int):
        """
        Sets the pins of the DC motor
        :param in1: int, the pin of the in1
        :param in2: int, the pin of the in2
        :param in3: int, the pin of the in3
        :param in4: int, the pin of the in4
        :param en_a: int, the pin of the enable pin a
        :param en_b: int, the pin of the enable pin b
        """
        self.In1 = Pin(in1, Pin.OUT)
        self.In2 = Pin(in2, Pin.OUT)
        self.EN_A = Pin(en_a, Pin.OUT)
        self.In3 = Pin(in3, Pin.OUT)
        self.In4 = Pin(in4, Pin.OUT)
        self.EN_B = Pin(en_b, Pin.OUT)

    def move_forward(self):
        """
        Moves the DC motor forward
        """
        self.In1.high()
        self.In2.low()
        self.In3.high()
        self.In4.low()

    def move_backward(self):
        """
        Moves the DC motor backward
        """
        self.In1.low()
        self.In2.high()
        self.In3.low()
        self.In4.high()

    def turn_right(self):
        """
        Moves the DC motor to the right
        """
        self.In1.low()
        self.In2.low()
        self.In3.low()
        self.In4.high()

    def turn_left(self):
        """
        Moves the DC motor to the left
        """
        self.In1.low()
        self.In2.high()
        self.In3.low()
        self.In4.low()

    def stop(self):
        """
        Stops the DC motor
        """
        self.In1.low()
        self.In2.low()
        self.In3.low()
        self.In4.low()
        
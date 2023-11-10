from machine import Pin


class DCMotor:
    In1: Pin
    In2: Pin
    EN_A: Pin
    In3: Pin
    In4: Pin
    EN_B: Pin

    def __init__(self, In1: int, In2: int, In3: int, In4: int, EN_A: int, EN_B: int):
        self.In1 = Pin(In1,Pin.OUT) 
        self.In2 = Pin(In2,Pin.OUT)  
        self.EN_A = Pin(EN_A,Pin.OUT)
        self.In3 = Pin(In3,Pin.OUT)  
        self.In4 = Pin(In4,Pin.OUT)  
        self.EN_B = Pin(EN_B,Pin.OUT)
        
    def set_pins(self, In1: int, In2: int, In3: int, In4: int, EN_A: int, EN_B: int):
        self.In1 = Pin(In1,Pin.OUT) 
        self.In2 = Pin(In2,Pin.OUT)  
        self.EN_A = Pin(EN_A,Pin.OUT)
        self.In3 = Pin(In3,Pin.OUT)  
        self.In4 = Pin(In4,Pin.OUT)  
        self.EN_B = Pin(EN_B,Pin.OUT)

    def move_forward(self):
        self.In1.high()
        self.In2.low()
        self.In3.high()
        self.In4.low()

    def move_backward(self):
        self.In1.low()
        self.In2.high()
        self.In3.low()
        self.In4.high()

    def turn_right(self):
        self.In1.low()
        self.In2.low()
        self.In3.low()
        self.In4.high()

    def turn_left(self):
        self.In1.low()
        self.In2.high()
        self.In3.low()
        self.In4.low()

    def stop(self):
        self.In1.low()
        self.In2.low()
        self.In3.low()
        self.In4.low()
        
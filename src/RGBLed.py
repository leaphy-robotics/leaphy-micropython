from machine import Pin, PWM

class RGBLed:
    """Turns a rgbled on to a self chosen color or a standard color"""
    Colors = {
        "Red": (255, 0, 0),
        "Blue": (0, 0, 255),
        "Groen": (0, 255, 0),
        "Yellow": (255, 255, 0),
        "Orange": (255, 165, 0),
        "Purple": (128, 0, 128),
        "Pink": (255, 192, 203),
        "Brown": (139, 69, 19),
    }

    def __init__(self, rpin: int, gpin: int, bpin: int):
        """Makes all the variables"""
        self.red = PWM(Pin(rpin))
        self.green = PWM(Pin(gpin))
        self.blue = PWM(Pin(bpin))

    def set_pins(self, rpin: int, gpin: int, bpin: int):
        """Defines the pins"""
        self.red = PWM(Pin(rpin))
        self.green = PWM(Pin(gpin))
        self.blue = PWM(Pin(bpin))

    def set_color(self, r: int, g: int, b: int):
        """Gives the pins the values"""
        self.red.freq(255)
        self.blue.freq(255)
        self.green.freq(255)

        self.red.duty_u16(r * 257)
        self.green.duty_u16(g * 257)
        self.blue.duty_u16(b * 257)

    def print_base_colors(self):
        """Prints the color values of the list"""
        for kleur, rgb in self.Colors.items():
            print(f"{kleur}: RGB{rgb}")


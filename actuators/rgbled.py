from leaphymicropython.utils.pins import set_pwm


class RGBLed:
    """
    A class to control an RGB LED
    """

    Colors = {
        "Red": (255, 0, 0),
        "Blue": (0, 0, 255),
        "Green": (0, 255, 0),
        "Yellow": (255, 255, 0),
        "Orange": (255, 165, 0),
        "Purple": (128, 0, 128),
        "Pink": (255, 192, 203),
        "Brown": (139, 69, 19),
    }

    def __init__(self, red_pin: int, green_pin: int, blue_pin: int):
        """
        Creates an RGB LED
        :param red_pin: int, the pin of the red led
        :param green_pin: int, the pin of the green led
        :param blue_pin: int, the pin of the blue led
        """
        self.red = red_pin
        self.green = green_pin
        self.blue = blue_pin

    def set_pins(self, red_pin: int, green_pin: int, blue_pin: int):
        """
        Sets the pins of the rgbled
        :param red_pin: int, the pin of the red led
        :param green_pin: int, the pin of the green led
        :param blue_pin: int, the pin of the blue led
        """
        self.red = red_pin
        self.green = green_pin
        self.blue = blue_pin

    def set_color(self, r: int, g: int, b: int):
        """
        Sets the color of the rgb-led
        :param r: int, the red value
        :param g: int, the green value
        :param b: int, the blue value
        """
        set_pwm(self.red, r, 255)
        set_pwm(self.green, g, 255)
        set_pwm(self.blue, b, 255)

    def print_base_colors(self):
        """Prints the color values of the list"""
        for kleur, rgb in self.Colors.items():
            print(f"{kleur}: RGB{rgb}")

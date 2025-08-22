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

    def __init__(self, red_pin: str, green_pin: str, blue_pin: str):
        """
        Creates an RGB LED
        :param red_pin: str, the pin of the red LED
        :param green_pin: str, the pin of the green LED
        :param blue_pin: str, the pin of the blue LED
        """
        self.red = red_pin
        self.green = green_pin
        self.blue = blue_pin

    def set_pins(self, red_pin: str, green_pin: str, blue_pin: str):
        """
        Sets the pins of the RGB LED
        :param red_pin: str, the pin of the red LED
        :param green_pin: str, the pin of the green LED
        :param blue_pin: str, the pin of the blue LED
        """
        self.red = red_pin
        self.green = green_pin
        self.blue = blue_pin

    def set_color(self, r: int, g: int, b: int):
        """
        Sets the color of the RGB LED
        :param r: int, the red value
        :param g: int, the green value
        :param b: int, the blue value
        """
        set_pwm(self.red, r, 255)
        set_pwm(self.green, g, 255)
        set_pwm(self.blue, b, 255)

    def print_base_colors(self):
        """
        Prints the color values of the list
        """
        for kleur, rgb in self.Colors.items():
            print(f"{kleur}: RGB{rgb}")

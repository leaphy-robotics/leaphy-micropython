import dht
import machine
from leaphymicropython.utils.boards_config import pin_to_gpio


class DHT22:
    """
    A class to control the dht22
    """

    def __init__(self, pin: int):
        """
        Sets the pins for the dht22
        :param pin: sets the pin for the dht22
        """
        pin = pin_to_gpio(pin)
        self.sensor = dht.DHT22(machine.Pin(pin))

    def read_temperature(self) -> float:
        """
        :return: temperature: gives the temperature in Celsius
        """
        self.sensor.measure()
        temperature = self.sensor.temperature()
        return temperature

    def read_humidity(self) -> float:
        """
        :return: humidity: gives the humidity in percentages
        """
        self.sensor.measure()
        humidity = self.read_humidity()
        return humidity

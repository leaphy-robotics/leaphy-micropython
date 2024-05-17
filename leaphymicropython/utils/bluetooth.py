from machine import UART


class BLUETOOTH:
    """
    A class for the use of bluetooth
    """

    def __init__(self, baudrate: int) -> None:
        """
        set baudrate
        """
        self.uart = UART(0, baudrate)

    def read_uart(self) -> bytes:
        """
        Read uart from your bluetooth module
        """
        if self.uart.any() > 0:
            data = self.uart.read()
            return data
        return b""

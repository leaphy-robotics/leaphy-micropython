# pylint: disable=no-member
import bluetooth
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

# Nordic UART Service (NUS)
_UART_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")  # board -> phone
_UART_RX_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")  # phone -> board

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x03)
_ADV_TYPE_UUID128_COMPLETE = const(0x07)


def advertising_payload(name: str = None, services: list = None) -> bytearray:
    """
    Builds a BLE advertising payload
    :param name: str, the device name to advertise
    :param services: list, the service UUIDs to advertise
    :return: bytearray, the advertising payload (max 31 bytes)
    """
    payload = bytearray()

    def _append(adv_type: int, value: bytes) -> None:
        payload.extend(bytes((len(value) + 1, adv_type)))
        payload.extend(value)

    _append(_ADV_TYPE_FLAGS, b"\x06")  # flags: general discoverable, no BR/EDR
    if name:
        _append(_ADV_TYPE_NAME, name.encode())
    if services:
        for uuid in services:
            uuid_bytes = bytes(uuid)
            if len(uuid_bytes) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, uuid_bytes)
            elif len(uuid_bytes) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, uuid_bytes)
    if len(payload) > 31:
        raise ValueError(
            f"Advertising payload must be at most 31 bytes, yours is {len(payload)}"
        )
    return payload


class BLEUart:
    """
    A class for serial communication over Bluetooth Low Energy (BLE)

    Uses the Nordic UART Service (NUS) so the board shows up as a serial
    device in apps such as the nRF Connect or Serial Bluetooth Terminal app.
    """

    def __init__(self, name: str = "Nano RP2040") -> None:
        """
        Starts the BLE radio and advertises the device
        :param name: str, the name the device advertises itself with
        """
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._connections = set()
        self._rx_callback = None

        tx = (_UART_TX_UUID, bluetooth.FLAG_NOTIFY)
        rx = (_UART_RX_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE)
        uart_service = (_UART_SERVICE_UUID, (tx, rx))
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services(
            (uart_service,)
        )

        # A 128-bit UUID (18 bytes) plus the name does not fit in 31 bytes,
        # so advertise the name only; apps find the service after connecting.
        self._payload = advertising_payload(name=name)
        self._advertise()

    def _irq(self, event: int, data) -> None:
        """
        Handles BLE events
        :param event: int, the event id
        :param data: the event data belonging to the event
        """
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.discard(conn_handle)
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._rx_handle and self._rx_callback:
                self._rx_callback(self._ble.gatts_read(self._rx_handle))

    def _advertise(self, interval_us: int = 100_000) -> None:
        """
        Starts advertising the device so it can be discovered
        :param interval_us: int, the advertising interval in microseconds
        """
        self._ble.gap_advertise(interval_us, self._payload)

    def on_receive(self, callback) -> None:
        """
        Registers a function called when data is received
        :param callback: a function that takes the received bytes as argument
        """
        self._rx_callback = callback

    def is_connected(self) -> bool:
        """
        Checks whether a device is connected
        :return: bool, True if at least one device is connected
        """
        return len(self._connections) > 0

    def send(self, data) -> None:
        """
        Sends data to all connected devices
        :param data: str or bytes, the data to send
        """
        if isinstance(data, str):
            data = data.encode()
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._tx_handle, data)

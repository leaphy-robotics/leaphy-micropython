"""Lets you send and receive data over Bluetooth Low Energy (BLE)"""

from time import sleep
from leaphymicropython.utils.ble_uart import BLEUart

uart = BLEUart("Nano RP2040")


def on_receive(data):
    """Prints data received from a connected device"""
    print("Received:", data)


uart.on_receive(on_receive)

count = 0
while True:
    if uart.is_connected():
        count += 1
        uart.send(f"Hello, World #{count}\n")
        print("Sent message", count)
    sleep(1)
"""This module provides i2c address finding functions"""  # Single-line docstring

from machine import Pin, SoftI2C  # pylint: disable=E0401


def is_device_address_visible(i2c, target_address):
    """
    Check if a specific I2C address is visible on the bus.

    Performs an I2C scan and checks if the target address is present
    in the list of detected device addresses.

    Args:
        i2c (machine.I2C): An initialized I2C object from the machine module.
        target_address (int): The 7-bit I2C address to search for.

    Returns:
        bool: True if the target address is found on the bus, False otherwise.
    """
    devices = i2c.scan()
    is_visible = target_address in devices
    return is_visible


def find_i2c_address(scl_pin: int, sda_pin: int) -> list[hex]:
    """
    Find an I2C address for a device
    """
    i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
    print("I2C SCANNER")
    devices = i2c.scan()

    if len(devices) == 0:
        print("No i2c device !")
    else:
        print("i2c devices found:", len(devices))

    for device in devices:
        print("I2C hexadecimal address: ", hex(device))
    return devices

from machine import Pin, SoftI2C


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

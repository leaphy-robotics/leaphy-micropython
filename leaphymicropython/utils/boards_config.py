from machine import unique_id

GND = -1
RUN = -2
NOTHING = 0
VCC = -3
EN = -4
VSYS = -5
VBUS = -6


"""
PINS:
    Key = Physical Pin
    Value = GPIO Pin
"""
RP_NANO_MAKER = {
    "pins": {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 7,
        8: 8,
        9: 9,
        10: 17,
        11: 19,
        12: 16,
        13: 18,
        14: 26,
        15: 27,
        16: 28,
        17: 29,
        18: 12,
        19: 13,
        20: 14,  # A6
        21: 15,  # A7
    }
}

"""
PINS:
    Key = Physical Pin
    Value = GPIO Pin
"""
PICO_W = {
    "pins": {
        1: 0,
        2: 1,
        3: GND,
        4: 2,
        5: 3,
        6: 4,
        7: 5,
        8: GND,
        9: 6,
        10: 7,
        11: 8,
        12: 9,
        14: 10,
        15: 11,
        16: 12,
        17: 13,
        18: GND,
        19: 14,
        20: 15,
        21: 16,
        22: 17,
        23: GND,
        24: 18,
        25: 19,
        26: 20,
        27: 21,
        28: GND,
        29: 22,
        30: RUN,
        31: 26,
        32: 27,
        33: GND,
        34: 28,
        35: NOTHING,
        36: VCC,
        37: EN,
        38: GND,
        39: VSYS,
        40: VBUS,
    }
}

"""
PINS:
    Key = Physical Pin
    Value = GPIO Pin
"""
NANO_CONNECT = {
    "pins": {
        13: 6,
        14: 26,
        15: 27,
        16: 28,
        17: 29,
        18: 12,
        19: 13,
        20: 20,
        21: 21,
        12: 4,
        11: 7,
        10: 5,
        9: 21,
        8: 20,
        7: 19,
        6: 18,
        5: 17,
        4: 16,
        3: 15,
        2: 25,
        1: 1,
        0: 0,
    }
}


BOARDS = {
    "RP_NANO_MAKER": RP_NANO_MAKER,
    "PICO_W": PICO_W,
    "NANO_CONNECT": NANO_CONNECT,
}


def get_board_type():
    """
    Get board type,
    :return: which board it is
    """
    id_u: bytes = unique_id()
    decoded_id: str = "".join([f"{byte:02X}" for byte in id_u])
    board = "UNKNOWN_BOARD"

    if str(decoded_id).startswith("E6611C"):
        board = "RP_NANO_MAKER"
    elif str(decoded_id).startswith("E66164"):
        board = "PICO_W"
    elif str(decoded_id).startswith("503533"):
        board = "NANO_CONNECT"
    return board


def pin_to_gpio(pin: int):
    """
    Convert physical pin to GPIO
    :param pin: The pin to convert
    :return: GPIO pin number
    """
    return BOARDS[get_board_type()]["pins"][pin]

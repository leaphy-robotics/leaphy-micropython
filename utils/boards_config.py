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

BOARDS = {
    "RP_NANO_MAKER": RP_NANO_MAKER,
    "PICO_W": PICO_W,
}

id_u: str = unique_id()

decoded_id: str = "".join(["{:02X}".format(byte) for byte in id_u])
board = "UNKNOWN_BOARD"

if str(decoded_id).startswith("E6611C"):
    board = "RP_NANO_MAKER"
elif str(decoded_id).startswith("E66164"):
    board = "PICO_W"


def get_board_type():
    """
    Get board type,
    :return: which board it is
    """
    return board


def pin_to_gpio(pin: int):
    return BOARDS[get_board_type()]["pins"][pin]

from machine import unique_id

rp2040_nano_maker = {
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
        20: 14, # A6
        21: 15, # A7
    }
}

rp2040_leaphy = {
    "pins": {
    }
}

def getBoardType():
    unique_id = unique_id()

    decoded_id = ''.join(['{:02X}'.format(byte) for byte in unique_id])

    if decoded_id == "E6611C08CB7E3222":
        return "rp2040_nano_maker"
    else:
        return decoded_id

def pinToGPIO(pin):
    board_type = getBoardType()
    board_to_pins = {
        "rp2040_nano_maker": rp2040_nano_maker,
        "rp2040_leaphy": rp2040_leaphy,
    }
    return board_to_pins[board_type]["pins"][pin]
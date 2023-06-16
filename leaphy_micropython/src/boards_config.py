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
    id_u: str = unique_id()

    decoded_id: str = ''.join(['{:02X}'.format(byte) for byte in id_u])
    print(decoded_id)
    if str(decoded_id).startswith("E6611C08CB"):
        print("a")
        return "rp2040_nano_maker"
    else:
        return "unknown"

def pinToGPIO(pin: int):
    board_type: str = getBoardType()
    board_to_pins = {
        "rp2040_nano_maker": rp2040_nano_maker,
        "rp2040_leaphy": rp2040_leaphy,
    }
    return board_to_pins[board_type]["pins"][pin]

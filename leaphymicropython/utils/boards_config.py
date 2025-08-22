from machine import unique_id

GND = -1
RUN = -2
NOTHING = 0
VCC = -3
EN = -4
VSYS = -5
VBUS = -6


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
    elif str(decoded_id).startswith("503"):
        board = "NANO_CONNECT"
    if str(decoded_id).startswith("E66054"):
        board = "PICO"
    return board



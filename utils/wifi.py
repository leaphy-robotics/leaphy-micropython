from time import sleep
import network

def connect(ssid: str, password: str) -> str:
    """
    Connects the pico to the wifi
    :param ssid: gives the wifi name to the pico
    :param password: gives the password from the wifi to the pico
    :return: ip_addresses: returns the address from the pico w
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        sleep(1)
        print("Connecting to WiFi...")
    return wlan.ifconfig()[0]

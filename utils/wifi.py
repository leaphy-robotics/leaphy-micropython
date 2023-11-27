from time import sleep
import network

def connect(ssid, password):
    """
    Connects the pico to the wifi
    :param ssid: str, gives the wifi name to the pico
    :param password: str, gives the password from the wifi to the pico
    :return: ip_addresses: tuple[str]int, gives the ip addresses from the pico w
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        sleep(1)
        print("Connecting to WiFi...")
    return wlan.ifconfig()

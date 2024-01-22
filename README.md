# Leaphy Micropython
Source Code for the Leaphy MicroPython Library

# How to install the package on your microcontroller:
    First connect it to the wifi you need to do this in the repl from your microcontroller:
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(“wifi name”, “wifi password”)
    After that you are going to install the package with mip still in your repl:
    import mip
    mip.install(“github:leaphy-robotics/leaphy-micropython”)
# Microcontrollers that we support:
    nano rp2040 maker
    Pico w
    Nano rp2040 connect

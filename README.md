# Leaphy Micropython
Source Code for the Leaphy MicroPython Library

# How to install the package on your microcontroller
First connect your microcontroller to the wifi, you need to do this in the REPL mode in a terminal
```py
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("wifi name", "wifi password")
```
Then we are going to install the package with mip still in REPL mode
```py
import mip
mip.install("github:leaphy-robotics/leaphy-micropython")
```
# Supported microcontrollers
* Maker Nano RP2040
* Pico W
* Nano RP2040 Connect

    
"""Reads the distance"""

from time import sleep
from leaphymicropython.sensors.sonar import read_distance

while True:
    print(read_distance("D3", "A2"))
    sleep(1)

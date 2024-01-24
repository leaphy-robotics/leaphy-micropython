"""Reads the distance"""
from time import sleep
from leaphymicropython.sensors.sonar import read_distance

while True:
    print(read_distance(1))
    sleep(1)

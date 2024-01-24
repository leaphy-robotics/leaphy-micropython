"""Reads the distance"""
from leaphymicropython.sensors.sonar import read_distance
from time import sleep

while True:
    print(read_distance(1))
    sleep(1)

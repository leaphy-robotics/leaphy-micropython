"""Reads the line sensor"""
from leaphymicropython.sensors.linesensor import read_line_sensor
from time import sleep

while True:
    print(read_line_sensor(1))
    sleep(1)
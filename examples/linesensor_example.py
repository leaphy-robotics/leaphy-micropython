"""Reads the line sensor"""
from time import sleep
from leaphymicropython.sensors.linesensor import read_line_sensor

while True:
    print(read_line_sensor(1))
    sleep(1)

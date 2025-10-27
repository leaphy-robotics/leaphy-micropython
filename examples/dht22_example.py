"""Reads the DHT22 sensor and returns temperature and humidity"""

from leaphymicropython.sensors.dht22 import DHT22

sensor = DHT22("D1")
while True:
    print(sensor.read_temperature())
    print(sensor.read_humidity())

from machine import Pin, PWM, time_pulse_us
from utime import sleep_us
from .boards_config import pinToGPIO

def getDistanceSonar(trigPin: int, echoPin: int):
    """ Get distance from sonar,\n
        trigPin: int, echoPin: int\n
        returns a value between 0 and 1313"""
    trigPin = pinToGPIO(trigPin)
    echoPin = pinToGPIO(echoPin)
    duration: float
    distance: float
    tries: int = 0
    echo = Pin(echoPin, Pin.IN)
    trig = Pin(trigPin, Pin.OUT)
    trig.low()
    sleep_us(2)
    trig.high()
    sleep_us(10)
    trig.low()
    duration = time_pulse_us(echo, 1, 29000)
    distance = (duration / 2.0) / 29
    if distance == 0:
      distance = 1313
    return round(distance)

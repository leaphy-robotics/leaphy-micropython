from time import sleep

from leaphymicropython.actuators.dcmotor import DCMotor
from leaphymicropython.sensors.sonar import read_distance

while True:
    distance = read_distance()
    motor = DCMotor()
    if distance < 10:
        motor.left(255, 1)
        sleep(1)
    else:
        motor.forward(255)

import time
from math import degrees, atan2

from machine import I2C

from leaphymicropython.sensors.compass import QMC5883L

i2c = I2C(0)
qmc = QMC5883L(i2c)
print(qmc.magnetic)


def vector_2_degrees(x, y):
    """
    vector 2 degree function
    """
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle = angle + 360
    return angle


def get_heading(sensor):
    """
    get heading
    """
    mag_x, mag_y, _ = sensor.magnetic
    return vector_2_degrees(mag_x, mag_y)


while True:
    print(f"heading: {get_heading(qmc):.2f} degrees")
    time.sleep(0.2)

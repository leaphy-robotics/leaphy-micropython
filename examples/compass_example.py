from leaphymicropython.sensors.compass import Compass
from time import sleep

compass = Compass()

while True:
    x, y, z = compass.read_compass()
    print(compass.get_azimuth(x, y))
    sleep(1)

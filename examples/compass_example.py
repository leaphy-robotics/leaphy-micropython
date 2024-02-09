from time import sleep
from leaphymicropython.sensors.compass import Compass


compass = Compass()

while True:
    x, y, z = compass.read_compass()
    print(compass.get_azimuth(x, y))
    sleep(1)

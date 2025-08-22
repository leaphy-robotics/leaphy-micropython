# Leaphy Micropython
Source Code for the Leaphy MicroPython Library

# Supported microcontrollers
* Maker Nano RP2040
* Pico W
* Nano RP2040 Connect


# How to Install the Package on Your Microcontroller



### What is REPL Mode?
REPL (Read-Eval-Print Loop) mode allows you to execute Python code one line at a time directly on your microcontroller. This mode is useful for testing and debugging as you can see immediate results of your commands.

### Methods for Installing the Package
For Linux Users:
If you're using Linux, you can easily access REPL mode using tio, a terminal tool that interacts with your microcontroller via USB.

#### Install tio:

First, install tio by running the following command in your terminal:

```bash
sudo apt install tio
```
### Launch tio on the USB Port:

Connect to your microcontroller by launching tio on the appropriate USB port.

```bash
tio /dev/ttyACM0
````
This will bring you into REPL mode, indicated by the prompt:

```py
>>>
```

### Using Thonny IDE:
If you prefer a graphical interface, you can use Thonny, a Python IDE designed for beginners, but also suitable for microcontroller programming.

#### Install Thonny:

Download and install Thonny from thonny.org

#### Connect to Your Microcontroller:

Open Thonny and ensure your microcontroller is connected. At the bottom of the Thonny window, you should see the REPL prompt:

```py
>>>
```


## Install the Package:
Install the Package:
To begin, you need to connect your microcontroller to Wi-Fi. This is done in REPL mode, follow these steps:

Connect to the wifi:
```py
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("wifi name", "wifi password")
```
You can now type the following command in the REPL to install the package:

```py
import mip
mip.install("github:leaphy-robotics/leaphy-micropython")
```

# How to Make a Buzzer Beep
Follow these steps to make a buzzer beep using the leaphymicropython library:

1. Start by importing the set_buzzer function into your script:
```py
from leaphymicropython.actuators.buzzer import set_buzzer
```
## Usage of the set_buzzer function

Call the set_buzzer function with the appropriate parameters:

```py
set_buzzer(pin_name, pwm_value, frequency)
```
## Pin (str):

The pin name to which the buzzer is connected.

## Pwm_value: 

The duty cycle for the buzzer, determining the volume of the beep, this value is between 0 - 255

## frequency: 

The frequency of the beep, which controls the pitch of the sound (e.g., 1000 for a standard tone).

# How to read values using the QMC5883L

Follow these steps to read magnetic heading values using the QMC5883L sensor with the leaphymicropython library:

## Import the necessary modules:

Start by importing the required libraries and setting up the I2C connection:

```py
import time
from math import degrees, atan2
from machine import I2C
from leaphymicropython.sensors.compass import QMC5883L
```

## Initialize the sensor:

Create an I2C object and initialize the QMC5883L sensor:
    
```py
i2c = I2C(0)
qmc = QMC5883L(i2c)
print(qmc.magnetic)
```

## Define helper functions:

Define the functions needed to convert magnetic vector data into degrees and to get the heading:

```py
def vector_2_degrees(x, y):
    """
    Converts a vector to degrees.
    """
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return angle

def get_heading(sensor):
    """
    Calculates the heading from the sensor data.
    """
    mag_x, mag_y, _ = sensor.magnetic
    return vector_2_degrees(mag_x, mag_y)
```

## Read and print the heading:

Use a loop to continuously read and print the heading in degrees:

```py
while True:
    print(f"heading: {get_heading(qmc):.2f} degrees")
    time.sleep(0.2)
```
## Explanation of the functions
## vector_2_degrees(x, y):

Converts the X and Y magnetic vector components into an angle in degrees, ensuring the angle is positive.

## get_heading(sensor):
Retrieves the magnetic X and Y components from the sensor and calculates the heading in degrees.

# How to Control a DC Motor Based on Distance
Follow these steps to control a DC motor using the leaphymicropython library, based on the distance 
measured by an ultrasonic sensor using the leaphymicropython library:

## Import the necessary modules:

Start by importing the required libraries:

```py
from time import sleep
from leaphymicropython.actuators.dcmotor import DCMotor
from leaphymicropython.sensors.sonar import read_distance
```


## Use a loop to continuously read the distance and control the motor based on the distance:

```py
while True:
    distance = read_distance()
    motor = DCMotor()
    if distance < 10:
        motor.left(255, 1)
        sleep(1)
    else:
        motor.forward(255)
```
## read_distance():
Reads the distance from the ultrasonic sensor and returns the value in centimeters.

## DCMotor()
Initializes the DC motor object, allowing you to control its movements.

## motor.left(speed, duration)
Turns the motor to the left at the specified speed (0-255) for the given duration in seconds.

## motor.forward(speed)
Moves the motor forward at the specified speed (0-255). The motor will continue to move forward until another command is issued.

## Example Behavior:
If the distance measured by the ultrasonic sensor is less than 10 cm, the motor will turn 
left at full speed for 1 second. If the distance is greater than or equal to 10 cm, the
motor will move forward at full speed.

# How to read temperature and humidity using the dht22

Follow these steps to read temperature and humidity values using the DHT22 sensor with the leaphymicropython library:

## Import the necessary module:

Start by importing the DHT22 module:

```py
from leaphymicropython.sensors.dht22 import DHT22
```
## Initialize the sensor:

Create a DHT22 sensor object on the correct pin:
```py
sensor = DHT22("D1")
```
## Read and print temperature and humidity:
Use a loop to continuously read and print the temperature and humidity values:

```py
while True:
    print(sensor.read_temperature())
    print(sensor.read_humidity())
```
## DHT22(pin_number)
Initializes the DHT22 sensor object on the specified pin.

## read_temperature()
Reads the current temperature from the sensor and returns it in degrees Celsius.

## read_humidity()
Reads the current humidity from the sensor and returns it as a percentage.

# How to Read Values Using the Line Sensor
Follow these steps to read values from a line sensor using the leaphymicropython library:

## Import the necessary module:
Start by importing the read_line_sensor function:
```py
from time import sleep
from leaphymicropython.sensors.linesensor import read_line_sensor
```
## Read and print the sensor value:

Use a loop to continuously read and print the value from the line sensor:

```py
while True:
    print(read_line_sensor("D1"))
    sleep(1)
```
## read_line_sensor(pin: str)
Reads the value from the line sensor connected to the specified pin name.

# How to Make the RGB LED Blink
Follow these steps to make the RGB LED blink using the leaphymicropython library:

## Import the Necessary Modules:

Start by importing the required libraries:

```py
from time import sleep
from leaphymicropython.actuators.rgbled import RGBLed
```

## Initialize the RGB LED:  

Create an RGBLed object by specifying the pins connected to the red, green, and blue channels:

```py
led = RGBLed("D1", "D2", "D4")
```
## Set the LED Color and Blink:

Use a loop to continuously set the LED color and toggle it:

```py
while True:
    led.set_color(255, 0, 0)  # Set color to red
    sleep(1)
    led.set_color(0, 0, 0)    # Turn off the LED
    sleep(1)
```
## RGBLed(red_pin: str, green_pin: str, blue_pin: str)
Initializes the RGB LED object by specifying the pin names connected to the red, green, and blue components.

### Parameters:
    Red_pin: The pin connected to the red LED channel.
    Green_pin: The pin connected to the green LED channel.
    blue_pin: The pin connected to the blue LED channel.

## set_color(red, green, blue)
Sets the color of the RGB LED by specifying the intensity of the red, green, and blue channels. Each parameter should be a value between 0 and 255.

### Parameters:
    Red: Intensity of the red channel (0-255).
    Green: Intensity of the green channel (0-255).
    Blue: Intensity of the blue channel (0-255).

# How to Control a Servo Motor
Follow these steps to control a servo motor using the leaphymicropython library:

## Import the Necessary Module:

Start by importing the set_servo_angle function:

```py
from leaphymicropython.actuators.servo import set_servo_angle
```
## Set the Servo Angle:

Use the set_servo_angle function to rotate the servo to the desired angle:

```py
set_servo_angle("D1", 90)
```
## set_servo_angle(pin: str, angle)
This function rotates the servo motor to a specified angle.

### Parameters:
    pin: The pin name to which the servo is connected.
    angle: The angle to which the servo should rotate (0-180 degrees).

# How to Read Distance Using a Sonar Sensor
Follow these steps to read distance using a sonar sensor with the leaphymicropython library:

## Import the Necessary Module:

Start by importing the read_distance function:

```py
from time import sleep
from leaphymicropython.sensors.sonar import read_distance
```
## Read and Print the Distance:

Use a loop to continuously read and print the distance in centimeters:

```py
while True:
    print(read_distance("D1", "D2"))
    sleep(1)
```
## read_distance(trig_pin: str, echo_pin: str)
This function reads the distance from a sonar sensor connected to the specified pins and returns the distance in centimeters.

### Parameters:
    trig_pin: The pin name to which the sonar sensor's trigger pin is connected.
	 echo_pin: The pin name to which the sonar sensor's echo pin is connected.
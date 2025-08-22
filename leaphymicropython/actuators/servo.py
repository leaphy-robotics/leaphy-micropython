from machine import Pin, PWM



def set_servo_angle(pin: str, angle: int) -> None:
    """
    Puts the servo on an angle
    :param pin: The pin name to which the servo motor is connected
    :param angle: The angle to set the servo motor to
    """
    if not 0 <= angle <= 180:
        raise ValueError("The angle must be between 0 and 180")

    pwm = PWM(Pin(pin))
    pwm.freq(50)

    # Use Arduino's pulse width mapping (544-2400 microseconds)
    min_pulse = 544
    max_pulse = 2400

    # Map angle (0-180) to pulse width in microseconds
    pulse_width = min_pulse + (angle * (max_pulse - min_pulse) / 180)

    # Convert microseconds to 16-bit duty cycle value
    # 20ms period (50Hz) = 20,000 microseconds
    # duty_u16 takes a value from 0-65535
    duty_cycle = int((pulse_width / 20000) * 65535)

    pwm.duty_u16(duty_cycle)

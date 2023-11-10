from machine import Pin, PWM
from .boards_config import pinToGPIO

def set_buzzer(pin : int, loud : int):
    """Turns a buzzer and you can choose how hard the sound is."""
    buzzerpin = pinToGPIO(pin)
    buzzer = PWM(Pin(buzzerpin))
    buzzer.freq(255)
    if loud < 0 or loud > 255: raise ValueError("Buzzer values must be in between 0 and 255")
    buzzer.duty_u16(loud * 257)

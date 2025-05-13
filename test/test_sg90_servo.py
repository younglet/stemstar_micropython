from sg90 import Servo
from machine import Pin
from time import sleep

servo = Servo(Pin(4))


angles = [10, 30, 90, 120, 170, 90]

for angle in angles:
    servo.move(angle)
    print(f'现已转至{angle}度')
    sleep(2)

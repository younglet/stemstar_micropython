from sg90 import SG90
from machine import UART, Pin
from hcsr04 import HCSR04
import time

# 初始化串口通信
uart = UART(2, baudrate=115200, tx=Pin(26), rx=Pin(27))
# 初始化距离传感器
sensor = HCSR04(Pin(32), Pin(33))
# 初始化舵机
servo = SG90(Pin(4))

# 变量初始化
angle = 10
step = 5

while True:
    servo.move(angle)

    time.sleep(0.5)
    distance = sensor.get_distance()
    msg = f"角度: {angle} 距离: {distance:.1f} \n"
    uart.write(msg)
    print(msg)
    
    angle += step
    if angle >= 170:
        angle = 10


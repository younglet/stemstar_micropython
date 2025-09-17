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
angle = 10 # 初始角度
step = 5   # 每次移动的角度步长

while True:
    # 控制舵机移动到指定角度，并测量距离
    servo.move_to(angle)
    distance = sensor.get_distance()

    #整理角度和距离数据，并通过串口发送
    msg = f"角度: {angle} 距离: {distance:.1f} \n"
    uart.write(msg)
    print(msg)
    
    # 更新角度，控制舵机在10到170度之间来回摆动
    angle += step
    if angle >= 170:
        angle = 10
    time.sleep(0.5)

from sg90 import SG90
from machine import Pin, UART
from hcsr04 import HCSR04
from time import sleep_ms


uart = UART(2, baudrate=115200)                      # 初始化串口通信
sensor = HCSR04(Pin(32), Pin(33))                    # 初始化距离传感器
servo = SG90(Pin(4))                                 # 初始化舵机

angle = 10                                           # 初始角度变量
step = 5                                             # 每次移动的角度步长

while True:
    
    angle += step                                    # 更新角度
    servo.move_to(angle)                             # 控制舵机移动到指定角度
    distance = sensor.get_distance()                 # 获取距离数据

    msg = f"角度: {angle} 距离: {distance:.1f} \n"    # 格式化字符串
    uart.write(msg)                                  # 通过串口发送数据
    print(msg)                                       # 在控制台打印发送的数据
    
    if angle >= 170:                                 # 超出右边界
        step = -5                                    # 开始往回扫
    elif angle <= 10:                                # 超出左边界
        step = 5                                     # 开始向前扫

    sleep_ms(50)                                     # 延时50毫秒，等待舵机稳定
from hcsr04 import HCSR04
from machine import Pin
from time import sleep_us

# 初始化引脚,使用 GPIO14 作为 Trigger , 使用 GPIO15 作为 Echo
trigger = Pin(14, Pin.OUT)  
echo = Pin(15, Pin.IN)  

# 简化写法
# trigger = Pin(14)
# echo = Pin(15)

# 创建传感器实例
sensor = HCSR04(trigger_pin=trigger, echo_pin=echo)

# 循环测量距离
print("开始测量距离...")

while True:
    try:
        distance = sensor.get_distance()
        print(f"距离: {distance:.1f} cm ")
    except Exception as e:
        print("错误:", e)

    sleep_us(500_000)  # 每隔 0.5 秒测一次
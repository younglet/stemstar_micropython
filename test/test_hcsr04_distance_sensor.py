import time
from machine import Pin
from hcsr04 import HCSR04


print('''
【超声波传感器】正在启动...
──────────────────────────────────────────────
【Trig】 -> GPIO14
【Echo】 -> GPIO12
──────────────────────────────────────────────
请按照如上接线说明进行接线，然后按车继续：''')

input()  # 等待用户确认接线完成并回车继续
# 初始化引脚
try:
    print("🚩 开始测试 HCS04 超声波测距...")
    print("🔧 正在初始化 HCS04 超声波测距...")
    trig = Pin(14, Pin.OUT)   # Trig 引脚
    echo = Pin(12, Pin.IN)    # Echo 引脚

    # 创建传感器实例
    sensor = HCSR04(trig_pin=trig, echo_pin=echo)

    print("📡 正在开始测量距离...")
    print("🔄 每隔 1 秒测量一次，按 Ctrl+C 退出程序")

    while True:
        print("🔍 正在获取当前距离数据...")
        distance = sensor.get_distance()
        print(f"📏 当前距离: {distance:.1f} cm")
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 程序已退出，关闭传感器")

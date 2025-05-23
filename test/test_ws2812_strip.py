from neopixel import NeoPixel
from machine import Pin
from time import sleep
from colors import *


print('''
【WS2812灯带测试程序】
──────────────────────────────────────────────
【数据控制线】 -> GPIO4（30 颗灯珠）
──────────────────────────────────────────────
请按照如上接线说明进行接线，然后按车继续：
''')

input()  # 等待用户确认接线完成并回车继续
print("🚩 开始测试 WS2812 灯带功能...")

print("🔧 正在初始化 NeoPixel 灯带...")
strip = NeoPixel(Pin(4), 30)  # 初始化灯带（30颗灯）

print("🐎 开始执行跑马灯效果")
try:
    # 跑马灯效果：从左到右
    for i in range(0, 30):
        print(f"🏃‍♂️ 正在点亮第 {i + 1} 颗灯")
        strip.fill(BLACK)
        strip[i] = RED
        strip.write()
        sleep(0.05)

    # 跑马灯效果：从右到左
    for i in range(29, -1, -1):
        print(f"🏃‍♀️ 正在点亮第 {i + 1} 颗灯")
        strip.fill(BLACK)
        strip[i] = RED
        strip.write()
        sleep(0.05)

    print("🌈 开始执行彩虹颜色闪烁效果")
    for color in RAINBOW:
        print(f"🎨 显示颜色: {color}")
        strip.fill(color)
        strip.write()
        sleep(0.2)

        strip.fill(BLACK)
        strip.write()
        sleep(0.2)

    print("🌬️ 开始执行呼吸灯效果（白光）")
    for _ in range(2):  # 呼吸两次
        for brightness in range(0, 256, 8):
            print(f"💡 当前亮度: {brightness}")
            strip.fill((brightness, brightness, brightness))
            strip.write()
            sleep(0.02)

        for brightness in range(255, -1, -8):
            print(f"💡 当前亮度: {brightness}")
            strip.fill((brightness, brightness, brightness))
            strip.write()
            sleep(0.02)
    print("🎉 所有测试完成！")
except KeyboardInterrupt:
    print("\n👋 您按下了 Ctrl+C，程序即将退出...")

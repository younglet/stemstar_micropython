from machine import I2C, Pin
from time import sleep
from ssd import SSD1306_I2C

print('''
【SSD1306 OLED 屏幕测试程序】
──────────────────────────────────────────────
【SCL】   ->    GPIO25
【SDA】   ->    GPIO26
──────────────────────────────────────────────
请按照如上接线说明进行接线，然后按车继续：''')

input()  # 等待用户确认接线完成并回车继续


try:
    print("🚩 开始测试波形图...")
    print("🔧 正在初始化 OLED 屏幕...")
    i2c = I2C(1)  # 使用 I2C 总线 1
    screen = SSD1306_I2C(128, 64, i2c)
    screen.poweron()
    print("📌 开始执行屏幕测试...")
    # 测试 1：点亮所有像素
    print("点亮全屏白色...")
    screen.fill(1)
    screen.show()
    sleep(2)

    # 测试 2：关闭所有像素
    print("关闭全屏（清屏）")
    screen.fill(1)
    screen.show()
    sleep(1)

    # 测试 3：显示文字
    print("显示文字测试")
    screen.text("Hello!", 0, 0, 1)
    screen.text("OLED Display", 0, 16, 1)
    screen.text("Resolution:", 0, 32, 1)
    screen.text("128x64", 0, 48, 1)
    screen.show()
    sleep(3)

    # 测试 4：清屏并结束
    print("测试完成，正在清屏...")
    screen.fill(0)
    screen.show()
    print("🎉 所有测试完成！")
except KeyboardInterrupt:
    print("\n👋 您按下了 Ctrl+C，程序即将退出...")
    
from sg90 import SG90
import time


print('''
──────────────────────────────────────────────
【舵机测试程序】正在启动...
【舵机信号线】 -> GPIO4
──────────────────────────────────────────────
【请按照如上接线说明进行接线后回车继续】：
''')

input()  # 等待用户确认接线完成并回车继续
try:
    print("🚩 开始测试舵机功能...")

    print("🔧 正在初始化舵机...")
    servo = SG90(Pin(4))  # 初始化舵机引脚

    angles = [10, 30, 90, 120, 170, 90]

    print("🔄 开始测试舵机角度旋转")
    print("📌 按 Ctrl+C 可随时退出程序\n")

    for angle in angles:
        print(f"🧭 正在转动到 {angle}°")
        servo.move_to(angle)
        print(f"✅ 已转至 {angle}°")
        time.sleep(2)
    print("🎉 所有测试完成！")
except KeyboardInterrupt:
    print("\n👋 您按下了 Ctrl+C，程序即将退出...")
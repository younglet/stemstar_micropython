from button import Button
from machine import Pin
import time

print('''
【按钮测试程序】
──────────────────────────────────────────────
【按钮】   ->  GPIO2 （请按下按钮）
──────────────────────────────────────────────
请按照如上接线说明进行接线，然后回车继续：''')

input()  # 等待用户确认接线完成并回车继续

try:
    print("🚩 开始测试按钮功能...")

    print("🔧 正在初始化按钮...")
    btn_pin = Pin(2, Pin.IN, Pin.PULL_DOWN)
    btn = Button(btn_pin)

    print("🔘 等待首次按下按钮...")
    while True:
        if btn.is_pressed():
            print("✅ 按钮已按下")
            break
        time.sleep_ms(10)

    print("\n🔁 进入实时按钮状态监测（持续5秒）...")
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < 5000:
        if btn.is_pressed():
            print("🔵 按钮被按下", end='\r')
        else:
            print("⚪ 按钮未按下", end='\r')
        time.sleep_ms(50)

    print("\n🔚 按钮状态监测结束")

    print("🎉 所有测试完成！")

except KeyboardInterrupt:
    print("\n程序已退出")
except Exception as e:
    print("发生错误：", e)

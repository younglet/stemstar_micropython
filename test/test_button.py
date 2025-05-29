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

    # ===== 测试 is_pressed() =====
    print("\n🔘 正在测试 is_pressed()（持续5秒）...")
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < 5000:
        if btn.is_pressed():
            print("🔵 按钮被按下", end='\r')
        else:
            print("⚪ 按钮未按下", end='\r')
        time.sleep_ms(50)
    print("\n✅ is_pressed() 测试完成")


    # ===== 测试 is_clicked() =====
    print("\n🔘 正在测试 is_clicked()（持续10秒）...")
    print("👉 请在这段时间内尝试多次按下并松开按钮以测试点击检测\n")
    start_time = time.ticks_ms()
    click_count = 0
    while time.ticks_diff(time.ticks_ms(), start_time) < 10000:
        if btn.is_clicked():
            click_count += 1
            print(f"👇 检测到一次完整点击！（第 {click_count} 次）")
        time.sleep_ms(50)
    print("✅ is_clicked() 测试完成")

    print("\n🔚 所有测试已完成！")

except KeyboardInterrupt:
    print("\n程序已退出")
except Exception as e:
    print("发生错误：", e)
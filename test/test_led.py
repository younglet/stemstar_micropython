from led import LED
from machine import Pin
import time


    print('''
【LED测试程序】
──────────────────────────────────────────────
【LED】   ->  GPIO2 （PWM 输出）
──────────────────────────────────────────────
请按照如上接线说明进行接线，然后回车继续：''')

    input()  # 等待用户确认接线完成并回车继续

    try:
        print("🚩 开始测试 LED 功能...")

        print("🔧 正在初始化LED...")
        led = LED(Pin(2))  # 使用 GPIO2

        print("💡 正在打开 LED")
        led.on()
        time.sleep(1)

        print("💡 正在关闭 LED")
        led.off()
        time.sleep(1)

        print("✨ 正在执行 blink 闪烁")
        led.blink(times=3, interval=500)
        time.sleep(1)

        print("🌅 正在执行 fade_in 淡入")
        led.set_brightness(512)  # 设定初始亮度为中间值
        led.fade_in(target_brightness=1023, steps=50, interval=20)
        time.sleep(1)

        print("🌇 正在执行 fade_out 淡出")
        led.set_brightness(512)  # 设定初始亮度为中间值
        led.fade_out(target_brightness=0, steps=50, interval=20)
        time.sleep(1)

        print("🌬️ 正在执行 breathe 呼吸灯")
        led.breathe(steps=50, interval=20)

        print("🎉 所有测试完成！")
    except KeyboardInterrupt:
        print("程序已退出")
    except Exception as e:
        print("发生错误：", e)
    finally:
        led.off()

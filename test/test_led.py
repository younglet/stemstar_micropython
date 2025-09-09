from led import LED
from machine import Pin
import time

    print('''
【LED测试程序】
──────────────────────────────────────────────
【LED】   ->  GPIO4（PWM 输出）
──────────────────────────────────────────────
请按照如上接线说明进行接线，然后回车继续：''')

    input()  # 等待用户确认接线完成并回车继续

    try:
        print("🚩 开始测试 LED 功能...")

        print("🔧 正在初始化LED...")
        led = LED(Pin(4))  # 使用 GPIO4

        # -------------------- 1. 基础开关测试 --------------------
        print("💡 正在打开 LED")

        led.on()
        time.sleep(1)

        print("💡 正在关闭 LED")
        led.off()
        time.sleep(1)

        # -------------------- 2. 切换功能测试 --------------------
        print("🔁 正在测试 switch() 功能")
        led.switch()  # 打开
        time.sleep(1)
        led.switch()  # 关闭
        time.sleep(1)

        # -------------------- 3. 闪烁测试 --------------------
        print("✨ 正在执行 blink()： 闪烁（3次）")
        led.blink(times=3, interval=500)
        time.sleep(1)


        # -------------------- 4. 设置亮度 --------------------
        print("✨ 正在测试 set_brightness()：设置亮度为 1023")
        led.set_brightness(1023)
        time.sleep(1)

        # -------------------- 5. 亮度调节测试 --------------------

        print("📉 正在测试 darker()：重复3次，每次变暗100")
        for _ in range(3):
            led.darker(300)
            print(f"  ➡️ 亮度降低 → {led.brightness}")
            time.sleep(1)
        time.sleep(1)

        print("📈 正在测试 brighter()：重复3次，每次变亮100")
        for _ in range(3):
            led.brighter(300)
            print(f"  ➡️ 亮度增加 → {led.brightness}")
            time.sleep(1)
        time.sleep(1)



        # -------------------- 6. 淡入淡出测试 --------------------
        print("🌇 正在执行 fade_off()： 淡出")
        led.fade_off()
        time.sleep(1)


        print("🌅 正在执行 fade_on()： 淡入")
        led.fade_on()
        time.sleep(1)

        # -------------------- 7. 渐变到指定亮度 --------------------
        print("🎨 正在执行 fade_to(100)：500 → 100")
        led.fade_to(100)

        print("🎨 正在执行 fade_to(500)：100 → 500")
        led.fade_to(500)

        print("🎨 正在执行 fade_to(0)：500 → 0")
        led.fade_to(0)



        # -------------------- 8. 呼吸灯测试 --------------------
        print("🌬️ 正在执行 breathe()： 呼吸")
        led.set_brightness(800)
        led.breathe()

        # -------------------- 8. 最终状态 --------------------
        print("🎉 所有 LED 功能测试完成！")


    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print("发生错误：", e)

import time
from machine import Pin, PWM
 
class LED:
    def __init__(self, pin):
        """
        初始化 LED 并默认启用 PWM 模式
        :param pin: 引脚编号（int）或 Pin 对象
        """
        self.pin = pin
        
        # 默认启用 PWM
        self.pwm_obj = PWM(self.pin)
        self.pwm_obj.freq(500)  # 设置频率为 500Hz，可以根据需要调整
        self.brightness = 0  # 当前亮度，默认为0（关闭）

    def set_brightness(self, brightness):
        """设置 LED 的亮度"""
        if 0 <= brightness <= 1023:
            self.brightness = brightness
            self.pwm_obj.duty(self.brightness)
        else:
            raise ValueError("Brightness must be between 0 and 1023")

    def on(self):
        """打开 LED 至最大亮度"""
        self.set_brightness(1023)

    def off(self):
        """关闭 LED"""
        self.set_brightness(0)

    def blink(self, times=1, interval=0.5):
        """
        让 LED 闪烁指定次数
        :param times: 闪烁次数
        :param interval: 亮灭间隔时间（秒）
        """
        for _ in range(times):
            self.on()
            time.sleep(interval)
            self.off()
            time.sleep(interval)

    def fade_in(self, target_brightness=1023, steps=50, interval=0.02):
        """逐渐变亮"""
        start_brightness = self.brightness
        step_size = (target_brightness - start_brightness) // steps
        for duty in range(start_brightness, target_brightness + 1, step_size):
            self.set_brightness(duty)
            time.sleep(interval)
        self.set_brightness(target_brightness)

    def fade_out(self, target_brightness=0, steps=50, interval=0.02):
        """逐渐熄灭"""
        start_brightness = self.brightness
        step_size = (start_brightness - target_brightness) // steps
        for duty in range(start_brightness, target_brightness - 1, -step_size):
            self.set_brightness(duty)
            time.sleep(interval)
        self.set_brightness(target_brightness)

    def breathe(self, steps=50, interval=0.02):
        """模拟呼吸灯效果"""
        self.fade_in(steps=steps, interval=interval)
        self.fade_out(steps=steps, interval=interval)


if __name__ == "__main__":
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
        # 初始化 LED
        print("🚩 开始测试 LED 功能...")
        
        print("🔧 正在初始化LED...")
        led = LED(Pin(2))  # 默认启用 PWM

        print("💡 正在打开 LED")
        led.on()
        time.sleep(1)

        print("💡 正在关闭 LED")
        led.off()
        time.sleep(1)

        print("✨ 正在执行 blink 闪烁")
        led.blink(times=3)
        time.sleep(1)

        print("🌅 正在执行 fade_in 淡入")
        led.set_brightness(512)  # 设定初始亮度为中间值
        led.fade_in(target_brightness=1023, steps=50, interval=0.02)
        time.sleep(1)

        print("🌇 正在执行 fade_out 淡出")
        led.set_brightness(512)  # 设定初始亮度为中间值
        led.fade_out(target_brightness=0, steps=50, interval=0.02)
        time.sleep(1)

        print("🌬️ 正在执行 breathe 呼吸灯")
        led.breathe(steps=50, interval=0.02)

        print("🎉 所有测试完成！")
    except KeyboardInterrupt:
        print("程序已退出")
    except Exception as e:
        print("发生错误：", e)
    finally:
        led.off()

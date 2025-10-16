import time
from machine import Pin, PWM

class LED:
    def __init__(self, pin):
        """
        初始化 LED 并默认启用 PWM 模式
        :param pin: 引脚编号（int）或 Pin 对象
        """
        if isinstance(pin, int):
            self.pin = Pin(pin, Pin.OUT)
        else:
            if not isinstance(pin, Pin):
                raise TypeError("pin must be an integer or a machine.Pin object")
            pin.init(mode=Pin.OUT)
            self.pin = pin

        # 初始化 PWM（频率500Hz）
        try:
            self.pwm_obj = PWM(self.pin, freq=500, duty=0)
        except Exception as e:
            raise RuntimeError(f"PWM initialization failed on pin {self.pin}: {e}")

        self._brightness = 1023     # 当前亮度，默认为0（关闭）
        self.is_on = False       # 记录 LED 状态
        

    @property
    def brightness(self):
        """获取当前亮度"""
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        """设置亮度并更新 PWM 输出"""
        if not (0 <= value <= 1023):
            raise ValueError("Brightness must be between 0 and 1023")
        self._brightness = value
        self.pwm_obj.duty(value)  # 注意：ESP32/ESP8266 的 duty 范围通常是 0~1023
    
    def set_brightness(self, brightness):
        self.brightness = brightness

    def on(self):
        """打开 LED 至当前亮度"""
        if self.is_on:
            print("⚠️ LED 原本就是开启的状态")
            return
        self.pwm_obj.duty(self.brightness)
        self.is_on = True
        if self._brightness < 20:
            print(f"⚠️ 警告：当前亮度为{self.brightness}，LED 亮度可能不明显。")

    def off(self):
        """关闭 LED"""
        if not self.is_on:
            print("⚠️ LED 原本就是关闭的状态")
            return
        self.pwm_obj.duty(0)
        self.is_on = False

    def switch(self):
        """切换 LED 状态"""
        if self.is_on:
            self.off()
        else:
            self.on()
        

    def brighter(self, step=100):
        """
        增加亮度
        :param step: 增加的亮度步长
        """
        new_brightness = min(1023, self._brightness + step)
        self.brightness = new_brightness  # 使用 setter 自动更新 PWM
        if self.brightness > 0:
            self.is_on = True
        else:
            self.is_on = False
        

    def darker(self, step=100):
        """
        降低亮度
        :param step: 降低的亮度步长
        """
        new_brightness = max(0, self._brightness - step)
        self.brightness = new_brightness  # 使用 setter 自动更新 PWM
        if self.brightness > 0:
            self.is_on = True
        else:
            self.is_on = False


    def blink(self, times=1, interval=500):
        """
        让 LED 闪烁指定次数
        :param times: 闪烁次数
        :param interval: 亮灭间隔时间（毫秒）
        """
        for _ in range(times):
            self.on()
            time.sleep_ms(interval)
            self.off()
            time.sleep_ms(interval)

    def fade_to(self, target_brightness=1023, steps=50, interval=40):
        """
        从当前亮度平滑过渡到指定目标亮度。
        完成后当前亮度设为 target_brightness。
        
        :param target_brightness: 目标亮度 (0~1023)
        :param steps: 渐变步数
        :param interval: 每步间隔时间（毫秒）
        """
        if not (0 <= target_brightness <= 1023):
            raise ValueError("Target brightness must be between 0 and 1023")

        start_brightness = self.brightness if self.is_on else 0
        if start_brightness == target_brightness:
            return  # 无需操作

        for i in range(steps + 1):
            duty = start_brightness + (target_brightness - start_brightness) * i // steps
            self.set_brightness(duty)
            time.sleep_ms(interval)
        
        # 确保最终值精确等于目标（补偿整数误差）
        self.brightness = target_brightness
        if self.brightness > 0:
            self.is_on = True
        else:
            self.is_on = False


    def fade_on(self, steps=50, interval=40):
        """
        平滑打开 LED：从当前亮度渐变到记忆亮度。
        如果已经是开启状态，则不操作。
        """
        
        if self.is_on and self.pwm_obj.duty():
            print("⚠️ LED 原本就是开启的状态")
            return

        start_brightness = 0
        target_brightness = self.brightness  # 目标就是当前记忆亮度

        # 如果当前亮度为0，可以考虑设置一个默认值（可选）
        # if target_brightness == 0:
        #     target_brightness = 512  # 或其他默认值

        if start_brightness == target_brightness:
            self.is_on = True
            return

        for i in range(steps + 1):
            duty = start_brightness + (target_brightness - start_brightness) * i // steps
            self.pwm_obj.duty(duty)
            time.sleep_ms(interval)

        self.is_on = True  


    def fade_off(self, steps=50, interval=40):
        """
        平滑关闭 LED：从当前亮度渐变到 0。
        如果已经是关闭状态，则不操作。
        """
        if not self.is_on and self.pwm_obj.duty() == 0:
            print("⚠️ LED 原本就是关闭的状态")
            return

        start_brightness = self.brightness
        target_brightness = 0

        if start_brightness == target_brightness:
            self.is_on = False
            return

        for i in range(steps + 1):
            duty = start_brightness + (target_brightness - start_brightness) * i // steps
            self.pwm_obj.duty(duty)
            time.sleep_ms(interval)

        self.is_on = False  # ✅ 标记为关闭状态
            

    def breathe(self, steps=50, interval=20):
        """
        模拟呼吸灯效果
        :param steps: 变化步数
        :param interval: 每步间隔时间（毫秒）
        """
        self.fade_on(steps=steps, interval=interval)
        self.fade_off(steps=steps, interval=interval)

    @classmethod
    def test(cls):
        """测试方法，创建一个 LED 实例并执行简单的开关测试"""
        print('【LED测试程序】')

        try:
            pin_num = int(input("请输入 LED 的引脚号（如 4）: ") or "4")
        except:
            print("❌ 输入无效，默认使用 GPIO4")
            pin_num = 4
        
        try:
            print("🚩 开始测试 LED(Pin{pin_num}) 功能...")

            print("🔧 正在初始化LED...")
            led = cls(pin_num)  

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


if __name__ == '__main__':
    LED.test()

from machine import Pin, PWM
import time

class Motor:
    def __init__(self, pin1, pin2, direction=1, freq=5000, max_duty=1023):
        if direction not in (1, -1):
            raise ValueError("方向必须设置为 1 或 -1")

        # 创建 Pin 对象（不指定 mode）
        self._pin1_obj = Pin(pin1) if isinstance(pin1, int) else pin1
        self._pin2_obj = Pin(pin2) if isinstance(pin2, int) else pin2

        # 初始化 PWM
        self._pwm1 = PWM(self._pin1_obj, freq=freq)
        self._pwm2 = PWM(self._pin2_obj, freq=freq)

        self._max_duty = max_duty
        self._direction = direction
        self._speed = 0.0

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        value = max(-1.0, min(1.0, float(value)))
        self._speed = value
        actual_value = value * self._direction
        duty = int(abs(actual_value) * self._max_duty)

        if actual_value > 0:
            self._pwm1.duty(duty)
            self._pwm2.duty(0)
        elif actual_value < 0:
            self._pwm1.duty(0)
            self._pwm2.duty(duty)
        else:
            self._pwm1.duty(0)
            self._pwm2.duty(0)

    def deinit(self):
        self._pwm1.deinit()
        self._pwm2.deinit()
    
    def set_speed(self, speed):
        """设置电机速度（-1.0 ~ +1.0）"""
        self.speed = speed
    
    def stop(self):
        self.speed = 0
        

    @property
    def direction(self):
        return self._direction
    


    @classmethod
    def test(cls):
        """测试方法，创建一个 Motor 实例并执行基本功能测试"""
        print('【电机驱动测试程序】')

        try:
            pin1_str = input("请输入电机控制引脚1（如 14）: ") or "14"
            pin2_str = input("请输入电机控制引脚2（如 15）: ") or "15"
            pin1 = int(pin1_str)
            pin2 = int(pin2_str)
        except:
            print("❌ 输入无效，默认使用 GPIO14 和 GPIO15")
            pin1, pin2 = 14, 15

        try:
            dir_input = input("电机方向是否需要反转？(y/N): ").strip().lower()
            direction = -1 if dir_input == 'y' else 1
        except:
            direction = 1
        
        try:

            print(f"🚩 开始测试电机(GPIO{pin1}, GPIO{pin2})，方向修正: {'反转' if direction == -1 else '正常'}...")
            time.sleep(1)

            print("🔧 正在初始化电机...")
            motor = cls(pin1=pin1, pin2=pin2, direction=direction)

            # -------------------- 1. 正转测试 --------------------
            print("▶️  正在测试正转（speed = 0.6）")
            motor.speed = 0.6
            print(f"   ➡️ 当前速度: {motor.speed}")
            time.sleep(2)

            # -------------------- 2. 反转测试 --------------------
            print("◀️  正在测试反转（speed = -0.6）")
            motor.speed = -0.6
            print(f"   ➡️ 当前速度: {motor.speed}")
            time.sleep(2)

            # -------------------- 3. 停止 --------------------
            print("⏹️  正在停止电机")
            motor.stop()
            print(f"   ➡️ 当前速度: {motor.speed}")
            time.sleep(1)

            print("✅ 电机测试完成，释放资源")
            motor.deinit()

        except Exception as e:
            print("❌ 测试过程中发生错误：", e)
            motor.stop()

    @staticmethod
    def help():
        print("""
【Motor 直流电机驱动类】
--------------------
[硬件要求]:
    - 必须使用 H 桥驱动模块（如 L298N、TB6612FNG 等）
    - 不可将电机直接连接到 GPIO！否则可能烧毁主控
    - 电机电源电压应匹配电机额定电压（如 6V、12V）
    - 电压影响：
        • 电压过低 → 电机无力、无法启动
        • 电压过高 → 电机过热、寿命缩短甚至损坏
        • PWM 控制的是“有效电压比例”，实际转速受供电电压直接影响
--------------------
[初始化]:
    motor = Motor(pin1, pin2, direction=1, freq=5000, max_duty=1023)
    # pin1, pin2 : 两个 GPIO 引脚，分别接 H 桥的 IN1/IN2
    # freq       : PWM 频率（Hz），推荐 1k~10kHz，默认 5000
    # max_duty   : 最大占空比值（ESP32 默认 1023，Pico 需改为 65535）
    # direction  : 方向修正，1（默认）或 -1（用于接线反向时）
[属性]:
    speed      : 当前速度（可读写），范围 -1.0（全速反转）~ +1.0（全速正转）
    direction  : 当前方向修正系数（只读）
[方法]:
    stop()         # 立即停止电机（等效于 speed = 0）
    deinit()       # 释放 PWM 资源（程序结束前建议调用）
--------------------
[使用示例]:
    from motor import Motor
    from machine import Pin
    import time

    # 初始化电机（接 GPIO14 和 15，方向正常）
    motor = Motor(Pin(14), Pin(15)）

    motor.speed = 0.7      # 正转 70%
    time.sleep(2)
    motor.speed = -0.5     # 反转 50%
    time.sleep(2)
    motor.stop()           # 停止

    # 若电机转向与预期相反，只需改 direction=-1，无需改逻辑
    motor = Motor(Pin(14), Pin(15), direction=-1)
    motor.speed = 0.6     # 逻辑正转（即使物理接线反了）
--------------------
""")

if __name__ == "__main__":
    Motor.test()

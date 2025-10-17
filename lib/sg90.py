from machine import Pin, PWM

class SG90:
    # 标准 SG90 舵机参数（PWM 频率 50Hz，对应周期 20ms）
    __servo_pwm_freq = 50
    __min_u10_duty = 26   # 对应 0.5ms 脉宽（0° 位置）
    __max_u10_duty = 123  # 对应 2.5ms 脉宽（180° 位置）
    min_angle = 0         # 最小角度（可修改）
    max_angle = 180       # 最大角度（可修改）

    def __init__(self, pin):
        """
        初始化 SG90 舵机驱动，**不会让舵机在初始化时转动**
        :param pin: 引脚编号（整数）或 machine.Pin 对象
        """
        # 处理引脚输入：支持整数或 Pin 对象
        if isinstance(pin, int):
            self.pin = pin  # 直接保存编号，交给 PWM 处理
            self.__motor = PWM(Pin(pin), freq=self.__servo_pwm_freq, duty=0)
        elif isinstance(pin, Pin):
            pin.init(mode=Pin.OUT)
            self.pin = pin
        else:
            raise TypeError("引脚参数必须是整数或 machine.Pin 对象")

        # 初始化 PWM，频率设为 50Hz，初始占空比为 0（不输出信号，舵机保持静止）
        try:
            self.__motor = PWM(self.pin, freq=self.__servo_pwm_freq, duty=0)
        except Exception as e:
            raise RuntimeError(f"在引脚 {self.pin} 上初始化 PWM 失败: {e}")

        # 当前角度设为 None，表示尚未设置目标角度
        self.__current_angle = None

        # 预计算角度到占空比的转换系数，提升运行效率
        self.__angle_conversion_factor = (
            (self.__max_u10_duty - self.__min_u10_duty) /
            (self.max_angle - self.min_angle)
        )

    @property
    def angle(self):
        """获取当前目标角度"""
        return self.__current_angle

    @angle.setter
    def angle(self, value):
        """设置目标角度（会自动移动舵机）"""
        self.move_to(value)

    def move_to(self, angle):
        """
        将舵机转动到指定角度
        :param angle: 目标角度（浮点数或整数），必须在 min_angle 到 max_angle 范围内
        """
        # 检查角度是否在合法范围内
        if not (self.min_angle <= angle <= self.max_angle):
            raise ValueError(
                f"角度值超出范围！必须在 {self.min_angle}° 到 {self.max_angle}° 之间，"
                f"但收到了 {angle}°"
            )

        # 保留两位小数，避免因浮点误差导致舵机微抖
        angle = round(float(angle), 2)

        # 仅当目标角度与当前角度不同时才执行转动
        if self.__current_angle != angle:
            self.__current_angle = angle
            duty_u10 = self.__angle_to_u10_duty(angle)
            self.__motor.duty(duty_u10)

    def __angle_to_u10_duty(self, angle):
        """
        将角度转换为 10 位精度的 PWM 占空比值（范围 0~1023）
        """
        return int((angle - self.min_angle) * self.__angle_conversion_factor) + self.__min_u10_duty

    def deinit(self):
        """
        停止 PWM 信号输出，使舵机释放扭矩（进入“自由”状态）
        """
        self.__motor.deinit()

    @classmethod
    def test(cls):
        print('【SG90 舵机测试程序】')
        try:
            pin_num = int(input("请输入舵机信号线连接的GPIO(建议连接至GPIO4): ") or "4")
        except:
            print("❌ 输入无效，默认使用 GPIO4")
            pin_num = 4
        
        servo = None
        try:
            print(f"🚩 开始 SG90 舵机(GPIO{pin_num}) 功能测试...")
            import time

            print("🔧 正在初始化舵机...")
            servo = cls(Pin(pin_num))  # 初始化舵机引脚

            angles = [
                (  0,  "⬅️"), 
                ( 45,  "↖️"), 
                ( 90,  "⬆️"), 
                (135,  "↗️"), 
                (180,  "➡️"), 
            ]

            print("🔄 开始测试舵机角度旋转")
            print("📌 按 Ctrl+C 可随时退出程序\n")

            for angle, emoji in angles:
                print(f"🧭 正在转动到 {angle}°")
                servo.move_to(angle)
                print(f"{emoji} 已转至 {angle}°")
                time.sleep(2)

            print("🛑 测试完成，正在释放舵机扭矩...")
            servo.deinit()
            print("🎉 所有测试完成！")
        except KeyboardInterrupt:
            print("\n❗ 测试被用户中断，正在释放舵机扭矩...")
            servo.deinit()
            print("🎉 测试结束！")

    @staticmethod
    def help():
        print("""
【SG90 舵机驱动类】
--------------------
[硬件参数]:
    - PWM 频率: 50Hz (周期 20ms)
    - 最小脉宽: 0.5ms (对应 0°)
    - 最大脉宽: 2.5ms (对应 180°)
    - 默认角度范围: 0° 到 180° (若硬件支持，可通过修改 min_angle 和 max_angle 属性调整)
--------------------
[初始化]:
    servo = SG90(pin)     # pin: machine.Pin 对实例
[属性]:
    angle: 当前目标角度（可读写，设置时会自动转动舵机）  
[方法]:
    move_to(angle)        # 将舵机转动到指定角度
    deinit()              # 停止 PWM 信号输出，使舵机释放扭矩
--------------------
[示例]:
    servo = SG90(4)       # 初始化舵机，信号线连接到 GPIO4
    servo.move_to(90)     # 转动到 90°
    servo.angle = 45      # 也可以通过属性设置角度，转动到 45°
    print(servo.angle)    # 读取当前目标角度
    servo.deinit()        # 停止 PWM，释放舵机扭矩
--------------------
""")

if __name__ == "__main__":
    SG90.test()
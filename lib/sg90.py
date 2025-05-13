from machine import Pin, PWM

class Servo:
    # 这些默认值适用于标准 TowerPro SG90 舵机
    __servo_pwm_freq = 50
    __min_u10_duty = 26 - 0  # 用于校正的偏移量（最小占空比）
    __max_u10_duty = 123 - 0 # 用于校正的偏移量（最大占空比）
    min_angle = 0
    max_angle = 180
    current_angle = 0.001


    def __init__(self, pin):
        # 初始化角度为 -0.001，确保第一次调用 move() 时能触发移动
        self.current_angle = -0.001
        # 计算角度到占空比的转换因子
        self.__angle_conversion_factor = (self.__max_u10_duty - self.__min_u10_duty) / (self.max_angle - self.min_angle)
        # 初始化 PWM 引脚
        self.__motor = PWM(pin)
        # 设置 PWM 频率为舵机要求的频率
        self.__motor.freq(self.__servo_pwm_freq)


    def move(self, angle):
        # 将角度保留两位小数，以减少不必要的舵机微调
        angle = round(angle, 2)
        # 是否需要移动？
        if angle == self.current_angle:
            return
        self.current_angle = angle
        # 计算新的占空比并控制舵机转动
        duty_u10 = self.__angle_to_u10_duty(angle)
        self.__motor.duty(duty_u10)

    def __angle_to_u10_duty(self, angle):
        # 将角度转换为对应的 10-bit 占空比值（u10）
        return int((angle - self.min_angle) * self.__angle_conversion_factor) + self.__min_u10_duty


if __name__ == '__main__':
    from machine import Pin
    from time import sleep

    servo = Servo(Pin(4))


    angles = [10, 30, 90, 120, 170, 90]

    for angle in angles:
        servo.move(angle)
        print(f'现已转至{angle}度')
        sleep(2)

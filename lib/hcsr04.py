from machine import Pin, time_pulse_us
from utime import sleep_us


class HCSR04:
    """
    HC-SR04 超声波传感器驱动程序
    支持传入已初始化的 Pin 实例
    测距范围：2cm ~ 400cm
    """

    def __init__(self, trigger_pin: Pin, echo_pin: Pin, echo_timeout_us=500 * 2 * 30):
        """
        :param trigger_pin: 已初始化的 Pin 实例（输出模式）
        :param echo_pin: 已初始化的 Pin 实例（输入模式）
        :param echo_timeout_us: 等待回声信号的最大时间（微秒）
        """
        self.echo_timeout_us = echo_timeout_us
        self.trigger = trigger_pin
        self.echo = echo_pin
        
        # 初始化设置引脚状态
        self.trigger.init(mode=Pin.OUT)
        self.echo.init(mode=Pin.IN)

        # 确保 trigger 初始状态为低电平
        self.trigger.value(0)

    def _send_pulse_and_wait(self):
        """
        发送触发脉冲并等待回响信号返回
        返回高电平持续时间（微秒）
        """
        self.trigger.value(0)
        sleep_us(5)
        self.trigger.value(1)
        sleep_us(10)  # 至少 10us 高电平
        self.trigger.value(0)

        pulse_time = time_pulse_us(self.echo, 1, self.echo_timeout_us)
        if pulse_time < 0:
            # 如果超时，设定最大距离对应的时间值
            MAX_RANGE_CM = const(500)
            pulse_time = int(MAX_RANGE_CM * 29.1)
        return pulse_time



    def get_distance(self):
        """
        获取距离，单位厘米（浮点数）
        """
        pulse_time = self._send_pulse_and_wait()
        cm = (pulse_time / 2) / 29.1
        return cm



if __name__ == "__main__":
    # 初始化引脚
    trigger = Pin(14, Pin.OUT)  # 示例：使用 GPIO14 作为 Trigger
    echo = Pin(15, Pin.IN)   # 示例：使用 GPIO15 作为 Echo
    
    # 简化写法
    # trigger = Pin(14)
    # echo = Pin(15)

    # 创建传感器实例
    sensor = HCSR04(trigger_pin=trigger, echo_pin=echo)

    # 循环测量距离
    print("开始测量距离...")

    while True:
        try:
            distance = sensor.get_distance()
            print(f"距离: {distance:.1f} cm ")
        except Exception as e:
            print("错误:", e)

        sleep_us(500_000)  # 每隔 0.5 秒测一次
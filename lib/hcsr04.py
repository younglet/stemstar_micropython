from machine import Pin, time_pulse_us
from utime import sleep_us

 
class HCSR04:
    """
    HC-SR04 超声波传感器驱动程序
    支持传入已初始化的 Pin 实例
    测距范围：2cm ~ 400cm
    """

    def __init__(self, trig_pin: Pin, echo_pin: Pin, echo_timeout_us=500 * 2 * 30):
        """
        :param trig_pin: 已初始化的 Pin 实例（输出模式）
        :param echo_pin: 已初始化的 Pin 实例（输入模式）
        :param echo_timeout_us: 等待回声信号的最大时间（微秒）
        """
        self.echo_timeout_us = echo_timeout_us
        self.trig = trig_pin
        self.echo = echo_pin
        
        # 初始化设置引脚状态
        self.trig.init(mode=Pin.OUT)
        self.echo.init(mode=Pin.IN)

        # 确保 trig 初始状态为低电平
        self.trig.value(0)

    def _send_pulse_and_wait(self):
        """
        发送触发脉冲并等待回响信号返回
        返回高电平持续时间（微秒）
        """
        self.trig.value(0)
        sleep_us(5)
        self.trig.value(1)
        sleep_us(10)  # 至少 10us 高电平
        self.trig.value(0)

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
    import time
    from machine import Pin
    
    print('''
【超声波传感器】正在启动...
──────────────────────────────────────────────
【Trig】 -> GPIO14
【Echo】 -> GPIO12
──────────────────────────────────────────────
请按照如上接线说明进行接线，然后按车继续：''')

    input()  # 等待用户确认接线完成并回车继续
    # 初始化引脚
    try:
        print("🚩 开始测试 HCS04 超声波测距...")
        print("🔧 正在初始化 HCS04 超声波测距...")
        trig = Pin(14, Pin.OUT)   # Trig 引脚
        echo = Pin(12, Pin.IN)    # Echo 引脚

        # 创建传感器实例
        sensor = HCSR04(trig_pin=trig, echo_pin=echo)

        print("📡 正在开始测量距离...")
        print("🔄 每隔 1 秒测量一次，按 Ctrl+C 退出程序")

        while True:
            print("🔍 正在获取当前距离数据...")
            distance = sensor.get_distance()
            print(f"📏 当前距离: {distance:.1f} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 程序已退出，关闭传感器")

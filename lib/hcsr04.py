from machine import Pin, time_pulse_us
from utime import sleep_us

 
class HCSR04:
    """
    HC-SR04 超声波传感器驱动程序
    支持传入已初始化的 Pin 实例
    测距范围：2cm ~ 400cm
    """

    def __init__(self, trig_pin, echo_pin, echo_timeout_us=500 * 2 * 30):
        """
        初始化超声波传感器（如 HC-SR04）。

        :param trig_pin: GPIO 编号（int）或已初始化的 Pin 实例
        :param echo_pin: GPIO 编号（int）或已初始化的 Pin 实例
        :param echo_timeout_us: 等待回声信号的最大时间（微秒）
        """
        # 处理 trig_pin
        if isinstance(trig_pin, int):
            self.trig = Pin(trig_pin, Pin.OUT)
        elif isinstance(trig_pin, Pin):
            self.trig = trig_pin
            self.trig.init(Pin.OUT)
        else:
            raise TypeError("trig_pin 必须是整数（GPIO编号）或 machine.Pin 实例")

        # 处理 echo_pin
        if isinstance(echo_pin, int):
            self.echo = Pin(echo_pin, Pin.IN)
        elif isinstance(echo_pin, Pin):
            self.echo = echo_pin
            self.echo.init(Pin.IN)
        else:
            raise TypeError("echo_pin 必须是整数（GPIO编号）或 machine.Pin 实例")

        self.echo_timeout_us = echo_timeout_us
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

    @property
    def distance(self):
        """只读属性：等同于 get_distance()，返回当前距离值（厘米）"""
        return self.get_distance()

    @classmethod
    def test(cls):
        print("【超声波传感器（HC-SR04）测试程序】")
        try:
            trig_pin_num = int(input("请输入 Trig 引脚连接的 GPIO（建议 GPIO14）: ") or "14")
        except:
            print("❌ 输入无效，默认使用 GPIO14")
            trig_pin_num = 14
        try:
            echo_pin_num = int(input("请输入 Echo 引脚连接的 GPIO（建议 GPIO12）: ") or "12")
        except:
            print("❌ 输入无效，默认使用 GPIO12")
            echo_pin_num = 12
        print(f"🔧 初始化 HC-SR04（Trig GPIO{trig_pin_num}，Echo GPIO{echo_pin_num}）...")
        trig = Pin(trig_pin_num, mode=Pin.OUT)
        echo = Pin(echo_pin_num, mode=Pin.IN)
        sensor = cls(trig_pin=trig, echo_pin=echo)
        print("📡 开始读取距离数据（按 Ctrl+C 停止）")
        try:
            while True:
                distance = sensor.get_distance()
                print(f"📏 当前距离: {distance:.1f} cm")
                sleep_us(500000)  # 500ms
        except KeyboardInterrupt:
            print("\n👋 程序已退出，关闭传感器")

    @staticmethod
    def help():
        print("""
【HC-SR04 超声波传感器驱动类】
--------------------
[硬件要求]:
  - HC-SR04 超声波传感器模块
--------------------
[初始化]:
    sensor = HCSR04(tri
--------------------g_pin, echo_pin, echo_timeout_us=30000)
    # trig_pin         : 已初始化的 Pin 实例（输出模式）
    # echo_pin         : 已初始化的 Pin 实例（输入模式）
    # echo_timeout_us  : 等待回声信号的最大时间（微秒），默认 30000us（约 5 米）
[属性]:
    - distance        : 只读属性，当前测量的距离值（厘米）

[方法]:
    - get_distance()  : 获取当前测量的距离值（厘米）

--------------------
[示例代码]:
    from machine import Pin
    from hcsr04 import HCSR04

    sensor = HCSR04(Pin(14), Pin(12))
    distance = sensor.get_distance()
    print("当前距离: {:.1f} cm".format(distance))
""")

if __name__ == "__main__":
    HCSR04.test()
from machine import Pin
from time import sleep_ms

# 初始化GPIO引脚2为输出
led = Pin(2, Pin.OUT)

# 定义简化版的软件PWM函数
def simple_pwm(pin, period_ms=20, duty_cycle=50):
    """
    简单的软件PWM实现。
    :param pin: 要控制的Pin对象
    :param period_ms: PWM周期，单位毫秒
    :param duty_cycle: 占空比，范围0到100
    """
    on_duration = int(period_ms * duty_cycle / 100)  # 高电平持续时间
    off_duration = period_ms - on_duration           # 低电平持续时间
    
    pin.on()
    sleep_ms(on_duration)
    pin.off()
    sleep_ms(off_duration)

# 主循环
while True:
    # 使用固定参数调用simple_pwm
    simple_pwm(led, period_ms=20, duty_cycle=50)  # 周期为20ms，占空比为50%
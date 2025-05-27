# button.py

import time
from machine import Pin

class Button:
    def __init__(self, pin, debounce_delay=10):
        """
        初始化按钮对象
        :param pin: 已经配置好的 Pin 实例（输入模式）
        """
        if not isinstance(pin, Pin):
            raise ValueError("pin 参数必须是 machine.Pin 的实例")
        
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.last_state = self.pin.value()
        self.debounce_delay = debounce_delay
        self.last_debounce_time = time.ticks_ms()
        self.state = self.last_state

    def is_pressed(self):
        """
        返回按钮是否被按下（带防抖）
        :return: bool
        """
        current_value = self.pin.value()
        current_time = time.ticks_ms()

        # 如果状态改变
        if current_value != self.last_state:
            self.last_debounce_time = current_time
            self.last_state = current_value
        
        # 如果超过了防抖时间，则返回稳定的状态
        if time.ticks_diff(current_time, self.last_debounce_time) > self.debounce_delay:
            self.state = self.last_state
            
        return self.state


if __name__ == "__main__":
    from machine import Pin
    import time

    print('''
【按钮测试程序】
──────────────────────────────────────────────
【按钮】   ->  GPIO2 （请按下按钮）
──────────────────────────────────────────────
请按照如上接线说明进行接线，然后回车继续：''')

    input()  # 等待用户确认接线完成并回车继续

    try:
        print("🚩 开始测试按钮功能...")

        print("🔧 正在初始化按钮...")
        btn_pin = Pin(2, Pin.IN, Pin.PULL_DOWN)
        btn = Button(btn_pin)

        print("🔘 等待首次按下按钮...")
        while True:
            if btn.is_pressed():
                print("✅ 按钮已按下")
                break
            time.sleep_ms(10)

        print("\n🔁 进入实时按钮状态监测（持续5秒）...")
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < 5000:
            if btn.is_pressed():
                print("🔵 按钮被按下", end='\r')
            else:
                print("⚪ 按钮未按下", end='\r')
            time.sleep_ms(50)

        print("\n🔚 按钮状态监测结束")

        print("🎉 所有测试完成！")

    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print("发生错误：", e)

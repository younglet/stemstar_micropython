# button.py

import time
from machine import Pin

class Button:
    def __init__(self, pin, debounce_delay=10):
        """
        初始化按钮对象
        :param pin: 已经配置好的 Pin 实例（输入模式）
        """
                
        if isinstance(pin, int):
            self.pin = Pin(pin)
        else:
            pin = pin.init(Pin.IN, Pin.PULL_DOWN)
            self.pin = pin
        
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.last_state = self.pin.value()
        self.debounce_delay = debounce_delay
        self.last_debounce_time = time.ticks_ms()
        self.state = self.last_state
        self.last_click_time = 0  # 可选：用于防止连续误判
        self.previous_stable_state = self.state

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

    def is_clicked(self, min_interval=50):
        """
        判断是否发生了一次点击（按下后松开）
        :param min_interval: 最小点击间隔（毫秒），防止连续误判
        :return: bool
        """
        current_state = self.is_pressed()
        prev = self.previous_stable_state

        # 更新 previous_stable_state
        if time.ticks_diff(time.ticks_ms(), self.last_debounce_time) > self.debounce_delay:
            self.previous_stable_state = current_state

        now = time.ticks_ms()
        # 检测从高到低的下降沿（即松开时）
        if prev and not current_state:
            if now - self.last_click_time > min_interval:
                self.last_click_time = now
                return True
        return False


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

        # ===== 测试 is_pressed() =====
        print("\n🔘 正在测试 is_pressed()（持续5秒）...")
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < 5000:
            if btn.is_pressed():
                print("🔵 按钮被按下", end='\r')
            else:
                print("⚪ 按钮未按下", end='\r')
            time.sleep_ms(50)
        print("\n✅ is_pressed() 测试完成")


        # ===== 测试 is_clicked() =====
        print("\n🔘 正在测试 is_clicked()（持续10秒）...")
        print("👉 请在这段时间内尝试多次按下并松开按钮以测试点击检测\n")
        start_time = time.ticks_ms()
        click_count = 0
        while time.ticks_diff(time.ticks_ms(), start_time) < 10000:
            if btn.is_clicked():
                click_count += 1
                print(f"👇 检测到一次完整点击！（第 {click_count} 次）")
            time.sleep_ms(50)
        print("✅ is_clicked() 测试完成")

        print("\n🔚 所有测试已完成！")

    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print("发生错误：", e)

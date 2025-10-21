from machine import Pin, PWM
import time

class TriLight:
    """
    三通道 PWM 光输出控制器（如 RGB LED）
    支持共阳极（is_0_max=True：duty=0 最亮）或共阴极（默认）
    """

    def __init__(self, pin1, pin2, pin3, freq=5000, max_duty=1023, is_0_max=False):
        """
        初始化三通道 PWM
        
        参数:
            pin1, pin2, pin3: GPIO 引脚（int 或 Pin）
            freq: PWM 频率（Hz）
            max_duty: 最大占空比（ESP32 默认 1023，Pico 用 65535）
            is_0_max: bool，若为 True，表示 duty=0 时光线最强（共阳极）
        """
        self._pins = []
        self._pwms = []

        for pin in (pin1, pin2, pin3):
            pin_obj = Pin(pin) if isinstance(pin, int) else pin
            self._pins.append(pin_obj)
            self._pwms.append(PWM(pin_obj, freq=freq))

        self._max_duty = max_duty
        self._is_0_max = bool(is_0_max)
        self._rgb = [0, 0, 0]  # 内部存储 [r, g, b]，0~255

        # 初始化关闭
        self._apply_duty(0, 0, 0)

    def _map_8bit_to_duty(self, val_8bit):
        """将 0~255 映射到 0~max_duty"""
        return int(val_8bit * self._max_duty / 255)

    def _apply_duty(self, r, g, b):
        """将 RGB (0~255) 转为 PWM 输出"""
        rgb_vals = [r, g, b]
        for i, val in enumerate(rgb_vals):
            val = max(0, min(255, int(val)))
            duty = self._map_8bit_to_duty(val)
            output = self._max_duty - duty if self._is_0_max else duty
            self._pwms[i].duty(output)
            self._rgb[i] = val

    # ========== 方法 ==========
    def set_rgb(self, r, g, b):
        """设置 RGB 颜色，接收三个独立参数（0~255）"""
        self._apply_duty(r, g, b)

    def set_color(self, color):
        """设置颜色，接收一个 RGB 元组或列表，如 (255, 128, 0)"""
        if not isinstance(color, (tuple, list)) or len(color) != 3:
            raise ValueError("color 必须是长度为3的元组或列表，如 (r, g, b)")
        r, g, b = color
        self._apply_duty(r, g, b)

    def off(self):
        """关闭所有通道"""
        self._apply_duty(0, 0, 0)

    def deinit(self):
        """释放 PWM 资源"""
        for pwm in self._pwms:
            pwm.deinit()

    # ========== 属性：color ==========
    @property
    def color(self):
        """返回当前 RGB 值 (r, g, b)，每个分量 0~255"""
        return tuple(self._rgb)

    @color.setter
    def color(self, color):
        """支持 light.color = (r, g, b)"""
        self.set_color(color)

    # ========== 属性：r, g, b ==========
    @property
    def r(self):
        return self._rgb[0]

    @r.setter
    def r(self, val):
        self._apply_duty(val, self._rgb[1], self._rgb[2])

    @property
    def g(self):
        return self._rgb[1]

    @g.setter
    def g(self, val):
        self._apply_duty(self._rgb[0], val, self._rgb[2])

    @property
    def b(self):
        return self._rgb[2]

    @b.setter
    def b(self, val):
        self._apply_duty(self._rgb[0], self._rgb[1], val)

    # ========== 测试与帮助 ==========
    @classmethod
    def test(cls):
        print('【TriLight 三通道光输出测试】')
        try:
            p1 = int(input("R 引脚（如 12）: ") or "12")
            p2 = int(input("G 引脚（如 13）: ") or "13")
            p3 = int(input("B 引脚（如 14）: ") or "14")
        except:
            print("❌ 使用默认引脚 12,13,14")
            p1, p2, p3 = 12, 13, 14

        mode = input("是否共阳极？(y/N，即 0=最亮): ").strip().lower()
        is_0_max = (mode == 'y')

        light = cls(p1, p2, p3, is_0_max=is_0_max)
        print("💡 测试流程...")

        try:
            light.set_rgb(255, 0, 0); print("🔴 红"); time.sleep(0.5)
            light.set_color((0, 255, 0)); print("🟢 绿"); time.sleep(0.5)
            light.color = (0, 0, 255); print("🔵 蓝"); time.sleep(0.5)
            light.r = 255; light.g = 255; light.b = 0; print("🟡 黄"); time.sleep(0.5)
            light.off(); print("⚫ 关")
            print("当前值:", light.color)
        except Exception as e:
            print("❌ 错误:", e)
        finally:
            light.deinit()
        print("✅ 测试完成")

    @staticmethod
    def help():
        print("""
【TriLight 三通道 PWM 光输出类】
----------------------------------
[初始化]:
    light = TriLight(R_pin, G_pin, B_pin, is_0_max=False)
    # R_pin, G_pin, B_pin : 三个 GPIO 引脚（Pin 对象）
    # is_0_max            : bool，True 表示 duty=0 最亮（共阳极），默认 False（共阴极）

[属性]:
    color : 当前颜色 (r, g, b)，每个分量 0~255（可读写）
    r     : 红色分量 0~255（可读写）
    g     : 绿色分量 0~255（可读写）
    b     : 蓝色分量 0~255（可读写）

[方法]:
    set_rgb(r, g, b)   : 设置颜色，三个独立参数 0~255
    set_color((r,g,b)) : 设置颜色，传入一个 RGB 元组或列表
    off()              : 关闭所有通道
    deinit()          : 释放资源
----------------------------------
[示例代码]:
    from trilight import TriLight
    from machine import Pin
    from time import sleep_ms

    light = TriLight(12, 13, 14, is_0_max=False)  # 共阴极 RGB LED
    light.set_rgb(255, 0, 0)  # 红色
    sleep_ms(500)
    light.color = (0, 255, 0)  # 绿色
    sleep_ms(500)
    light.b = 255              # 绿色+蓝色 = 青色
    sleep_ms(500)
    light.off()                # 关闭
----------------------------------
""")


if __name__ == "__main__":
    TriLight.test()
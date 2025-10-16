from math import isinf
from machine import I2C, Pin, ADC
from ssd1306 import SSD1306_I2C
from time import sleep
import time


class Waveform:
    def __init__(self, screen, show_current_value=True,
                 value_update_interval=2, average_range=1):
        self.screen = screen
        self.width = screen.width
        self.height = screen.height
        self.DEFAULT_RANGE = self.height // 4
        self.show_current_value = show_current_value

        # 新增参数
        self.value_update_interval = value_update_interval
        self.average_range = average_range

        # 数据缓存区
        self.data_buffer = []

        # 极值用于归一化
        self.min_val = float('inf')
        self.max_val = -float('inf')

        # 内部计数器，用于控制更新频率
        self.update_counter = 0

    def add_value(self, value):
        if value is None:
            return

        self.data_buffer.append(value)
        if len(self.data_buffer) > self.width:
            self.data_buffer.pop(0)

        self.update_min_max()

        current_avg = sum(self.data_buffer) / len(self.data_buffer)

        # 使用默认范围或动态范围
        range_val = self.max_val - self.min_val
        if range_val < self.DEFAULT_RANGE:
            # 使用默认范围并居中
            avg = current_avg
            min_val = avg - self.DEFAULT_RANGE / 2
            max_val = avg + self.DEFAULT_RANGE / 2
        else:
            min_val = self.min_val
            max_val = self.max_val

        range_val = max_val - min_val
        if range_val <= 0:
            range_val = 1

        points = [
            self.height - int((val - min_val) / range_val * self.height)
            for val in self.data_buffer
        ]

        self._update(points)

    def update_min_max(self):
        if not self.data_buffer:
            return

        current_min = min(self.data_buffer)
        current_max = max(self.data_buffer)

        alpha = 0.95  # 平滑系数

        # 如果是初始值（无穷大/小），直接设置为当前值
        if self.min_val == float('inf') or self.max_val == -float('inf'):
            self.min_val = current_min
            self.max_val = current_max
            return

        # 更新最小值（平滑处理）
        if current_min < self.min_val:
            self.min_val = int(current_min * (1 - alpha) + self.min_val * alpha)
        else:
            self.min_val = int(current_min * alpha + self.min_val * (1 - alpha))

        # 更新最大值（平滑处理）
        if current_max > self.max_val:
            self.max_val = int(current_max * alpha + self.max_val * (1 - alpha))
        else:
            self.max_val = int(current_max * (1 - alpha) + self.max_val * alpha)

        # 防止极值范围过小
        if self.max_val - self.min_val < 5:
            self.min_val = int(current_min)
            self.max_val = int(current_max)

    def _update(self, points):
        self.screen.fill(0)

        # 绘制波形线
        if len(points) >= 2:
            for i in range(1, len(points)):
                x1, y1 = i - 1, points[i - 1]
                x2, y2 = i, points[i]
                self.screen.line(x1, y1, x2, y2, 1)

        # 更新左上角数值（根据间隔）
        if self.show_current_value and self.data_buffer and \
           self.update_counter % self.value_update_interval == 0:
            avg_count = min(len(self.data_buffer), self.average_range)
            recent_values = self.data_buffer[-avg_count:]
            self.avg_value = sum(recent_values) // avg_count
        self.screen.fill_rect(0, 0, 36, 10, 0)  # 清除旧值区域
        self.screen.text(f"{self.avg_value:04d}", 2, 1, 1)

        # 计数器自增
        self.update_counter += 1

        self.screen.show()


if __name__ == "__main__":
    print('''
【OLED波形图测试程序】
──────────────────────────────────────────────
【屏幕】   ->   I2C1 (SCL: GPIO25; SDA: GPIO26)
【传感器】 ->   ADC (GPIO33)
──────────────────────────────────────────────
请按照如上接线说明进行接线，然后按车继续：''')

    input()  # 等待用户确认接线完成并回车继续
    print("🚩 开始测试波形图...")
    try:
        print("🔧 正在初始化 OLED 屏幕...")
        
        i2c = I2C(1)  # 使用 I2C 总线 1
        screen = SSD1306_I2C(128, 64, i2c)


        print("📡 正在初始化模拟传感器（ADC on GPIO33）...")
        sensor = ADC(Pin(33))

        print("📊 正在创建波形图实例")
        waveform = Waveform(screen)

        print("🔄 开始实时采集数据并绘制波形图")
        print("📌 按 Ctrl+C 可随时退出程序\n")

        while True:
            waveform.add_value(sensor.read())
            time.sleep(0.1)
    except OSError:
        print("\n❌ OLED 屏幕初始化失败，请检查接线，程序即将退出...")
    except KeyboardInterrupt:
        print("\n👋 您按下了 Ctrl+C，程序即将退出...")



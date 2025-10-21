from machine import Pin, ADC
import time

class LDR:
    """
    光敏电阻（LDR）传感器驱动类
    通过 ADC 读取原始模拟值，值越大表示光线越强（取决于电路接法）
    """

    def __init__(self, pin, attenuation=ADC.ATTN_11DB):
        """
        初始化光敏传感器
        
        参数:
            pin: GPIO 引脚号（如 34）或已创建的 Pin 对象
            attenuation: ADC 衰减等级（默认 11dB，适用于 0~3.6V 输入，适合 ESP32）
        """
        self._pin_obj = Pin(pin) if isinstance(pin, int) else pin
        self._adc = ADC(self._pin_obj)
        self._adc.atten(attenuation)

    def read(self):
        """
        读取原始 ADC 值
        
        返回:
            int: ADC 原始值 → 0~4095（12位）
        """
        return self._adc.read()

    @property
    def value(self):
        """只读属性：等同于 read()，返回当前 ADC 原始值"""
        return self.read()

    def deinit(self):
        """释放资源（MicroPython 中 ADC 通常无需显式释放，保留接口一致性）"""
        pass

    @classmethod
    def test(cls):
        """测试方法：读取并打印光敏传感器值"""
        print('【光敏传感器（LDR）测试程序】')

        try:
            pin_str = input("请输入光敏传感器连接的 GPIO 引脚（如 34）: ") or "34"
            pin = int(pin_str)
        except:
            print("❌ 输入无效，默认使用 GPIO34")
            pin = 34

        print(f"🔧 初始化 LDR（GPIO{pin}，ATTN_11DB）...")
        sensor = cls(pin, attenuation=ADC.ATTN_11DB)

        print("📡 开始读取数据（按 Ctrl+C 停止）")
        try:
            while True:
                print(f"   ➡️ ADC 原始值: {sensor.value}")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n⏹️  测试结束")
        finally:
            sensor.deinit()

    @staticmethod
    def help():
        print("""
【LDR 光敏电阻传感器驱动类】
--------------------
[硬件要求]:
    - 使用光敏电阻（LDR）+ 分压电阻（如 10kΩ）组成分压电路
    - 输出端接主控 ADC 引脚（如 ESP32 的 GPIO34/35/32/33 等仅输入引脚）
    - 注意：ESP32 的 GPIO34–39 仅支持输入，不能配置上拉/下拉
--------------------
[初始化]:
    ldr = LDR(pin, attenuation=ADC.ATTN_11DB)
    # pin: GPIO 引脚号（如 34）
    # attenuation: ADC 衰减等级，ESP32 推荐用 ATTN_11DB（支持 0~3.6V）
--------------------
[属性]:
    value → 返回当前原始 ADC 值（只读，等同于 read()）
[方法]:
    read()   → 返回原始 ADC 值（整数）
    deinit() → 释放资源
--------------------
[使用示例]:
    from ldr import LDR
    from machine import ADC

    ldr = LDR(34, attenuation=ADC.ATTN_11DB)

    print("当前值:", ldr.value)   # 推荐方式
    print("当前值:", ldr.read())  # 等效方式

    # 注意：数值与光线强弱的关系取决于硬件接线
    #   • LDR 接 GND 侧 → 光线越强，value 越大
    #   • LDR 接 VCC 侧 → 光线越强，value 越小
--------------------
""")


if __name__ == "__main__":
    LDR.test()

# knob.py
from machine import ADC, Pin
import time

class Knob:
    """
    旋钮（电位器）驱动，简单好用
    支持传入引脚号（int）或已配置的 Pin 对象
    """

    def __init__(self, pin, min_val=0, max_val=100, adc_bits=12):
        # 处理 pin 参数：支持 int 或 Pin 对象
        if isinstance(pin, int):
            self.pin = Pin(pin)
        else:
            if not isinstance(pin, Pin):
                raise TypeError("pin 必须是整数或 machine.Pin 实例")
            self.pin = pin

        # 创建 ADC 对象（必须是输入引脚）
        self.adc = ADC(self.pin)

        # 配置 ADC 衰减（支持 0~3.3V），适用于 ESP32
        try:
            self.adc.atten(ADC.ATTN_11DB)
        except Exception:
            pass  # 兼容 ESP8266、RP2040 等不支持 atten 的平台

        self.min_val = min_val
        self.max_val = max_val
        self.max_adc = (1 << adc_bits) - 1  # 如 12位 -> 4095

    def read(self):
        """读取原始 ADC 值"""
        return self.adc.read()
    
    @property
    def percent(self):
        """返回百分比（保留1位小数）"""
        return round((self.read() / self.max_adc) * 100, 1)


    @property
    def value(self):  
        """返回映射到 min_val ~ max_val 的浮点值"""
        return (self.read() / self.max_adc) * (self.max_val - self.min_val) + self.min_val

    @property
    def value_int(self): 
        """返回映射到 min_val ~ max_val 的整数值"""
        return int(self.value)
    
    @classmethod
    def test(cls):
        print('【旋钮测试程序】')


        try:
            pin_num = int(input("请输入 ADC 引脚号（推荐使用GPIO32-39，如 34）: "))
        except:
            print("❌ 输入无效，默认使用 GPIO34")
            pin_num = 34

        try:
            min_val = int(input("最小映射值 (默认 0): ") or "0")
            max_val = int(input("最大映射值 (默认 100): ") or "100")
        except:
            print("❌ 输入无效，使用默认范围 0~100")
            min_val, max_val = 0, 100

        # 创建 Knob（传入 int 引脚号）
        print(f"🚩 开始测试 旋钮(GPIO{pin_num}) 功能...")
        time.sleep(1)

        print("🔧 正在初始化旋钮...")
        knob = cls(pin=pin_num, min_val=min_val, max_val=max_val)

        print(f"\n✅ 开始读取 旋钮(GPIO{pin_num}) 并映射至 {min_val}~{max_val})，按 Ctrl+C 退出...")
        print(f"\n{'原始':^6} | {'百分比':^6} | {'映射整数值':^6}")
        print("-" * 20)

        while True:
            try:
                print(f"{knob.read():^6} | {knob.percent:^6} | {knob.value_int:^6}", end='\r')
                time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n👋 退出程序")
                break
    
    @staticmethod
    def help():
        print("""
【旋钮（电位器）驱动类】
--------------------
[硬件参数]:
    - 支持 ADC 读取
    - 支持映射至自定义范围（min_val ~ max_val）
    - 支持百分比读取
--------------------
[初始化]:
    Knob(pin, min_val=0, max_val=100, adc_bits=12)
        - pin: machine.Pin 实例
        - min_val: 映射的最小值（默认 0）
        - max_val: 映射的最大值（默认 100）
        - adc_bits: ADC 分辨率位数（默认 12 位）
[属性]:
    read: 读取原始 ADC 值
    percent: 返回百分比（0~100，保留1位小数）
    value: 返回映射到 min_val ~ max_val 的浮点值
    value_int: 返回映射到 min_val ~ max_val 的整数值
--------------------
[示例]:
    knob = Knob(pin=34, min_val=0, max_val=100)  # 初始化旋钮，连接到 GPIO34，映射范围 0~100
    while True:
        print("原始 ADC 值:", knob.read())
        print("百分比:", knob.percent)
        print("映射浮点值:", knob.value)
        print("映射整数值:", knob.value_int)
        time.sleep_ms(500)
--------------------

""")


if __name__ == "__main__":
    Knob.test()

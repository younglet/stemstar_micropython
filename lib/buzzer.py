# buzzer.py

import time
from machine import Pin, PWM

class Buzzer:
    # 大调音名和对应的基准频率（C4 ~ B4）
    NOTE_FREQUENCIES = {
        'C': 261.63,   # C4
        'D': 293.66,   # D4
        'E': 329.63,   # E4
        'F': 349.23,   # F4
        'G': 392.00,   # G4
        'A': 440.00,   # A4
        'B': 493.88,   # B4
    }

    def __init__(self, pin, active_high=True, is_active_buzzer=True):
        """
        初始化蜂鸣器
        :param pin: 引脚编号（int）或 Pin 对象
        :param active_high: 高电平触发还是低电平触发，默认高电平触发
        :param is_active_buzzer: 是否是有源蜂鸣器（只需通电即可响）
        """
        self.pin = pin if isinstance(pin, Pin) else Pin(pin)
        self.pin.init(Pin.OUT)
        self.active_high = active_high
        self.is_active_buzzer = is_active_buzzer
        self.pwm_obj = None
        
        # 如果是无源蜂鸣器，启用PWM
        if not self.is_active_buzzer:
            self.pwm_obj = PWM(self.pin)
            self.pwm_obj.freq(1000)  # 默认频率1kHz
            self.pwm_obj.duty(512)   # 默认占空比50%
        
        self.off()  # 初始化默认关闭

    def on(self):
        """打开蜂鸣器"""
        if self.is_active_buzzer:
            self.pin.value(1 if self.active_high else 0)
        else:
            self.pwm_obj.duty(512)  # 启动PWM发声

    def off(self):
        """关闭蜂鸣器"""
        if self.is_active_buzzer:
            self.pin.value(0 if self.active_high else 1)
        else:
            self.pwm_obj.duty(0)

    def beep(self, times=1, duration=0.2, interval=0.1):
        """
        发出指定次数的蜂鸣声
        :param times: 响多少次
        :param duration: 每次响多久（秒）
        :param interval: 次数之间的间隔时间（秒）
        """
        for _ in range(times):
            self.on()
            time.sleep(duration)
            self.off()
            time.sleep(interval)

    def play_note(self, note='C4', duration=0.5):
        """
        根据指定的大调音名播放对应的音调
        :param note: 音名加八度，例如 'C4', 'D5' 等
        :param duration: 音调持续的时间（秒）
        """
        if note == '':
            return time.sleep(duration)
        note_name = ''.join(filter(str.isalpha, note)).upper()  # 提取音名部分
        octave = int(''.join(filter(str.isdigit, note))) if any(char.isdigit() for char in note) else 4  # 提取八度部分，默认4
        
        base_frequency = self.NOTE_FREQUENCIES.get(note_name)
        if base_frequency is None:
            print(f"⚠️ 未知的音名：{note}")
            return

        frequency = base_frequency * (2 ** (octave - 4))  # 计算对应八度的频率
        if not self.is_active_buzzer:
            self.set_tone_freq(frequency, 512)
            self.on()
            time.sleep(duration)
            self.off()
            time.sleep(0.05)  # 小段静默区分音符
        else:
            print("⚠️ 无法设置音调：当前是有源蜂鸣器")

    def set_tone_freq(self, frequency=1000, duty=512):
        """
        设置无源蜂鸣器的频率和占空比
        :param frequency: 频率（Hz）
        :param duty: 占空比（0~1023）
        """
        if not self.is_active_buzzer:
            self.pwm_obj.freq(int(frequency))
            self.pwm_obj.duty(duty)
        else:
            print("⚠️ 无法设置音调：当前是有源蜂鸣器")

    def __del__(self):
        self.deinit()

    def deinit(self):
        """释放蜂鸣器占用的资源"""
        if not self.is_active_buzzer and self.pwm_obj:
            self.off()  # 先关闭
            self.pwm_obj.deinit()  # 释放 PWM 资源
            self.pwm_obj = None
        self.pin.value(0 if self.active_high else 1)  # 确保引脚低电平

    @classmethod
    def test(cls):
        print("【无源蜂鸣器测试程序】")
        try:
            pin_num = int(input("请输入蜂鸣器的引脚号（如 4）: ") or "4")
        except:
            print("❌ 输入无效，默认使用 GPIO4")
            pin_num = 4

        try:
            buzzer_type = input("请选择蜂鸣器类型（1-有源，2-无源，默认1）: ") or "1"
        except:
            print("❌ 输入无效，默认使用有源蜂鸣器")
            buzzer_type = "1"

        is_active_buzzer = True if buzzer_type == "1" else False
        
        try:
            print(f"🚩 开始测试蜂鸣器(GPIO{pin_num})功能...")
            time.sleep(1)

            print("🔧 正在初始化蜂鸣器...")
            buzzer = cls(Pin(pin_num), is_active_buzzer=is_active_buzzer)  # 根据用户选择初始化

            print("🔊 正在发出一次短促蜂鸣")
            buzzer.beep(times=1, duration=0.3)
            time.sleep(1)

            print("🔊 正在连续蜂鸣三次")
            buzzer.beep(times=3, duration=0.2, interval=0.1)
            time.sleep(1)

            if not is_active_buzzer:

                print("🎼 正在播放一段旋律:《兰亭序》")
                melody = [
                    'G4', 'A4', 'C5', 'D5', '', '', 'C5', 'D5', 'C5', 'E5', 'D5', 'C5', '', '',
                    'C5', 'D5', 'E5', 'G5', '', '', 'E5', 'D5', 'C5', 'A4', 'G4', 'E5', '', '',
                    'E5', 'G5', 'A5', 'E5', '', '', 'D5', 'D5', 'C5', 'E5', 'D5', 'C5', '', '',
                    'A4', 'C5', 'E5', 'D5', '', '', 'C5', 'A4', 'G4', 'E5', 'D5', 'C5', '', '',
                ]
                for note in melody:
                    print(f"🎵 正在播放 {note}")
                    buzzer.play_note(note=note, duration=0.2)
                    

                print("🎉 所有测试完成！")
            else:
                print("注意：由于使用的是有源蜂鸣器，不能通过play_note方法播放不同音调")
        except KeyboardInterrupt:
            print("程序已退出")
        except Exception as e:
            print("发生错误：", e)
        finally:
            buzzer.off()
            buzzer.deinit()
            print("资源已释放")
    



if __name__ == '__main__':
    Buzzer.test()
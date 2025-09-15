# mic.py - 高性能声音传感器驱动（支持可选后台定时器 + O(1) 滑动窗口 + 自动校准）

from machine import ADC, Pin, Timer
import time
import math


class Microphone:
    """
    模拟麦克风/声音传感器驱动
    特性：
      - use_timer=True: 后台定时更新平均值，read() 极速返回
      - use_timer=False: read() 时临时采样 sample_count 次取平均
      - 使用 running_total 实现 O(1) 平均值更新（定时器模式）
      - 兼容 ESP32/ESP8266/RP2050 等平台
      - 支持自动校准环境噪声基线
    """

    def __init__(self, pin, min_val=0, max_val=100, peak_threshold=0.15, 
                adc_bits=12, sample_count=50, use_timer=True, timer_id=0, freq=50):
        """
        初始化麦克风
        :param pin: 引脚号(int) 或 Pin 对象
        :param min_val: 映射最小值
        :param max_val: 映射最大值
        :param peak_threshold: 峰值检测阈值（相对于最大ADC值的比例）
        :param adc_bits: ADC 位数（默认 12）
        :param sample_count: 采样数量（滑动窗口大小）
        :param use_timer: 是否启用后台定时器（默认 True）
        :param timer_id: 定时器 ID（建议 0~3）
        :param freq: 定时更新频率（Hz，默认 50）
        """
        # 处理 pin 参数
        if isinstance(pin, int):
            self.pin = Pin(pin)
        else:
            if not isinstance(pin, Pin):
                raise TypeError("pin 必须是整数或 machine.Pin 实例")
            self.pin = pin

        # 初始化 ADC
        self.adc = ADC(self.pin)
        try:
            self.adc.atten(ADC.ATTN_11DB)
        except Exception:
            pass  # 兼容不支持平台

        self.min_val = min_val
        self.max_val = max_val
        self.max_adc = (1 << adc_bits) - 1
        self.sample_count = max(1, sample_count)
        self.use_timer = use_timer
        self.peak_threshold = peak_threshold
        self._timer = None
        
        # 校准相关变量
        self._calibrated = False
        self._noise_floor = 0
        self._noise_std_dev = 0
        self._dynamic_threshold = self.peak_threshold

        # 核心状态变量
        self._latest_value = 0  # 最新平均值（供 read() 使用）

        if self.use_timer:
            # 定时器模式：预分配缓冲区 + running_total
            self._samples = [0] * self.sample_count
            self._running_total = 0
            self._index = 0

            # 初始读一次，填充所有样本为相同值（避免突变）
            initial = self.adc.read()
            for i in range(self.sample_count):
                self._samples[i] = initial
            self._running_total = initial * self.sample_count
            self._latest_value = initial

            # 启动定时器
            try:
                self._timer = Timer(timer_id)
                self._timer.init(
                    period=1000 // freq,
                    mode=Timer.PERIODIC,
                    callback=self._update
                )
            except Exception as e:
                raise RuntimeError(f"无法初始化定时器 {timer_id}: {e}")
        else:
            # 非定时器模式：无需维护窗口
            self._samples = None
            self._running_total = 0
            self._index = 0

    def _update(self, tim):
        """定时器回调：O(1) 更新滑动窗口平均值"""
        new_val = self.adc.read()
        old_val = self._samples[self._index]

        # 更新累计和
        self._running_total = self._running_total - old_val + new_val

        # 写入新值，移动指针
        self._samples[self._index] = new_val
        self._index = (self._index + 1) % self.sample_count

        # 更新最新平均值（O(1)，无 sum()）
        self._latest_value = self._running_total // self.sample_count

    def calibrate(self, duration=3, quiet_environment=True):
        """
        自动校准环境噪声基线
        :param duration: 校准持续时间（秒）
        :param quiet_environment: 是否在安静环境中校准（True=安静环境，False=当前环境）
        :return: 成功返回True，失败返回False
        """
        if quiet_environment:
            print("🔇 请保持环境安静，正在进行噪声校准...")
        else:
            print("🔊 正在校准当前环境噪声...")
        
        print(f"⏱️  校准时长: {duration}秒")
        
        # 临时禁用定时器（如果启用）
        timer_was_running = False
        if self.use_timer and self._timer is not None:
            self._timer.deinit()
            timer_was_running = True
        
        try:
            # 收集样本
            samples = []
            start_time = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), start_time) < duration * 1000:
                samples.append(self.adc.read())
                time.sleep_ms(10)  # 采样间隔10ms
            
            # 计算噪声基线和标准差
            self._noise_floor = sum(samples) / len(samples)
            
            # 计算标准差
            variance = sum((x - self._noise_floor) ** 2 for x in samples) / len(samples)
            self._noise_std_dev = math.sqrt(variance)
            
            # 设置动态阈值（噪声基线 + 3倍标准差）
            self._dynamic_threshold = self._noise_floor + 3 * self._noise_std_dev
            self._calibrated = True
            
            print(f"✅ 校准完成!")
            print(f"   📊 噪声基线: {self._noise_floor:.2f}")
            print(f"   📈 标准差: {self._noise_std_dev:.2f}")
            print(f"   🚦 动态阈值: {self._dynamic_threshold:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ 校准失败: {e}")
            self._calibrated = False
            return False
            
        finally:
            # 恢复定时器（如果之前是启用的）
            if timer_was_running:
                try:
                    self._timer.init(
                        period=1000 // 50,  # 默认50Hz
                        mode=Timer.PERIODIC,
                        callback=self._update
                    )
                except Exception as e:
                    print(f"⚠️ 无法恢复定时器: {e}")

    def reset_calibration(self):
        """重置校准状态，恢复使用固定阈值"""
        self._calibrated = False
        print("🔄 已重置校准状态，使用固定阈值")

    def read_raw(self):
        """读取单次原始 ADC 值"""
        return self.adc.read()

    def read(self):
        """
        返回声音强度平均值
        根据 use_timer 决定行为：
          True  -> 返回定时器维护的 _latest_value（极快）
          False -> 临时采样 sample_count 次并返回平均
        """
        if self.use_timer:
            return self._latest_value
        else:
            total = 0
            for _ in range(self.sample_count):
                total += self.adc.read()
            return total // self.sample_count

    @property
    def percent(self):
        """返回百分比（0.0 ~ 100.0）"""
        avg = self.read()
        return round((avg / self.max_adc) * 100, 1)

    @property
    def value(self):
        """映射到 min_val ~ max_val 的浮点值"""
        avg = self.read()
        return (avg / self.max_adc) * (self.max_val - self.min_val) + self.min_val

    @property
    def value_int(self):
        """映射后的整数值"""
        return int(self.value)

    def peak_detected(self):
        """
        检测是否发生显著声音脉冲
        如果已校准：使用动态阈值（噪声基线 + 3倍标准差）
        如果未校准：使用固定阈值（peak_threshold * max_adc）
        """
        current = self.read_raw()
        avg = self.read()
        
        if self._calibrated:
            # 使用校准后的动态阈值
            return (current - avg) > self._dynamic_threshold
        else:
            # 使用固定阈值
            threshold = self.max_adc * self.peak_threshold
            return (current - avg) > threshold

    @property
    def is_calibrated(self):
        """返回是否已进行校准"""
        return self._calibrated

    @property
    def noise_floor(self):
        """返回噪声基线值（仅在校准后有效）"""
        return self._noise_floor if self._calibrated else None

    @property
    def noise_std_dev(self):
        """返回噪声标准差（仅在校准后有效）"""
        return self._noise_std_dev if self._calibrated else None

    def deinit(self):
        """释放资源：关闭定时器"""
        if self._timer is not None:
            self._timer.deinit()
            self._timer = None


# ======================
#   主程序测试
# ======================

if __name__ == '__main__':
    print("🎤 声音传感器测试程序（高性能优化版 + 自动校准）")

    try:
        pin_num = int(input("请输入 ADC 引脚号（如 34）: ") or "34")
    except:
        print("❌ 输入无效，默认使用 GPIO34")
        pin_num = 34

    try:
        min_val = int(input("最小映射值 (默认 0): ") or "0")
    except:
        print("❌ 最小值输入无效，使用 0")
        min_val = 0

    try:
        max_val = int(input("最大映射值 (默认 100): ") or "100")
    except:
        print("❌ 最大值输入无效，使用 100")
        max_val = 100

    try:
        sample_count = int(input("采样数量 (默认 50): ") or "50")
    except:
        print("❌ 采样数量输入无效，使用 50")
        sample_count = 50

    use_timer_input = input("启用后台定时器? (y/n 默认 y): ").strip().lower()
    if use_timer_input in ('y', 'yes', '1', '', None, 'Yes', 'Y', 'YES'):
        use_timer = True
    elif use_timer_input in ('n', 'no', '0', 'No', 'N', 'NO'):
        use_timer = False
    else:
        print("❌ 输入无效，默认启用定时器")
        use_timer = True

    try:
        timer_id = int(input("定时器ID (默认 0): ") or "0")
    except:
        print("❌ 定时器ID无效，使用 0")
        timer_id = 0

    try:
        freq = int(input("更新频率 Hz (默认 50): ") or "50")
    except:
        print("❌ 频率输入无效，使用 50Hz")
        freq = 50

    # 创建实例
    try:
        mic = Microphone(
            pin=pin_num,
            min_val=min_val,
            max_val=max_val,
            sample_count=sample_count,
            use_timer=use_timer,
            timer_id=timer_id,
            freq=freq
        )
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("💡 提示：尝试更换 timer_id（如 1 或 2）")
        raise

    # 询问是否进行校准
    calibrate_input = input("是否进行环境噪声校准? (y/n 默认 y): ").strip().lower()
    if calibrate_input in ('y', 'yes', '1', '', None, 'Yes', 'Y', 'YES'):
        mic.calibrate(duration=3, quiet_environment=True)
    else:
        print("⏭️  跳过校准，使用固定阈值")

    print(f"\n✅ 开始监听 (GPIO{pin_num})")
    print(f"⚙️  模式: {'后台定时更新' if use_timer else '每次读取采样'}")
    print(f"⏱️  更新频率: {freq}Hz | 采样数: {sample_count}")
    print(f"📊 校准状态: {'✅ 已校准' if mic.is_calibrated else '❌ 未校准'}")
    if mic.is_calibrated:
        print(f"   📈 噪声基线: {mic.noise_floor:.2f}")
        print(f"   📊 标准差: {mic.noise_std_dev:.2f}")
    print("🔊 制造声音观察变化，按 Ctrl+C 退出...")
    print(f"\n{'原始':^8} | {'平均':^8} | {'百分比':^8} | {'映射':^6} | {'峰值':^6} | {'校准':^6}")
    print("-" * 58)

    try:
        while True:
            raw = mic.read_raw()
            avg = mic.read()
            percent = mic.percent
            value = mic.value
            peak = "✅" if mic.peak_detected() else "❌"
            calibrated = "✅" if mic.is_calibrated else "❌"

            print(f"{raw:^8} | {avg:^8} | {percent:^8} | {value:^6} | {peak:^6} | {calibrated:^6}", end='\r')
            time.sleep(0.1)
    except KeyboardInterrupt:
        mic.deinit()
        print("\n\n👋 退出程序")
    except Exception as e:
        mic.deinit()
        print(f"\n\n💥 程序异常: {e}")

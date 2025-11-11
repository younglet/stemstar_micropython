import ntptime
import time

class TimeSyncer:
    """
    使用 NTP 同步 RTC，并提供本地时间与 HTTP 时间格式。
    """

    _SECONDS_IN_4H = 4 * 3600

    def __init__(self, timezone=8):
        """
        初始化时间同步器
        
        :param timezone: 本地时区偏移（小时），默认 8（北京时间）
        """
        self.timezone = timezone
        self._last_sync_timestamp = 0  # 上次成功同步的本地时间戳（秒）

    def sync(self, timeout=5, force=False):
        """
        通过 NTP 同步时间到 RTC（设置为 UTC）
        
        :param timeout: NTP 请求超时时间（秒）
        :param force: 是否强制同步（忽略 24 小时限制）
        :return: bool - 成功返回 True，失败返回 False
        """
        if not force:
            current = time.time()
            # 如果系统时间有效（> 2020年）且未过 24 小时，则跳过
            if current > 1577836800:  # 2020-01-01 UTC
                if current - self._last_sync_timestamp < self._SECONDS_IN_4H:
                    print("✅ 距离上次同步不足 4 小时，跳过同步")
                    return True

        try:
            print(f"📡 正在通过 NTP 同步 UTC 时间（超时: {timeout}s）...")
            ntptime.timeout = timeout
            ntptime.settime()  # 设置 RTC 为 UTC
            self._last_sync_timestamp = time.time()
            print("✅ 时间同步成功")
            return True
        except OSError as e:
            print(f"❌ NTP 同步失败: {e}")
            return False

    def now(self, formatted=True):
        """
        获取本地时区时间
        
        :param formatted: 是否返回 'YYYY-MM-DD HH:MM:SS' 字符串
        :return: str 或 tuple(time.localtime 格式)
        """
        utc_tuple = time.localtime()
        utc_ts = time.mktime(utc_tuple)
        local_ts = utc_ts + self.timezone * 3600
        local_time = time.localtime(local_ts)

        if formatted:
            return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                local_time[0], local_time[1], local_time[2],
                local_time[3], local_time[4], local_time[5]
            )
        return local_time

    def http_time(self):
        """
        获取符合 HTTP/1.1 RFC 1123 标准的 UTC 时间字符串
        
        示例: 'Sun, 28 Sep 2025 03:43:00 GMT'
        
        :return: str
        """
        t = time.localtime()
        weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        return "{}, {:02d} {} {:04d} {:02d}:{:02d}:{:02d} GMT".format(
            weekday_names[t[6]],  # weekday (0=Mon)
            t[2],                 # day
            month_names[t[1] - 1],# month
            t[0],                 # year
            t[3], t[4], t[5]      # hour, min, sec
        )

    @property
    def is_synchronized(self):
        """判断是否曾成功同步过时间（基于时间有效性）"""
        return time.time() > 1577836800  # > 2020-01-01

    def status(self):
        """打印当前时间状态"""
        print(f"🕒 本地时间: {self.now()}")
        print(f"🌐 HTTP 时间: {self.http_time()}")
        print(f"✅ 已同步: {'是' if self.is_synchronized else '否'}")
    
    @classmethod
    def test(cls):
        """测试方法，执行时间同步并显示结果"""
        print("【时间同步测试程序】")
        ts = cls(timezone=8)  # 北京时间 UTC+8
        if ts.sync(force=True):
            ts.status()
        else:
            print("❌ 时间同步测试失败")
    
    @staticmethod
    def help():
        print("""
【时间同步模块 TimeSyncer 类】
--------------------------------
[功能说明]：
    使用 NTP 同步 RTC 时间，并提供本地时间和 HTTP 时间格式的获取方法。
--------------------------------
[初始化]：
    ts = TimeSyncer(timezone=8)     # 设置本地时区为 UTC+8（北京时间）
[属性]：
    ts.is_synchronized              # 返回是否已成功同步时间（布尔值）
[方法]：
    ts.sync(timeout=5, force=False) # 通过 NTP 同步时间
    ts.now(formatted=True)          # 获取本地时间，格式化字符串或 time.localtime 元组
    ts.http_time()                  # 获取符合 HTTP 标准的 UTC 时间字符串
    ts.status()                     # 打印当前时间状态
--------------------------------
[示例]：
    ts = TimeSyncer(timezone=8)
    ts.sync()
    print(ts.now())
    print(ts.http_time())
""")

if __name__ == "__main__":
    TimeSyncer.test()
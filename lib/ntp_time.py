# file: rtc_time.py
import ntptime
import time
from machine import RTC

# 记录上次成功同步的 UTC 时间戳（秒），初始为 0 表示从未同步
_last_sync_time = 0
_SECONDS_IN_24H = 24 * 3600


def sync_time(timeout=5, force=False):
    """
    同步网络时间（使用 NTP，默认设置 RTC 为 UTC 时间）

    参数:
        timeout (int): NTP 请求超时时间（秒）
        force (bool): 是否强制同步（忽略 24 小时限制）

    返回:
        bool: 成功返回 True，失败返回 False
    """
    global _last_sync_time

    if not force:
        current_time = time.time()
        # 如果系统时间看起来无效（< 2020年），也允许同步
        if current_time > 1577836800:  # 2020-01-01 UTC
            if current_time - _last_sync_time < _SECONDS_IN_24H:
                print("✅ 距离上次同步不足 24 小时，跳过同步")
                return True

    try:
        print(f"📡 正在通过 NTP 同步 UTC 时间（超时: {timeout}s）...")
        ntptime.timeout = timeout
        ntptime.settime()  # 设置 RTC 为 UTC 时间
        _last_sync_time = time.time()  # 记录本次同步时间
        print("✅ 时间同步成功")
        return True
    except OSError as e:
        print(f"❌ NTP 同步失败: {e}")
        return False


def get_local_time(hours_offset=8, formatted=True):
    """
    获取本地时区时间（如北京时间 UTC+8）

    参数:
        hours_offset (int): 与 UTC 的小时偏移量，默认 8（北京时间）
        formatted (bool): 是否返回 'YYYY-MM-DD HH:MM:SS' 格式字符串

    返回:
        str 或 tuple: 格式化字符串 或 time.localtime() 元组（基于本地时区）
    """
    utc_tuple = time.localtime()
    utc_timestamp = time.mktime(utc_tuple)
    local_timestamp = utc_timestamp + hours_offset * 3600
    local_time = time.localtime(local_timestamp)

    if formatted:
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            local_time[0], local_time[1], local_time[2],
            local_time[3], local_time[4], local_time[5]
        )
    else:
        return local_time


def get_http_time():
    """
    获取符合 HTTP 协议标准的时间字符串（RFC 1123 格式），基于 UTC 时间。

    示例: 'Sun, 28 Sep 2025 03:43:00 GMT'

    返回:
        str: HTTP 格式时间字符串（始终为 UTC）
    """
    year, month, day, hour, minute, second, weekday, _ = time.localtime()

    _DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    _MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    return "{}, {:02d} {} {:04d} {:02d}:{:02d}:{:02d} GMT".format(
        _DAY_NAMES[weekday],
        day,
        _MONTH_NAMES[month - 1],
        year,
        hour, minute, second
    )


if __name__ == "__main__":
    if sync_time():
        print(f"🌍 UTC 时间: {get_local_time(hours_offset=0)}")
        print(f"📍 北京时间: {get_local_time(hours_offset=8)}")
        print(f"🌐 HTTP 时间: {get_http_time()}")
    else:
        print("⚠️ 时间同步失败，请检查网络。")
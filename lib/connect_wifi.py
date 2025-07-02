import time
import network

def connect_wifi(ssid='stemstaroffice', password='ilovestem', timeout=10, retry=1, hostname=None):
    """
    连接指定的 Wi-Fi 网络，带超时控制和重试机制。
    
    :param ssid: Wi-Fi 名称
    :param password: Wi-Fi 密码
    :param timeout: 单次连接等待时间（秒）
    :param retry: 重试次数（默认不重试）
    :param hostname: 本地主机名
    :return: 成功返回 True，否则 False
    """
    wlan = network.WLAN(network.STA_IF)
    
    if hostname:
        network.hostname(hostname)

    if wlan.isconnected():
        print(f"✅ 已经连接到 Wi-Fi:{ssid}")
        print("📶 网络配置:", wlan.ifconfig())
        if hostname:
            print(f"🖥️ 本设备的局域网地址为：{network.hostname()}.local")
        return True

    for attempt in range(retry + 1):
        wlan.active(True)
        print(f"📡 正在尝试连接 Wi-Fi: {ssid}", end="")
        
        wlan.connect(ssid, password)

        start_time = time.time()
        while not wlan.isconnected() and (time.time() - start_time) < timeout:
            time.sleep(0.5)
            print(".", end="")

        if wlan.isconnected():
            print(f"\n🎉 成功连接到 Wi-Fi:{ssid}")
            print("📶 网络配置:", wlan.ifconfig())
            if hostname:
                print(f"🖥️ 本设备的局域网地址为：{network.hostname()}.local")
            return True
        else:
            print(f"\n❌ 第 {attempt + 1} 次连接失败：{ssid}")
            wlan.active(False)
            time.sleep(1)
            wlan.active(True)  # 准备下一次重连

    print("💔 达到最大重试次数，连接失败")
    return False

if __name__ == '__main__':
    import requests
    

    is_connected = connect_wifi(ssid='stemstaroffice', password='ilovestem')
    if is_connected:
        try:
            WEATHER_API_URL = 'https://ai.stemstar.com/api/mp/public/weather/current?city=shanghai'

            response = requests.get(WEATHER_API_URL)
            data = response.json()

            description = data.get("description", "未知")
            temp = data.get("temp", "N/A")
            humidity = data.get("humidity", "N/A")

            print(f'🌤️ 上海今日天气：{description}')
            print(f'🌡️ 温度：{temp}°C')
            print(f'💧 湿度：{humidity}%RH')

        except Exception as e:
            print(f"⚠️ 请求失败或解析错误: {e}")
    else:
        print("❌ 无法连接网络，请检查Wi-Fi设置")

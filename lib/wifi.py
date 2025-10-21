import time
import network

class Wifi:
    def __init__(self, ssid='stemstaroffice', password='ilovestem', timeout=10, retry=1, hostname=None):
        self.ssid = ssid
        self.password = password
        self.timeout = timeout
        self.retry = retry
        self.hostname = hostname

        # 网络信息属性（初始为 None）
        self.ip = None
        self.subnet = None
        self.gateway = None
        self.dns = None
        self.local_hostname = None
        self.is_connected = False

        # 初始化 WLAN 接口
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        # 设置主机名（如果提供）
        if self.hostname:
            try:
                network.hostname(self.hostname)
            except Exception:
                pass  # 某些平台可能不支持动态设置

        # 如果已经连接
        if self.wlan.isconnected():
            print(f"✅ 已经连接到 Wi-Fi: {self.ssid}")
            config = self.wlan.ifconfig()
            print("📶 网络配置:", config)
            if self.hostname:
                print(f"🖥️ 本设备的局域网地址为：{network.hostname()}.local")
            # 更新属性
            self._set_network_attributes(config)
            self.is_connected = True
            return True

        # 开始连接尝试
        for attempt in range(self.retry + 1):
            self.wlan.active(True)
            print(f"📡 正在尝试连接 Wi-Fi: {self.ssid}", end="")

            self.wlan.connect(self.ssid, self.password)

            start_time = time.time()
            while not self.wlan.isconnected() and (time.time() - start_time) < self.timeout:
                time.sleep(0.5)
                print(".", end="")

            if self.wlan.isconnected():
                print(f"\n🎉 成功连接到 Wi-Fi: {self.ssid}")
                config = self.wlan.ifconfig()
                print("📶 网络配置:", config)
                if self.hostname:
                    host = network.hostname()
                    print(f"🖥️ 本设备的局域网地址为：{host}.local")
                    self.local_hostname = f"{host}.local"
                # 更新属性
                self._set_network_attributes(config)
                self.is_connected = True
                return True
            else:
                print(f"\n❌ 第 {attempt + 1} 次连接失败：{self.ssid}")
                self.wlan.active(False)
                time.sleep(1)

        print("💔 达到最大重试次数，连接失败")
        self.is_connected = False
        return False

    def _set_network_attributes(self, config):
        """从 ifconfig 元组中提取并设置属性"""
        self.ip = config[0]
        self.subnet = config[1]
        self.gateway = config[2]
        self.dns = config[3]
        # local_hostname 已在 connect 中设置（如果 hostname 存在）
    def disconnect(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()
            print(f"🔌 已断开 Wi-Fi: {self.ssid}")
        else:
            print("ℹ️ 当前未连接任何 Wi-Fi 网络")
        self.is_connected = False
    
    @classmethod
    def scan(cls):
        print("🔍 扫描可用的 Wi-Fi 网络...")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        networks = wlan.scan()
        networks.sort(key=lambda x: x[3], reverse=True)  # 按信号强度排序
        # ssid去重
        seen_ssids = []
        for net in networks:
            ssid, bssid, channel, rssi, authmode, hidden = net[0], net[1], net[2], net[3], net[4], net[5]
            ssid = ssid.decode('utf-8') if isinstance(ssid, bytes) else ssid
            bssid = ':'.join(f'{b:02x}' for b in bssid)  # '90:16:ba:38:10:e8'
            mode = {
                0: "开放",
                1: "WEP",
                2: "WPA-PSK",
                3: "WPA2-PSK",
                4: "WPA/WPA2-PSK"
            }.get(authmode, "未知")
            if ssid in seen_ssids:
                continue
            print(f"[📶 {rssi:<2} dBm] SSID: {ssid:<33} ")
            seen_ssids.append(ssid)
        wlan.active(False) 
        return networks
    
    @classmethod
    def test(cls):
        print("【Wi-Fi 连接测试程序】")
        networks = cls.scan()
        print("\n可用的 Wi-Fi 网络扫描完成。\n")
        
        ssid = input("请输入 Wi-Fi 名称 (SSID): ").strip()
        password = input("请输入 Wi-Fi 密码: ").strip()
        timeout_str = input("请输入连接超时时间（秒，默认10）: ").strip()
        retry_str = input("请输入重试次数（默认1）: ").strip()
        hostname = input("请输入本地主机名（可选）: ").strip() or None

        timeout = int(timeout_str) if timeout_str.isdigit() else 10
        retry = int(retry_str) if retry_str.isdigit() else 1

        wifi = cls(ssid=ssid, password=password, timeout=timeout, retry=retry, hostname=hostname)
        connected = wifi.connect()
        if connected:
            print("✅ Wi-Fi 连接测试成功！")
            print(f"📶 IP 地址: {wifi.ip}")
            print(f"📶 子网掩码: {wifi.subnet}")
            print(f"📶 网关: {wifi.gateway}")
            print(f"📶 DNS 服务器: {wifi.dns}")
            if wifi.local_hostname:
                print(f"🖥️ 本地主机名: {wifi.local_hostname}")
        else:
            print("❌ Wi-Fi 连接测试失败！请检查 SSID 和密码是否正确。")
    
    @staticmethod
    def help():
        print("""
【Wi-Fi 连接类 Wifi】
--------------------
[功能]:
    - 连接指定的 Wi-Fi 网络，带超时控制和重试机制
    - 支持设置本地主机名
    - 提供网络信息属性（IP、子网掩码、网关、DNS、本地主机名）
    - 扫描可用的 Wi-Fi 网络列表
    - 默认连接到斯坦星球办公网络: stemstaroffice

--------------------
[创建实例]:
    wifi = Wifi(ssid='your_ssid', password='your_password', timeout=10, retry=1, hostname='mydevice')
    # ssid: Wi-Fi 名称
    # password: Wi-Fi 密码, 如果是开放网络则为空字符串
    # timeout: 单次连接等待时间（秒）
    # retry: 重试次数（默认不重试）
    # hostname: 本地主机名（可选）
[属性]:
    - ip: 获取分配的 IP 地址
    - subnet: 获取子网掩码
    - gateway: 获取网关地址
    - dns: 获取 DNS 服务器地址
    - local_hostname: 获取本地主机名（如果设置了 hostname）
    - is_connected: 当前是否已连接到 Wi-Fi 网络（布尔值）

[方法]:
    - connect(): 连接到指定的 Wi-Fi 网络，返回 True/False 表示连接成功与否
    - disconnect(): 断开当前的 Wi-Fi 连接
    - scan(): 扫描并打印可用的 Wi-Fi 网络列表，返回网络列表
--------------------
[使用示例]:
    from wifi import Wifi

    wifi = Wifi(ssid='your_ssid', password='your_password')
    success = wifi.connect()
--------------------
""")


if __name__ == '__main__':
    Wifi.test()
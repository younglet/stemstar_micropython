import requests
from connect_wifi import connect_wifi

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

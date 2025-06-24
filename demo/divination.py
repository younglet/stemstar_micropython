from machine import  Pin, I2C
from ssd1306 import SSD1306_I2C
import  random
import time

i2c = I2C(1)
screen = SSD1306_I2C(128, 64, i2c)
screen.poweron()

button  = Pin(2, Pin.IN)

def yin(idx):
    x = idx * 16 + 24
    screen.fill_rect(x, 12, 4, 12, 1)
    screen.fill_rect(x, 24, 4, 12, 0)
    screen.fill_rect(x, 36, 4, 12, 1)
    screen.show()
    
def yang(idx):
    x = idx * 16 +24
    screen.fill_rect(x, 12, 4, 36, 1)
    screen.show()

def roll(idx, num):
    if num % 2:
        yang(idx)
    else:
        yin(idx)
 

for i in range(8):
    for idx in range(6):
        if random.randint(1, 64)%2:
            yin(idx)
        else:
            yang(idx)
    time.sleep(0.5)
screen.fill(0)
screen.show()


import requests
import network

wlan = network.WLAN(network.STA_IF)  # 创建WLAN对象并设置为station模式
wlan.active(True)  # 激活网络接口
ssid = 'stemstaroffice'
password = 'ilovestem'
wlan.connect(ssid, password)
while not wlan.isconnected():
    pass

print('赛博算命启动成功，请集中精力，默想所占之事, 点击按钮起爻六次：')
    
res = []
for idx in range(6):
    while not button.value():
        pass
    while button.value():
        pass
    current = 63 + random.randint(0, 1)
    res.append(current%2)
    for i in range(current):
        roll(idx, i)
        time.sleep(0.001)


print(f'卦象为：'+'、'.join(['阴' if r==1 else '阳' for r in res]))
res = ['yin' if r==1 else 'yang' for r in res]

def divination(res):
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": "Bearer sk-9c7380369ed8496490c93942cfcdf2ad",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": 'Help me interpret the hexagrams according to the original principles of Yijing. \
               and reply in Chinese within 200~300 characters.No MarkDown!' + str(res) }
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()['choices'][0]['message']['content']

print('正在为您解卦，请耐心等候...')


result = divination(res)
print('\n\n')
for c in result:
    print(c, end='')
    time.sleep(0.04)

from machine import Pin,RTC
from led import LED
from time import ticks_ms, sleep_ms


import dht

led = LED(Pin(2))
dht = dht.DHT11(Pin(4))
rtc = RTC()

duration = 1000 * 60 * 60 * 24  #总共持续24小时
interval = 1000 * 60 # 每次间隔1分钟

def get_data():
    dht.measure()
    led.blink(3, 200) # 闪烁3次,相当于延迟1200ms
    temperature = dht.temperature()
    humidity = dht.humidity()
    return temperature, humidity


with open('log.csv', 'w') as log:
    sleep_ms(interval)
    log.write('time,temperature,humidity\n')
    start_time  = ticks_ms()
    while ticks_ms()-start_time < duration:
        year, month, day, _, hour, minute, second, _ = rtc.datetime()
        now =  f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
        temperature, humidity = get_data()
        log.write(f'{now},{temperature},{humidity}\n')
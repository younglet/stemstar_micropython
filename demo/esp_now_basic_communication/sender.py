import network
import espnow
import time

from machine import Pin
from led import LED

led = LED(Pin(2))
led.blink()

sta = network.WLAN(network.WLAN.IF_STA)
sta.active(True)
print("我的MAC地址是：", sta.config('mac'))

e = espnow.ESPNow()
e.active(True)
peer_mac = b'\xd0\xefv\xee\xfb\xe8'
e.add_peer(peer_mac)


while True:
    e.send(peer_mac, "Hello from B")
    led.blink(3, 100)
    time.sleep(2)

import network
import espnow
import time

from machine import Pin
from led import LED
from button  import Button

led = LED(Pin(2))
button = Button(Pin(4))

sta = network.WLAN(network.WLAN.IF_STA)
sta.active(True)
print("我的MAC地址是：", sta.config('mac'))

e = espnow.ESPNow()
e.active(True)
peer_mac = b'\xd0\xefv\xef\x08\x98'
e.add_peer(peer_mac)


while True:
    if button.is_pressed():
        try:
            e.send(peer_mac, "1")
        except:
            print('e')
        
        time.sleep_ms(20)
        led.on()
    else:
        led.off()
        


from machine import Pin
import time 



led = Pin(2, Pin.OUT)


def fast_on_off(on_duration=10, off_duration=10):
    led.on()
    time.sleep_ms(on_duration)
    pin.off()
    led.sleep_ms(off_duration)
    
    
while True:
    pin.fast_on_off(20, 50)

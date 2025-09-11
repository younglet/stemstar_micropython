import machine
import time 


high_level_duration = 512
low_level_duration = 1024 - high_level_duration


pwm_pin = machine.Pin(2, machine.Pin.OUT)

while True:
    pwm_pin.on()
    time.sleep_us(high_level_duration)
    pwm_pin.off()
    time.sleep_us(low_level_duration)
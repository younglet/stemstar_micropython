from neopixel import NeoPixel
from machine import Pin
from time import sleep
from colors import *

# 引脚接线说明
# 灯带数据控制线  -> GPIO14


strip = NeoPixel(Pin(14), 30)



# 跑马灯测试
for i in range(0, 30, 1):
    strip.fill(BLACK)
    strip[i] = RED
    strip.write()
    sleep(0.05)
    
for i in range(29, -1, -1):
    strip.fill(BLACK)
    strip[i] = RED
    strip.write()
    sleep(0.05)
    
    
    
# 颜色闪烁测试
for color in RAINBOW:
    strip.fill(color)
    strip.write()
    sleep(0.2)
    
    strip.fill(BLACK)
    strip.write()
    sleep(0.2)



# 呼吸灯测试
for i in range(2):
    for _ in range(0, 255, 1):
        strip.fill([_]*3)
        strip.write()
    for _ in range(255, 0, -1):
        strip.fill([_]*3)
        strip.write()

strip.fill(BLACK)
strip.write()




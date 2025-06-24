import time

from machine import Pin, I2C
from morse_code import morse_code_dict
from buzzer import Buzzer
from button import Button
from ssd1306 import SSD1306_I2C

DIT_DURATION = 150
DAH_DURATION = 500
TIMEOUT = 550


buzzer = Buzzer(Pin(4, Pin.OUT), is_active_buzzer=False)
button = Button(Pin(2))
screen = SSD1306_I2C(128, 64, I2C(1))
screen.poweron()

def decode_morse(signals):
    return morse_code_dict.get(signals, False)

def update_screen(inputs):
    screen.fill(0)
    for i,c in enumerate(inputs):
        x = i%16*8 + 2
        y = i//16*10
        screen.text(c, x, y)
    screen.show()


start_flag = False
start_time = rest_time = time.ticks_ms()
signals, inputs = '', ''


while True:
    current_time = time.ticks_ms()
    if button.is_pressed():
        buzzer.on()
        
        if not start_flag:
            start_flag = True
            start_time = current_time
    else:
        buzzer.off()
        
        if start_flag:
            start_flag = False
            rest_time = current_time
            duration = current_time - start_time
            if duration < DIT_DURATION:
                signals += '.'
            elif duration < DAH_DURATION:
                signals += '-'
            else:
                signals, inputs = '', ''
                update_screen(inputs)
                

        if current_time-rest_time > TIMEOUT:
            if decode_morse(signals):
                inputs += decode_morse(signals)
                update_screen(inputs)
            signals = ''

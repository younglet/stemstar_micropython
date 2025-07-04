from microdot import Microdot, send_file
from ssd1306 import SSD1306_I2C
from machine import Pin, SoftI2C, Timer
from snake import Snake


i2c = SoftI2C(scl=Pin(20), sda=Pin(21), freq=100000)
screen = SSD1306_I2C(128, 64, i2c)

snake = Snake(screen)

def update(timer):
    snake.update()

Timer(0).init(period=300, mode=Timer.PERIODIC, callback=update)

app = Microdot()

@app.get('/')
async def index(request):
    return send_file('/static/index.html', max_age=3600)

@app.get('/left')
async def index(request): 
    snake.left()
    return 'turned left'

@app.get('/right')
async def index(request): 
    snake.right()
    return 'turned right'

@app.get('/reset')
async def index(request):
    global snake
    snake = Snake(screen)
    return 'reseted'



app.run(port=80)
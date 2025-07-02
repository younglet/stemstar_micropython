from microdot import Microdot, send_file
from machine import Pin
from neopixel import NeoPixel


strip = NeoPixel(Pin(20), 30)
app = Microdot()


@app.get('/')
async def index(request):
    return send_file('/static/index.html', max_age=3600)

@app.get('/on')
async def index(request):
    strip.fill([255, 255, 255])
    strip.write()
    return 'turned on'

@app.get('/off')
async def index(request):
    strip.fill([0, 0, 0])
    strip.write()
    return  'turned off'

@app.post('/strip/color')
async def set_color(request):
    data = request.json
    color = [data['r'], data['g'], data['b']]
    strip.fill(color)
    strip.write()
    return 'test'

app.run(port=80)

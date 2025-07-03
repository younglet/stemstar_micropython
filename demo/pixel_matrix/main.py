from microdot import Microdot, send_file
from machine import Pin
from pixel_matrix import PixelMatrix


screen = PixcelMatrix(Pin(4), Pin(17), Pin(12), Pin(14))
app = Microdot()


@app.get('/')
async def index(request):
    return send_file('/static/index.html', max_age=3600)

@app.post('/bitmap/set')
async def index(request):
    screen.set_bitmap(request.json)
    return 'ok'
    

app.run(port=80)
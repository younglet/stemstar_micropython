from neopixel import NeoPixel
from machine import Pin
from time import sleep
from colors import *

class PixelMatrix:
    def __init__(self, pin1, pin2, pin3, pin4):
        self.matrixes = [
            NeoPixel(pin1, 64),
            NeoPixel(pin2, 64),
            NeoPixel(pin3, 64),
            NeoPixel(pin4, 64)
        ]

    def get_pixel_idx(self, x, y):
        # 计算该像素所在的 8x8 块的行列索引
        block_col = x // 8   # 列方向块索引（对应原 idx_x）
        block_row = y // 8   # 行方向块索引（对应原 idx_y）

        # 计算该像素在块内的局部坐标
        local_x = x % 8
        local_y = y % 8
        
        # 计算灯板的索引
        matrix_idx = block_row * 2 + block_col

        # 像素在这块中的线性索引（0~63）
        pixel_idx = local_y * 8 + local_x

        return matrix_idx, pixel_idx

    def fill(self, color):
        for matrix in self.matrixes:
            matrix.fill(color)
            matrix.write()
            
    def set_pixel_color(self, x, y, color):
        matrix_idx, pixel_idx = self.get_pixel_idx(x, y)
        self.matrixes[matrix_idx][pixel_idx] = color
        self.matrixes[matrix_idx].write()  # 刷新当前矩阵显示
        
    def set_bitmap(self, bitmap):
        self.fill(BLACK)
        for y, row in enumerate(bitmap):
            for x, color in enumerate(row):
                self.set_pixel_color(x, y, color)
                
        
        
    


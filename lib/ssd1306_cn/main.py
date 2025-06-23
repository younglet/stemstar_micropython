from micropython import const
import framebuf


# 中文支持
DEFUALT_BITMAP = 'FFF801801801801801801801801801801FFF' # 没有位图使用的默认位图
SPECIAL_BITMAPS = { # 常用的中文标点
    65292: "000000000000000000000000300300100200",
    65307: "000000000300300000000000300300100200",
    65306: "000000000300300000000000000300300000",
    65311: "000000700880880080100200200000200000",
    65281: "000000200700700700200200200000200000",
    65288: "000004008008010010010010010008008004",
    65289: "000400200200100100100100100200200400",
    65291: "0000000000400400403F8040040040000000",
    65293: "0000000000000000003F8000000000000000",
    65309: "0000000000000003F80003F8000000000000"
}

# register definitions
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_IREF_SELECT = const(0xAD)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)


# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()
        
        self.PRELOAD_BITMAPS = {} # 存储预渲染的bitmap

    def init_display(self):
        for cmd in (
            SET_DISP,  # display off
            # address setting
            SET_MEM_ADDR,
            0x00,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE,  # start at line 0
            SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc
            # display
            SET_CONTRAST,
            0xFF,  # maximum
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            SET_IREF_SELECT,
            0x30,  # enable internal IREF during display on
            # charge pump
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,  # display on
        ):  # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)
    
    def convert_raw_bitmap_to_framebuffer(self, raw_bitmap, width):
        data = bytearray((int(bit) for bit in  f'{int("0x"+raw_bitmap, 16):0>72b}'))
        return framebuf.FrameBuffer(data, width, 12, framebuf.MONO_HLSB)

    
    def preload(self, text):
        
        self.PRELOAD_BITMAPS = {ord(c): DEFUALT_BITMAP for c in set(text)}  # 为每个字符准备一个默认的bitmap
        
        total_count = len(set(text)) # 需要匹配bitmap的字符数量
        found_count = 0 # 已经匹配的bitmap数量

        with open('lib/ssd1306_cn/chinese.font','r') as f: # 从字库文件中匹配字符的bitmap
            for idx, line in enumerate(f):
                if idx in self.PRELOAD_BITMAPS and line != '\n':
                    self.PRELOAD_BITMAPS[idx] = line.strip('\n')
                    found_count += 1
                    if found_count>=total_count:  # 检查是否找到所有字符并提前跳出循环
                        break
                    
    def clear_loaded_bitmaps(self):
        self.PRELOAD_BITMAPS = {}
                 
    def text(self, text, x0, y0, color):
        text_dict = {ord(c): DEFUALT_BITMAP for c in set(text)}
        
        found_count = 0
        total_count = len(set(text))
        
        for key, value in text_dict.items():
            if key in SPECIAL_BITMAPS :
                text_dict[key] = SPECIAL_BITMAPS [key]
                found_count += 1
                if found_count>=total_count:
                        break
            if key in self.PRELOAD_BITMAPS :
                text_dict[key] = self.PRELOAD_BITMAPS [key]
                found_count += 1
                if found_count>=total_count:
                        break
            
        if found_count<total_count:      
            with open('lib/ssd1306_cn/chinese.font','r') as f:
                for idx, line in enumerate(f):
                    if idx in text_dict and line != '\n':
                        text_dict[idx] = line.strip('\n')
                        found_count += 1
                        if found_count>=total_count:
                            break
        for char in text:
            raw_bitmap = text_dict[ord(char)]
            width = 12 if len(raw_bitmap)>18 else 6
            bitmap_in_10 = int('0x'+text_dict[ord(char)], 16)
            bits = f'{bitmap_in_10:0>72b}' if width==6 else f'{bitmap_in_10:0>144b}'
            for i, bit in enumerate(bits):
                if bit == '0':
                    continue
                y = i//width
                x = i% width
                self.pixel(x0+x, y0+y, color)
            x0 += width
            if x0 >= self.width:
                break

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def rotate(self, rotate):
        self.write_cmd(SET_COM_OUT_DIR | ((rotate & 1) << 3))
        self.write_cmd(SET_SEG_REMAP | (rotate & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width != 128:
            # narrow displays use centred columns
            col_offset = (128 - self.width) // 2
            x0 += col_offset
            x1 += col_offset
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)


class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        import time

        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)


if __name__ == "__main__":
    from machine import I2C, Pin
    from time import sleep
    print('''
──────────────────────────────────────────────
【屏幕】  ->  I2C0 (SCL: GPIO18; SDA: GPIO19)
──────────────────────────────────────────────
【请按照如上接线说明进行接线后回车继续】：''')

    input()  # 等待用户确认接线完成并回车继续

  

    

    try:
        print("🔧 正在初始化 OLED 屏幕...")
        i2c = I2C(0)  # 使用 I2C 总线 0
        screen = SSD1306_I2C(128, 64, i2c)
        screen.poweron()
        print("📌 开始执行屏幕测试...")
        # 测试 1：点亮所有像素
        print("点亮全屏白色...")
        screen.fill(1)
        screen.show()
        sleep(2)

        # 测试 2：关闭所有像素
        print("关闭全屏（清屏）")
        screen.fill(0)
        screen.show()
        sleep(1)

        # 测试 3：显示文字
        print("显示文字测试")
        screen.text("Hello!", 0, 0, 1)
        screen.text("OLED Display", 0, 16, 1)
        screen.text("Resolution:", 0, 32, 1)
        screen.text("128x64", 0, 48, 1)
        screen.show()
        sleep(3)

        # 测试 4：清屏并结束
        print("测试完成，正在清屏...")
        screen.fill(0)
        screen.show()
        print("🎉 所有测试完成！")
    except KeyboardInterrupt:
        print("\n👋 您按下了 Ctrl+C，程序即将退出...")
        
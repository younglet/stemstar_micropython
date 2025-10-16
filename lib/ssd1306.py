# MicroPython SSD1306 OLED driver, I2C and SPI interfaces

from micropython import const
import framebuf
import time


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

    @classmethod
    def test(cls, screen):
       
        screen.poweron()
        print("📌 开始执行屏幕测试...")
        # 测试 1：点亮所有像素
        print("点亮全屏白色...")
        screen.fill(1)
        screen.show()
        time.sleep(2)

        # 测试 2：关闭所有像素
        print("关闭全屏（清屏）")
        screen.fill(0)
        screen.show()
        time.sleep(1)

        # 测试 3：显示文字
        print("显示文字测试")
        screen.text("Hello, STEMSTAR!", 0, 0, 1)
        screen.text("OLED Display", 0, 16, 1)
        screen.text("Resolution:", 0, 32, 1)
        screen.text("128x64", 0, 48, 1)
        screen.show()
        time.sleep(3)

        # 测试 4：清屏并结束
        print("测试完成，正在清屏...")
        screen.fill(0)
        screen.show()
        print("🎉 所有测试完成！")

            





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
    
    @classmethod
    def test(cls):
        print('【SSD1306_I2C OLED 屏幕测试程序】')
        from machine import I2C, Pin
        import time
        
        try:
            sda_num = int(input("请输入 SSD1306 SCL 引脚连接的GPIO(建议连接至GPIO21): ") or "21")
        except:
            print("❌ 输入无效，默认使用 GPIO21")
            sda_num = 21
    
        try:
            scl_num = int(input("请输入 SSD1306 SDL 引脚连接的GPIO(建议连接至GPIO22): ") or "22")
        except:
            print("❌ 输入无效，默认使用 GPIO22")
            scl_num = 22


        try:
            print(f"🚩 开始 SSD1306 OLED(SCL:GPIO{scl_num}, SDA:GPIO{sda_num}) 屏幕测试...")
            time.sleep(1)

            print("🔧 正在初始化 OLED 屏幕...")
            i2c = I2C(1, scl=Pin(scl_num), sda=Pin(sda_num), freq=115200)
            screen = cls(128, 64, i2c)
            SSD1306.test(screen)
        except Exception as e:
            print("发生错误：", e)


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
    
    @classmethod
    def test(cls):
        print('【SSD1306_SPI OLED 屏幕测试程序】(该方法还没验证通过，请谨慎使用)')
        from machine import Pin, SPI
        import time

        try:
            sck_num = int(input("请输入 SSD1306 SCK 引脚连接的GPIO(建议连接至GPIO18): ") or "18")
        except:
            print("❌ 输入无效，默认使用 GPIO18")
            sck_num = 18

        try:
            mosi_num = int(input("请输入 SSD1306 MOSI 引脚连接的GPIO(建议连接至GPIO23): ") or "23")
        except:
            print("❌ 输入无效，默认使用 GPIO23")
            mosi_num = 23

        try:
            dc_num = int(input("请输入 SSD1306 DC 引脚连接的GPIO(建议连接至GPIO16): ") or "16")
        except:
            print("❌ 输入无效，默认使用 GPIO16")
            dc_num = 16

        try:
            res_num = int(input("请输入 SSD1306 RES 引脚连接的GPIO(建议连接至GPIO17): ") or "17")
        except:
            print("❌ 输入无效，默认使用 GPIO17")
            res_num = 17

        try:
            cs_num = int(input("请输入 SSD1306 CS 引脚连接的GPIO(建议连接至GPIO5): ") or "5")
        except:
            print("❌ 输入无效，默认使用 GPIO5")
            cs_num = 5

        try:
            print(f"🚩 开始 SSD1306 OLED(SCK:GPIO{sck_num}, MOSI:GPIO{mosi_num}, DC:GPIO{dc_num}, RES:GPIO{res_num}, CS:GPIO{cs_num}) 屏幕测试...")
            time.sleep(1)

            print("🔧 正在初始化 OLED 屏幕...")
            spi = SPI(2, baudrate=10000000, polarity=0, phase=0, sck=Pin(sck_num), mosi=Pin(mosi_num))
            dc = Pin(dc_num)
            res = Pin(res_num)
            cs = Pin(cs_num)
            screen = cls(128, 64, spi, dc, res, cs)
            SSD1306.test(screen)
        except Exception as e:
            print("发生错误：", e)


if __name__ == '__main__':
    SSD1306_I2C.test()

import serial
import time
import turtle


# 海龟画图配置
screen = turtle.Screen()                               # 创建画布
screen.setup(width=800, height=600, bgcolor='black')   # 设置画布大小和背景色
turtle.speed(0)                                        # 画笔速度最快
turtle.pensize(5)                                      # 画笔粗细

def emit_line(angle, distance, scale=10):
    """
    根据当前角度和距离画出线段，空旷区域为蓝色线段，红色线段为障碍物
    :param angle: 线段的角度
    :param distance: 线段的距离
    """
    if angle == 10:                 #  如果当前角度为10度，则清空画布
        turtle.clear()    
    
    turtle.penup()                  # 画笔抬起
    turtle.goto(0, -300)            # 画笔移动到画布底部中心
    turtle.setheading(angle)        # 画笔朝向当前角度

    turtle.pendown()                # 画笔落下
    turtle.pencolor('green')        # 画笔颜色为蓝色
    turtle.forward(distance*scale)  # 画笔向前移动，线段长度为距离*缩放比例
    turtle.pencolor('red')          # 画笔颜色为红色
    turtle.forward(1000)            # 确保线段能铺满画布


# 配置串口参数
SERIAL_PORT = '/dev/cu.wchusbserial14220'      # 根据实际情况修改为你的串口号   
BAUD_RATE = 115200                             # 波特率，固定为115200
TIMEOUT = 1                                    # 读超时设置，单位秒

# 打开串口，如果打不开此步会运行报错，请检查串口参数
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
print(f"已连接到 {SERIAL_PORT} @ {BAUD_RATE} baud")

while True:
    if ser.in_waiting > 0:                    # 如果有数据可读
        data = ser.readline().decode('utf-8') # 读取一行数据（以 \n 结尾）
        print(data)                           # 输出接受的数据
        data = data.split(' ')                # 利用空格分割数据
        angle = float(data[1])                # 获取当前角度
        distance = float(data[3])             # 获取当前距离
        emit_line(angle, distance)            # 画线
    else:
        time.sleep(0.1)                       # 暂停0.1秒后继续循环
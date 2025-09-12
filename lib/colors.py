# colors.py
import random


def _check_qualified_colors(colors):
    if not isinstance(colors, list):
        raise ValueError("colors 参数必须是一个列表")
    if not colors:
        raise ValueError("colors 列表不能为空")
    for color in colors:
        _check_qualified_color(color)
    return True

def _check_qualified_color(color):
    if not isinstance(color, (tuple, list)) or len(color) != 3:
        raise ValueError("颜色必须是一个 (r, g, b) 元组或列表")
    if not all(isinstance(comp, int) and 0 <= comp <= 255 for comp in color):
        raise ValueError("颜色分量必须是整数且在 0~255 范围内")
    return True

WHITE = 255, 255, 255    # 白色
BLACK = 0, 0, 0          # 黑色
GRAY = 128, 128, 128     # 灰色
GREY = GRAY              # 英式拼写别名
RED = 255, 0, 0          # 红色
ORANGE = 255, 165, 0     # 橙色
YELLOW = 255, 255, 0     # 黄色
GREEN = 0, 255, 0        # 绿色
CYAN = 0, 255, 255       # 青色
BLUE = 0, 0, 255         # 蓝色
PURPLE = 128, 0, 128     # 紫色
PINK = 255, 105, 180     # 柔和粉
MAGENTA = 255, 0, 255    # 品红色
LIME = 50, 205, 50        # 酸橙色      
TEAL = 0, 128, 128       # 水鸭色 
INDIGO = 99, 102, 241    # 靛蓝色
VIOLET = 139, 92, 246    # 紫罗兰色
FUCHSIA = 236, 72, 153   # 芙蓉色
ROSE =  244, 63, 94      # 玫瑰红
BROWN = 139, 69, 19      # 棕色
MAROON = 128, 0, 0       # 栗色
NAVY = 0, 0, 128         # 海军蓝
OLIVE = 128, 128, 0      # 橄榄色


# 包含所有颜色变量的列表
COLORS = [
    WHITE, BLACK, GRAY, RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE,
    PINK, MAGENTA, LIME, TEAL, INDIGO, VIOLET, FUCHSIA, ROSE, BROWN, MAROON, NAVY, OLIVE
]

# 彩虹颜色
RAINBOW = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE]

# 冷到暖渐变（适合音量条等）
VOLUME_BAR = [BLUE, CYAN, TEAL, GREEN, LIME, YELLOW, ORANGE, RED]


def is_qualified_color(color):
    """
    检查输入是否为合法的颜色格式 (r, g, b)，各分量范围 0~255。
    
    :param color: 输入颜色，期望格式为 (r, g, b)
    :return: 如果是合法颜色返回 True，否则抛出 ValueError
    """
    try:
        _check_qualified_color(color)
        return True
    except:
        return False


def generate_random_color():
    """返回一个随机的内置颜色"""
    return random.choice(COLORS)


def generate_random_rgb(min_val=0, max_val=255):
    """返回一个随机的 RGB 颜色"""
    return random.randint(min_val, max_val), random.randint(min_val, max_val), random.randint(min_val, 255)



def generate_gradient_colors(start_color, end_color, steps, mid_color=None):
    """
    生成从 start_color 到 end_color 的渐变颜色列表。
    可选：经过一个中间颜色 mid_color（用于创建非线性过渡效果）

    :param start_color: 起始颜色，格式为 (r, g, b)，各分量范围 0~255
    :param end_color: 结束颜色，格式为 (r, g, b)，各分量范围 0~255
    :param steps: 生成的颜色总数，必须为正整数
    :param mid_color: 可选的中间颜色，格式为 (r, g, b)。若提供，则渐变为 start → mid → end 的两段式过渡
    :return: 包含 RGB 元组或列表的列表，长度为 steps，每项为 (r, g, b)
    """
    if not isinstance(steps, int) or steps < 1:
        raise ValueError("steps 参数必须是正整数")
    
    colors = [start_color, end_color] + ([mid_color] if mid_color else [])

    _check_qualified_colors(colors)

    if steps == 1:
        return [start_color]
    if steps == 2:
        return [start_color, end_color]

    # 如果没有中点，直接线性插值
    if mid_color is None:
        gradient = []
        for i in range(steps):
            factor = i / (steps - 1)
            r = int(start_color[0] + (end_color[0] - start_color[0]) * factor)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * factor)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * factor)
            gradient.append((r, g, b))
        return gradient


    steps_first = (steps + 1) // 2  # 向上取整，确保至少1步
    steps_second = steps - steps_first

    gradient = []

    # 第一段：start 到 mid_color
    for i in range(steps_first):
        factor = i / max(1, steps_first - 1)
        r = int(start_color[0] + (mid_color[0] - start_color[0]) * factor)
        g = int(start_color[1] + (mid_color[1] - start_color[1]) * factor)
        b = int(start_color[2] + (mid_color[2] - start_color[2]) * factor)
        gradient.append((r, g, b))

    # 第二段：mid_color 到 end_color
    for i in range(steps_second):
        factor = i / max(1, steps_second - 1)
        r = int(mid_color[0] + (end_color[0] - mid_color[0]) * factor)
        g = int(mid_color[1] + (end_color[1] - mid_color[1]) * factor)
        b = int(mid_color[2] + (end_color[2] - mid_color[2]) * factor)
        gradient.append((r, g, b))

    return gradient


def generate_rainbow_colors(n):
    """
    生成长度为 n 的彩虹颜色序列。
    使用 RAINBOW 中的颜色作为关键点，通过插值生成平滑过渡的渐变。

    :param n: 期望的颜色数量（非负整数）
    :return: 包含 RGB 元组或列表的列表，长度为 n
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("n 参数必须是非负整数")
    if n <= 0:
        return []
    if n == 1:
        return [RED]

    # 如果只有 1 个灯，返回红色；否则生成渐变
    num_rainbow = len(RAINBOW)
    
    # 总共需要 n 个颜色，分布在 RAINBOW 的 (num_rainbow - 1) 个区间中
    colors = []
    for i in range(n):
        # 将 i 映射到 RAINBOW 颜色索引的浮点位置
        ratio = (i / max(1, n - 1)) * (num_rainbow - 1)
        idx = int(ratio)  # 当前区间起始索引
        frac = ratio - idx  # 插值比例

        # 边界保护
        idx = min(idx, num_rainbow - 2)

        # 使用 gradient_colors 在相邻两个彩虹色之间插值（只生成1个颜色）
        interpolated = generate_gradient_colors(RAINBOW[idx], RAINBOW[idx + 1], steps=2, mid_color=None)
        # 取第一个颜色（frac=0 ~ 1，我们用 frac 控制）
        c1 = RAINBOW[idx]
        c2 = RAINBOW[idx + 1]
        r = int(c1[0] + (c2[0] - c1[0]) * frac)
        g = int(c1[1] + (c2[1] - c1[1]) * frac)
        b = int(c1[2] + (c2[2] - c1[2]) * frac)
        colors.append((r, g, b))

    return colors

def offset_colors(colors, steps):
    """
    对输入的颜色列表进行偏移操作，并返回新的颜色列表。
    
    参数:
        colors: 输入的颜色列表，每个元素为 (r, g, b) 元组或列表。
        steps: 偏移步数。正数表示向右（末尾方向）偏移，负数表示向左（起始方向）偏移。
        
    返回:
        新的颜色列表，长度与原列表相同，但顺序根据偏移步数调整。
    """
    _check_qualified_colors(colors)

    if not colors or steps == 0:
        return colors
    
    # 计算有效偏移量（考虑steps可能大于colors长度的情况）
    effective_steps = steps % len(colors)
    
    # 如果偏移量为0，直接返回原始列表
    if effective_steps == 0:
        return colors
    
    # 使用切片操作完成偏移
    return colors[-effective_steps:] + colors[:-effective_steps]


def map_value_to_color(value, value_min, value_max, gradient_colors):
    """
    将一个数值映射到渐变颜色列表中的对应颜色。

    :param value: 需要映射的数值
    :param value_min: 数值的最小范围
    :param value_max: 数值的最大范围
    :param gradient_colors: 渐变颜色列表，包含 RGB 元组或列表
    :return: 对应于输入数值的颜色（RGB元组或列表）
    """
    _check_qualified_colors(gradient_colors)
    # 确保数值在范围内
    if value < value_min:
        return gradient_colors[0]
    elif value > value_max:
        return gradient_colors[-1]

    # 计算数值在总范围内的比例
    ratio = (value - value_min) / (value_max - value_min)

    # 根据比例计算颜色索引
    color_index = int(ratio * (len(gradient_colors) - 1))

    return gradient_colors[color_index]


def dim_color(color, factor=0.9):
    """
    按照给定的因子调整颜色的亮度。
    
    :param color: 输入颜色，格式为 (r, g, b)，各分量范围 0~255
    :param factor: 亮度调整因子，范围 0.0~1.0。1.0 表示不变，0.0 表示黑色。
    :return: 调整后的颜色，格式为 (r, g, b)
    """
    _check_qualified_color(color)
    if not (0.0 <= factor <= 1.0):
        raise ValueError("factor 参数必须在 0.0 到 1.0 范围内")
    
    r = int(color[0] * factor)
    g = int(color[1] * factor)
    b = int(color[2] * factor)
    
    return (r, g, b)

def brighten_color(color, factor=0.9):
    """
    按照给定的因子调整颜色的亮度。
    
    :param color: 输入颜色，格式为 (r, g, b)，各分量范围 0~255
    :param factor: 亮度调整因子，范围 0.0~1.0。1.0 表示不变，0.0 表示白色。
    :return: 调整后的颜色，格式为 (r, g, b)
    """
    _check_qualified_color(color)
    if not (0.0 <= factor <= 1.0):
        raise ValueError("factor 参数必须在 0.0 到 1.0 范围内")
    
    r = int(color[0] + (255 - color[0]) * (1 - factor))
    g = int(color[1] + (255 - color[1]) * (1 - factor))
    b = int(color[2] + (255 - color[2]) * (1 - factor))
    
    return (r, g, b)

def scale_color(color, scale):
    """
    按照给定的比例缩放颜色的亮度。
    
    :param color: 输入颜色，格式为 (r, g, b)，各分量范围 0~255
    :param scale: 亮度缩放比例，大于1表示变亮，小于1表示变暗
    :return: 调整后的颜色，格式为 (r, g, b)
    """
    _check_qualified_color(color)
    if scale < 0:
        raise ValueError("scale 参数必须是非负数")
    
    r = min(int(color[0] * scale), 255)
    g = min(int(color[1] * scale), 255)
    b = min(int(color[2] * scale), 255)
    
    return (r, g, b)

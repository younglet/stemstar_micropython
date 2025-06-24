import random
import time


# ================== Block 类 ==================
class Block:
    def __init__(self, x, y, is_food=False):
        self.x = x
        self.y = y
        self.is_food = is_food

    def draw(self, screen):
        screen.fill_rect(self.x * 2, self.y * 2, 2, 2, 1)

    def move(self, direction):
        return Block(self.x + direction[0], self.y + direction[1], self.is_food)

    @staticmethod
    def generate_food(screen, snake_blocks):
        screen_width_in_blocks = screen.width // 2
        screen_height_in_blocks = screen.height // 2
        while True:
            x = random.randint(1, screen_width_in_blocks - 2)
            y = random.randint(1, screen_height_in_blocks - 2)
            if not any(block.x == x and block.y == y for block in snake_blocks):
                return Block(x, y, is_food=True)


# ================== Snake 类 ==================
class Snake:
    def __init__(self, screen):
        self.screen = screen
        init_x = screen.width // 4
        init_y = screen.height // 4

        self.directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]  # 右、上、左、下
        self.direction = 0
        self.blocks = [Block(init_x, init_y)]  # 初始蛇身是一个普通 Block
        self.food = Block.generate_food(screen, self.blocks)  # 食物也是 Block，只是 is_food=True

    def update(self):
        head = self.blocks[0].move(self.directions[self.direction % 4])

        # 边界检测（考虑边框）
        if not (1 <= head.x < (self.screen.width // 2) - 1 and
                1 <= head.y < (self.screen.height // 2) - 1):
            print("Game Over: Edge Collision")
            return False

        # 自撞检测
        for block in self.blocks[1:]:
            if block.x == head.x and block.y == head.y:
                print("Game Over: Self Collision")
                return False

        # 插入新头部
        self.blocks.insert(0, head)

        # 如果吃到了食物
        if head.x == self.food.x and head.y == self.food.y:
            self.food = Block.generate_food(self.screen, self.blocks)  # 生成新的食物
        else:
            self.blocks.pop()  # 如果没吃到食物则删除尾部

        # 清屏并重绘
        self.screen.fill(0)

        # 绘制边框（单像素宽度的矩形框）
        self.screen.fill_rect(0, 0, self.screen.width, 2, 1)  # 上边框
        self.screen.fill_rect(0, self.screen.height - 2, self.screen.width, 2, 1)  # 下边框
        self.screen.fill_rect(0, 0, 2, self.screen.height, 1)  # 左边框
        self.screen.fill_rect(self.screen.width - 2, 0, 2, self.screen.height, 1)  # 右边框

        # 绘制蛇和食物
        for block in self.blocks:
            block.draw(self.screen)
        self.food.draw(self.screen)
        self.screen.show()

        return True

    def left(self):
        self.direction -= 1

    def right(self):
        self.direction += 1


# ================== 主程序入口 ==================
if __name__ == "__main__":
    from machine import Pin, I2C
    from ssd1306 import SSD1306_I2C
    
    screen = SSD1306_I2C(128, 64, I2C(1))
    screen.poweron()

    snake = Snake(screen)

    left_button = Pin(12, Pin.IN, Pin.PULL_UP)
    right_button = Pin(14, Pin.IN, Pin.PULL_UP)

    # 等待按键函数
    def wait_key(duration_ms):
        last_key = None
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
            if not left_button.value():
                last_key = 'left'
                while not left_button.value():  # 等待释放
                    time.sleep_ms(10)
            elif not right_button.value():
                last_key = 'right'
                while not right_button.value():  # 等待释放
                    time.sleep_ms(10)
            time.sleep_ms(10)  # 防止 CPU 占满
        return last_key

    # ========== 游戏主循环 ==========
    running = True
    while running:
        key = wait_key(100)  # 每 100ms 检查一次按键
        if key == 'left':
            snake.left()
        elif key == 'right':
            snake.right()

        running = snake.update()
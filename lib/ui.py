class Node:
    def __init__(self, name):
        self.name = name

class MenuNode(Node):
    def __init__(self, name, parent=None):
        super().__init__(name)
        self._children = []
        if parent is not None:
            if not isinstance(parent, MenuNode):
                raise TypeError("Parent must be a MenuNode")
            parent.add_child(self)

    @property
    def children(self):
        if not self._children:
            return ['Blank Menu']
        return self._children + ['Back']

    def add_child(self, child):
        if not isinstance(child, Node):
            raise TypeError("Child must be a Node")
        self._children.append(child)


class ActionNode(Node):
    def __init__(self, name, parent=None, callback=None):
        super().__init__(name) 
        self.callback = callback or (lambda: print(f"⚠️ 动作 '{self.name}' 尚未绑定！"))
        if parent is not None:
            if not isinstance(parent, MenuNode):
                raise TypeError("Parent must be a MenuNode")
            parent.add_child(self)
    
    def execute(self):
        self.callback()

class UI:
    def __init__(self, screen, char_width=8, char_height=10):
        """
        初始化 UI 控制器
        :param screen: SSD1306 屏幕对象（需有 fill(), text(x,y), show() 方法）
        :param char_width: 字符平均宽度（像素）
        :param char_height: 字符高度（像素）
        :param screen_width: 屏幕宽度（像素）
        :param screen_height: 屏幕高度（像素）
        """
        self.screen = screen
        self.char_width = char_width
        self.char_height = char_height
        self.screen_width = screen.width
        self.screen_height = screen.height

        # 计算最多能显示多少行（第一行为标题，其余为菜单项）
        self.max_lines = (self.screen_height // self.char_height) - 1  # 减去标题行
        if self.max_lines < 1:
            self.max_lines = 1

        self.current_node = None
        self.current_item_index = 0
        self.scroll_offset = 0  # 当前滚动偏移（起始显示的菜单项索引）

    def set_root(self, root: MenuNode):
        """设置根菜单"""
        root._is_root = True 
        self.root_node = root
        self.current_node = root
        self.current_item_index = 0
        self.scroll_offset = 0
        self.render()

    def _get_display_items(self):
        """获取当前应显示的菜单项列表（处理 Back / Blank Menu）"""
        items = self.current_node.children[:]
        if getattr(self.current_node, '_is_root', False) and items and items[-1] == 'Back':
            items = items[:-1]
        return items

    def render(self):
        self.screen.fill(0)
        
        # 第一行：标题居中（基于字符宽度计算）
        title = self.current_node.name
        max_chars = self.screen_width // self.char_width
        centered_title = f"{title:^{max_chars}}"
        self.screen.text(centered_title[:max_chars], 0, 0, 1)

        # 获取完整菜单项（可能包含 'Back' 或 'Blank Menu' 字符串）
        all_items = self._get_display_items()
        total_items = len(all_items)

        # 更新滚动偏移，确保当前选中项可见
        if self.current_item_index < self.scroll_offset:
            self.scroll_offset = self.current_item_index
        elif self.current_item_index >= self.scroll_offset + self.max_lines:
            self.scroll_offset = self.current_item_index - self.max_lines + 1

        # 限制 scroll_offset 范围
        if self.scroll_offset > total_items - self.max_lines:
            self.scroll_offset = max(0, total_items - self.max_lines)
        if self.scroll_offset < 0:
            self.scroll_offset = 0

        # 显示可见范围内的菜单项
        start = self.scroll_offset
        end = min(start + self.max_lines, total_items)

        for i in range(start, end):
            y_pos = (i - start + 1) * self.char_height
            element = all_items[i]

            # 处理特殊字符串项
            if isinstance(element, str):
                display_text = element
            else:
                # 安全访问 .name（element 是 Node 的子类）
                name_part = element.name[:max_chars - 4]  # 预留空间给后缀和前缀
                if isinstance(element, MenuNode):
                    # 菜单项：右对齐并加 ">"
                    display_text = f"{name_part:<{max_chars - 3}}>"
                else:  # ActionNode
                    # 动作项：不加符号，但预留位置保持对齐
                    display_text = f"{name_part:<{max_chars - 2}}"

            # 添加选择前缀
            prefix = "* " if i == self.current_item_index else "  "
            line_text = prefix + display_text

            # 绘制文本（确保不超屏幕宽度）
            self.screen.text(line_text[:max_chars + 2], 0, y_pos, 1)

        self.screen.show()

    def navigate_up(self):
        if self.current_item_index > 0:
            self.current_item_index -= 1
            self.render()

    def navigate_down(self):
        all_items = self._get_display_items()
        if self.current_item_index < len(all_items) - 1:
            self.current_item_index += 1
            self.render()

    def select(self):
        all_items = self._get_display_items()
        if not all_items:
            return

        selected = all_items[self.current_item_index]

        if selected == 'Back':
            if hasattr(self, '_menu_stack') and self._menu_stack:
                self.current_node = self._menu_stack.pop()
                self.current_item_index = 0
                self.scroll_offset = 0
                self.render()
            return

        if selected == 'Blank Menu':
            return

        if isinstance(selected, ActionNode):
            selected.execute()
        elif isinstance(selected, MenuNode):
            if not hasattr(self, '_menu_stack'):
                self._menu_stack = []
            self._menu_stack.append(self.current_node)
            self.current_node = selected
            self.current_item_index = 0
            self.scroll_offset = 0
            self.render()
    
    @staticmethod
    def help():
        print("""
【UI 菜单系统 UI 类】
--------------------------------
[功能说明]：
    基于 SSD1306 屏幕实现的嵌套菜单系统，支持菜单导航和动作执行。
--------------------------------
[创建实例]：    
    ui = UI(screen, char_width=8, char_height=10)            # screen 为 SSD1306 屏幕对象
    root = MenuNode("Main Menu")                             # 创建根菜单节点
    menu1 = MenuNode("Submenu 1", parent=root)               # 创建子菜单节点
    ActionNode("Do Something", parent=menu1, callback=func)  # 创建动作节点

[方法]：
    ui.set_root(root)          # 设置根菜单节点
    ui.navigate_up()           # 菜单上移
    ui.navigate_down()         # 菜单下移
    ui.select()                # 选择当前菜单项（进入子菜单或执行动作）

[示例]：
    from ssd1306 import SSD1306_I2C
    from machine import I2C, Pin
    from ui import UI, MenuNode, ActionNode

    # 初始化屏幕
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    screen = SSD1306_I2C(128, 64, i2c)

    # 创建菜单节点
    root = MenuNode("Main Menu")
    submenu = MenuNode("Submenu", parent=root)
    ActionNode("Do Something", parent=submenu, callback=lambda: print("Action executed!"))
    ui = UI(screen)
    ui.set_root(root)
    ui.render()
--------------------------------
""")

    @staticmethod
    def test():
        print("【UI 菜单系统 测试程序】")

        import ssd1306
        from machine import I2C, Pin

        try:
            sda_num = int(input("请输入 I2C SDA 引脚号（默认 21）: ") or "21")
            scl_num = int(input("请输入 I2C SCL 引脚号（默认 22）: ") or "22")
        except ValueError:
            print("⚠️ 引脚号输入无效，使用默认值 SDA=21, SCL=22")
            sda_num = 21
            scl_num = 22
        i2c = I2C(0, scl=Pin(scl_num), sda=Pin(sda_num), freq=400000)
        screen = ssd1306.SSD1306_I2C(128, 64, i2c)

        # 创建根菜单
        root = MenuNode("NovaUI V1.0")
        
        # 创建子菜单和动作节点
        submenu1 = MenuNode("Menu 1", parent=root)
        ActionNode("Func 1-1", parent=submenu1, callback=lambda: print("执行了 功能 1-1"))
        ActionNode("Func 1-2", parent=submenu1, callback=lambda: print("执行了 功能 1-2"))
        submenu2 = MenuNode("Menu 2", parent=root)
        ActionNode("Func 2-1", parent=submenu2, callback=lambda: print("执行了 功能 2-1"))
        ActionNode("Func 2-2", parent=submenu2, callback=lambda: print("执行了 功能 2-2"))

        # 初始化 UI 并设置根菜单
        ui = UI(screen)
        ui.set_root(root)
        ui.set_root(root)

        print("✅ NovaUI started.")
        print("Commands:")
        print("  u → Move up")
        print("  d → Move down")
        print("  s → Select")
        print("  q → Quit")

        try:
            while True:
                cmd = input(">> ").strip().lower()
                if cmd == "u":
                    ui.navigate_up()
                elif cmd == "d":
                    ui.navigate_down()
                elif cmd == "s":
                    ui.select()
                elif cmd == "q":
                    print("exiting UI...")
                    break
                else:
                    print("❓ Use: u, d, s, q")
        except KeyboardInterrupt:
            print("\n⏹ User interrupted.")

if __name__ == "__main__":
    UI.test()
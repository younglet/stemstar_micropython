from machine import Pin
from motor import Motor
import time

class DiffDriveCar:
    def __init__(self, left_pin1, left_pin2, right_pin1, right_pin2,
                 default_speed=0.6, direction_left=1, direction_right=1,
                 freq=5000, max_duty=1023):
        """
        初始化双轮小车
        
        :param left_pin1, left_pin2: 左电机控制引脚（接 H 桥 IN1/IN2）
        :param right_pin1, right_pin2: 右电机控制引脚
        :param direction_left, direction_right: 方向修正（1 或 -1）
        :param freq: PWM 频率（Hz）
        :param max_duty: 最大占空比（ESP32 默认 1023）
        :param default_speed: 默认速度（0.0 ~ 1.0），用于 forward/backward 等方法
        """
        self._default_speed = max(0.0, min(1.0, float(default_speed)))

        self.left_motor = Motor(
            pin1=left_pin1,
            pin2=left_pin2,
            direction=direction_left,
            freq=freq,
            max_duty=max_duty
        )
        self.right_motor = Motor(
            pin1=right_pin1,
            pin2=right_pin2,
            direction=direction_right,
            freq=freq,
            max_duty=max_duty
        )

    @property
    def default_speed(self):
        return self._default_speed

    @default_speed.setter
    def default_speed(self, value):
        self._default_speed = max(0.0, min(1.0, float(value)))

    def set_speed(self, left_speed, right_speed):
        """直接设置左右轮速度（-1.0 ~ +1.0）"""
        self.left_motor.speed = left_speed
        self.right_motor.speed = right_speed

    def stop(self):
        """停止所有电机"""
        self.left_motor.stop()
        self.right_motor.stop()

    def forward(self, speed=None):
        """前进（两轮同向同速）"""
        s = self._default_speed if speed is None else speed
        self.set_speed(s, s)

    def backward(self, speed=None):
        """后退"""
        s = self._default_speed if speed is None else speed
        self.set_speed(-s, -s)

    def spin_left(self, speed=None):
        """原地向左旋转（左右轮反向）"""
        s = self._default_speed if speed is None else speed
        self.set_speed(-s, s)

    def spin_right(self, speed=None):
        """原地向右旋转"""
        s = self._default_speed if speed is None else speed
        self.set_speed(s, -s)

    # 兼容方法名
    turn_left = spin_left
    turn_right = spin_right
    left = spin_left
    right = spin_right

    def arc_turn(self, direction='left', forward_speed=None, turn_ratio=0.5):
        """
        弧线转弯（更平滑）
        :param direction: 'left' or 'right'
        :param forward_speed: 主速度（若为 None，使用 default_speed）
        :param turn_ratio: 转弯比例（0.0~1.0）
        """
        s = self._default_speed if forward_speed is None else forward_speed
        if direction == 'left':
            inner = s * (1 - turn_ratio)
            outer = s
            self.set_speed(inner, outer)
        else:
            inner = s * (1 - turn_ratio)
            outer = s
            self.set_speed(outer, inner)
    
    smooth_turn = arc_turn  # 兼容方法名

    def arc_left(self, forward_speed=None, turn_ratio=0.5):
        """弧线左转"""
        self.arc_turn('left', forward_speed, turn_ratio)
    def arc_right(self, forward_speed=None, turn_ratio=0.5):
        """弧线右转"""
        self.arc_turn('right', forward_speed, turn_ratio)

    smooth_left  =  arc_left
    smooth_right  =  arc_right
    

    def deinit(self):
        """释放资源"""
        self.left_motor.deinit()
        self.right_motor.deinit()

    @classmethod
    def test(cls):
        """交互式测试程序"""
        print("【双轮小车测试程序】")
        try:
            l1 = int(input("左电机引脚1 (IN1): ") or "14")
            l2 = int(input("左电机引脚2 (IN2): ") or "15")
            r1 = int(input("右电机引脚1 (IN1): ") or "16")
            r2 = int(input("右电机引脚2 (IN2): ") or "17")
        except:
            print("❌ 输入无效，使用默认引脚：L(14,15) R(16,17)")
            l1, l2, r1, r2 = 14, 15, 16, 17

        dir_l = -1 if input("左轮是否反转？(y/N): ").lower() == 'y' else 1
        dir_r = -1 if input("右轮是否反转？(y/N): ").lower() == 'y' else 1

        default_speed_input = input("默认速度（0.0~1.0，默认 0.6）: ") or "0.6"
        try:
            default_speed = float(default_speed_input)
        except:
            default_speed = 0.6

        print(f"🚩 初始化小车：左({l1},{l2}) 右({r1},{r2})，默认速度={default_speed:.2f}")
        car = cls(l1, l2, r1, r2,
                  direction_left=dir_l,
                  direction_right=dir_r,
                  default_speed=default_speed)

        try:
            print("🔼  测试 1：前进（使用默认速度）")
            car.forward()  # 不传 speed，用默认
            time.sleep(2)

            print("🔽  测试 2：后退（使用默认速度）")
            car.backward()
            time.sleep(2)

            print("◀️  测试 3：原地左转")
            car.spin_left()
            time.sleep(2)

            print("▶️  测试 4：原地右转")
            car.spin_right()
            time.sleep(2)

            print("🛑 停止")
            car.stop()
            time.sleep(1)

            print("✅ 所有测试完成！")
        except Exception as e:
            print("❌ 测试出错:", e)
        finally:
            car.stop()
            car.deinit()

    @staticmethod
    def help():
        print("""
【DiffDriveCar 双轮小车类】
----------------------------
[接线说明]:
    - 每个电机需接 H 桥驱动（如 L298N）
    - 左电机：IN1 → GPIO14, IN2 → GPIO15
    - 右电机：IN1 → GPIO16, IN2 → GPIO17
    - 电机电源独立供电（不要用开发板 3.3V/5V！）
[初始化]:
    car = DiffDriveCar(
        left_pin1=14, left_pin2=15,
        right_pin1=16, right_pin2=17,
        direction_left=1, direction_right=1
    )
[控制方法]:
    car.forward(speed)     # 前进
    car.backward(speed)    # 后退
    car.spin_left(speed)   # 原地左转
    car.spin_right(speed)  # 原地右转
    car.arc_turn('left', 0.6, 0.3)  # 弧线左转
    car.stop()             # 停止
    car.set_speed(left, right)  # 直接控制左右轮
[注意]:
    - speed 范围：0.0 ~ 1.0（建议不超过 0.8 避免电流过大）
    - 若某侧轮子转向反了，用 direction_left/right = -1 修正
----------------------------
""")

Car = DiffDriveCar         # 简化名称
DoubleWheelCar = DiffDriveCar  
DiffDriveRobot = DiffDriveCar  
TwoWheelCar = DiffDriveCar
TwoWheelRobot = DiffDriveCar


if __name__ == "__main__":
    DiffDriveCar.test()
    

from buzzer import Buzzer
from machine import Pin
import time

print('''
【蜂鸣器测试程序】
──────────────────────────────────────────────
【Buzzer】 ->  GPIO4 （输出引脚）
──────────────────────────────────────────────
请按照如上接线说明进行接线，并选择蜂鸣器类型（默认为无源）：
1 - 有源蜂鸣器
2 - 无源蜂鸣器（默认）
然后回车继续：''')

buzzer_type = input().strip()
is_active_buzzer = True if buzzer_type == "1" else False

try:
    print("🚩 开始测试蜂鸣器功能...")

    print("🔧 正在初始化蜂鸣器...")
    buzzer = Buzzer(Pin(4), is_active_buzzer=is_active_buzzer)  # 根据用户选择初始化

    print("🔊 正在发出一次短促蜂鸣")
    buzzer.beep(times=1, duration=0.3)
    time.sleep(1)

    print("🔊 正在连续蜂鸣三次")
    buzzer.beep(times=3, duration=0.2, interval=0.1)
    time.sleep(1)

    if not is_active_buzzer:

        print("🎼 正在播放一段旋律:《兰亭序》")
        melody = [
            'G4', 'A4', 'C5', 'D5', '', '', 'C5', 'D5', 'C5', 'E5', 'D5', 'C5', '', '',
            'C5', 'D5', 'E5', 'G5', '', '', 'E5', 'D5', 'C5', 'A4', 'G4', 'E5', '', '',
            'E5', 'G5', 'A5', 'E5', '', '', 'D5', 'D5', 'C5', 'E5', 'D5', 'C5', '', '',
            'A4', 'C5', 'E5', 'D5', '', '', 'C5', 'A4', 'G4', 'E5', 'D5', 'C5', '', '',
        ]
        for note in melody:
            print(f"🎵 正在播放 {note}")
            buzzer.play_note(note=note, duration=0.2)
            

        print("🎉 所有测试完成！")
    else:
        print("注意：由于使用的是有源蜂鸣器，不能通过play_note方法播放不同音调")
except KeyboardInterrupt:
    print("程序已退出")
except Exception as e:
    print("发生错误：", e)
finally:
    buzzer.off()

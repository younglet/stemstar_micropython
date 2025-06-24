from machine import UART
import time

class MP3Player:
    def __init__(self, uart):
        self.uart = uart
    
    def _calculate_checksum(self, cmd_bytes):
        """计算校验和"""
        return sum(cmd_bytes) & 0xFF
    
    def _send_command(self, command):
        """发送命令并等待响应"""
        self.uart.write(command)
        time.sleep_ms(200)  # 等待设备响应
        res = self.uart.read()
        if res is not None:
            print(f"接收到 {len(res)} 字节: {list(res)}")
        else:
            print("没有接收到数据。")
    
    def query_play_status(self):
        """查询播放状态"""
        cmd = bytearray([0xAA, 0x01, 0x00])
        cmd.append(self._calculate_checksum(cmd))
        self._send_command(cmd)
    
    def play(self):
        """播放"""
        cmd = bytearray([0xAA, 0x02, 0x00, 0xAC])
        self._send_command(cmd)
    
    def pause(self):
        """暂停"""
        cmd = bytearray([0xAA, 0x03, 0x00, 0xAD])
        self._send_command(cmd)
    
    def stop(self):
        """停止"""
        cmd = bytearray([0xAA, 0x04, 0x00, 0xAE])
        self._send_command(cmd)

    def next_track(self):
        """下一曲"""
        cmd = bytearray([0xAA, 0x06, 0x00, 0xB0])
        self._send_command(cmd)
    
    def previous_track(self):
        """上一曲"""
        cmd = bytearray([0xAA, 0x05, 0x00, 0xAF])
        self._send_command(cmd)
    
    def set_volume(self, volume):
        """设置音量"""
        if not (0 <= volume <= 255): raise ValueError("音量应在0到20之间")
        cmd = bytearray([0xAA, 0x13, 0x01, volume])
        cmd.append(self._calculate_checksum(cmd[:-1]))
        self._send_command(cmd)
        
if __name__ == '__main__':                
    from machine import Uart
    
    uart  = Uart(2, 115200, tx=Pin(26), rx=Pin(27))
    mp3_player = MP3Player(uart)
    mp3_player.play()


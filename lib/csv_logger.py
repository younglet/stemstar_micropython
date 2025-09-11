# micropython_csv_logger.py
import time
import os

class CSVLogger:
    def __init__(self, filename='log.csv', headers=None, append=True):
        """
        初始化 CSV 日志记录器

        :param filename: 日志文件名
        :param headers: CSV 列标题（列表），例如 ['timestamp', 'level', 'message', 'temp', 'humidity']
        :param append: 是否追加到已有文件（True），或覆盖（False）
        """
        self.filename = filename
        self.headers = headers or ['timestamp', 'level', 'message']

        # 检查文件是否存在，不存在则创建并写入 header
        file_exists = self._file_exists(filename)

        # 如果是新文件或不追加，则写入 header
        if not file_exists or not append:
            self._write_row(self.headers, mode='w')

    def _file_exists(self, path):
        """检查文件是否存在"""
        try:
            with open(path, 'r'):
                return True
        except OSError:
            return False

    def _write_row(self, data, mode='a'):
        """将列表数据写入 CSV 文件的一行"""
        line = ','.join([f'"{str(d)}"' for d in data]) + '\n'  # 使用引号包裹字段，避免逗号干扰
        with open(self.filename, mode) as f:
            f.write(line)

    def _log(self, level, message, **fields):
        """记录日志的核心方法"""
        # 获取本地时间
        t = time.localtime()
        timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*t[:6])

        # 构建日志行
        row = [timestamp, level, message]

        # 补充自定义字段（按 headers 顺序）
        for key in self.headers[3:]:  # 跳过 timestamp, level, message
            row.append(fields.get(key, ''))

        self._write_row(row)

    def debug(self, msg, **fields):
        self._log('DEBUG', msg, **fields)

    def info(self, msg, **fields):
        self._log('INFO', msg, **fields)

    def warning(self, msg, **fields):
        self._log('WARNING', msg, **fields)

    def error(self, msg, **fields):
        self._log('ERROR', msg, **fields)

    def critical(self, msg, **fields):
        self._log('CRITICAL', msg, **fields)

    def close(self):
        """关闭日志（目前仅作占位）"""
        pass  # MicroPython 中文件写入后自动关闭
# MicroPython 自制驱动与案例项目

这是一个专注于自制硬件驱动开发的MicroPython项目，包括了驱动程序、驱动测试代码以及基于这些驱动实现的案例项目代码。

## 项目结构
```
micropython-project/
│
├── lib/           # 存放自制的驱动库
│   ├── driver1.py
│   ├── driver2.py
│   └── ...
│
├── test/          # 硬件测试程序目录
│   ├── test_driver1.py
│   ├── test_driver2.py
│   └── ...
│
└── demo/          # 案例项目代码目录
├── project_example1.py
├── project_example2.py
└── ...
```

### 驱动使用

驱动位于`lib/`目录下，其中文件可以镜像拷贝到micropython设备的`lib/`目录下，然后通过以下方式导入：

```python
from driver1 import Driver1

driver = Driver1()
```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
坏习惯统计器 - 桌面运行脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入主应用
from badhabit_tracker import BadHabitTrackerApp

if __name__ == '__main__':
    # 运行应用
    BadHabitTrackerApp().run()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体助手模块 - 解决中文显示乱码问题
"""

import os
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path

def register_chinese_fonts():
    """注册中文字体，解决中文显示乱码问题"""
    
    # 尝试注册系统中文字体
    chinese_fonts = [
        # Windows系统字体
        "C:/Windows/Fonts/simhei.ttf",      # 黑体
        "C:/Windows/Fonts/simsun.ttc",      # 宋体
        "C:/Windows/Fonts/simkai.ttf",      # 楷体
        "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
        "C:/Windows/Fonts/msyhbd.ttc",      # 微软雅黑粗体
        
        # Linux系统字体
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/droid/DroidSansFallback.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        
        # macOS系统字体
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
    ]
    
    available_font = None
    
    # 查找可用的中文字体
    for font_path in chinese_fonts:
        if os.path.exists(font_path):
            available_font = font_path
            break
    
    if available_font:
        print(f"使用字体: {available_font}")
        try:
            # 注册字体
            LabelBase.register(
                name='ChineseFont',
                fn_regular=available_font,
                fn_bold=available_font,
                fn_italic=available_font,
                fn_bolditalic=available_font
            )
            return 'ChineseFont'
        except Exception as e:
            print(f"注册字体失败: {e}")
    
    # 如果系统字体不可用，创建简单的默认字体配置
    print("使用默认字体，可能不支持中文")
    return 'Roboto'

def get_font_name():
    """获取推荐的中文字体名称"""
    return register_chinese_fonts()

# 预加载字体
DEFAULT_CHINESE_FONT = get_font_name()
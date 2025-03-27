#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GUI包初始化文件
此文件标记gui目录为Python包，允许从其他模块导入
"""

# 从各个模块导入类和功能
from gui.ui.button import Button
from gui.views.city_view import CityView
from gui.constants import (
    WHITE, BLACK, RED, GREEN, BLUE, GOLD, BACKGROUND_COLOR
)

# 定义导出的符号
__all__ = [
    'Button',          # GUI组件
    'CityView',        # 城市视图
    # 颜色常量
    'WHITE', 'BLACK', 'RED', 'GREEN', 'BLUE', 'GOLD', 'BACKGROUND_COLOR'
]

# 注意：BattleView应该直接从gui.views导入，而不是在这里导入
# 这样可以避免循环导入问题 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GUI包初始化文件
此文件标记gui目录为Python包，允许从其他模块导入
"""

# 从各个模块导入类和功能
from gui.ui.button import Button
from gui.views.battle_view import BattleView
from gui.views.city_view import CityView
from gui.constants import (
    WHITE, BLACK, RED, GREEN, BLUE, GOLD, BACKGROUND_COLOR
)

# 为了向后兼容，原来从views模块导入的内容现在从这里导出
from gui.views.battle_view import BattleView
from gui.views.city_view import CityView
from gui.ui.button import Button

# 定义导出的符号
__all__ = [
    'Button',          # GUI组件
    'BattleView',      # 战斗视图
    'CityView',        # 城市视图
    # 颜色常量
    'WHITE', 'BLACK', 'RED', 'GREEN', 'BLUE', 'GOLD', 'BACKGROUND_COLOR'
] 
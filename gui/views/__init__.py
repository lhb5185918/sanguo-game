"""
视图组件包
"""
# 暂时注释掉BattleView的导入，稍后再修复
#from gui.views.battle_view import BattleView
from gui.views.city_view import CityView
from gui.ui.button import Button  # 为了向后兼容，从ui包导入Button

__all__ = ['CityView', 'Button']  # 暂时移除BattleView 
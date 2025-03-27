#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
按钮UI组件模块
"""

import arcade
from gui.constants import WHITE

class Button:
    """按钮类，用于创建交互式按钮"""
    
    def __init__(self, center_x, center_y, width, height, text, 
                 text_color=WHITE, bg_color=(100, 100, 150), hover_color=(150, 150, 200)):
        """初始化按钮属性"""
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.pressed = False
        self.font_size = 16
        
    def draw(self):
        """绘制按钮"""
        # 绘制按钮背景
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # 如果按钮被按下，绘制稍暗的颜色
        if self.pressed:
            color = (max(0, color[0] - 30), max(0, color[1] - 30), max(0, color[2] - 30))
        
        arcade.draw_rectangle_filled(
            self.center_x, self.center_y, self.width, self.height, color
        )
        
        # 绘制按钮边框
        arcade.draw_rectangle_outline(
            self.center_x, self.center_y, self.width, self.height, WHITE, 2
        )
        
        # 绘制按钮文本
        arcade.draw_text(
            self.text,
            self.center_x, self.center_y,
            self.text_color,
            font_size=self.font_size,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center", anchor_y="center"
        )
    
    def check_mouse_hover(self, x, y):
        """检查鼠标是否悬停在按钮上"""
        self.is_hovered = (
            self.center_x - self.width/2 <= x <= self.center_x + self.width/2 and
            self.center_y - self.height/2 <= y <= self.center_y + self.height/2
        )
        return self.is_hovered
    
    def check_mouse_press(self, x, y):
        """检查鼠标是否点击了按钮"""
        pressed = (
            self.center_x - self.width/2 <= x <= self.center_x + self.width/2 and
            self.center_y - self.height/2 <= y <= self.center_y + self.height/2
        )
        if pressed:
            self.pressed = True
            # 使用arcade.schedule让按钮按下效果在0.1秒后恢复
            arcade.schedule(self.release_button, 0.1)
        return pressed
    
    def release_button(self, delta_time):
        """释放按钮按下状态"""
        self.pressed = False 
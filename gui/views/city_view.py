#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
城市视图模块
"""

import arcade
from gui.constants import WHITE, BACKGROUND_COLOR
from gui.ui.button import Button

class CityView(arcade.View):
    """
    城市界面视图
    
    注意：此处只提供了框架，实际实现需要将views.py中的完整CityView类代码复制过来
    包括以下主要方法:
    - __init__: 初始化城市视图
    - setup: 设置城市界面
    - on_show: 当视图被显示时
    - on_draw: 绘制城市界面
    - on_mouse_motion: 鼠标移动事件
    - on_mouse_press: 鼠标点击事件
    - on_key_press: 键盘按键事件
    """
    
    def __init__(self, game_window, window_size, player, city_data=None):
        """初始化城市视图"""
        super().__init__()
        self.game_window = game_window
        self.window_size = window_size
        self.player = player
        self.city_data = city_data
        
        # 背景纹理
        try:
            self.background_texture = arcade.load_texture("assets/images/backgrounds/city.jpg")
        except:
            self.background_texture = None
            
        # UI元素
        self.buttons = []
        self.setup()
        
    def setup(self):
        """设置城市界面"""
        # 添加返回主菜单按钮
        back_button = Button(
            100, self.window_size[1] - 50,
            150, 40, "返回",
            bg_color=(100, 100, 150),
            hover_color=(120, 120, 180)
        )
        self.buttons.append(back_button)
        
    def on_show(self):
        """当视图被显示时"""
        arcade.set_background_color(BACKGROUND_COLOR)
        
    def on_draw(self, delta_time=0):
        """绘制城市界面"""
        arcade.start_render()
        
        # 绘制背景
        if self.background_texture:
            arcade.draw_texture_rectangle(
                self.window_size[0] // 2, self.window_size[1] // 2,
                self.window_size[0], self.window_size[1],
                self.background_texture
            )
        else:
            # 如果没有背景纹理，绘制纯色背景
            arcade.draw_rectangle_filled(
                self.window_size[0] // 2, self.window_size[1] // 2,
                self.window_size[0], self.window_size[1],
                BACKGROUND_COLOR
            )
            
        # 绘制界面标题
        arcade.draw_text(
            "城市管理",
            self.window_size[0] // 2, self.window_size[1] - 50,
            WHITE,
            font_size=36,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 绘制城市信息（如果有）
        if self.city_data:
            arcade.draw_text(
                f"城市名称: {self.city_data.name}",
                self.window_size[0] // 2, self.window_size[1] - 100,
                WHITE,
                font_size=24,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
        else:
            arcade.draw_text(
                "未选择城市",
                self.window_size[0] // 2, self.window_size[1] // 2,
                WHITE,
                font_size=24,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
        # 绘制按钮
        for button in self.buttons:
            button.draw()
            
    def on_mouse_motion(self, x, y, dx, dy):
        """鼠标移动事件"""
        for button in self.buttons:
            button.check_mouse_hover(x, y)
            
    def on_mouse_press(self, x, y, button, modifiers):
        """鼠标点击事件"""
        for i, ui_button in enumerate(self.buttons):
            if ui_button.check_mouse_press(x, y):
                if i == 0:  # 返回按钮
                    from three_kingdoms_arcade import MainMenuView
                    main_menu_view = MainMenuView(self.player.game)
                    self.window.show_view(main_menu_view)
                    
    def on_key_press(self, key, modifiers):
        """键盘按键事件"""
        if key == arcade.key.ESCAPE:
            from three_kingdoms_arcade import MainMenuView
            main_menu_view = MainMenuView(self.player.game)
            self.window.show_view(main_menu_view) 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
战斗视图模块
"""

import arcade
import random
import math
from models.army import TroopType, Terrain, Army
from gui.constants import WHITE, BLACK, RED, GREEN, BLUE, GOLD, BACKGROUND_COLOR
from gui.ui.button import Button

class BattleView(arcade.View):
    """战斗界面视图"""
    
    def __init__(self, game_window, window_size, player, battle_data):
        """初始化战斗视图"""
        super().__init__()  # arcade.View只需要简单初始化，不需要参数
        self.window = game_window  # 游戏窗口，用于返回主菜单等操作
        self.window_size = window_size
        self.player = player
        self.battle_data = battle_data
        self.attacker = battle_data.attacker
        self.defender = battle_data.defender
        self.attacker_general = battle_data.attacker_general
        self.defender_general = battle_data.defender_general
        
        # 战场位置设置
        self.attacker_positions = []  # 存储攻击方部队位置和引用
        self.defender_positions = []  # 存储防御方部队位置和引用
        
        # 战斗状态
        self.battle_phase = "准备"  # 准备, 远程, 近战, 追击, 撤退
        self.battle_log = []
        self.buttons = []
        
        # 加载背景图
        try:
            self.background_texture = arcade.load_texture("resources/battlefield.jpg")
        except:
            self.background_texture = None
        
        # 创建返回按钮
        back_button = Button(
            100, 50, 150, 50, "返回", 
            bg_color=(100, 100, 100), hover_color=(150, 150, 150)
        )
        self.buttons.append(back_button)
        
        # 添加初始战斗日志
        self.battle_log.append("战斗开始！")
        self.battle_log.append(f"进攻方: {self.attacker.size}兵力")
        self.battle_log.append(f"防守方: {self.defender.size}兵力")
        
        # 设置部队位置
        self.setup_armies()
    
    def setup_armies(self):
        """设置军队位置"""
        # 战场中心位置
        battlefield_center_x = self.window_size[0] / 2
        battlefield_center_y = self.window_size[1] / 2
        
        # 部署进攻方军队
        attacker_base_x = battlefield_center_x - 200  # 进攻方在左侧
        self.attacker_positions.append((attacker_base_x, battlefield_center_y, self.attacker))
        
        # 部署防守方军队
        defender_base_x = battlefield_center_x + 200  # 防守方在右侧
        self.defender_positions.append((defender_base_x, battlefield_center_y, self.defender))
    
    def on_show(self):
        """显示视图时调用"""
        arcade.set_background_color(BACKGROUND_COLOR)
    
    def on_draw(self):
        """绘制界面"""
        arcade.start_render()
        
        # 绘制背景
        if self.background_texture:
            arcade.draw_texture_rectangle(
                self.window_size[0] // 2, self.window_size[1] // 2,
                self.window_size[0], self.window_size[1],
                self.background_texture
            )
        
        # 绘制战场背景
        self.draw_battlefield_background()
        
        # 绘制军队
        self.draw_armies()
        
        # 绘制战斗日志
        self.draw_battle_log()
        
        # 绘制按钮
        for button in self.buttons:
            button.draw()
    
    def draw_battlefield_background(self):
        """绘制战场背景"""
        # 绘制战场区域
        battlefield_color = (100, 180, 100, 150)  # 半透明绿色（草地）
        if hasattr(self.battle_data, 'terrain'):
            # 根据地形调整颜色
            if self.battle_data.terrain == Terrain.MOUNTAIN:
                battlefield_color = (150, 150, 150, 150)  # 山地灰色
            elif self.battle_data.terrain == Terrain.FOREST:
                battlefield_color = (60, 120, 60, 150)  # 森林深绿
            elif self.battle_data.terrain == Terrain.RIVER:
                battlefield_color = (100, 150, 200, 150)  # 河流蓝色
        
        # 绘制战场区域
        arcade.draw_rectangle_filled(
            self.window_size[0] // 2, self.window_size[1] // 2,
            800, 400, battlefield_color
        )
        arcade.draw_rectangle_outline(
            self.window_size[0] // 2, self.window_size[1] // 2,
            800, 400, WHITE, 2
        )
        
        # 绘制标题
        arcade.draw_text(
            "战场",
            self.window_size[0] // 2, self.window_size[1] - 50,
            GOLD, font_size=36, font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 绘制战斗阶段
        arcade.draw_text(
            f"当前阶段: {self.battle_phase}",
            self.window_size[0] // 2, self.window_size[1] - 100,
            WHITE, font_size=24, font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
    
    def draw_armies(self):
        """绘制军队"""
        # 绘制进攻方
        for x, y, army in self.attacker_positions:
            # 绘制军队圆形
            arcade.draw_circle_filled(x, y, 50, (200, 50, 50, 180))
            arcade.draw_circle_outline(x, y, 50, WHITE, 2)
            
            # 绘制兵力数量
            arcade.draw_text(
                f"{army.size}",
                x, y,
                WHITE, font_size=18, font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center", anchor_y="center"
            )
            
            # 绘制兵种
            arcade.draw_text(
                f"{army.primary_type.value}",
                x, y - 25,
                WHITE, font_size=14, font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
        
        # 绘制防守方
        for x, y, army in self.defender_positions:
            # 绘制军队圆形
            arcade.draw_circle_filled(x, y, 50, (50, 50, 200, 180))
            arcade.draw_circle_outline(x, y, 50, WHITE, 2)
            
            # 绘制兵力数量
            arcade.draw_text(
                f"{army.size}",
                x, y,
                WHITE, font_size=18, font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center", anchor_y="center"
            )
            
            # 绘制兵种
            arcade.draw_text(
                f"{army.primary_type.value}",
                x, y - 25,
                WHITE, font_size=14, font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
        
        # 绘制将领信息
        if self.attacker_general:
            arcade.draw_text(
                f"将领: {self.attacker_general.name}",
                self.attacker_positions[0][0], self.attacker_positions[0][1] + 80,
                GOLD, font_size=18, font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
        
        if self.defender_general:
            arcade.draw_text(
                f"将领: {self.defender_general.name}",
                self.defender_positions[0][0], self.defender_positions[0][1] + 80,
                GOLD, font_size=18, font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
    
    def draw_battle_log(self):
        """绘制战斗日志"""
        # 绘制日志背景
        arcade.draw_rectangle_filled(
            self.window_size[0] - 200, self.window_size[1] // 2,
            350, 400, (30, 30, 60, 180)
        )
        arcade.draw_rectangle_outline(
            self.window_size[0] - 200, self.window_size[1] // 2,
            350, 400, WHITE, 2
        )
        
        # 绘制日志标题
        arcade.draw_text(
            "战斗日志",
            self.window_size[0] - 200, self.window_size[1] // 2 + 180,
            GOLD, font_size=24, font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 绘制日志内容 - 最多显示10条
        log_y = self.window_size[1] // 2 + 150
        for log in self.battle_log[-10:]:
            arcade.draw_text(
                log,
                self.window_size[0] - 350, log_y,
                WHITE, font_size=14, font_name=("SimHei", "Microsoft YaHei"),
            )
            log_y -= 30
    
    def on_mouse_motion(self, x, y, dx, dy):
        """处理鼠标移动"""
        # 检查按钮悬停
        for button in self.buttons:
            button.check_mouse_hover(x, y)
    
    def on_mouse_press(self, x, y, button, modifiers):
        """处理鼠标点击"""
        # 返回按钮
        if self.buttons[0].check_mouse_press(x, y):
            from three_kingdoms_arcade import MainMenuView
            main_menu_view = MainMenuView(self.player.game)
            self.window.show_view(main_menu_view)
    
    def on_key_press(self, key, modifiers):
        """处理键盘按键"""
        if key == arcade.key.ESCAPE:
            from three_kingdoms_arcade import MainMenuView
            main_menu_view = MainMenuView(self.player.game)
            self.window.show_view(main_menu_view) 
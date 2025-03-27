﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
视图模块 - 向后兼容
此文件为向后兼容性而存在，实际实现已移至各个模块中
"""

# 导入所有需要的常量
from gui.constants import (
    WHITE, BLACK, RED, GREEN, BLUE, GOLD, BACKGROUND_COLOR
)

# 导入按钮类
from gui.ui.button import Button

# 导入视图类
from gui.views.battle_view import BattleView
from gui.views.city_view import CityView

# 为了让代码能正常工作，需要再导入一些依赖
import arcade
import random
import math
import time
import pygame
from PIL import Image, ImageDraw, ImageFont
from models.army import TroopType, Terrain, Army
from models.general import Skill

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

class BattleView(arcade.View):
    """战斗界面视图"""
    
    def __init__(self, game_window, window_size, player, battle_data):
        """初始化战斗视图"""
        super().__init__()  # arcade.View只需要简单初始化，不需要参数
        self.game_window = game_window
        self.window_size = window_size
        self.player = player
        self.battle_data = battle_data
        self.attacker = battle_data.attacker
        self.defender = battle_data.defender
        self.attacker_general = battle_data.attacker_general
        self.defender_general = battle_data.defender_general
        
        # 初始化字体对象
        # self.font_small = arcade.font.SysFont("SimHei", 14)
        # self.font_medium = arcade.font.SysFont("SimHei", 18)
        # self.screen = game_window.get_screen()  # 获取游戏窗口屏幕对象供pygame绘图
        
        # 战场位置设置
        self.attacker_positions = []  # 存储攻击方部队位置和引用
        self.defender_positions = []  # 存储防御方部队位置和引用
        
        # 战斗状态
        self.battle_phase = "准备"  # 准备, 远程, 近战, 追击, 撤退
        self.battle_log = []
        self.phase_buttons = []
        self.animations = []
        self.animation_enabled = True  # 是否启用动画
        self.animation_speed = 1.0     # 动画速度
        self.current_round = 1  # 当前回合数
        self.max_rounds = 5  # 最大回合数
        
        # 加载背景图
        try:
            self.background_texture = arcade.load_texture("assets/images/backgrounds/battlefield.jpg")
        except:
            self.background_texture = None
        
        # 士兵纹理
        self.soldier_textures = {}  # 用于存储不同兵种的士兵纹理
        
        # 特效纹理
        self.effect_textures = {
            "arrow": None,
            "fire": None,
            "sword": None,
            "shield": None
        }
        
        # 将领肖像
        self.general_portraits = {}
        
        # 初始化战场
        self.setup_battle()
    
    def setup_battle(self):
        """设置战斗界面"""
        # 清理旧数据
        self.attacker_positions = []
        self.defender_positions = []
        self.battle_log = []
        self.phase_buttons = []
        self.animations = []
        
        # 加载各类纹理和资源
        self.load_effect_textures()  # 加载特效纹理
        self.load_soldier_textures()  # 加载士兵纹理
        
        # 加载将军肖像
        if self.attacker_general:
            self.load_general_portraits()
        
        # 战场中心位置
        battlefield_center_x = self.window_size[0] / 2
        battlefield_center_y = self.window_size[1] / 2
        
        # 部署进攻方军队 - 采用更分散的阵型
        attacker_base_x = battlefield_center_x - 200  # 进攻方在左侧
        
        # 将进攻方军队分成多个单位，每个单位最多500兵力，更小的单位便于混战展示
        y_offset = 0
        remaining_troops = self.attacker.size
        while remaining_troops > 0:
            unit_size = min(500, remaining_troops)
            unit = Army(
                size=unit_size,
                primary_type=self.attacker.primary_type,
                secondary_type=self.attacker.secondary_type,
                morale=self.attacker.morale,
                training=self.attacker.training
            )
            
            # 创建更加随机化的阵型
            row = y_offset // 4
            col = y_offset % 4
            random_offset_x = random.uniform(-40, 40)
            random_offset_y = random.uniform(-30, 30)
            
            unit_x = attacker_base_x - 80 + col * 100 + random_offset_x
            unit_y = battlefield_center_y - 150 + row * 80 + random_offset_y
            
            self.attacker_positions.append((unit_x, unit_y, unit))
            remaining_troops -= unit_size
            y_offset += 1
        
        # 部署防守方军队 - 也采用更分散的阵型
        defender_base_x = battlefield_center_x + 200  # 防守方在右侧
        
        # 将防守方军队分成多个单位，每个单位最多500兵力
        y_offset = 0
        remaining_troops = self.defender.size
        while remaining_troops > 0:
            unit_size = min(500, remaining_troops)
            unit = Army(
                size=unit_size,
                primary_type=self.defender.primary_type,
                secondary_type=self.defender.secondary_type,
                morale=self.defender.morale,
                training=self.defender.training
            )
            
            # 创建更加随机化的阵型
            row = y_offset // 4
            col = y_offset % 4
            random_offset_x = random.uniform(-40, 40)
            random_offset_y = random.uniform(-30, 30)
            
            unit_x = defender_base_x + 80 - col * 100 + random_offset_x
            unit_y = battlefield_center_y - 150 + row * 80 + random_offset_y
            
            self.defender_positions.append((unit_x, unit_y, unit))
            remaining_troops -= unit_size
            y_offset += 1
        
        # 创建战斗控制按钮
        button_y = 50
        button_width = 150
        button_height = 40
        button_margin = 20
        
        # 添加下一阶段按钮
        next_button = Button(
            self.window_size[0]/2 - button_width - button_margin,
            button_y,
            button_width, button_height,
            "下一阶段", text_color=WHITE, bg_color=(180, 180, 220), hover_color=(100, 100, 150)
        )
        self.phase_buttons.append(("next_phase", next_button))
        
        # 添加自动战斗按钮
        auto_button = Button(
            self.window_size[0]/2 + button_margin,
            button_y,
            button_width, button_height,
            "自动战斗", text_color=WHITE, bg_color=(180, 220, 180), hover_color=(100, 150, 100)
        )
        self.phase_buttons.append(("auto_battle", auto_button))
        
        # 添加撤退按钮
        retreat_button = Button(
            self.window_size[0]/2 - button_width - button_margin,
            button_y - button_height - 10,
            button_width, button_height,
            "撤退", text_color=WHITE, bg_color=(220, 180, 180), hover_color=(150, 100, 100)
        )
        self.phase_buttons.append(("retreat", retreat_button))
        
        # 添加开关动画按钮
        animation_button = Button(
            self.window_size[0]/2 + button_margin,
            button_y - button_height - 10,
            button_width, button_height,
            "关闭动画" if self.animation_enabled else "开启动画",
            text_color=WHITE, bg_color=(180, 180, 180), hover_color=(120, 120, 120)
        )
        self.phase_buttons.append(("toggle_animation", animation_button))
        
        # 初始战斗日志
        terrain_effect = f"{self.battle_data.terrain}地形对{'进攻方' if self.battle_data.terrain_advantage == 'attacker' else '防守方' if self.battle_data.terrain_advantage == 'defender' else '双方均不'}有利"
        self.battle_log.append(f"战斗开始！{terrain_effect}")
        self.battle_log.append(f"进攻方: {self.attacker.size}兵力，{self.attacker.primary_type.value}为主")
        self.battle_log.append(f"防守方: {self.defender.size}兵力，{self.defender.primary_type.value}为主")
    
    def on_show(self):
        """视图显示时"""
        arcade.set_background_color(BACKGROUND_COLOR)
    
    def on_draw(self, delta_time=0):
        """绘制界面"""
        arcade.start_render()
        
        # 绘制背景图 - 新增
        if hasattr(self, 'background_texture') and self.background_texture:
            arcade.draw_texture_rectangle(
                640, 360,  # 画面中心
                1280, 720,  # 画面尺寸
                self.background_texture,
                alpha=150  # 调整透明度
            )
        
        # 绘制战场背景
        self.draw_battlefield_elements()
        
        # 绘制动画效果
        self.draw_animations(delta_time)
        
        # 绘制将领信息栏（界面右侧）
        self.draw_generals()
        
        # 绘制按钮
        for button_id, button in self.phase_buttons:
            button.draw()
    
    def draw_battlefield_elements(self):
        """绘制战场元素"""
        # 绘制战场背景
        self.draw_battlefield_background()
        
        # 绘制战况信息
        self.draw_battle_info()
        
        # 绘制进攻方部队
        self.draw_army(self.attacker_positions, is_attacker=True)
        
        # 绘制防守方部队
        self.draw_army(self.defender_positions, is_attacker=False)
        
        # 绘制将领
        self.draw_generals_on_battlefield()
        
        # 绘制战斗线 - 如果正在战斗中
        if self.battle_phase in ["近战", "远程", "冲锋"]:
            self.draw_battle_lines()
        
        # 绘制战场控制按钮
        self.draw_battle_controls()
        
        # 绘制战斗日志
        self.draw_battle_log()
        
    def draw_battlefield_background(self):
        """绘制战场背景"""
        # 绘制地形背景
        if self.battle_data.terrain == Terrain.PLAIN:
            bg_color = (100, 180, 100)  # 平原绿色
        elif self.battle_data.terrain == Terrain.MOUNTAIN:
            bg_color = (150, 150, 150)  # 山地灰色
        elif self.battle_data.terrain == Terrain.FOREST:
            bg_color = (60, 120, 60)  # 森林深绿
        elif self.battle_data.terrain == Terrain.RIVER:
            bg_color = (100, 150, 200)  # 河流蓝色
        elif self.battle_data.terrain == Terrain.MARSH:
            bg_color = (130, 110, 70)  # 沼泽棕色
        else:
            bg_color = (150, 150, 150)  # 默认灰色
        
        # 绘制战场区域
        arcade.draw_rectangle_filled(640, 360, 800, 400, bg_color)
        arcade.draw_rectangle_outline(640, 360, 800, 400, WHITE, 2)
        
        # 绘制中线
        arcade.draw_line(640, 160, 640, 560, WHITE, 2)
        
    def draw_army(self, positions, is_attacker=True):
        """绘制军队"""
        for x, y, army in positions:
            # 根据单位规模确定显示大小
            scale_factor = min(1.0, max(0.5, army.size / 1000))
            unit_width = 60 * scale_factor
            unit_height = 40 * scale_factor
            
            # 绘制军队底部阴影
            arcade.draw_ellipse_filled(x, y - 5 * scale_factor, 70 * scale_factor, 20 * scale_factor, (0, 0, 0, 80))
            
            # 确定兵种纹理和尺寸
            texture = None
            texture_width = 60 * scale_factor
            texture_height = 60 * scale_factor
            
            # 根据兵种选择纹理
            texture_prefix = "red" if is_attacker else "blue"
            if army.primary_type == TroopType.INFANTRY:
                texture = self.soldier_textures[f"infantry_{texture_prefix}"]
            elif army.primary_type == TroopType.CAVALRY:
                texture = self.soldier_textures[f"cavalry_{texture_prefix}"]
                texture_height = 65 * scale_factor  # 骑兵稍高一些
            elif army.primary_type == TroopType.ARCHER:
                texture = self.soldier_textures[f"archer_{texture_prefix}"]
            elif army.primary_type == TroopType.NAVY:
                texture = self.soldier_textures[f"navy_{texture_prefix}"]
            else:
                # 默认使用步兵纹理
                texture = self.soldier_textures[f"infantry_{texture_prefix}"]
            
            # 绘制士兵纹理
            if texture:
                arcade.draw_texture_rectangle(
                    x, y, 
                    texture_width, texture_height, 
                    texture
                )
            
            # 绘制士气条
            # 士气条背景
            arcade.draw_rectangle_filled(x, y + texture_height/2 + 5 * scale_factor, 50 * scale_factor, 6 * scale_factor, (50, 50, 50))
            
            # 士气条
            morale_width = 50 * scale_factor * (army.morale / 100)
            morale_color = arcade.color.GREEN
            if army.morale < 50:
                morale_color = arcade.color.YELLOW
            if army.morale < 25:
                morale_color = arcade.color.RED
                
            arcade.draw_rectangle_filled(
                x - 25 * scale_factor + morale_width/2, 
                y + texture_height/2 + 5 * scale_factor, 
                morale_width, 6 * scale_factor, 
                morale_color
            )
            
            # 绘制兵种标识
            arcade.draw_text(
                army.primary_type.value[:2],
                x, y - texture_height/2 - 10 * scale_factor,
                WHITE,
                font_size=max(10, int(16 * scale_factor)),
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center", anchor_y="center"
            )
            
            # 绘制兵力数量
            arcade.draw_text(
                f"{army.size}",
                x, y - texture_height/2 - 25 * scale_factor,
                WHITE,
                font_size=max(10, int(14 * scale_factor)),
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center", anchor_y="center"
            )

    def draw_battle_lines(self):
        """绘制战斗连接线，表示双方交战"""
        if not self.attacker_positions or not self.defender_positions:
            return
            
        # 获取游戏时间以创建动画效果
        current_time = pygame.time.get_ticks() / 1000.0
        
        # 找出前线的对战单位
        attacker_frontline = sorted(self.attacker_positions, key=lambda p: p[0], reverse=True)[:3]
        defender_frontline = sorted(self.defender_positions, key=lambda p: p[0])[:3]
        
        # 为每个前线单位创建战斗线
        for attacker_pos in attacker_frontline:
            for defender_pos in defender_frontline:
                # 计算距离
                dist = math.sqrt((attacker_pos[0] - defender_pos[0])**2 + (attacker_pos[1] - defender_pos[1])**2)
                
                # 只连接距离适中的单位
                if dist < 350:
                    # 动态决定线条颜色 - 根据战斗阶段
                    if self.battle_phase == "近战":
                        line_color = (200, 50, 50)  # 红色表示近战
                    elif self.battle_phase == "远程":
                        line_color = (50, 150, 50)  # 绿色表示远程
                    else:  # 冲锋
                        line_color = (200, 150, 50)  # 黄色表示冲锋
                    
                    # 计算两点之间的中点，稍微随机化位置
                    mid_x = (attacker_pos[0] + defender_pos[0]) / 2 + random.uniform(-15, 15)
                    mid_y = (attacker_pos[1] + defender_pos[1]) / 2 + random.uniform(-15, 15)
                    
                    # 创建波浪效果 - 使用正弦函数
                    segments = 12
                    last_x, last_y = attacker_pos[0], attacker_pos[1]
                    
                    # 绘制从进攻方到防守方的分段线条
                    for i in range(1, segments + 1):
                        t = i / segments
                        # 使用二次贝塞尔曲线计算点
                        next_x = (1-t)**2 * attacker_pos[0] + 2*(1-t)*t*mid_x + t**2 * defender_pos[0]
                        next_y = (1-t)**2 * attacker_pos[1] + 2*(1-t)*t*mid_y + t**2 * defender_pos[1]
                        
                        # 添加基于时间的波动效果
                        wave_factor = 5 * math.sin(current_time * 5 + i)
                        next_x += wave_factor * math.sin(i / segments * math.pi)
                        next_y += wave_factor * math.cos(i / segments * math.pi)
                        
                        # 绘制线段
                        arcade.draw_line(
                            last_x, last_y,
                            next_x, next_y,
                            line_color, 2
                        )
                        
                        last_x, last_y = next_x, next_y
                        
                    # 如果是近战，添加一些冲突粒子
                    if self.battle_phase == "近战" and random.random() < 0.1:
                        conflict_x = mid_x + random.uniform(-10, 10)
                        conflict_y = mid_y + random.uniform(-10, 10)
                        
                        # 添加冲突特效
                        for _ in range(4):
                            angle = random.uniform(0, math.pi * 2)
                            speed = random.uniform(20, 40)
                            lifetime = random.uniform(0.2, 0.5)
                            
                            particle = {
                                "x": conflict_x,
                                "y": conflict_y,
                                "vx": math.cos(angle) * speed,
                                "vy": math.sin(angle) * speed,
                                "color": (255, 200, 50),
                                "size": random.uniform(2, 4),
                                "life": lifetime,
                                "max_life": lifetime
                            }
                            
                            self.animations.append(particle)
        
    def draw_battle_controls(self):
        """绘制战场控制按钮"""
        for button_id, button in self.phase_buttons:
            button.draw()
            
    def draw_battle_log(self):
        """绘制战斗日志"""
        log_y = 500
        for i, log in enumerate(self.battle_log[-5:]):  # 只显示最新的5条日志
            arcade.draw_text(
                log,
                1050, log_y - i * 30,
                WHITE,
                font_size=14,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
    
    def draw_battle_info(self):
        """绘制战斗信息"""
        # 绘制战斗阶段
        arcade.draw_text(
            f"当前阶段: {self.battle_phase}   回合: {self.current_round}/{self.max_rounds}",
            640, 620,
            WHITE,
            font_size=24,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 绘制战场地形
        arcade.draw_text(
            f"战场地形: {self.battle_data.terrain.value}",
            200, 620,
            WHITE,
            font_size=18,
            font_name=("SimHei", "Microsoft YaHei")
        )
    
    def on_mouse_motion(self, x, y, dx, dy):
        """处理鼠标移动"""
        # 检查鼠标是否悬停在按钮上
        for button_id, button in self.phase_buttons:
            button.check_mouse_hover(x, y)
            
    def on_mouse_press(self, x, y, button, modifiers):
        """处理鼠标点击"""
        # 检查是否点击了任何按钮
        for button_id, btn in self.phase_buttons:
            if btn.check_mouse_press(x, y):
                if button_id == "next_phase":
                    self.next_battle_phase()
                elif button_id == "auto_battle":
                    self.auto_battle()
                elif button_id == "retreat":
                    self.retreat()
                elif button_id == "toggle_animation":
                    self.toggle_animations()
                    # 更新按钮文本
                    btn.text = "关闭动画" if self.animation_enabled else "开启动画"
    
    def toggle_animations(self):
        """切换动画效果"""
        self.animation_enabled = not self.animation_enabled
        status = "开启" if self.animation_enabled else "关闭"
        self.battle_log.append(f"战斗动画效果已{status}")
    
    def create_attack_animation(self, attacker_position, defender_position, attack_type="arrow"):
        """创建攻击动画"""
        if not self.animation_enabled:
            return
            
        # 获取单位位置
        start_x, start_y, _ = attacker_position
        end_x, end_y, _ = defender_position
        
        # 创建基本动画
        animation = {
            "type": attack_type,
            "start": (start_x, start_y),
            "end": (end_x, end_y),
            "progress": 0.0,
            "speed": 0.02 * self.animation_speed if hasattr(self, 'animation_speed') else 0.02,
            "particles": []
        }
        
        # 根据类型添加粒子效果
        if attack_type == "arrow":
            # 箭矢轨迹粒子
            for _ in range(5):
                animation["particles"].append({
                    "x": start_x,
                    "y": start_y,
                    "vx": (end_x - start_x) * 0.02 + random.uniform(-1, 1),
                    "vy": (end_y - start_y) * 0.02 + random.uniform(-1, 1),
                    "size": random.uniform(1, 3),
                    "color": (200, 200, 200, 150)
                })
                
        elif attack_type == "fire":
            # 火焰粒子
            for _ in range(15):
                animation["particles"].append({
                    "x": start_x,
                    "y": start_y,
                    "vx": (end_x - start_x) * 0.02 + random.uniform(-2, 2),
                    "vy": (end_y - start_y) * 0.02 + random.uniform(-2, 2),
                    "size": random.uniform(2, 5),
                    "color": (255, random.randint(100, 200), 0, 150)
                })
                
        elif attack_type == "sword":
            # 剑气粒子
            for _ in range(10):
                animation["particles"].append({
                    "x": start_x,
                    "y": start_y,
                    "vx": (end_x - start_x) * 0.02 + random.uniform(-1.5, 1.5),
                    "vy": (end_y - start_y) * 0.02 + random.uniform(-1.5, 1.5),
                    "size": random.uniform(1.5, 4),
                    "color": (200, 200, 255, 150)
                })
                
        self.animations.append(animation)
    
    def next_battle_phase(self):
        """进入下一战斗阶段"""
        # 战斗阶段顺序
        phases = ["准备", "远程阶段", "近战阶段", "追击阶段", "撤退阶段"]
        
        current_index = phases.index(self.battle_phase)
        if current_index < len(phases) - 1:
            self.battle_phase = phases[current_index + 1]
            self.battle_log.append(f"进入{self.battle_phase}")
            
            # 根据阶段添加相应的战斗效果
            if self.battle_phase == "远程阶段":
                self.simulate_ranged_combat()
            elif self.battle_phase == "近战阶段":
                self.simulate_melee_combat()
            elif self.battle_phase == "追击阶段":
                self.simulate_pursuit_phase()
        else:
            # 回合结束，进入新回合
            self.current_round += 1
            if self.current_round <= self.max_rounds:
                self.battle_phase = phases[0]
                self.battle_log.append(f"回合{self.current_round}开始")
            else:
                # 战斗结束
                self.battle_log.append("战斗结束")
                self.end_battle()
    
    def simulate_ranged_combat(self):
        """模拟远程战斗阶段"""
        # 检查双方是否有弓箭手单位
        attacker_archers = [pos for pos in self.attacker_positions 
                           if pos[2].primary_type == TroopType.ARCHER or 
                              pos[2].secondary_type == TroopType.ARCHER]
        
        defender_archers = [pos for pos in self.defender_positions 
                           if pos[2].primary_type == TroopType.ARCHER or 
                              pos[2].secondary_type == TroopType.ARCHER]
        
        # 进攻方弓箭手攻击
        if attacker_archers:
            self.battle_log.append("进攻方弓箭手发动攻击")
            for archer_pos in attacker_archers:
                if self.defender_positions:
                    target = random.choice(self.defender_positions)
                    # 计算伤害
                    damage = int(archer_pos[2].size * 0.1)
                    target[2].take_casualties(damage)
                    
                    self.battle_log.append(f"我方弓箭手部队射击，敌军损失{damage}人")
                    
                    # 创建箭矢动画
                    self.create_attack_animation(archer_pos, target, "arrow")
        
        # 防守方弓箭手攻击
        if defender_archers:
            self.battle_log.append("防守方弓箭手发动攻击")
            for archer_pos in defender_archers:
                if self.attacker_positions:
                    target = random.choice(self.attacker_positions)
                    # 计算伤害
                    damage = int(archer_pos[2].size * 0.1)
                    target[2].take_casualties(damage)
                    
                    self.battle_log.append(f"敌方弓箭手部队射击，我军损失{damage}人")
                    
                    # 创建箭矢动画
                    self.create_attack_animation(archer_pos, target, "arrow")
        
        # 将领技能效果
        if self.attacker_general and hasattr(self.attacker_general, 'skills'):
            # 检查火攻技能
            if any(skill == Skill.FIRE_ATTACK for skill in self.attacker_general.skills):
                self.battle_log.append(f"{self.attacker_general.name}发动火攻!")
                
                for i, defender_pos in enumerate(self.defender_positions):
                    # 火攻造成额外伤害
                    fire_damage = int(defender_pos[2].size * 0.05)
                    defender_pos[2].take_casualties(fire_damage)
                    
                    # 创建火焰动画
                    if self.attacker_positions:
                        attacker_source = random.choice(self.attacker_positions)
                        self.create_attack_animation(attacker_source, defender_pos, "fire")
                
                self.battle_log.append(f"火攻造成了额外伤害!")
    
    def simulate_melee_combat(self):
        """模拟近战战斗阶段"""
        # 初始化战斗结果数据
        attacker_casualties = 0
        defender_casualties = 0
        attacker_morale_loss = 0
        defender_morale_loss = 0
        combat_log_entries = []
        
        # 检查是否存在将领，并获取将领加成
        attacker_general_bonus = 0
        defender_general_bonus = 0
        
        if self.attacker_general:
            attacker_general_bonus = self.attacker_general.strength * 0.02  # 将领武力值转换为战斗加成
            combat_log_entries.append(f"{self.attacker_general.name}指挥进攻，提供{attacker_general_bonus:.1f}战斗加成")
        
        if self.defender_general:
            defender_general_bonus = self.defender_general.strength * 0.02
            combat_log_entries.append(f"{self.defender_general.name}指挥防守，提供{defender_general_bonus:.1f}战斗加成")
        
        # 计算总战斗力
        attacker_strength = self.attacker.size * (1 + self.attacker.training * 0.1) * (1 + attacker_general_bonus)
        defender_strength = self.defender.size * (1 + self.defender.training * 0.1) * (1 + defender_general_bonus)
        
        # 考虑特殊地形效果
        terrain_modifier = 1.0
        if self.battle_data.terrain == Terrain.FOREST and self.attacker.primary_type == TroopType.CAVALRY:
            terrain_modifier = 0.7
            combat_log_entries.append("森林地形削弱了骑兵的冲击力")
        elif self.battle_data.terrain == Terrain.MOUNTAIN:
            # 山地对防守方有利
            defender_strength *= 1.2
            combat_log_entries.append("山地地形增强了防守方的防御力")
        elif self.battle_data.terrain == Terrain.PLAIN and self.attacker.primary_type == TroopType.CAVALRY:
            # 平原对骑兵有利
            attacker_strength *= 1.2
            combat_log_entries.append("平原地形增强了进攻方骑兵的冲击力")
        
        # 计算战斗过程
        combat_ratio = attacker_strength / max(1, defender_strength)
        base_casualties_percentage = 0.05  # 基础伤亡率
        
        # 将领混战效果 - 如果双方都有将领，有机会触发将领个人战斗
        general_duel_occurred = False
        if self.attacker_general and self.defender_general and random.random() < 0.4:  # 40%概率触发将领决斗
            general_duel_occurred = True
            combat_log_entries.append(f"🏆 {self.attacker_general.name}与{self.defender_general.name}展开了将领决斗！")
            
            # 决定决斗胜负
            attacker_duel_strength = self.attacker_general.strength * (0.8 + random.random() * 0.4)  # 随机因素
            defender_duel_strength = self.defender_general.strength * (0.8 + random.random() * 0.4)
            
            # 显示将领技能效果
            if hasattr(self.attacker_general, 'skills') and self.attacker_general.skills:
                skill = self.attacker_general.skills[0]
                attacker_duel_strength *= 1.1  # 技能提供10%加成
                combat_log_entries.append(f"{self.attacker_general.name}发动了{skill.name}，战斗力提升！")
                # 添加特效
                self.add_skill_effect(is_attacker=True)
            
            if hasattr(self.defender_general, 'skills') and self.defender_general.skills:
                skill = self.defender_general.skills[0]
                defender_duel_strength *= 1.1  # 技能提供10%加成
                combat_log_entries.append(f"{self.defender_general.name}发动了{skill.name}，战斗力提升！")
                # 添加特效
                self.add_skill_effect(is_attacker=False)
            
            if attacker_duel_strength > defender_duel_strength * 1.2:  # 显著优势
                # 进攻方将领大胜
                combat_log_entries.append(f"👑 {self.attacker_general.name}大胜，大幅提升军队士气！")
                attacker_morale_loss -= 5  # 减少士气损失
                defender_morale_loss += 10  # 增加对方士气损失
                defender_casualties += int(self.defender.size * 0.03)  # 额外伤亡
                combat_ratio *= 1.3  # 战斗力提升
                
                # 添加将领胜利特效
                self.add_general_victory_effect(is_attacker=True)
                
            elif attacker_duel_strength > defender_duel_strength:
                # 进攻方将领小胜
                combat_log_entries.append(f"👑 {self.attacker_general.name}小胜，提升军队士气！")
                attacker_morale_loss -= 3
                defender_morale_loss += 5
                combat_ratio *= 1.15
                
                # 添加将领胜利特效
                self.add_general_victory_effect(is_attacker=True)
                
            elif defender_duel_strength > attacker_duel_strength * 1.2:
                # 防守方将领大胜
                combat_log_entries.append(f"👑 {self.defender_general.name}大胜，大幅提升军队士气！")
                defender_morale_loss -= 5
                attacker_morale_loss += 10
                attacker_casualties += int(self.attacker.size * 0.03)
                combat_ratio *= 0.7
                
                # 添加将领胜利特效
                self.add_general_victory_effect(is_attacker=False)
                
            else:
                # 防守方将领小胜
                combat_log_entries.append(f"👑 {self.defender_general.name}小胜，提升军队士气！")
                defender_morale_loss -= 3
                attacker_morale_loss += 5
                combat_ratio *= 0.85
                
                # 添加将领胜利特效
                self.add_general_victory_effect(is_attacker=False)
        
        # 计算实际伤亡
        if combat_ratio > 1.5:
            # 进攻方优势明显
            attacker_casualty_percentage = base_casualties_percentage * 0.7
            defender_casualty_percentage = base_casualties_percentage * 1.5 * combat_ratio
            attacker_morale_loss += 1
            defender_morale_loss += 4
            
            if combat_ratio > 2.5:
                combat_log_entries.append("进攻方压倒性优势，防守方损失惨重！")
            else:
                combat_log_entries.append("进攻方占优势，防守方承受较大损失")
                
        elif combat_ratio < 0.67:
            # 防守方优势明显
            attacker_casualty_percentage = base_casualties_percentage * 1.5 / combat_ratio
            defender_casualty_percentage = base_casualties_percentage * 0.7
            attacker_morale_loss += 4
            defender_morale_loss += 1
            
            if combat_ratio < 0.4:
                combat_log_entries.append("防守方压倒性优势，进攻方损失惨重！")
            else:
                combat_log_entries.append("防守方占优势，进攻方承受较大损失")
                
        else:
            # 势均力敌
            attacker_casualty_percentage = base_casualties_percentage * (1.2 - 0.4 * combat_ratio)
            defender_casualty_percentage = base_casualties_percentage * combat_ratio
            attacker_morale_loss += 2
            defender_morale_loss += 2
            combat_log_entries.append("双方势均力敌，战斗激烈")
        
        # 计算实际伤亡人数
        attacker_casualties += int(self.attacker.size * attacker_casualty_percentage)
        defender_casualties += int(self.defender.size * defender_casualty_percentage)
        
        # 部队减员
        self.attacker.size -= attacker_casualties
        self.defender.size -= defender_casualties
        
        # 处理士气损失
        self.attacker.morale = max(0, self.attacker.morale - attacker_morale_loss)
        self.defender.morale = max(0, self.defender.morale - defender_morale_loss)
        
        # 记录战斗结果到日志
        combat_log_entries.append(f"进攻方损失: {attacker_casualties}兵力，士气降低{attacker_morale_loss}点")
        combat_log_entries.append(f"防守方损失: {defender_casualties}兵力，士气降低{defender_morale_loss}点")
        
        # 更新战斗日志
        self.battle_log.extend(combat_log_entries)
        
        # 创建战斗动画效果
        if self.animation_enabled:
            self.create_melee_combat_animations(attacker_casualties, defender_casualties, general_duel_occurred)
        
        # 检查战斗是否结束
        self.check_battle_end()
    
    def add_skill_effect(self, is_attacker=True):
        """添加将领技能特效"""
        if not self.animation_enabled:
            return
            
        effect_count = 20
        
        if is_attacker:
            if not self.attacker_general:
                return
                
            general_pos = (self.window_size[0] * 0.25, self.window_size[1] * 0.4)
            color = (255, 215, 0)  # 金色
        else:
            if not self.defender_general:
                return
                
            general_pos = (self.window_size[0] * 0.75, self.window_size[1] * 0.4)
            color = (0, 191, 255)  # 蓝色
        
        # 创建光芒四射特效
        for i in range(effect_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(80, 150)
            size = random.uniform(3, 8)
            lifetime = random.uniform(0.5, 1.5)
            
            particle = {
                "x": general_pos[0],
                "y": general_pos[1],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": color,
                "size": size,
                "life": lifetime,
                "max_life": lifetime
            }
            
            self.animations.append(particle)
    
    def add_general_victory_effect(self, is_attacker=True):
        """添加将领胜利特效"""
        if not self.animation_enabled:
            return
            
        if is_attacker:
            if not self.attacker_general:
                return
                
            general_pos = (self.window_size[0] * 0.25, self.window_size[1] * 0.4)
            color = (255, 215, 0)  # 金色
        else:
            if not self.defender_general:
                return
                
            general_pos = (self.window_size[0] * 0.75, self.window_size[1] * 0.4)
            color = (0, 191, 255)  # 蓝色
        
        # 创建圆形扩散效果
        for radius in [40, 60, 80]:
            for i in range(int(radius)):
                angle = (i / radius) * math.pi * 2
                x = general_pos[0] + math.cos(angle) * radius
                y = general_pos[1] + math.sin(angle) * radius
                lifetime = 0.8 + (radius / 100)
                
                particle = {
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * 20,
                    "vy": math.sin(angle) * 20,
                    "color": color,
                    "size": 3,
                    "life": lifetime,
                    "max_life": lifetime
                }
                
                self.animations.append(particle)
        
        # 添加文字特效
        text_particle = {
            "x": general_pos[0],
            "y": general_pos[1] - 70,
            "vx": 0,
            "vy": -15,
            "text": "将领胜利!",
            "color": color,
            "size": 24,
            "life": 2.0,
            "max_life": 2.0,
            "is_text": True
        }
        
        self.animations.append(text_particle)
        
    def create_melee_combat_animations(self, attacker_casualties, defender_casualties, general_duel_occurred=False):
        """创建近战战斗的动画效果"""
        if not self.animation_enabled:
            return
            
        # 获取双方位置
        attacker_center = self.calculate_army_center(self.attacker_positions)
        defender_center = self.calculate_army_center(self.defender_positions)
        
        # 创建冲突点 - 在两军中点略微随机化
        conflict_x = (attacker_center[0] + defender_center[0]) / 2 + random.uniform(-30, 30)
        conflict_y = (attacker_center[1] + defender_center[1]) / 2 + random.uniform(-30, 30)
        
        # 双方伤亡血液效果
        self.create_blood_effects(conflict_x, conflict_y, attacker_casualties, True)
        self.create_blood_effects(conflict_x, conflict_y, defender_casualties, False)
        
        # 如果发生将领决斗，添加特殊效果
        if general_duel_occurred and self.attacker_general and self.defender_general:
            # 创建决斗线
            attacker_general_pos = (self.window_size[0] * 0.25, self.window_size[1] * 0.4)
            defender_general_pos = (self.window_size[0] * 0.75, self.window_size[1] * 0.4)
            
            # 创建闪光效果
            for _ in range(10):
                flash_x = (attacker_general_pos[0] + defender_general_pos[0]) / 2 + random.uniform(-50, 50)
                flash_y = (attacker_general_pos[1] + defender_general_pos[1]) / 2 + random.uniform(-30, 30)
                
                # 闪光粒子
                for i in range(15):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(30, 80)
                    size = random.uniform(2, 6)
                    lifetime = random.uniform(0.5, 1.0)
                    
                    particle = {
                        "x": flash_x,
                        "y": flash_y,
                        "vx": math.cos(angle) * speed,
                        "vy": math.sin(angle) * speed,
                        "color": (255, 255, 200) if random.random() > 0.5 else (200, 200, 255),
                        "size": size,
                        "life": lifetime,
                        "max_life": lifetime
                    }
                    
                    self.animations.append(particle)
            
            # 添加文字特效
            text_particle = {
                "x": (attacker_general_pos[0] + defender_general_pos[0]) / 2,
                "y": (attacker_general_pos[1] + defender_general_pos[1]) / 2 - 50,
                "vx": 0,
                "vy": -10,
                "text": "将领决斗!",
                "color": (255, 215, 0),
                "size": 26,
                "life": 2.0,
                "max_life": 2.0,
                "is_text": True
            }
            
            self.animations.append(text_particle)
            
    def calculate_army_center(self, positions):
        """计算军队的中心位置"""
        if not positions:
            return (0, 0)
            
        total_x = 0
        total_y = 0
        total_units = len(positions)
        
        for pos in positions:
            total_x += pos[0]
            total_y += pos[1]
            
        return (total_x / total_units, total_y / total_units)
        
    def create_blood_effects(self, center_x, center_y, casualties, is_attacker):
        """创建伤亡血液效果"""
        if casualties <= 0:
            return
            
        # 根据伤亡数量确定特效数量
        effect_count = min(int(casualties / 100) + 1, 20)
        
        # 决定特效颜色
        color = (200, 50, 50)  # 血红色
        
        # 决定方向 - 伤亡方向相反
        direction_x = -1 if is_attacker else 1
        
        # 创建粒子
        for _ in range(effect_count):
            # 随机化位置
            x = center_x + random.uniform(-40, 40)
            y = center_y + random.uniform(-30, 30)
            
            # 随机化速度，但保持方向性
            vx = direction_x * random.uniform(20, 50)
            vy = random.uniform(-30, 30)
            
            # 随机大小和生命周期
            size = random.uniform(3, 6)
            lifetime = random.uniform(0.5, 1.2)
            
            # 创建粒子
            particle = {
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "color": color,
                "size": size,
                "life": lifetime,
                "max_life": lifetime
            }
            
            self.animations.append(particle)
    
    def simulate_pursuit_phase(self):
        """模拟追击阶段"""
        # 计算双方剩余兵力
        attacker_remaining = sum(army.size for _, _, army in self.attacker_positions)
        defender_remaining = sum(army.size for _, _, army in self.defender_positions)
        
        # 判断谁占上风
        if attacker_remaining > defender_remaining * 1.2:
            # 进攻方占上风，追击
            self.battle_log.append("我军占据优势，开始追击")
            
            for defender_pos in self.defender_positions:
                # 追击造成额外伤害
                pursuit_damage = int(defender_pos[2].size * 0.1)
                defender_pos[2].take_casualties(pursuit_damage)
                
                # 创建追击动画
                if self.attacker_positions:
                    attacker_source = random.choice(self.attacker_positions)
                    self.create_attack_animation(attacker_source, defender_pos, "sword")
            
            self.battle_log.append(f"追击造成敌军额外损失")
            
        elif defender_remaining > attacker_remaining * 1.2:
            # 防守方占上风，反击
            self.battle_log.append("敌军反击")
            
            for attacker_pos in self.attacker_positions:
                # 反击造成额外伤害
                counter_damage = int(attacker_pos[2].size * 0.1)
                attacker_pos[2].take_casualties(counter_damage)
                
                # 创建反击动画
                if self.defender_positions:
                    defender_source = random.choice(self.defender_positions)
                    self.create_attack_animation(defender_source, attacker_pos, "sword")
            
            self.battle_log.append(f"敌军反击造成我军额外损失")
            
        else:
            # 势均力敌，双方撤退
            self.battle_log.append("双方势均力敌，各自后撤整顿")
            
        # 将领鼓舞效果
        if self.attacker_general and hasattr(self.attacker_general, 'skills'):
            # 检查鼓舞技能
            if any(skill == Skill.INSPIRE for skill in self.attacker_general.skills) and self.attacker_positions:
                self.battle_log.append(f"{self.attacker_general.name}鼓舞军心!")
                
                # 为所有友军单位提升士气
                for i, (x, y, army) in enumerate(self.attacker_positions):
                    # 提升士气
                    army.morale = min(100, army.morale + 10)
                    self.attacker_positions[i] = (x, y, army)
                
                # 创建鼓舞效果动画
                for pos in self.attacker_positions:
                    animation = {
                        "type": "shield",
                        "start": (pos[0], pos[1]),
                        "end": (pos[0], pos[1] + 20),
                        "progress": 0.0,
                        "speed": 0.02 * self.animation_speed,
                        "particles": []
                    }
                    
                    # 添加光芒粒子
                    for _ in range(10):
                        angle = random.uniform(0, math.pi * 2)
                        speed = random.uniform(0.5, 1.5)
                        animation["particles"].append({
                            "x": pos[0],
                            "y": pos[1],
                            "vx": math.cos(angle) * speed,
                            "vy": math.sin(angle) * speed,
                            "size": random.uniform(2, 4),
                            "color": (255, 255, 200, 180)
                        })
                    
                    self.animations.append(animation)
                
                self.battle_log.append(f"军心大振，士气提升!")
    
    def auto_battle(self):
        """自动战斗"""
        self.battle_log.append("自动战斗开始")
        
        # 模拟各个战斗阶段
        if self.animation_enabled:
            # 有动画时，依次执行每个阶段
            phases = ["远程阶段", "近战阶段", "追击阶段"]
            for phase in phases:
                self.battle_phase = phase
                self.battle_log.append(f"进入{phase}")
                
                if phase == "远程阶段":
                    self.simulate_ranged_combat()
                elif phase == "近战阶段":
                    self.simulate_melee_combat()
                elif phase == "追击阶段":
                    self.simulate_pursuit_phase()
        else:
            # 无动画时，快速计算战斗结果
            for _ in range(self.max_rounds - self.current_round + 1):
                # 计算远程战斗伤亡
                for i, (x, y, army) in enumerate(self.attacker_positions):
                    if army.primary_type == TroopType.ARCHER:
                        casualties_multiplier = 0.2
                    else:
                        casualties_multiplier = 0.15
                        
                    casualties = int(army.size * casualties_multiplier)
                    army.take_casualties(casualties)
                    self.attacker_positions[i] = (x, y, army)
                
                for i, (x, y, army) in enumerate(self.defender_positions):
                    if army.primary_type == TroopType.ARCHER:
                        casualties_multiplier = 0.2
                    else:
                        casualties_multiplier = 0.15
                        
                    casualties = int(army.size * casualties_multiplier)
                    army.take_casualties(casualties)
                    self.defender_positions[i] = (x, y, army)
                
                # 将领效果
                if self.attacker_general and hasattr(self.attacker_general, 'skills'):
                    # 火攻技能
                    if any(skill == Skill.FIRE_ATTACK for skill in self.attacker_general.skills):
                        for i, (x, y, army) in enumerate(self.defender_positions):
                            fire_damage = int(army.size * 0.05)
                            army.take_casualties(fire_damage)
                            self.defender_positions[i] = (x, y, army)
                        self.battle_log.append(f"{self.attacker_general.name}的火攻造成额外伤害")
                    
                    # 鼓舞技能
                    if any(skill == Skill.INSPIRE for skill in self.attacker_general.skills):
                        for i, (x, y, army) in enumerate(self.attacker_positions):
                            army.morale = min(100, army.morale + 5)
                            self.attacker_positions[i] = (x, y, army)
                        self.battle_log.append(f"{self.attacker_general.name}鼓舞军心，提升士气")
        
        # 战斗结束
        self.battle_log.append("战斗结束")
        self.end_battle()
    
    def retreat(self):
        """撤退"""
        self.battle_log.append("你选择了撤退")
        
        # 撤退惩罚：士气降低
        for _, _, army in self.attacker_positions:
            army.morale = max(10, army.morale - 30)
        
        # 结束战斗
        self.end_battle(is_retreat=True)
    
    def end_battle(self, is_retreat=False):
        """结束战斗"""
        # 计算剩余兵力
        attacker_remaining = sum(army.size for _, _, army in self.attacker_positions)
        defender_remaining = sum(army.size for _, _, army in self.defender_positions)
        
        # 判断胜负
        if is_retreat:
            winner = "defender"
            self.battle_result = "defeat"
            self.battle_log.append("战斗失败！你的军队撤退了")
        elif attacker_remaining > defender_remaining * 1.5:
            winner = "attacker"
            self.battle_result = "victory"
            self.battle_log.append("战斗胜利！敌军被击溃")
            
            # 胜利特效
            if self.animation_enabled:
                # 为所有友军单位创建胜利动画
                for pos in self.attacker_positions:
                    animation = {
                        "type": "shield",
                        "start": (pos[0], pos[1]),
                        "end": (pos[0], pos[1] + 30),
                        "progress": 0.0,
                        "speed": 0.01 * self.animation_speed,
                        "particles": []
                    }
                    
                    # 添加胜利光芒粒子
                    for _ in range(15):
                        angle = random.uniform(0, math.pi * 2)
                        speed = random.uniform(0.5, 2.0)
                        animation["particles"].append({
                            "x": pos[0],
                            "y": pos[1],
                            "vx": math.cos(angle) * speed,
                            "vy": math.sin(angle) * speed,
                            "size": random.uniform(2, 5),
                            "color": (255, 255, 100, 180)
                        })
                    
                    self.animations.append(animation)
            
        elif defender_remaining > attacker_remaining * 1.5:
            winner = "defender"
            self.battle_result = "defeat"
            self.battle_log.append("战斗失败！我军被击溃")
            
            # 失败特效
            if self.animation_enabled:
                # 为所有友军单位创建失败动画
                for pos in self.attacker_positions:
                    animation = {
                        "type": "fire",
                        "start": (pos[0], pos[1]),
                        "end": (pos[0], pos[1]),
                        "progress": 0.0,
                        "speed": 0.01 * self.animation_speed,
                        "particles": []
                    }
                    
                    # 添加失败烟雾粒子
                    for _ in range(10):
                        angle = random.uniform(0, math.pi * 2)
                        speed = random.uniform(0.3, 1.0)
                        animation["particles"].append({
                            "x": pos[0],
                            "y": pos[1],
                            "vx": math.cos(angle) * speed,
                            "vy": math.sin(angle) * speed,
                            "size": random.uniform(3, 6),
                            "color": (100, 100, 100, 150)
                        })
                    
                    self.animations.append(animation)
                    
        else:
            winner = "draw"
            self.battle_result = "draw"
            self.battle_log.append("战斗平局！双方均有损失")
        
        # 创建结束战斗的按钮
        self.buttons = []
        
        # 显示战斗结果
        result_text = "战斗胜利" if self.battle_result == "victory" else "战斗失败" if self.battle_result == "defeat" else "战斗平局"
        result_bg_color = (80, 150, 80) if self.battle_result == "victory" else (150, 80, 80) if self.battle_result == "defeat" else (100, 100, 100)
        
        # 战斗结果按钮（仅用于显示）
        result_button = Button(
            640, 180, 300, 70, result_text, 
            bg_color=result_bg_color
        )
        self.buttons.append(result_button)
        
        # 返回地图按钮
        end_button = Button(
            640, 100, 200, 50, "返回地图", bg_color=(100, 100, 100)
        )
        self.buttons.append(end_button)
        
        # 在这里可以添加战斗结算逻辑
        # 经验值、战利品等
    
    def on_key_press(self, key, modifiers):
        """处理键盘按键事件"""
        # ESC键返回主菜单
        if key == arcade.key.ESCAPE:
            from three_kingdoms_arcade import MainMenuView
            main_menu_view = MainMenuView(self.game)
            self.window.show_view(main_menu_view)

    def load_effect_textures(self):
        """加载特效纹理"""
        try:
            self.effect_textures["arrow"] = arcade.load_texture("resources/effects/arrow.png")
        except:
            # 创建一个简单的箭头纹理 - 使用PIL代替
            arrow_img = Image.new("RGBA", (80, 20), (0, 0, 0, 0))
            draw = ImageDraw.Draw(arrow_img)
            # 绘制箭头三角形
            draw.polygon([(0, 10), (60, 0), (60, 20)], fill=(255, 255, 255, 255))
            draw.polygon([(60, 0), (80, 10), (60, 20)], fill=(255, 255, 255, 255))
            
            # 转换为arcade纹理
            self.effect_textures["arrow"] = arcade.Texture("arrow", arrow_img)
            
        try:
            self.effect_textures["fire"] = arcade.load_texture("resources/effects/fire.png")
        except:
            # 创建一个简单的火焰纹理
            fire_img = Image.new("RGBA", (40, 60), (0, 0, 0, 0))
            draw = ImageDraw.Draw(fire_img)
            # 绘制椭圆形火焰
            draw.ellipse((5, 10, 35, 50), fill=(255, 100, 0, 200))
            draw.ellipse((10, 5, 30, 40), fill=(255, 200, 0, 200))
            
            # 转换为arcade纹理
            self.effect_textures["fire"] = arcade.Texture("fire", fire_img)
            
        try:
            self.effect_textures["sword"] = arcade.load_texture("resources/effects/sword.png")
        except:
            # 创建一个简单的剑纹理
            sword_img = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
            draw = ImageDraw.Draw(sword_img)
            # 绘制剑身
            draw.rectangle((26, 5, 34, 55), fill=(192, 192, 192, 255))  # 银色
            # 绘制剑柄
            draw.rectangle((15, 12, 45, 18), fill=(255, 215, 0, 255))  # 金色
            
            # 转换为arcade纹理
            self.effect_textures["sword"] = arcade.Texture("sword", sword_img)
            
        try:
            self.effect_textures["shield"] = arcade.load_texture("resources/effects/shield.png")
        except:
            # 创建一个简单的盾牌纹理
            shield_img = Image.new("RGBA", (50, 60), (0, 0, 0, 0))
            draw = ImageDraw.Draw(shield_img)
            # 绘制椭圆形盾牌
            draw.ellipse((0, 0, 50, 60), fill=(100, 100, 100, 200))
            draw.ellipse((5, 5, 45, 55), fill=(150, 150, 150, 200))
            
            # 转换为arcade纹理
            self.effect_textures["shield"] = arcade.Texture("shield", shield_img)
    
    def load_general_portraits(self):
        """加载将领头像"""
        # 尝试加载默认将领头像
        try:
            self.default_general_texture = arcade.load_texture("resources/generals/liubei.png")
        except:
            # 创建默认将领头像 - 使用PIL
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建默认头像图像
            portrait_img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
            draw = ImageDraw.Draw(portrait_img)
            # 绘制圆形背景
            draw.ellipse((5, 5, 95, 95), fill=(112, 128, 144, 255))  # 蓝灰色
            draw.ellipse((10, 10, 90, 90), fill=(211, 211, 211, 255))  # 浅灰色
            
            # 写入文字 - PIL不支持中文，我们用简单的形状代替
            # 绘制两条线代表文字
            draw.line((40, 40, 60, 40), fill=(0, 0, 0, 255), width=3)
            draw.line((40, 60, 60, 60), fill=(0, 0, 0, 255), width=3)
            
            # 转换为arcade纹理
            self.default_general_texture = arcade.Texture("default_general", portrait_img)
        
        # 设置将领属性
        self.attacker_general = self.battle_data.attacker_general
        self.defender_general = self.battle_data.defender_general
        
        # 如果有进攻方将领，加载其头像
        if self.attacker_general:
            # 尝试加载将领头像
            if hasattr(self.attacker_general, 'image_path') and self.attacker_general.image_path:
                try:
                    self.general_portraits[self.attacker_general.name] = arcade.load_texture(self.attacker_general.image_path)
                except:
                    self.general_portraits[self.attacker_general.name] = self.default_general_texture
            else:
                self.general_portraits[self.attacker_general.name] = self.default_general_texture
        
        # 如果有防守方将领，加载其头像
        if self.defender_general:
            if hasattr(self.defender_general, 'image_path') and self.defender_general.image_path:
                try:
                    self.general_portraits[self.defender_general.name] = arcade.load_texture(self.defender_general.image_path)
                except:
                    self.general_portraits[self.defender_general.name] = self.default_general_texture
            else:
                self.general_portraits[self.defender_general.name] = self.default_general_texture
    
    def draw_animations(self, delta_time):
        """绘制战场动画效果"""
        # 移除已经完成的动画
        self.animations = [anim for anim in self.animations if "life" not in anim or anim["life"] > 0]
        
        # 绘制并更新每个粒子
        for particle in self.animations:
            # 更新粒子位置
            particle["x"] += particle["vx"] * delta_time
            particle["y"] += particle["vy"] * delta_time
            
            # 如果粒子有生命属性，则减少生命值
            if "life" in particle:
                particle["life"] -= delta_time
                
                # 计算透明度 - 随着生命减少而降低
                alpha = int(255 * (particle["life"] / particle["max_life"]))
                
                # 获取原始颜色并添加透明度
                r, g, b = particle["color"] if len(particle["color"]) == 3 else particle["color"][:3]
                color_with_alpha = (r, g, b, alpha)
                
                # 检查是否是文本粒子
                if "is_text" in particle and particle["is_text"]:
                    # 绘制文本
                    text_size = int(particle["size"])
                    font = pygame.font.SysFont("simhei", text_size, bold=True)
                    text_surface = font.render(particle["text"], True, color_with_alpha)
                    text_rect = text_surface.get_rect(center=(particle["x"], particle["y"]))
                    self.screen.blit(text_surface, text_rect)
                else:
                    # 绘制普通粒子
                    pygame.draw.circle(
                        self.screen, 
                        color_with_alpha, 
                        (int(particle["x"]), int(particle["y"])), 
                        int(particle["size"] * (particle["life"] / particle["max_life"]))
                    )
            else:
                # 无生命周期的粒子直接绘制
                pygame.draw.circle(
                    self.screen, 
                    particle["color"], 
                    (int(particle["x"]), int(particle["y"])), 
                    int(particle["size"])
                )

    def draw_generals(self):
        """绘制将领信息"""
        # 绘制进攻方将领信息
        if self.attacker_general:
            # 左侧面板背景
            arcade.draw_rectangle_filled(
                120, 360, 180, 200, 
                (20, 20, 50, 180)  # 深蓝色半透明
            )
            
            # 将领头像
            if self.attacker_general.name in self.general_portraits:
                texture = self.general_portraits[self.attacker_general.name]
                arcade.draw_texture_rectangle(
                    120, 450, 80, 80, texture
                )
            
            # 将领名称
            arcade.draw_text(
                self.attacker_general.name,
                120, 400,
                GOLD,
                font_size=18,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            # 将领属性
            arcade.draw_text(
                f"统率: {self.attacker_general.leadership}",
                120, 375,
                WHITE,
                font_size=14,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            arcade.draw_text(
                f"武力: {self.attacker_general.strength}",
                120, 350,
                WHITE,
                font_size=14,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            # 如果将领有技能，显示技能列表
            if hasattr(self.attacker_general, 'skills'):
                y = 325
                for skill in self.attacker_general.skills[:2]:  # 仅显示前两个技能
                    arcade.draw_text(
                        f"· {skill.value}",
                        120, y,
                        (255, 220, 150),  # 技能颜色
                        font_size=14,
                        font_name=("SimHei", "Microsoft YaHei"),
                        anchor_x="center"
                    )
                    y -= 20
        
        # 绘制防守方将领信息
        if self.defender_general:
            # 右侧面板背景
            arcade.draw_rectangle_filled(
                1160, 360, 180, 200, 
                (20, 20, 50, 180)  # 深蓝色半透明
            )
            
            # 将领头像
            if self.defender_general.name in self.general_portraits:
                texture = self.general_portraits[self.defender_general.name]
                arcade.draw_texture_rectangle(
                    1160, 450, 80, 80, texture
                )
            
            # 将领名称
            arcade.draw_text(
                self.defender_general.name,
                1160, 400,
                GOLD,
                font_size=18,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            # 将领属性
            arcade.draw_text(
                f"统率: {self.defender_general.leadership}",
                1160, 375,
                WHITE,
                font_size=14,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            arcade.draw_text(
                f"武力: {self.defender_general.strength}",
                1160, 350,
                WHITE,
                font_size=14,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )

    def draw_generals_on_battlefield(self):
        """在战场上绘制将领形象"""
        if not self.attacker_general and not self.defender_general:
            return

        # 获取游戏时间用于动画效果
        current_time = pygame.time.get_ticks() / 1000.0  # 转换为秒
        pulse_scale = 0.2 * math.sin(current_time * 3) + 1.0  # 创建脉动效果

        # 绘制进攻方将领
        if self.attacker_general:
            # 在战场左侧绘制将领，位置略靠近部队
            general_x = self.window_size[0] * 0.25
            general_y = self.window_size[1] * 0.4
            
            # 绘制光环效果
            halo_radius = 60 * pulse_scale
            pygame.draw.circle(self.screen, (255, 215, 0, 150), (int(general_x), int(general_y)), int(halo_radius), 2)
            
            # 绘制将领肖像
            if self.attacker_general.id in self.general_portraits:
                portrait = self.general_portraits[self.attacker_general.id]
                portrait_rect = portrait.get_rect(center=(general_x, general_y))
                # 根据脉动值调整肖像大小
                scaled_portrait = pygame.transform.scale(
                    portrait, 
                    (int(portrait.get_width() * (0.9 + 0.1 * pulse_scale)), 
                     int(portrait.get_height() * (0.9 + 0.1 * pulse_scale)))
                )
                scaled_rect = scaled_portrait.get_rect(center=(general_x, general_y))
                self.screen.blit(scaled_portrait, scaled_rect)
            else:
                # 如果没有肖像，绘制一个默认图标
                pygame.draw.circle(self.screen, (255, 100, 100), (int(general_x), int(general_y)), 30)
                pygame.draw.circle(self.screen, (200, 50, 50), (int(general_x), int(general_y)), 30, 3)
            
            # 绘制将领名称和属性
            general_name = self.font_medium.render(f"{self.attacker_general.name}", True, (255, 255, 255))
            name_rect = general_name.get_rect(center=(general_x, general_y - 45))
            
            # 添加文字阴影效果提高可读性
            general_name_shadow = self.font_medium.render(f"{self.attacker_general.name}", True, (0, 0, 0))
            name_shadow_rect = general_name_shadow.get_rect(center=(general_x + 2, general_y - 43))
            self.screen.blit(general_name_shadow, name_shadow_rect)
            self.screen.blit(general_name, name_rect)
            
            # 绘制将领的能力值
            str_text = self.font_small.render(f"武力: {self.attacker_general.strength}", True, (255, 200, 100))
            str_rect = str_text.get_rect(center=(general_x, general_y + 45))
            self.screen.blit(str_text, str_rect)
            
            # 绘制将领技能
            if hasattr(self.attacker_general, 'skills') and self.attacker_general.skills:
                skills_text = self.font_small.render(f"技能: {', '.join(skill.name for skill in self.attacker_general.skills[:2])}", True, (180, 220, 255))
                skills_rect = skills_text.get_rect(center=(general_x, general_y + 65))
                self.screen.blit(skills_text, skills_rect)
            
            # 找到最近的部队单位并绘制连接线
            closest_unit = None
            min_distance = float('inf')
            
            for pos in self.attacker_positions:
                unit_x, unit_y, _ = pos
                dist = math.sqrt((general_x - unit_x)**2 + (general_y - unit_y)**2)
                if dist < min_distance:
                    min_distance = dist
                    closest_unit = pos
            
            if closest_unit:
                unit_x, unit_y, _ = closest_unit
                # 绘制动态虚线连接将领和部队
                dash_length = 10
                dash_gap = 5
                total_length = math.sqrt((general_x - unit_x)**2 + (general_y - unit_y)**2)
                direction_x = (unit_x - general_x) / total_length
                direction_y = (unit_y - general_y) / total_length
                
                # 使用sin函数创建动画效果
                animation_offset = (current_time * 50) % (dash_length + dash_gap)
                
                current_length = 0
                current_x, current_y = general_x, general_y
                
                while current_length < total_length:
                    segment_start = (current_x, current_y)
                    segment_length = min(dash_length, total_length - current_length)
                    current_x += direction_x * segment_length
                    current_y += direction_y * segment_length
                    segment_end = (current_x, current_y)
                    
                    pygame.draw.line(self.screen, (255, 215, 0), segment_start, segment_end, 2)
                    
                    current_length += segment_length
                    if current_length >= total_length:
                        break
                        
                    # 添加间隙
                    current_length += dash_gap
                    current_x += direction_x * dash_gap
                    current_y += direction_y * dash_gap

        # 绘制防守方将领
        if self.defender_general:
            # 在战场右侧绘制将领，位置略靠近部队
            general_x = self.window_size[0] * 0.75
            general_y = self.window_size[1] * 0.4
            
            # 绘制光环效果
            halo_radius = 60 * pulse_scale
            pygame.draw.circle(self.screen, (0, 191, 255, 150), (int(general_x), int(general_y)), int(halo_radius), 2)
            
            # 绘制将领肖像
            if self.defender_general.id in self.general_portraits:
                portrait = self.general_portraits[self.defender_general.id]
                portrait_rect = portrait.get_rect(center=(general_x, general_y))
                # 根据脉动值调整肖像大小
                scaled_portrait = pygame.transform.scale(
                    portrait, 
                    (int(portrait.get_width() * (0.9 + 0.1 * pulse_scale)), 
                     int(portrait.get_height() * (0.9 + 0.1 * pulse_scale)))
                )
                scaled_rect = scaled_portrait.get_rect(center=(general_x, general_y))
                self.screen.blit(scaled_portrait, scaled_rect)
            else:
                # 如果没有肖像，绘制一个默认图标
                pygame.draw.circle(self.screen, (100, 100, 255), (int(general_x), int(general_y)), 30)
                pygame.draw.circle(self.screen, (50, 50, 200), (int(general_x), int(general_y)), 30, 3)
            
            # 绘制将领名称和属性
            general_name = self.font_medium.render(f"{self.defender_general.name}", True, (255, 255, 255))
            name_rect = general_name.get_rect(center=(general_x, general_y - 45))
            
            # 添加文字阴影效果提高可读性
            general_name_shadow = self.font_medium.render(f"{self.defender_general.name}", True, (0, 0, 0))
            name_shadow_rect = general_name_shadow.get_rect(center=(general_x + 2, general_y - 43))
            self.screen.blit(general_name_shadow, name_shadow_rect)
            self.screen.blit(general_name, name_rect)
            
            # 绘制将领的能力值
            str_text = self.font_small.render(f"武力: {self.defender_general.strength}", True, (255, 200, 100))
            str_rect = str_text.get_rect(center=(general_x, general_y + 45))
            self.screen.blit(str_text, str_rect)
            
            # 绘制将领技能
            if hasattr(self.defender_general, 'skills') and self.defender_general.skills:
                skills_text = self.font_small.render(f"技能: {', '.join(skill.name for skill in self.defender_general.skills[:2])}", True, (180, 220, 255))
                skills_rect = skills_text.get_rect(center=(general_x, general_y + 65))
                self.screen.blit(skills_text, skills_rect)
            
            # 找到最近的部队单位并绘制连接线
            closest_unit = None
            min_distance = float('inf')
            
            for pos in self.defender_positions:
                unit_x, unit_y, _ = pos
                dist = math.sqrt((general_x - unit_x)**2 + (general_y - unit_y)**2)
                if dist < min_distance:
                    min_distance = dist
                    closest_unit = pos
            
            if closest_unit:
                unit_x, unit_y, _ = closest_unit
                # 绘制动态虚线连接将领和部队
                dash_length = 10
                dash_gap = 5
                total_length = math.sqrt((general_x - unit_x)**2 + (general_y - unit_y)**2)
                direction_x = (unit_x - general_x) / total_length
                direction_y = (unit_y - general_y) / total_length
                
                # 使用sin函数创建动画效果
                animation_offset = (current_time * 50) % (dash_length + dash_gap)
                
                current_length = 0
                current_x, current_y = general_x, general_y
                
                while current_length < total_length:
                    segment_start = (current_x, current_y)
                    segment_length = min(dash_length, total_length - current_length)
                    current_x += direction_x * segment_length
                    current_y += direction_y * segment_length
                    segment_end = (current_x, current_y)
                    
                    pygame.draw.line(self.screen, (0, 191, 255), segment_start, segment_end, 2)
                    
                    current_length += segment_length
                    if current_length >= total_length:
                        break
                        
                    # 添加间隙
                    current_length += dash_gap
                    current_x += direction_x * dash_gap
                    current_y += direction_y * dash_gap

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

    def load_soldier_textures(self):
        """加载士兵纹理"""
        # 初始化纹理字典
        self.soldier_textures = {}
        
        # 尝试加载步兵纹理
        try:
            self.soldier_textures["infantry_red"] = arcade.load_texture("resources/arm/arm_bubing.png")
            self.soldier_textures["infantry_blue"] = arcade.load_texture("resources/arm/arm_bubing_blue.png")
        except Exception as e:
            print(f"加载步兵纹理失败: {e}")
            # 创建简单的步兵纹理
            self.create_simple_soldier_texture("infantry_red", (200, 50, 50))
            self.create_simple_soldier_texture("infantry_blue", (50, 50, 200))
        
        # 尝试加载骑兵纹理
        try:
            self.soldier_textures["cavalry_red"] = arcade.load_texture("resources/arm/arm_qibing.png")
            self.soldier_textures["cavalry_blue"] = arcade.load_texture("resources/arm/arm_qibing_blue.png")
        except Exception as e:
            print(f"加载骑兵纹理失败: {e}")
            # 创建简单的骑兵纹理
            self.create_simple_soldier_texture("cavalry_red", (200, 50, 50), is_cavalry=True)
            self.create_simple_soldier_texture("cavalry_blue", (50, 50, 200), is_cavalry=True)
        
        # 尝试加载弓箭手纹理
        try:
            self.soldier_textures["archer_red"] = arcade.load_texture("resources/arm/arm_gongbing.png")
            self.soldier_textures["archer_blue"] = arcade.load_texture("resources/arm/arm_gongbing_blue.png")
        except Exception as e:
            print(f"加载弓箭手纹理失败: {e}")
            # 创建简单的弓箭手纹理
            self.create_simple_soldier_texture("archer_red", (200, 50, 50), is_archer=True)
            self.create_simple_soldier_texture("archer_blue", (50, 50, 200), is_archer=True)
        
        # 尝试加载水军纹理
        try:
            self.soldier_textures["navy_red"] = arcade.load_texture("resources/arm/arm_shuijun.png")
            self.soldier_textures["navy_blue"] = arcade.load_texture("resources/arm/arm_shuijun_blue.png")
        except Exception as e:
            print(f"加载水军纹理失败: {e}")
            # 创建简单的水军纹理
            self.create_simple_soldier_texture("navy_red", (200, 50, 50), is_navy=True)
            self.create_simple_soldier_texture("navy_blue", (50, 50, 200), is_navy=True)
    
    def create_simple_soldier_texture(self, name, color, is_cavalry=False, is_archer=False, is_navy=False):
        """创建简单的士兵纹理"""
        from PIL import Image, ImageDraw
        
        # 创建一个纹理图像
        img = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制不同形状代表不同兵种
        if is_cavalry:
            # 骑兵 - 椭圆 + 三角形
            draw.ellipse((10, 20, 50, 50), fill=color)
            draw.polygon([(30, 10), (20, 30), (40, 30)], fill=color)
        elif is_archer:
            # 弓箭手 - 椭圆 + L形
            draw.ellipse((10, 20, 50, 50), fill=color)
            draw.rectangle((25, 5, 35, 20), fill=color)
            draw.rectangle((35, 15, 45, 20), fill=color)
        elif is_navy:
            # 水军 - 船形
            draw.polygon([(10, 40), (30, 20), (50, 40), (30, 50)], fill=color)
        else:
            # 步兵 - 椭圆
            draw.ellipse((10, 10, 50, 50), fill=color)
        
        # 转换为arcade纹理
        self.soldier_textures[name] = arcade.Texture(name, img)

    def check_battle_end(self):
        """检查战斗是否结束"""
        # 计算剩余兵力
        attacker_remaining = sum(army.size for _, _, army in self.attacker_positions)
        defender_remaining = sum(army.size for _, _, army in self.defender_positions)

        # 判断胜负
        if attacker_remaining <= 0:
            self.battle_log.append("战斗失败！我军被击溃")
            self.end_battle(is_retreat=False)
        elif defender_remaining <= 0:
            self.battle_log.append("战斗胜利！敌军被击溃")
            self.end_battle(is_retreat=False)

    def create_blood_effects(self, center_x, center_y, casualties, is_attacker):
        """创建伤亡血液效果"""
        if casualties <= 0:
            return

        # 根据伤亡数量确定特效数量
        effect_count = min(int(casualties / 100) + 1, 20)

        # 决定特效颜色
        color = (200, 50, 50)  # 血红色

        # 决定方向 - 伤亡方向相反
        direction_x = -1 if is_attacker else 1

        # 创建粒子
        for _ in range(effect_count):
            # 随机化位置
            x = center_x + random.uniform(-40, 40)
            y = center_y + random.uniform(-30, 30)

            # 随机化速度，但保持方向性
            vx = direction_x * random.uniform(20, 50)
            vy = random.uniform(-30, 30)

            # 随机大小和生命周期
            size = random.uniform(3, 6)
            lifetime = random.uniform(0.5, 1.2)

            # 确保粒子字典包含 'x' 和 'vx' 键
            particle = {
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "color": color,
                "size": size,
                "life": lifetime,
                "max_life": lifetime
            }

            self.animations.append(particle)

class CityView(arcade.View):
    """城市界面视图"""
    
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
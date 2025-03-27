#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arcade
import random
import math
from models.army import TroopType, Terrain, Army
from PIL import Image, ImageDraw
from models.general import Skill  # 导入Skill枚举

# 设置常量
WHITE = arcade.color.WHITE
BLACK = arcade.color.BLACK
RED = arcade.color.RED
GREEN = arcade.color.GREEN
BLUE = arcade.color.BLUE
GOLD = arcade.color.GOLD
BACKGROUND_COLOR = (30, 30, 60)

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
        
        # 战场位置设置
        self.attacker_positions = []  # 存储攻击方部队位置和引用
        self.defender_positions = []  # 存储防御方部队位置和引用
        
        # 战斗状态
        self.battle_phase = "准备"  # 准备, 远程, 近战, 追击, 撤退
        self.battle_log = []
        self.phase_buttons = []
        self.animations = []
        self.animation_enabled = True  # 是否启用动画
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
        
        # 部署进攻方军队
        attacker_x = self.window_size[0] * 0.3  # 进攻方在左侧
        
        # 将进攻方军队分成多个单位，每个单位最多1000兵力
        y_offset = 0
        remaining_troops = self.attacker.size
        while remaining_troops > 0:
            unit_size = min(1000, remaining_troops)
            unit = Army(
                size=unit_size,
                primary_type=self.attacker.primary_type,
                secondary_type=self.attacker.secondary_type,
                morale=self.attacker.morale,
                training=self.attacker.training
            )
            
            # 为大军队创建多行部署
            row = y_offset // 3
            col = y_offset % 3
            unit_x = attacker_x - 100 + col * 80
            unit_y = self.window_size[1] / 2 - 100 + row * 100
            
            self.attacker_positions.append((unit_x, unit_y, unit))
            remaining_troops -= unit_size
            y_offset += 1
        
        # 部署防守方军队
        defender_x = self.window_size[0] * 0.7  # 防守方在右侧
        
        # 将防守方军队分成多个单位，每个单位最多1000兵力
        y_offset = 0
        remaining_troops = self.defender.size
        while remaining_troops > 0:
            unit_size = min(1000, remaining_troops)
            unit = Army(
                size=unit_size,
                primary_type=self.defender.primary_type,
                secondary_type=self.defender.secondary_type,
                morale=self.defender.morale,
                training=self.defender.training
            )
            
            # 为大军队创建多行部署
            row = y_offset // 3
            col = y_offset % 3
            unit_x = defender_x + 100 - col * 80
            unit_y = self.window_size[1] / 2 - 100 + row * 100
            
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
    
    def on_draw(self):
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
        self.draw_battlefield()
        
        # 绘制部队
        self.draw_armies()
        
        # 绘制动画效果
        self.draw_animations()
        
        # 绘制战斗信息
        self.draw_battle_info()
        
        # 绘制将领信息栏（界面右侧）
        self.draw_generals()
        
        # 绘制按钮
        for button_id, button in self.phase_buttons:
            button.draw()
    
    def draw_battlefield(self):
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
    
    def draw_armies(self):
        """绘制军队"""
        # 绘制进攻方军队
        for x, y, army in self.attacker_positions:
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
            if army.primary_type == TroopType.INFANTRY:
                texture = self.soldier_textures["infantry_red"]
            elif army.primary_type == TroopType.CAVALRY:
                texture = self.soldier_textures["cavalry_red"]
                texture_height = 65 * scale_factor  # 骑兵稍高一些
            elif army.primary_type == TroopType.ARCHER:
                texture = self.soldier_textures["archer_red"]
            elif army.primary_type == TroopType.NAVY:
                texture = self.soldier_textures["navy_red"]
            else:
                # 默认使用步兵纹理
                texture = self.soldier_textures["infantry_red"]
            
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
        
        # 绘制防守方军队
        for x, y, army in self.defender_positions:
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
            if army.primary_type == TroopType.INFANTRY:
                texture = self.soldier_textures["infantry_blue"]
            elif army.primary_type == TroopType.CAVALRY:
                texture = self.soldier_textures["cavalry_blue"]
                texture_height = 65 * scale_factor  # 骑兵稍高一些
            elif army.primary_type == TroopType.ARCHER:
                texture = self.soldier_textures["archer_blue"]
            elif army.primary_type == TroopType.NAVY:
                texture = self.soldier_textures["navy_blue"]
            else:
                # 默认使用步兵纹理
                texture = self.soldier_textures["infantry_blue"]
            
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
        
        # 绘制将领位置为独立图标
        self.draw_generals_on_battlefield()
    
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
        
        # 绘制战斗日志
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
    
    def on_mouse_motion(self, x, y, dx, dy):
        """处理鼠标移动"""
        for button in self.phase_buttons:
            button.check_mouse_hover(x, y)
    
    def on_mouse_press(self, x, y, button, modifiers):
        """处理鼠标点击"""
        for i, btn in enumerate(self.phase_buttons):
            if btn.check_mouse_press(x, y):
                if btn.text == "下一阶段":
                    self.next_battle_phase()
                elif btn.text == "自动战斗":
                    self.auto_battle()
                elif btn.text == "撤退":
                    self.retreat()
                elif btn.text == "关闭动画" or btn.text == "开启动画":
                    self.toggle_animations()
    
    def toggle_animations(self):
        """切换动画效果"""
        self.animation_enabled = not self.animation_enabled
        status = "开启" if self.animation_enabled else "关闭"
        self.battle_log.append(f"战斗动画效果已{status}")
    
    def create_attack_animation(self, attacker_position, defender_position, attack_type="arrow"):
        """创建攻击动画"""
        if not self.show_animations:
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
            "speed": 0.02 * self.animation_speed,
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
        phases = ["部署阶段", "远程阶段", "近战阶段", "追击阶段", "撤退阶段"]
        
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
        # 检查双方是否有步兵或骑兵单位
        attacker_melee = [pos for pos in self.attacker_positions 
                         if pos[2].primary_type in [TroopType.INFANTRY, TroopType.CAVALRY]]
        
        defender_melee = [pos for pos in self.defender_positions 
                         if pos[2].primary_type in [TroopType.INFANTRY, TroopType.CAVALRY]]
        
        # 进攻方近战部队攻击
        if attacker_melee and defender_melee:
            self.battle_log.append("双方部队近战交锋")
            
            # 随机选择一些交战对
            num_combats = min(len(attacker_melee), len(defender_melee), 3)
            for _ in range(num_combats):
                if not attacker_melee or not defender_melee:
                    break
                    
                attacker = random.choice(attacker_melee)
                defender = random.choice(defender_melee)
                
                # 计算伤害
                attacker_damage = int(attacker[2].size * 0.15)
                defender_damage = int(defender[2].size * 0.15)
                
                # 考虑地形和兵种克制关系
                if self.terrain == Terrain.FOREST and attacker[2].primary_type == TroopType.CAVALRY:
                    attacker_damage = int(attacker_damage * 0.7)
                    self.battle_log.append("森林地形降低了骑兵的作战效率")
                
                # 兵种克制：骑兵克制步兵
                if attacker[2].primary_type == TroopType.CAVALRY and defender[2].primary_type == TroopType.INFANTRY:
                    attacker_damage = int(attacker_damage * 1.3)
                    self.battle_log.append("骑兵对步兵发动冲锋，造成更多伤害")
                    
                    # 创建骑兵冲锋动画
                    self.create_attack_animation(attacker, defender, "sword")
                else:
                    # 普通近战动画
                    self.create_attack_animation(attacker, defender, "sword")
                
                # 应用伤害
                defender[2].take_casualties(attacker_damage)
                attacker[2].take_casualties(defender_damage)
                
                self.battle_log.append(f"我军造成{attacker_damage}人伤亡，损失{defender_damage}人")
        
        # 将领技能效果
        if self.attacker_general and hasattr(self.attacker_general, 'skills'):
            # 检查冲阵技能
            if any(skill == Skill.CHARGE for skill in self.attacker_general.skills) and self.attacker_positions:
                self.battle_log.append(f"{self.attacker_general.name}发动冲阵!")
                
                # 随机选择一个敌方单位
                if self.defender_positions:
                    target = random.choice(self.defender_positions)
                    
                    # 冲阵造成额外伤害
                    charge_damage = int(target[2].size * 0.1)
                    target[2].take_casualties(charge_damage)
                    
                    # 创建冲锋动画
                    if self.attacker_positions:
                        attacker_source = random.choice(self.attacker_positions)
                        self.create_attack_animation(attacker_source, target, "sword")
                
                self.battle_log.append(f"冲阵造成了额外伤害!")
                
            # 检查铁壁技能
            if any(skill == Skill.IRON_DEFENSE for skill in self.attacker_general.skills) and self.attacker_positions:
                self.battle_log.append(f"{self.attacker_general.name}发动铁壁防御!")
                
                # 为所有友军单位创建盾牌动画
                for pos in self.attacker_positions:
                    self.create_attack_animation(pos, pos, "shield")
                
                # 减少我方伤亡
                for i, (x, y, army) in enumerate(self.attacker_positions):
                    # 恢复一些损失
                    recovery = int(army.size * 0.05)
                    army.size += recovery
                    self.attacker_positions[i] = (x, y, army)
                
                self.battle_log.append(f"铁壁防御减少了我方伤亡!")
    
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
        # 快速完成战斗
        self.battle_log.append("自动战斗中...")
        
        # 模拟各个战斗阶段
        if self.show_animations:
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
            if self.show_animations:
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
            if self.show_animations:
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
    
    def draw_animations(self):
        """绘制战斗动画效果"""
        # 只有在启用动画且有动画效果时才绘制
        if not self.animation_enabled or not self.animations:
            return
            
        for animation in self.animations[:]:
            # 检查动画是否完成
            if animation["progress"] >= 1.0:
                self.animations.remove(animation)
                continue
                
            # 更新动画进度
            animation["progress"] += animation["speed"]
            
            # 计算当前位置
            start_x, start_y = animation["start"]
            end_x, end_y = animation["end"]
            current_x = start_x + (end_x - start_x) * animation["progress"]
            current_y = start_y + (end_y - start_y) * animation["progress"]
            
            # 根据动画类型绘制效果
            if animation["type"] == "arrow":
                # 箭矢飞行动画
                texture = self.effect_textures["arrow"]
                if texture:
                    # 计算箭矢角度
                    angle = math.degrees(math.atan2(end_y - start_y, end_x - start_x))
                    arcade.draw_texture_rectangle(
                        current_x, current_y, 
                        40, 20, 
                        texture, 
                        angle
                    )
                else:
                    arcade.draw_line(
                        start_x, start_y, 
                        current_x, current_y, 
                        arcade.color.WHITE, 2
                    )
                    
            elif animation["type"] == "fire":
                # 火焰攻击动画
                texture = self.effect_textures["fire"]
                if texture:
                    arcade.draw_texture_rectangle(
                        current_x, current_y, 
                        40 + random.randint(-5, 5), 60 + random.randint(-10, 10), 
                        texture,
                        random.randint(-10, 10)
                    )
                else:
                    arcade.draw_circle_filled(
                        current_x, current_y, 
                        15 + random.randint(-5, 5), 
                        (255, 100, 0, 200)
                    )
                    
            elif animation["type"] == "sword":
                # 剑击动画
                texture = self.effect_textures["sword"]
                if texture:
                    arcade.draw_texture_rectangle(
                        current_x, current_y, 
                        60, 60, 
                        texture,
                        30 * math.sin(animation["progress"] * math.pi * 2)
                    )
                else:
                    arcade.draw_line(
                        current_x - 30, current_y, 
                        current_x + 30, current_y, 
                        arcade.color.SILVER, 3
                    )
                    
            elif animation["type"] == "shield":
                # 防御动画
                texture = self.effect_textures["shield"]
                if texture:
                    scale = 1.0 + 0.2 * math.sin(animation["progress"] * math.pi * 4)
                    arcade.draw_texture_rectangle(
                        current_x, current_y, 
                        50 * scale, 60 * scale, 
                        texture
                    )
                else:
                    radius = 25 + 5 * math.sin(animation["progress"] * math.pi * 4)
                    arcade.draw_circle_outline(
                        current_x, current_y, 
                        radius, 
                        arcade.color.SILVER, 3
                    )
            
            # 绘制粒子效果（如果有）
            if "particles" in animation:
                for particle in animation["particles"][:]:
                    # 更新粒子位置
                    particle["x"] += particle["dx"]
                    particle["y"] += particle["dy"]
                    particle["life"] -= 0.02
                    
                    # 移除已消失的粒子
                    if particle["life"] <= 0:
                        animation["particles"].remove(particle)
                        continue
                    
                    # 绘制粒子
                    arcade.draw_circle_filled(
                        particle["x"], particle["y"],
                        particle["size"] * particle["life"],
                        (particle["color"][0], 
                         particle["color"][1], 
                         particle["color"][2], 
                         int(255 * particle["life"]))
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
        """在战场上绘制将领图标"""
        # 在战场左侧显示进攻方将领
        if self.attacker_general:
            # 将领位置（左侧军队前方）
            general_x = 150
            general_y = 300
            
            # 画将领背景光环
            arcade.draw_circle_filled(general_x, general_y, 40, (200, 180, 80, 100))  # 金色光环
            
            # 绘制将领头像
            if self.attacker_general.name in self.general_portraits:
                texture = self.general_portraits[self.attacker_general.name]
                arcade.draw_texture_rectangle(
                    general_x, general_y, 60, 60, texture
                )
            
            # 绘制将领名称
            arcade.draw_text(
                self.attacker_general.name,
                general_x, general_y - 45,
                GOLD,
                font_size=16,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            # 绘制将领简要属性
            arcade.draw_text(
                f"武力: {self.attacker_general.strength}",
                general_x, general_y - 65,
                WHITE,
                font_size=12,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            # 绘制连接线，连接将领和最近的部队
            if self.attacker_positions:
                # 找到最近的部队
                closest_unit = min(self.attacker_positions, key=lambda pos: ((pos[0] - general_x) ** 2 + (pos[1] - general_y) ** 2) ** 0.5)
                
                # 绘制连接线 - 用多段短线模拟虚线
                start_x, start_y = general_x + 30, general_y
                end_x, end_y = closest_unit[0] - 30, closest_unit[1]
                dx, dy = end_x - start_x, end_y - start_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance > 0:
                    dx, dy = dx / distance, dy / distance
                    dash_length = 5
                    gap_length = 5
                    steps = int(distance / (dash_length + gap_length))
                    
                    for i in range(steps):
                        dash_start_x = start_x + i * (dash_length + gap_length) * dx
                        dash_start_y = start_y + i * (dash_length + gap_length) * dy
                        dash_end_x = dash_start_x + dash_length * dx
                        dash_end_y = dash_start_y + dash_length * dy
                        
                        arcade.draw_line(
                            dash_start_x, dash_start_y,
                            dash_end_x, dash_end_y,
                            (200, 180, 80),  # 金色线条
                            1  # 线宽
                        )
        
        # 在战场右侧显示防守方将领
        if self.defender_general:
            # 将领位置（右侧军队前方）
            general_x = 900
            general_y = 300
            
            # 画将领背景光环
            arcade.draw_circle_filled(general_x, general_y, 40, (100, 150, 200, 100))  # 蓝色光环
            
            # 绘制将领头像
            if self.defender_general.name in self.general_portraits:
                texture = self.general_portraits[self.defender_general.name]
                arcade.draw_texture_rectangle(
                    general_x, general_y, 60, 60, texture
                )
            
            # 绘制将领名称
            arcade.draw_text(
                self.defender_general.name,
                general_x, general_y - 45,
                GOLD,
                font_size=16,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            # 绘制将领简要属性
            arcade.draw_text(
                f"武力: {self.defender_general.strength}",
                general_x, general_y - 65,
                WHITE,
                font_size=12,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            # 绘制连接线，连接将领和最近的部队
            if self.defender_positions:
                # 找到最近的部队
                closest_unit = min(self.defender_positions, key=lambda pos: ((pos[0] - general_x) ** 2 + (pos[1] - general_y) ** 2) ** 0.5)
                
                # 绘制连接线 - 用多段短线模拟虚线
                start_x, start_y = general_x - 30, general_y
                end_x, end_y = closest_unit[0] + 30, closest_unit[1]
                dx, dy = end_x - start_x, end_y - start_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance > 0:
                    dx, dy = dx / distance, dy / distance
                    dash_length = 5
                    gap_length = 5
                    steps = int(distance / (dash_length + gap_length))
                    
                    for i in range(steps):
                        dash_start_x = start_x + i * (dash_length + gap_length) * dx
                        dash_start_y = start_y + i * (dash_length + gap_length) * dy
                        dash_end_x = dash_start_x + dash_length * dx
                        dash_end_y = dash_start_y + dash_length * dy
                        
                        arcade.draw_line(
                            dash_start_x, dash_start_y,
                            dash_end_x, dash_end_y,
                            (100, 150, 200),  # 蓝色线条
                            1  # 线宽
                        )

    def load_soldier_textures(self):
        """加载士兵纹理"""
        # 初始化士兵纹理字典
        self.soldier_textures = {
            "infantry_red": None,  # 红方步兵
            "infantry_blue": None,  # 蓝方步兵
            "cavalry_red": None,   # 红方骑兵
            "cavalry_blue": None,  # 蓝方骑兵
            "archer_red": None,    # 红方弓兵
            "archer_blue": None,   # 蓝方弓兵
            "navy_red": None,      # 红方水军
            "navy_blue": None      # 蓝方水军
        }
        
        # 尝试从文件加载纹理
        try:
            self.soldier_textures["infantry_red"] = arcade.load_texture("assets/images/units/infantry_red.png")
            self.soldier_textures["infantry_blue"] = arcade.load_texture("assets/images/units/infantry_blue.png")
            self.soldier_textures["cavalry_red"] = arcade.load_texture("assets/images/units/cavalry_red.png")
            self.soldier_textures["cavalry_blue"] = arcade.load_texture("assets/images/units/cavalry_blue.png")
            self.soldier_textures["archer_red"] = arcade.load_texture("assets/images/units/archer_red.png")
            self.soldier_textures["archer_blue"] = arcade.load_texture("assets/images/units/archer_blue.png")
            self.soldier_textures["navy_red"] = arcade.load_texture("assets/images/units/navy_red.png")
            self.soldier_textures["navy_blue"] = arcade.load_texture("assets/images/units/navy_blue.png")
        except Exception as e:
            print(f"加载士兵图片失败: {e}，将使用生成的简单图像")
            # 如果加载失败，则创建简单图像作为纹理
            self.create_soldier_textures()
    
    def create_soldier_textures(self):
        """创建简单的士兵形象纹理"""
        try:
            from PIL import Image, ImageDraw
            import io
            
            # 创建各种士兵形象
            # 步兵红色 - 使用矩形+旗帜表示
            infantry_red = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
            draw = ImageDraw.Draw(infantry_red)
            # 矩形主体
            draw.rectangle([10, 15, 50, 45], fill=(200, 100, 100, 255), outline=(255, 255, 255, 255))
            # 旗帜
            draw.polygon([(10, 15), (10, 5), (20, 10)], fill=(230, 80, 80, 255))
            # 盾牌轮廓
            draw.arc([15, 20, 45, 40], 0, 360, fill=(255, 255, 255, 255))
            # 转为纹理
            buffer = io.BytesIO()
            infantry_red.save(buffer, format="PNG")
            buffer.seek(0)
            self.soldier_textures["infantry_red"] = arcade.load_texture_from_pil_image(infantry_red)
            
            # 步兵蓝色
            infantry_blue = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
            draw = ImageDraw.Draw(infantry_blue)
            draw.rectangle([10, 15, 50, 45], fill=(100, 100, 200, 255), outline=(255, 255, 255, 255))
            draw.polygon([(50, 15), (50, 5), (40, 10)], fill=(80, 80, 230, 255))
            draw.arc([15, 20, 45, 40], 0, 360, fill=(255, 255, 255, 255))
            buffer = io.BytesIO()
            infantry_blue.save(buffer, format="PNG")
            buffer.seek(0)
            self.soldier_textures["infantry_blue"] = arcade.load_texture_from_pil_image(infantry_blue)
            
            # 骑兵红色 - 添加三角形表示马
            cavalry_red = Image.new("RGBA", (60, 65), (0, 0, 0, 0))
            draw = ImageDraw.Draw(cavalry_red)
            # 马的轮廓
            draw.polygon([(10, 45), (50, 45), (30, 25)], fill=(150, 100, 80, 255), outline=(255, 255, 255, 255))
            # 骑手
            draw.rectangle([20, 10, 40, 30], fill=(200, 100, 100, 255), outline=(255, 255, 255, 255))
            # 旗帜
            draw.polygon([(10, 25), (10, 15), (20, 20)], fill=(230, 80, 80, 255))
            buffer = io.BytesIO()
            cavalry_red.save(buffer, format="PNG")
            buffer.seek(0)
            self.soldier_textures["cavalry_red"] = arcade.load_texture_from_pil_image(cavalry_red)
            
            # 骑兵蓝色
            cavalry_blue = Image.new("RGBA", (60, 65), (0, 0, 0, 0))
            draw = ImageDraw.Draw(cavalry_blue)
            draw.polygon([(10, 45), (50, 45), (30, 25)], fill=(150, 100, 80, 255), outline=(255, 255, 255, 255))
            draw.rectangle([20, 10, 40, 30], fill=(100, 100, 200, 255), outline=(255, 255, 255, 255))
            draw.polygon([(50, 25), (50, 15), (40, 20)], fill=(80, 80, 230, 255))
            buffer = io.BytesIO()
            cavalry_blue.save(buffer, format="PNG")
            buffer.seek(0)
            self.soldier_textures["cavalry_blue"] = arcade.load_texture_from_pil_image(cavalry_blue)
            
            # 弓兵红色 - 添加弓的图案
            archer_red = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
            draw = ImageDraw.Draw(archer_red)
            # 士兵主体
            draw.rectangle([10, 15, 50, 45], fill=(200, 100, 100, 255), outline=(255, 255, 255, 255))
            # 弓箭
            draw.arc([45, 20, 55, 40], 280, 80, fill=(255, 255, 255, 255))
            draw.line([(50, 30), (60, 30)], fill=(255, 255, 255, 255), width=1)
            # 旗帜
            draw.polygon([(10, 15), (10, 5), (20, 10)], fill=(230, 80, 80, 255))
            buffer = io.BytesIO()
            archer_red.save(buffer, format="PNG")
            buffer.seek(0)
            self.soldier_textures["archer_red"] = arcade.load_texture_from_pil_image(archer_red)
            
            # 弓兵蓝色
            archer_blue = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
            draw = ImageDraw.Draw(archer_blue)
            draw.rectangle([10, 15, 50, 45], fill=(100, 100, 200, 255), outline=(255, 255, 255, 255))
            draw.arc([5, 20, 15, 40], 100, 260, fill=(255, 255, 255, 255))
            draw.line([(10, 30), (0, 30)], fill=(255, 255, 255, 255), width=1)
            draw.polygon([(50, 15), (50, 5), (40, 10)], fill=(80, 80, 230, 255))
            buffer = io.BytesIO()
            archer_blue.save(buffer, format="PNG")
            buffer.seek(0)
            self.soldier_textures["archer_blue"] = arcade.load_texture_from_pil_image(archer_blue)
            
            # 水军红色 - 添加波浪线
            navy_red = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
            draw = ImageDraw.Draw(navy_red)
            # 船体
            draw.rectangle([10, 15, 50, 40], fill=(200, 100, 100, 255), outline=(255, 255, 255, 255))
            # 波浪线
            for i in range(5, 60, 10):
                draw.arc([i-5, 45, i+5, 55], 0, 180, fill=(100, 150, 200, 255))
            # 旗帜
            draw.polygon([(10, 15), (10, 5), (20, 10)], fill=(230, 80, 80, 255))
            buffer = io.BytesIO()
            navy_red.save(buffer, format="PNG")
            buffer.seek(0)
            self.soldier_textures["navy_red"] = arcade.load_texture_from_pil_image(navy_red)
            
            # 水军蓝色
            navy_blue = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
            draw = ImageDraw.Draw(navy_blue)
            draw.rectangle([10, 15, 50, 40], fill=(100, 100, 200, 255), outline=(255, 255, 255, 255))
            for i in range(5, 60, 10):
                draw.arc([i-5, 45, i+5, 55], 0, 180, fill=(100, 150, 200, 255))
            draw.polygon([(50, 15), (50, 5), (40, 10)], fill=(80, 80, 230, 255))
            buffer = io.BytesIO()
            navy_blue.save(buffer, format="PNG")
            buffer.seek(0)
            self.soldier_textures["navy_blue"] = arcade.load_texture_from_pil_image(navy_blue)
            
        except Exception as e:
            print(f"创建士兵图片失败: {e}，将使用基本形状")
            # 如果连PIL也无法使用，则使用基本形状
            for key in self.soldier_textures.keys():
                self.soldier_textures[key] = None

class CityView(arcade.View):
    """城市管理界面"""
    def __init__(self, game, city):
        super().__init__()
        self.game = game
        self.city = city
        
        # UI元素
        self.buttons = []
        
        # 加载背景图 - 新增
        try:
            # 优先加载新背景图
            self.background_texture = arcade.load_texture("resources/back_ground.png")
        except:
            try:
                # 如果新背景加载失败，尝试加载旧背景
                self.background_texture = arcade.load_texture("resources/background.jpg")
            except:
                self.background_texture = None
        
        # 初始化UI
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI元素"""
        # 建筑按钮
        buildings = ["城墙", "粮仓", "集市", "兵营"]
        for i, building in enumerate(buildings):
            btn = Button(
                250, 500 - i * 60, 180, 50,
                f"升级{building}"
            )
            self.buttons.append(btn)
        
        # 扩建按钮
        expand_buttons = ["扩建农田", "扩建矿山"]
        for i, label in enumerate(expand_buttons):
            btn = Button(
                250, 300 - i * 60, 180, 50,
                label
            )
            self.buttons.append(btn)
        
        # 军事按钮
        military_buttons = ["征兵", "训练驻军"]
        for i, label in enumerate(military_buttons):
            btn = Button(
                450, 500 - i * 60, 180, 50,
                label
            )
            self.buttons.append(btn)
        
        # 经济按钮
        economic_buttons = ["调整税率", "查看收入"]
        for i, label in enumerate(economic_buttons):
            btn = Button(
                450, 300 - i * 60, 180, 50,
                label
            )
            self.buttons.append(btn)
        
        # 返回按钮
        back_btn = Button(
            640, 100, 200, 50,
            "返回主菜单", bg_color=(100, 100, 100)
        )
        self.buttons.append(back_btn)
    
    def on_show(self):
        """视图显示时"""
        arcade.set_background_color(BACKGROUND_COLOR)
    
    def on_draw(self):
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
            
            # 绘制半透明的城市管理背景板
            arcade.draw_rectangle_filled(
                640, 360,
                1000, 600,
                (20, 20, 50, 180)  # 深蓝色半透明
            )
        
        # 绘制城市信息
        self.draw_city_info()
        
        # 绘制按钮
        for button in self.buttons:
            button.draw()
    
    def draw_city_info(self):
        """绘制城市信息"""
        # 城市名称
        arcade.draw_text(
            f"{self.city.name} - {self.city.region}",
            640, 620,
            GOLD,
            font_size=36,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 城市基本信息
        info_text = (
            f"人口: {self.city.population}    繁荣度: {self.city.prosperity}    忠诚度: {self.city.loyalty}\n"
            f"农田: {self.city.farms}    矿山: {self.city.mines}    城防等级: {self.city.forts}\n"
            f"税率: {self.city.tax_rate * 100:.1f}%    驻军: {self.city.total_garrison_size()}"
        )
        
        arcade.draw_text(
            info_text,
            640, 570,
            WHITE,
            font_size=18,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 建筑信息
        arcade.draw_text(
            "建筑:",
            700, 500,
            WHITE,
            font_size=24,
            font_name=("SimHei", "Microsoft YaHei")
        )
        
        y = 470
        for name, building in self.city.buildings.items():
            arcade.draw_text(
                f"{name} (等级{building.level}): {list(building.benefits.keys())[0]} +{list(building.benefits.values())[0]}",
                700, y,
                WHITE,
                font_size=16,
                font_name=("SimHei", "Microsoft YaHei")
            )
            y -= 30
        
        # 资源产出
        arcade.draw_text(
            "月产出:",
            920, 500,
            WHITE,
            font_size=24,
            font_name=("SimHei", "Microsoft YaHei")
        )
        
        y = 470
        for resource, amount in self.city.production.items():
            arcade.draw_text(
                f"{resource}: {amount}",
                920, y,
                WHITE,
                font_size=16,
                font_name=("SimHei", "Microsoft YaHei")
            )
            y -= 30
    
    def on_mouse_motion(self, x, y, dx, dy):
        """处理鼠标移动"""
        for button in self.buttons:
            button.check_mouse_hover(x, y)
    
    def on_mouse_press(self, x, y, button, modifiers):
        """处理鼠标点击"""
        for i, btn in enumerate(self.buttons):
            if btn.check_mouse_press(x, y):
                # 处理按钮点击
                if i < 4:  # 建筑升级按钮
                    building_name = ["城墙", "粮仓", "集市", "兵营"][i]
                    self.upgrade_building(building_name)
                elif i == 4:  # 扩建农田
                    self.expand_farms()
                elif i == 5:  # 扩建矿山
                    self.expand_mines()
                elif i == 6:  # 征兵
                    self.recruit_troops()
                elif i == 7:  # 训练驻军
                    self.train_garrison()
                elif i == 8:  # 调整税率
                    self.adjust_tax_rate()
                elif i == 9:  # 查看收入
                    self.view_income()
                elif i == 10:  # 返回主菜单
                    self.return_to_main_menu()
    
    def upgrade_building(self, building_name):
        """升级建筑"""
        result = self.city.upgrade_building(building_name)
        if result:
            self.show_message(f"{building_name}升级成功！")
        else:
            self.show_message("资源不足，无法升级！")
    
    def expand_farms(self):
        """扩建农田"""
        # 在这里实现扩建农田的功能
        pass
    
    def expand_mines(self):
        """扩建矿山"""
        # 在这里实现扩建矿山的功能
        pass
    
    def recruit_troops(self):
        """征兵"""
        # 在这里实现征兵的功能
        pass
    
    def train_garrison(self):
        """训练驻军"""
        # 在这里实现训练驻军的功能
        pass
    
    def adjust_tax_rate(self):
        """调整税率"""
        # 在这里实现调整税率的功能
        pass
    
    def view_income(self):
        """查看收入"""
        # 在这里实现查看收入的功能
        pass
    
    def return_to_main_menu(self):
        """返回主菜单"""
        # 返回主菜单
        from three_kingdoms_arcade import MainMenuView
        main_menu_view = MainMenuView(self.game)
        self.window.show_view(main_menu_view)
    
    def show_message(self, message):
        """显示消息"""
        # 在这里可以实现消息提示功能
        print(message)  # 临时使用控制台输出
    
    def on_key_press(self, key, modifiers):
        """处理键盘按键事件"""
        # ESC键返回主菜单
        if key == arcade.key.ESCAPE:
            from three_kingdoms_arcade import MainMenuView
            main_menu_view = MainMenuView(self.game)
            self.window.show_view(main_menu_view)

class Button:
    """按钮类，用于界面交互"""
    def __init__(self, center_x, center_y, width, height, text, text_color=WHITE, bg_color=(80, 80, 120), hover_color=(100, 100, 150), corner_radius=10):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.corner_radius = corner_radius  # 圆角半径
        self.shadow_offset = 3  # 阴影偏移
        self.animation_progress = 0  # 用于动画效果
        self.pressed = False
        
    def draw(self):
        # 绘制按钮阴影
        if not self.pressed:
            shadow_color = (20, 20, 30, 100)  # 半透明黑色阴影
            arcade.draw_rectangle_filled(
                self.center_x + self.shadow_offset, 
                self.center_y - self.shadow_offset,
                self.width, self.height, 
                shadow_color,
                self.corner_radius
            )
        
        # 绘制按钮背景
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # 如果按钮被按下，稍微降低位置
        offset_y = -2 if self.pressed else 0
        
        # 绘制圆角矩形背景
        arcade.draw_rectangle_filled(
            self.center_x, self.center_y + offset_y, 
            self.width, self.height, 
            color,
            self.corner_radius
        )
        
        # 绘制按钮边框
        border_color = (220, 220, 220) if self.is_hovered else (180, 180, 180)
        arcade.draw_rectangle_outline(
            self.center_x, self.center_y + offset_y, 
            self.width, self.height, 
            border_color, 2,
            self.corner_radius
        )
        
        # 绘制内部高光效果（顶部边缘）
        highlight_color = (255, 255, 255, 80)  # 半透明白色高光
        arcade.draw_line(
            self.center_x - self.width/2 + self.corner_radius,
            self.center_y + self.height/2 - 2 + offset_y,
            self.center_x + self.width/2 - self.corner_radius,
            self.center_y + self.height/2 - 2 + offset_y,
            highlight_color, 2
        )
        
        # 悬停时的额外效果
        if self.is_hovered:
            # 脉动边框动画
            self.animation_progress = (self.animation_progress + 0.05) % 1.0
            glow_alpha = int(100 + 155 * abs(math.sin(self.animation_progress * 3.14)))
            glow_color = (255, 255, 200, glow_alpha)
            
            arcade.draw_rectangle_outline(
                self.center_x, self.center_y + offset_y, 
                self.width + 4, self.height + 4,
                glow_color, 2,
                self.corner_radius + 2
            )
        
        # 绘制按钮文本
        text_offset_y = -2 if self.pressed else 0  # 按下时文本也稍微下移
        arcade.draw_text(
            self.text,
            self.center_x, self.center_y + offset_y + text_offset_y,
            self.text_color,
            font_size=18,
            font_name=("SimHei", "Microsoft YaHei"),
            width=self.width - 20,
            align="center",
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
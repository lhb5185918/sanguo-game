#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arcade
import os
import time
import math
from three_kingdoms_game import ThreeKingdomsGame
from gui.views import Button, BattleView, CityView

# 设置常量
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "三国霸业"

# 颜色常量
WHITE = arcade.color.WHITE
BLACK = arcade.color.BLACK
RED = arcade.color.RED
GREEN = arcade.color.GREEN
BLUE = arcade.color.BLUE
YELLOW = arcade.color.YELLOW
GOLD = arcade.color.GOLD
BACKGROUND_COLOR = (30, 30, 60)

class TextInputBox:
    """文本输入框类"""
    def __init__(self, center_x, center_y, width, height, text="", placeholder="请输入...", max_length=15):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.placeholder = placeholder
        self.active = False
        self.max_length = max_length
        self.cursor_visible = True
        self.cursor_blink_time = 0
        
    def draw(self):
        # 绘制输入框背景
        bg_color = (30, 30, 50) if not self.active else (50, 50, 70)
        arcade.draw_rectangle_filled(
            self.center_x, self.center_y, self.width, self.height, bg_color
        )
        
        # 绘制输入框边框
        border_color = GOLD if self.active else (150, 150, 150)
        border_width = 3 if self.active else 2
        
        # 绘制圆角矩形边框
        corner_radius = 10
        arcade.draw_rectangle_outline(
            self.center_x, self.center_y, self.width, self.height, 
            border_color, border_width, corner_radius
        )
        
        # 绘制内部高光效果（顶部边缘）
        if self.active:
            highlight_color = (255, 255, 255, 80)  # 半透明白色高光
            arcade.draw_line(
                self.center_x - self.width/2 + corner_radius,
                self.center_y + self.height/2 - 2,
                self.center_x + self.width/2 - corner_radius,
                self.center_y + self.height/2 - 2,
                highlight_color, 2
            )
        
        # 绘制文本或占位符
        display_text = self.text if self.text else self.placeholder
        text_color = WHITE if self.text else (150, 150, 150)
        
        arcade.draw_text(
            display_text,
            self.center_x - self.width/2 + 15, self.center_y,
            text_color,
            font_size=20,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="left", anchor_y="center"
        )
        
        # 绘制闪烁的光标
        if self.active:
            # 更新光标闪烁时间
            self.cursor_blink_time += 0.02
            if self.cursor_blink_time > 1.0:
                self.cursor_blink_time = 0
                self.cursor_visible = not self.cursor_visible
            
            if self.cursor_visible:
                # 计算光标位置（根据文本宽度）
                if self.text:
                    # 使用arcade.draw_text的文本测量方法
                    text_width = len(self.text) * 12  # 简化的文本宽度估计，每个字符约12像素
                    if len(self.text) > 0 and '\u4e00' <= self.text[0] <= '\u9fff':
                        # 如果是中文字符，它们通常更宽
                        text_width = len(self.text) * 20  # 中文字符约20像素宽
                    
                    cursor_x = self.center_x - self.width/2 + 15 + text_width
                else:
                    cursor_x = self.center_x - self.width/2 + 15
                
                # 绘制光标
                arcade.draw_line(
                    cursor_x, self.center_y - self.height/2 + 10,
                    cursor_x, self.center_y + self.height/2 - 10,
                    WHITE, 2
                )
    
    def check_mouse_press(self, x, y):
        """检查鼠标是否点击了输入框"""
        return (
            self.center_x - self.width/2 <= x <= self.center_x + self.width/2 and
            self.center_y - self.height/2 <= y <= self.center_y + self.height/2
        )
    
    def add_character(self, character):
        """添加字符到输入框"""
        if len(self.text) < self.max_length:
            self.text += character
            # 重置光标可见性，使其立即显示
            self.cursor_visible = True
            self.cursor_blink_time = 0
    
    def remove_character(self):
        """删除最后一个字符"""
        if self.text:
            self.text = self.text[:-1]
            # 重置光标可见性，使其立即显示
            self.cursor_visible = True
            self.cursor_blink_time = 0

class WelcomeView(arcade.View):
    """欢迎界面"""
    def __init__(self):
        super().__init__()
        
        # 游戏核心
        self.game = ThreeKingdomsGame()
        
        # UI元素
        self.buttons = []
        self.setup()
        
        # 加载背景
        try:
            # 优先加载新背景图
            self.background_texture = arcade.load_texture("resources/back_ground.png")
        except:
            try:
                # 如果新背景加载失败，尝试加载旧背景
                self.background_texture = arcade.load_texture("resources/background.jpg")
            except:
                self.background_texture = None
            
        # 按钮音效
        self.hover_sound = arcade.load_sound(":resources:sounds/laser1.wav")
        self.click_sound = arcade.load_sound(":resources:sounds/hit1.wav")
        self.last_hovered_button = None
        
        # 动画效果
        self.title_animation = 0
    
    def setup(self):
        """设置界面元素"""
        # 添加开始按钮
        start_button = Button(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
            300, 60, "开始游戏",
            bg_color=(80, 100, 160),
            hover_color=(100, 120, 200)
        )
        self.buttons.append(start_button)
        
        # 添加退出按钮
        exit_button = Button(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130,
            300, 60, "退出游戏", 
            bg_color=(160, 60, 60), 
            hover_color=(200, 80, 80)
        )
        self.buttons.append(exit_button)
    
    def on_show(self):
        """视图显示时"""
        arcade.set_background_color(BACKGROUND_COLOR)
    
    def on_draw(self):
        """绘制界面"""
        arcade.start_render()
        
        # 绘制背景
        if self.background_texture:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                self.background_texture
            )
        
        # 绘制边框装饰
        border_width = 5
        border_color = GOLD
        padding = 20
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH - padding * 2, SCREEN_HEIGHT - padding * 2,
            border_color, border_width
        )
        
        # 绘制标题背景
        title_bg_width = 500
        title_bg_height = 100
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200,
            title_bg_width, title_bg_height,
            (20, 20, 50, 200)  # 半透明深蓝色
        )
        
        # 标题动画效果
        self.title_animation = (self.title_animation + 0.02) % 1.0
        title_scale = 1.0 + 0.05 * math.sin(self.title_animation * 2 * math.pi)
        
        # 绘制标题
        arcade.draw_text(
            "三国霸业",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200,
            GOLD,
            font_size=int(72 * title_scale),
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 绘制副标题
        arcade.draw_text(
            "公元184年，黄巾起义爆发，天下大乱\n各路英雄豪杰崛起，群雄逐鹿，天下三分\n你将在这乱世中建立霸业，成就一番伟业",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 300,
            WHITE,
            font_size=24,
            font_name=("SimHei", "Microsoft YaHei"),
            width=800,
            align="center",
            anchor_x="center"
        )
        
        # 绘制按钮
        for button in self.buttons:
            button.draw()
            
        # 绘制底部版权信息
        arcade.draw_text(
            "三国霸业 - 群雄逐鹿",
            SCREEN_WIDTH // 2, 30,
            (200, 200, 200, 150),  # 半透明灰白色
            font_size=18,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
    
    def on_mouse_motion(self, x, y, dx, dy):
        """处理鼠标移动"""
        # 检查按钮悬停
        hovered_button = None
        for button in self.buttons:
            if button.check_mouse_hover(x, y):
                hovered_button = button
                break
        
        # 播放悬停音效
        if hovered_button is not None and hovered_button != self.last_hovered_button:
            arcade.play_sound(self.hover_sound, 0.3)
            self.last_hovered_button = hovered_button
        elif hovered_button is None:
            self.last_hovered_button = None
    
    def on_mouse_press(self, x, y, button, modifiers):
        """处理鼠标点击"""
        if self.buttons[0].check_mouse_press(x, y):  # 开始游戏
            arcade.play_sound(self.click_sound, 0.5)
            self.game.initialize_game()
            create_player_view = CreatePlayerView(self.game)
            self.window.show_view(create_player_view)
        elif self.buttons[1].check_mouse_press(x, y):  # 退出游戏
            arcade.play_sound(self.click_sound, 0.5)
            arcade.close_window()
    
    def on_key_press(self, key, modifiers):
        """处理键盘按键事件"""
        # ESC键退出游戏
        if key == arcade.key.ESCAPE:
            arcade.close_window()
    
    def on_text(self, text):
        """处理文本输入事件"""
        pass  # 欢迎界面不需要处理文本输入，但需要实现此方法

class CreatePlayerView(arcade.View):
    """角色创建界面"""
    def __init__(self, game):
        super().__init__()
        self.game = game
        
        # UI元素
        self.buttons = []
        self.text_inputs = []
        self.active_text_input = None
        self.setup()
        
        # 加载背景
        try:
            # 优先加载新背景图
            self.background_texture = arcade.load_texture("resources/back_ground.png")
        except:
            try:
                # 如果新背景加载失败，尝试加载旧背景
                self.background_texture = arcade.load_texture("resources/background.jpg")
            except:
                self.background_texture = None
            
        # 按钮音效
        self.hover_sound = arcade.load_sound(":resources:sounds/laser1.wav")
        self.click_sound = arcade.load_sound(":resources:sounds/hit1.wav")
        self.last_hovered_button = None
        
        # 尝试加载刘备图片作为示例将领
        try:
            self.liubei_image = arcade.load_texture("resources/generals/liubei.png")
        except:
            self.liubei_image = None
    
    def setup(self):
        """设置界面元素"""
        # 添加名字输入框
        name_input = TextInputBox(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
            350, 50, placeholder="请输入您的名字"
        )
        self.text_inputs.append(name_input)
        
        # 添加势力选择按钮
        kingdoms = ["魏国", "蜀国", "吴国", "自立门户"]
        kingdom_colors = [
            (80, 80, 160),  # 魏国 - 蓝色
            (60, 140, 60),  # 蜀国 - 绿色
            (160, 60, 60),  # 吴国 - 红色
            (140, 100, 40)   # 自立门户 - 棕色
        ]
        
        # 左侧按钮（魏国，蜀国）
        for i in range(2):
            kingdom_button = Button(
                SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50 - i * 80,
                250, 60, kingdoms[i],
                bg_color=kingdom_colors[i],
                hover_color=(
                    min(kingdom_colors[i][0] + 40, 255),
                    min(kingdom_colors[i][1] + 40, 255),
                    min(kingdom_colors[i][2] + 40, 255)
                )
            )
            self.buttons.append(kingdom_button)
            
        # 右侧按钮（吴国，自立门户）
        for i in range(2, 4):
            kingdom_button = Button(
                SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 - 50 - (i-2) * 80,
                250, 60, kingdoms[i],
                bg_color=kingdom_colors[i],
                hover_color=(
                    min(kingdom_colors[i][0] + 40, 255),
                    min(kingdom_colors[i][1] + 40, 255),
                    min(kingdom_colors[i][2] + 40, 255)
                )
            )
            self.buttons.append(kingdom_button)
        
        # 添加返回按钮
        back_button = Button(
            SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 50,
            120, 50, "返回", bg_color=(100, 100, 100)
        )
        self.buttons.append(back_button)
    
    def on_show(self):
        """视图显示时"""
        arcade.set_background_color(BACKGROUND_COLOR)
    
    def on_draw(self):
        """绘制界面"""
        arcade.start_render()
        
        # 绘制背景
        if self.background_texture:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                self.background_texture
            )
        
        # 绘制边框装饰
        border_width = 5
        border_color = GOLD
        padding = 20
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH - padding * 2, SCREEN_HEIGHT - padding * 2,
            border_color, border_width
        )
        
        # 绘制标题背景
        title_bg_width = 500
        title_bg_height = 80
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            title_bg_width, title_bg_height,
            (20, 20, 50, 200)  # 半透明深蓝色
        )
        
        # 绘制标题
        arcade.draw_text(
            "创建角色",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            GOLD,
            font_size=48,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 绘制名字输入提示背景
        prompt_bg_width = 400
        prompt_bg_height = 40
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
            prompt_bg_width, prompt_bg_height,
            (30, 30, 60, 180)  # 半透明深色
        )
        
        # 绘制说明文本
        arcade.draw_text(
            "请创建你的角色:",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
            WHITE,
            font_size=24,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 绘制势力选择提示背景
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            400, 40,
            (30, 30, 60, 180)  # 半透明深色
        )
        
        arcade.draw_text(
            "请选择你效忠的势力:",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            WHITE,
            font_size=24,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 绘制输入框
        for text_input in self.text_inputs:
            text_input.draw()
        
        # 绘制按钮
        for button in self.buttons:
            button.draw()
            
        # 显示一个示例将领图片（如果有）
        if self.liubei_image:
            # 计算图片位置和大小
            image_width = 150
            image_height = 150
            image_x = SCREEN_WIDTH - 120
            image_y = SCREEN_HEIGHT - 120
            
            # 绘制图片边框
            arcade.draw_rectangle_filled(
                image_x, image_y, 
                image_width + 10, image_height + 10,
                (255, 215, 0, 150)  # 淡金色边框
            )
            
            # 绘制图片
            arcade.draw_texture_rectangle(
                image_x, image_y,
                image_width, image_height,
                self.liubei_image
            )
            
            # 绘制图片说明
            arcade.draw_text(
                "刘备",
                image_x, image_y - 90,
                WHITE,
                font_size=18,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
        
        # 绘制底部说明
        arcade.draw_text(
            "输入名字并选择势力开始游戏",
            SCREEN_WIDTH // 2, 30,
            (200, 200, 200, 150),  # 半透明灰白色
            font_size=18,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
    
    def on_mouse_motion(self, x, y, dx, dy):
        """处理鼠标移动"""
        # 检查按钮悬停
        hovered_button = None
        for button in self.buttons:
            if button.check_mouse_hover(x, y):
                hovered_button = button
                break
        
        # 播放悬停音效
        if hovered_button is not None and hovered_button != self.last_hovered_button:
            arcade.play_sound(self.hover_sound, 0.3)
            self.last_hovered_button = hovered_button
        elif hovered_button is None:
            self.last_hovered_button = None
    
    def on_mouse_press(self, x, y, button, modifiers):
        """处理鼠标点击"""
        # 检查文本输入框点击
        active_input_found = False
        for text_input in self.text_inputs:
            if text_input.check_mouse_press(x, y):
                self.active_text_input = text_input
                text_input.active = True
                active_input_found = True
            else:
                text_input.active = False
        
        if not active_input_found:
            self.active_text_input = None
        
        # 返回按钮
        if self.buttons[-1].check_mouse_press(x, y):
            arcade.play_sound(self.click_sound, 0.5)
            welcome_view = WelcomeView()
            self.window.show_view(welcome_view)
            return
        
        # 势力选择按钮
        for i, kingdom_button in enumerate(self.buttons[:-1]):
            if kingdom_button.check_mouse_press(x, y):
                arcade.play_sound(self.click_sound, 0.5)
                
                # 保存玩家信息，创建角色
                name = self.text_inputs[0].text
                if not name:
                    name = "无名英雄"
                
                # 创建玩家角色
                self.create_player(name, i)
                
                # 进入主菜单
                main_menu_view = MainMenuView(self.game)
                self.window.show_view(main_menu_view)
                break
    
    def on_key_press(self, key, modifiers):
        """处理键盘按键事件"""
        # ESC键返回
        if key == arcade.key.ESCAPE:
            welcome_view = WelcomeView()
            self.window.show_view(welcome_view)
        
        # 处理文本输入
        if self.active_text_input:
            if key == arcade.key.BACKSPACE:
                self.active_text_input.remove_character()
            elif key == arcade.key.ENTER:
                self.active_text_input.active = False
                self.active_text_input = None
            # 注意：对于中文输入，我们不在这里处理普通字符输入，而是在on_text方法中处理
    
    def on_text(self, text):
        """处理文本输入事件"""
        if self.active_text_input:
            self.active_text_input.add_character(text)
    
    def create_player(self, name, kingdom_choice):
        """创建玩家角色"""
        if kingdom_choice == 3:  # 自立门户
            kingdom_name = f"{name}军"
            player_kingdom = self.create_custom_kingdom(kingdom_name, name)
        else:
            player_kingdom = self.game.kingdoms[kingdom_choice]
        
        # 创建玩家角色
        from models.player import Player
        import random
        
        self.game.player = Player(
            name=name,
            kingdom=player_kingdom,
            leadership=random.randint(70, 95),
            strength=random.randint(70, 95),
            intelligence=random.randint(70, 95),
            politics=random.randint(70, 95),
            charisma=random.randint(70, 95)
        )
        
        # 分配初始军队
        from models.army import Army, TroopType
        
        initial_army = Army(
            size=5000,
            morale=80,
            training=70,
            primary_type=TroopType.INFANTRY,
            secondary_type=TroopType.CAVALRY
        )
        
        self.game.player.armies.append(initial_army)
    
    def create_custom_kingdom(self, name, leader_name):
        """创建自定义势力"""
        from models.kingdom import Kingdom
        
        new_kingdom = Kingdom(name, leader_name, "紫色")
        self.game.kingdoms.append(new_kingdom)
        return new_kingdom

class MainMenuView(arcade.View):
    """主菜单界面"""
    def __init__(self, game):
        super().__init__()
        self.game = game
        
        # UI元素
        self.buttons = []
        self.setup()
        
        # 加载背景
        try:
            # 优先加载新背景图
            self.background_texture = arcade.load_texture("resources/back_ground.png")
        except:
            try:
                # 如果新背景加载失败，尝试加载旧背景
                self.background_texture = arcade.load_texture("resources/background.jpg")
            except:
                self.background_texture = None
            
        # 按钮悬停音效
        self.hover_sound = arcade.load_sound(":resources:sounds/laser1.wav")
        self.click_sound = arcade.load_sound(":resources:sounds/hit1.wav")
        self.last_hovered_button = None
        
        # 尝试加载刘备图片
        try:
            self.liubei_image = arcade.load_texture("resources/generals/liubei.png")
        except:
            self.liubei_image = None
    
    def setup(self):
        """设置界面元素"""
        # 主菜单选项
        menu_options = [
            "继续剧情", "查看将领", "管理军队",
            "进行战斗", "城池管理", "外交联盟",
            "保存游戏", "退出游戏"
        ]
        
        # 更好看的按钮颜色
        button_colors = [
            (80, 80, 160), # 继续剧情 - 蓝色
            (100, 60, 140), # 查看将领 - 紫色
            (60, 120, 80), # 管理军队 - 绿色
            (160, 60, 60), # 进行战斗 - 红色
            (100, 100, 60), # 城池管理 - 黄褐色
            (60, 100, 140), # 外交联盟 - 蓝绿色
            (100, 80, 60), # 保存游戏 - 棕色
            (120, 60, 60)  # 退出游戏 - 暗红色
        ]
        
        # 改进按钮布局为两列
        button_width = 280
        button_height = 60
        button_spacing = 20
        
        # 左列按钮（前4个）
        left_column_x = SCREEN_WIDTH // 2 - 150
        for i in range(4):
            y_pos = SCREEN_HEIGHT - 280 - i * (button_height + button_spacing)
            button = Button(
                left_column_x, y_pos,
                button_width, button_height, 
                menu_options[i],
                bg_color=button_colors[i],
                hover_color=(min(button_colors[i][0] + 40, 255), 
                             min(button_colors[i][1] + 40, 255), 
                             min(button_colors[i][2] + 40, 255))
            )
            self.buttons.append(button)
        
        # 右列按钮（后4个）
        right_column_x = SCREEN_WIDTH // 2 + 150
        for i in range(4, 8):
            y_pos = SCREEN_HEIGHT - 280 - (i - 4) * (button_height + button_spacing)
            button = Button(
                right_column_x, y_pos,
                button_width, button_height, 
                menu_options[i],
                bg_color=button_colors[i],
                hover_color=(min(button_colors[i][0] + 40, 255), 
                             min(button_colors[i][1] + 40, 255), 
                             min(button_colors[i][2] + 40, 255))
            )
            self.buttons.append(button)
    
    def on_show(self):
        """视图显示时"""
        arcade.set_background_color(BACKGROUND_COLOR)
    
    def on_draw(self):
        """绘制界面"""
        arcade.start_render()
        
        # 绘制背景
        if self.background_texture:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                self.background_texture
            )
        
        # 绘制装饰性边框
        border_width = 5
        border_color = GOLD
        padding = 20
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH - padding * 2, SCREEN_HEIGHT - padding * 2,
            border_color, border_width
        )
        
        # 绘制标题背景
        title_bg_height = 120
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - title_bg_height // 2,
            SCREEN_WIDTH - padding * 4, title_bg_height,
            (20, 20, 50, 200)  # 半透明深蓝色
        )
        
        # 绘制标题
        arcade.draw_text(
            "主菜单",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80,
            GOLD,
            font_size=64,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 绘制玩家信息背景
        if self.game.player:
            info_bg_width = 600
            info_bg_height = 80
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT - 140,
                info_bg_width, info_bg_height,
                (30, 30, 60, 180)  # 半透明深色
            )
            
            # 绘制玩家信息
            arcade.draw_text(
                f"{self.game.player.name} - {self.game.player.kingdom.name}",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT - 140,
                GOLD,
                font_size=32,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            # 绘制玩家兵力信息
            arcade.draw_text(
                f"当前兵力: {sum(army.size for army in self.game.player.armies)}",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT - 170,
                WHITE,
                font_size=24,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
        
        # 绘制按钮
        for button in self.buttons:
            button.draw()
        
        # 显示刘备图片（如果有）
        if hasattr(self, 'liubei_image') and self.liubei_image:
            # 计算图片位置和大小
            image_width = 200
            image_height = 200
            image_x = SCREEN_WIDTH - 140
            image_y = SCREEN_HEIGHT - 260
            
            # 绘制图片背景
            arcade.draw_rectangle_filled(
                image_x, image_y, 
                image_width + 20, image_height + 20,
                (40, 40, 70, 180)  # 半透明背景
            )
            
            # 绘制图片边框
            arcade.draw_rectangle_outline(
                image_x, image_y, 
                image_width + 20, image_height + 20,
                GOLD, 2
            )
            
            # 绘制图片
            arcade.draw_texture_rectangle(
                image_x, image_y,
                image_width, image_height,
                self.liubei_image
            )
            
            # 绘制图片说明
            arcade.draw_text(
                "刘备",
                image_x, image_y - 110,
                GOLD,
                font_size=24,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            arcade.draw_text(
                "蜀国君主",
                image_x, image_y - 140,
                WHITE,
                font_size=18,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
        
        # 绘制底部版权信息
        arcade.draw_text(
            "三国霸业 - 群雄逐鹿",
            SCREEN_WIDTH // 2, 30,
            (200, 200, 200, 150),  # 半透明灰白色
            font_size=18,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
    
    def on_mouse_motion(self, x, y, dx, dy):
        """处理鼠标移动"""
        # 检查按钮悬停
        hovered_button = None
        for button in self.buttons:
            if button.check_mouse_hover(x, y):
                hovered_button = button
                break
        
        # 播放悬停音效
        if hovered_button is not None and hovered_button != self.last_hovered_button:
            arcade.play_sound(self.hover_sound, 0.3)
            self.last_hovered_button = hovered_button
        elif hovered_button is None:
            self.last_hovered_button = None
    
    def on_mouse_press(self, x, y, button, modifiers):
        """处理鼠标点击"""
        for i, btn in enumerate(self.buttons):
            if btn.check_mouse_press(x, y):
                arcade.play_sound(self.click_sound, 0.5)
                self.handle_main_menu_selection(i)
    
    def handle_main_menu_selection(self, index):
        """处理主菜单选择"""
        # 继续剧情
        if index == 0:
            # 创建并显示剧情界面
            story_view = StoryView(self.game)
            self.window.show_view(story_view)
            return
        
        # 查看将领
        elif index == 1:
            # 创建并显示将领界面
            generals_view = GeneralsView(self.game)
            self.window.show_view(generals_view)
            return
            
        # 管理军队
        elif index == 2:
            # Army management view implementation would go here
            pass
            
        # 进行战斗
        elif index == 3:
            # For demonstration, create a simple battle
            from models.army import Army, TroopType, Terrain
            
            # 创建玩家军队
            player_army = Army(
                size=5000,
                morale=80,
                training=70,
                primary_type=TroopType.INFANTRY,
                secondary_type=TroopType.CAVALRY
            )
            
            # 创建敌方军队
            enemy_army = Army(
                size=4000,
                morale=70,
                training=60,
                primary_type=TroopType.INFANTRY,
                secondary_type=TroopType.ARCHER
            )
            
            # 创建战斗数据对象
            class BattleData:
                def __init__(self, game):
                    self.game = game
                    self.attacker = player_army
                    self.defender = enemy_army
                    self.attacker_general = game.player.generals[0] if hasattr(game.player, 'generals') and game.player.generals else None
                    self.defender_general = None
                    self.terrain = Terrain.PLAIN
                    self.terrain_advantage = "neutral"  # 可以是 "attacker", "defender", "neutral"
            
            battle_data = BattleData(self.game)  # 传递游戏对象
            
            # 启动战斗视图
            battle_view = BattleView(
                self.window,  # 游戏窗口
                (self.window.width, self.window.height),  # 窗口尺寸
                self.game.player,  # 玩家对象
                battle_data  # 战斗数据
            )
            self.window.show_view(battle_view)
            
        # 城池管理
        elif index == 4:
            # For demonstration, use a sample city
            from models.city import City
            
            # If the player doesn't have a city yet, create a sample one
            if not hasattr(self.game, 'sample_city'):
                self.game.sample_city = City(
                    name="测试城市",
                    population=50000,
                    prosperity=70,
                    farms=30,
                    mines=10,
                    forts=1,
                    region="中原"
                )
                self.game.sample_city.owner = self.game.player.kingdom
            
            city_view = CityView(self.game, self.game.sample_city)
            self.window.show_view(city_view)
            
        # 外交联盟
        elif index == 5:
            # Diplomacy view implementation would go here
            pass
            
        # 保存游戏
        elif index == 6:
            # Save game implementation would go here
            arcade.draw_text(
                "游戏已保存！",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                GREEN,
                font_size=24,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
        # 退出游戏
        elif index == 7:
            arcade.close_window()
    
    def on_key_press(self, key, modifiers):
        """处理键盘按键事件"""
        # ESC键返回欢迎界面
        if key == arcade.key.ESCAPE:
            welcome_view = WelcomeView()
            self.window.show_view(welcome_view)
    
    def on_text(self, text):
        """处理文本输入事件"""
        pass  # 主菜单不需要处理文本输入，但需要实现此方法

class StoryView(arcade.View):
    """剧情展示界面"""
    def __init__(self, game):
        super().__init__()
        self.game = game
        
        # 获取当前章节内容
        self.chapter_title = ""
        self.chapter_intro = ""
        self.chapter_events = []
        self.chapter_choices = []
        self.current_event_index = 0
        self.display_text = ""
        self.text_speed = 2  # 文字显示速度
        self.text_progress = 0
        self.text_animation_active = False
        self.show_choices = False
        
        # 加载背景
        try:
            # 优先加载新背景图
            self.background_texture = arcade.load_texture("resources/back_ground.png")
        except:
            try:
                # 如果新背景加载失败，尝试加载旧背景
                self.background_texture = arcade.load_texture("resources/background.jpg")
            except:
                self.background_texture = None
        
        # 按钮
        self.buttons = []
        self.choice_buttons = []
        
        # 音效
        self.click_sound = arcade.load_sound(":resources:sounds/hit1.wav")
        self.hover_sound = arcade.load_sound(":resources:sounds/laser1.wav")
        self.last_hovered_button = None
        
        # 获取当前章节
        chapter_data = self.get_current_chapter_data()
        if chapter_data:
            # 确保章节标题不会太长
            self.chapter_title = self.limit_title_length(chapter_data['title'])
            self.chapter_intro = chapter_data['intro']
            self.chapter_events = chapter_data['events']
            self.chapter_choices = chapter_data.get('choices', [])
            
            # 开始显示介绍
            self.display_text = self.chapter_intro
            self.text_animation_active = True
        
        # 创建继续按钮
        continue_button = Button(
            SCREEN_WIDTH // 2, 100,
            200, 50, "继续", bg_color=(60, 100, 160)
        )
        self.buttons.append(continue_button)
        
        # 创建返回按钮
        back_button = Button(
            SCREEN_WIDTH - 100, 50,
            150, 50, "返回", bg_color=(100, 100, 100)
        )
        self.buttons.append(back_button)
    
    def limit_title_length(self, title):
        """限制标题长度，防止超出边框"""
        max_length = 12  # 最大标题字符数
        if len(title) > max_length:
            return title[:max_length-1] + '…'
        return title
    
    def get_current_chapter_data(self):
        """获取当前章节数据"""
        if hasattr(self.game, 'story') and self.game.story:
            chapters = self.game.story.chapters
            chapter_index = self.game.chapter
            
            if 0 <= chapter_index < len(chapters):
                chapter = chapters[chapter_index]
                return {
                    'title': chapter.title,
                    'intro': self.process_text_for_display(chapter.intro),
                    'events': [self.process_text_for_display(event) for event in chapter.events],
                    'choices': chapter.choices
                }
        
        # 如果无法获取章节数据，返回默认数据
        return {
            'title': '黄巾起义',
            'intro': self.process_text_for_display('建宁元年(公元168年)，黄巾军揭竿而起，以"苍天已死，黄天当立"为口号，席卷天下。朝廷命各地州郡镇压叛乱...'),
            'events': [
                self.process_text_for_display('你是一名地方上的小官吏，正值壮年，目睹黄巾军的暴行，决定挺身而出。'),
                self.process_text_for_display('当地太守征召勇士组建义军，你毫不犹豫地报名参加。'),
                self.process_text_for_display('在一场战斗中，你表现出色，成功击退了一支黄巾军，救下了一个村庄。'),
                self.process_text_for_display('你的名声开始在当地传开...')
            ],
            'choices': [
                {
                    'text': '加入官军，为朝廷效力',
                    'result': self.process_text_for_display('你加入了官军，在太守麾下效力。太守对你委以重任，给予你一支小队的指挥权。')
                },
                {
                    'text': '自立队伍，招募乡勇',
                    'result': self.process_text_for_display('你决定自立队伍，招募乡勇保卫家乡。不少当地青壮年响应你的号召，你很快组建了一支小型部队。')
                },
                {
                    'text': '投奔一方诸侯',
                    'result': self.process_text_for_display('你听闻刘备、曹操、孙坚等人都在各地起兵抗击黄巾，决定前去投奔一方诸侯。')
                }
            ]
        }
    
    def process_text_for_display(self, text):
        """处理文本以适应显示区域"""
        # 检查文本长度
        if len(text) <= 30:  # 短文本不需要特殊处理
            return text
            
        # 长文本根据标点符号添加换行
        result = ""
        chars_since_break = 0
        break_points = ['。', '！', '？', '，', '；', '：', '.', '!', '?', ',', ';', ':']
        
        for char in text:
            result += char
            chars_since_break += 1
            
            # 在标点符号处考虑换行
            if char in break_points and chars_since_break >= 20:
                result += "\n"
                chars_since_break = 0
                continue
            
            # 强制换行避免太长的句子
            if chars_since_break >= 30:
                # 添加换行，避免在单词中间断开
                if not result.endswith("\n"):
                    result += "\n"
                chars_since_break = 0
                
        return result
    
    def setup_choice_buttons(self):
        """设置选择按钮"""
        self.choice_buttons = []
        if self.chapter_choices:
            num_choices = len(self.chapter_choices)
            button_height = 60
            spacing = 20
            
            # 调整按钮位置到文本框下方，避免与文本重叠
            total_height = num_choices * button_height + (num_choices - 1) * spacing
            
            # 起始位置调整到文本框下方的中心位置
            start_y = SCREEN_HEIGHT // 2 - 50  # 文本框下方的起始位置
            
            for i, choice in enumerate(self.chapter_choices):
                y_pos = start_y - i * (button_height + spacing)
                
                # 创建渐变色按钮，使每个选项按钮颜色有区分
                base_color = (60, 80, 120)
                color_shift = i * 15  # 每个按钮颜色略有不同
                
                btn = Button(
                    SCREEN_WIDTH // 2, y_pos,
                    500, button_height, choice['text'],
                    bg_color=(base_color[0] + color_shift, 
                             base_color[1] + color_shift, 
                             base_color[2]),
                    hover_color=(min(base_color[0] + color_shift + 40, 255), 
                                min(base_color[1] + color_shift + 40, 255), 
                                min(base_color[2] + 40, 255))
                )
                self.choice_buttons.append(btn)
    
    def on_show(self):
        """视图显示时"""
        arcade.set_background_color(BACKGROUND_COLOR)
    
    def on_draw(self):
        """绘制界面"""
        arcade.start_render()
        
        # 绘制背景
        if self.background_texture:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                self.background_texture
            )
        
        # 绘制边框
        border_width = 5
        border_color = GOLD
        padding = 20
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH - padding * 2, SCREEN_HEIGHT - padding * 2,
            border_color, border_width
        )
        
        # 绘制章节标题背景 - 增加宽度以容纳更长的标题
        title_bg_width = 700
        title_bg_height = 80
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80,
            title_bg_width, title_bg_height,
            (20, 20, 50, 200)  # 半透明深蓝色
        )
        
        # 绘制章节标题
        arcade.draw_text(
            self.chapter_title,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80,
            GOLD,
            font_size=40,  # 稍微减小字体大小
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 如果显示选择，调整文本区域高度，给选择按钮留出空间
        text_bg_width = 1000
        text_bg_height = 450 if not self.show_choices else 350
        text_y_offset = 0 if not self.show_choices else 50  # 选择模式下上移文本区域
        
        # 绘制文本背景
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + text_y_offset,
            text_bg_width, text_bg_height,
            (30, 30, 60, 230)  # 调整透明度
        )
        
        # 绘制文本内容
        if self.text_animation_active:
            # 动画展示文本
            self.text_progress += self.text_speed
            visible_text = self.display_text[:int(self.text_progress)]
            if int(self.text_progress) >= len(self.display_text):
                self.text_animation_active = False
        else:
            visible_text = self.display_text
        
        # 文本渲染区域调整，优化显示效果
        text_margin = 40  # 增加文本边距
        text_width = text_bg_width - text_margin * 2  # 减小文本宽度，确保不会超出边框
        
        # 绘制文本内容，使用更清晰的渲染设置
        arcade.draw_text(
            visible_text,
            SCREEN_WIDTH // 2 - text_bg_width // 2 + text_margin, 
            SCREEN_HEIGHT // 2 + text_bg_height // 2 - text_margin + text_y_offset,
            WHITE,
            font_size=24,  # 调整为更小的字体
            font_name=("SimHei", "Microsoft YaHei"),
            width=text_width,
            multiline=True,
            anchor_x="left", anchor_y="top",
            align="left"
        )
        
        # 绘制选择按钮（如果显示选择）
        if self.show_choices:
            # 绘制选择提示背景
            choice_prompt_bg_width = 400
            choice_prompt_bg_height = 40
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130,
                choice_prompt_bg_width, choice_prompt_bg_height,
                (40, 40, 80, 200)  # 半透明背景
            )
            
            # 绘制选择提示文字
            arcade.draw_text(
                "请做出你的选择:",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130,
                GOLD,
                font_size=24,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
            
            # 绘制选择按钮
            for button in self.choice_buttons:
                button.draw()
        
        # 绘制操作按钮
        for button in self.buttons:
            button.draw()
    
    def on_mouse_motion(self, x, y, dx, dy):
        """处理鼠标移动"""
        # 检查按钮悬停
        hovered_button = None
        
        # 检查常规按钮
        for button in self.buttons:
            if button.check_mouse_hover(x, y):
                hovered_button = button
                break
        
        # 如果显示选择，检查选择按钮
        if self.show_choices:
            for button in self.choice_buttons:
                if button.check_mouse_hover(x, y):
                    hovered_button = button
                    break
        
        # 播放悬停音效
        if hovered_button is not None and hovered_button != self.last_hovered_button:
            arcade.play_sound(self.hover_sound, 0.3)
            self.last_hovered_button = hovered_button
        elif hovered_button is None:
            self.last_hovered_button = None
    
    def on_mouse_press(self, x, y, button, modifiers):
        """处理鼠标点击"""
        # 检查常规按钮
        for i, btn in enumerate(self.buttons):
            if btn.check_mouse_press(x, y):
                arcade.play_sound(self.click_sound, 0.5)
                
                if i == 0:  # 继续按钮
                    self.advance_story()
                elif i == 1:  # 返回按钮
                    main_menu_view = MainMenuView(self.game)
                    self.window.show_view(main_menu_view)
                return
        
        # 检查选择按钮
        if self.show_choices:
            for i, btn in enumerate(self.choice_buttons):
                if btn.check_mouse_press(x, y):
                    arcade.play_sound(self.click_sound, 0.5)
                    self.make_choice(i)
                    return
    
    def on_key_press(self, key, modifiers):
        """处理键盘按键"""
        if key == arcade.key.SPACE or key == arcade.key.ENTER:
            self.advance_story()
        elif key == arcade.key.ESCAPE:
            main_menu_view = MainMenuView(self.game)
            self.window.show_view(main_menu_view)
    
    def advance_story(self):
        """推进剧情"""
        # 如果文本动画正在进行，直接显示完整文本
        if self.text_animation_active:
            self.text_animation_active = False
            self.text_progress = len(self.display_text)
            return
        
        # 如果已经显示选择，不再推进
        if self.show_choices:
            return
        
        # 推进到下一个事件
        if self.current_event_index < len(self.chapter_events):
            event_text = self.chapter_events[self.current_event_index]
            # 确保文本已经正确处理换行
            if not isinstance(event_text, str):
                # 如果已经处理过，直接使用
                self.display_text = event_text
            else:
                # 如果没有处理过，先处理再使用
                self.display_text = self.process_text_for_display(event_text)
                
            self.text_animation_active = True
            self.text_progress = 0
            self.current_event_index += 1
        else:
            # 所有事件已展示，显示选择
            if self.chapter_choices:
                self.setup_choice_buttons()
                self.show_choices = True
            else:
                # 没有选择，章节结束，回到主菜单
                self.display_text = "章节结束"
                self.text_animation_active = True
                self.text_progress = 0
                # 增加章节序号
                self.game.chapter += 1
    
    def make_choice(self, choice_index):
        """做出选择"""
        if 0 <= choice_index < len(self.chapter_choices):
            choice = self.chapter_choices[choice_index]
            # 显示选择结果
            result_text = choice['result']
            if not isinstance(result_text, str):
                # 如果已经处理过，直接使用
                self.display_text = result_text
            else:
                # 如果没有处理过，先处理再使用
                self.display_text = self.process_text_for_display(result_text)
            
            self.text_animation_active = True
            self.text_progress = 0
            self.show_choices = False
            
            # 应用选择效果（在实际游戏中会更复杂）
            if 'effect' in choice and callable(choice['effect']):
                choice['effect'](self.game.player)
            
            # 增加章节序号
            self.game.chapter += 1
    
    def on_text(self, text):
        """处理文本输入事件"""
        pass  # 剧情界面不需要处理文本输入，但需要实现此方法

class GeneralsView(arcade.View):
    """将领查看界面"""
    def __init__(self, game):
        super().__init__()
        self.game = game
        
        # UI元素
        self.buttons = []
        self.generals_display = []
        self.current_page = 0
        self.generals_per_page = 4
        self.setup()
        
        # 加载背景
        try:
            # 优先加载新背景图
            self.background_texture = arcade.load_texture("resources/back_ground.png")
        except:
            try:
                # 如果新背景加载失败，尝试加载旧背景
                self.background_texture = arcade.load_texture("resources/background.jpg")
            except:
                self.background_texture = None
            
        # 按钮音效
        self.hover_sound = arcade.load_sound(":resources:sounds/laser1.wav")
        self.click_sound = arcade.load_sound(":resources:sounds/hit1.wav")
        self.last_hovered_button = None
        
        # 尝试加载刘备图片作为默认将领图片
        try:
            self.default_general_image = arcade.load_texture("resources/generals/liubei.png")
        except:
            self.default_general_image = None
    
    def setup(self):
        """设置界面元素"""
        # 根据玩家拥有的将领数量计算总页数
        player_generals = self.get_player_generals()
        total_pages = max(1, (len(player_generals) + self.generals_per_page - 1) // self.generals_per_page)
        
        # 添加返回按钮
        back_button = Button(
            100, 50,
            150, 50, "返回", bg_color=(100, 100, 100)
        )
        self.buttons.append(back_button)
        
        # 如果有多页，添加翻页按钮
        if total_pages > 1:
            # 上一页按钮
            prev_button = Button(
                SCREEN_WIDTH // 2 - 150, 50,
                150, 50, "上一页", bg_color=(80, 80, 160)
            )
            self.buttons.append(prev_button)
            
            # 下一页按钮
            next_button = Button(
                SCREEN_WIDTH // 2 + 150, 50,
                150, 50, "下一页", bg_color=(80, 80, 160)
            )
            self.buttons.append(next_button)
    
    def get_player_generals(self):
        """获取玩家的将领列表"""
        if not self.game.player or not hasattr(self.game.player, 'generals') or not self.game.player.generals:
            # 如果玩家没有将领，创建一些测试将领数据
            from models.general import General
            
            # 创建测试将领
            test_generals = [
                General(
                    name="刘备",
                    leadership=80,
                    strength=75,
                    intelligence=85,
                    politics=90,
                    charisma=95,
                    kingdom_name="蜀国",
                    image_path="resources/generals/liubei.png"
                ),
                General(
                    name="关羽",
                    leadership=90,
                    strength=97,
                    intelligence=80,
                    politics=70,
                    charisma=85,
                    kingdom_name="蜀国"
                ),
                General(
                    name="张飞",
                    leadership=85,
                    strength=97,
                    intelligence=70,
                    politics=65,
                    charisma=75,
                    kingdom_name="蜀国"
                ),
                General(
                    name="诸葛亮",
                    leadership=95,
                    strength=65,
                    intelligence=100,
                    politics=95,
                    charisma=90,
                    kingdom_name="蜀国"
                ),
                General(
                    name="赵云",
                    leadership=85,
                    strength=90,
                    intelligence=80,
                    politics=75,
                    charisma=85,
                    kingdom_name="蜀国"
                )
            ]
            
            # 如果玩家对象存在但没有将领列表，初始化将领列表
            if self.game.player and not hasattr(self.game.player, 'generals'):
                self.game.player.generals = []
            
            # 将测试将领添加到玩家的将领列表中
            if self.game.player:
                if not hasattr(self.game.player, 'generals'):
                    self.game.player.generals = []
                
                if not self.game.player.generals:
                    self.game.player.generals = test_generals
            
            # 返回测试将领数据
            return test_generals
            
        return self.game.player.generals
    
    def on_show(self):
        """视图显示时"""
        arcade.set_background_color(BACKGROUND_COLOR)
    
    def on_draw(self):
        """绘制界面"""
        arcade.start_render()
        
        # 绘制背景
        if self.background_texture:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                self.background_texture
            )
        
        # 绘制边框装饰
        border_width = 5
        border_color = GOLD
        padding = 20
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH - padding * 2, SCREEN_HEIGHT - padding * 2,
            border_color, border_width
        )
        
        # 绘制标题背景
        title_bg_width = 500
        title_bg_height = 80
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80,
            title_bg_width, title_bg_height,
            (20, 20, 50, 200)  # 半透明深蓝色
        )
        
        # 绘制标题
        arcade.draw_text(
            "将领查看",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80,
            GOLD,
            font_size=48,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
        
        # 获取当前页的将领列表
        player_generals = self.get_player_generals()
        start_idx = self.current_page * self.generals_per_page
        current_page_generals = player_generals[start_idx:start_idx + self.generals_per_page]
        
        # 如果没有将领，显示提示信息
        if not current_page_generals:
            # 绘制提示信息背景
            info_bg_width = 600
            info_bg_height = 100
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                info_bg_width, info_bg_height,
                (30, 30, 60, 200)  # 半透明深蓝色
            )
            
            # 绘制提示信息
            arcade.draw_text(
                "你目前没有将领。\n可以通过游戏剧情或招募功能获取将领。",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                WHITE,
                font_size=24,
                font_name=("SimHei", "Microsoft YaHei"),
                width=550,
                align="center",
                anchor_x="center", anchor_y="center"
            )
        else:
            # 绘制将领信息
            for i, general in enumerate(current_page_generals):
                # 计算每个将领卡片的位置
                # 将屏幕分为2行2列
                row = i // 2
                col = i % 2
                
                # 计算卡片位置
                card_width = 450
                card_height = 220
                card_spacing_x = 80
                card_spacing_y = 50
                
                # 计算中心位置
                center_x = SCREEN_WIDTH // 4 + (SCREEN_WIDTH // 2) * col + (col * card_spacing_x)
                center_y = SCREEN_HEIGHT - 180 - (card_height + card_spacing_y) * row
                
                # 绘制卡片背景
                arcade.draw_rectangle_filled(
                    center_x, center_y,
                    card_width, card_height,
                    (40, 40, 70, 220)  # 半透明深色
                )
                
                # 绘制卡片边框
                arcade.draw_rectangle_outline(
                    center_x, center_y,
                    card_width, card_height,
                    GOLD, 2
                )
                
                # 绘制将领头像背景
                portrait_size = 150
                portrait_x = center_x - card_width // 2 + portrait_size // 2 + 15
                portrait_y = center_y
                
                arcade.draw_rectangle_filled(
                    portrait_x, portrait_y,
                    portrait_size, portrait_size,
                    (60, 60, 100, 180)  # 半透明背景
                )
                
                # 尝试加载将领特定的图像
                general_image = None
                if hasattr(general, 'image_path') and general.image_path:
                    try:
                        general_image = arcade.load_texture(general.image_path)
                    except:
                        general_image = None
                
                # 如果没有特定图像，使用默认的刘备图像
                if general_image is None:
                    general_image = self.default_general_image
                
                # 绘制将领头像
                if general_image:
                    arcade.draw_texture_rectangle(
                        portrait_x, portrait_y,
                        portrait_size - 10, portrait_size - 10,
                        general_image
                    )
                
                # 绘制将领名称和基本信息
                name_x = center_x + 50
                name_y = center_y + card_height // 2 - 40
                
                # 绘制将领名字
                arcade.draw_text(
                    general.name,
                    name_x, name_y,
                    GOLD,
                    font_size=28,
                    font_name=("SimHei", "Microsoft YaHei"),
                    anchor_x="left"
                )
                
                # 绘制将领属性
                stats_x = name_x
                stats_spacing = 30
                
                # 统率
                arcade.draw_text(
                    f"统率: {general.leadership}",
                    stats_x, name_y - stats_spacing,
                    WHITE,
                    font_size=20,
                    font_name=("SimHei", "Microsoft YaHei"),
                    anchor_x="left"
                )
                
                # 武力
                arcade.draw_text(
                    f"武力: {general.strength}",
                    stats_x, name_y - stats_spacing * 2,
                    WHITE,
                    font_size=20,
                    font_name=("SimHei", "Microsoft YaHei"),
                    anchor_x="left"
                )
                
                # 智力
                arcade.draw_text(
                    f"智力: {general.intelligence}",
                    stats_x, name_y - stats_spacing * 3,
                    WHITE,
                    font_size=20,
                    font_name=("SimHei", "Microsoft YaHei"),
                    anchor_x="left"
                )
                
                # 政治
                arcade.draw_text(
                    f"政治: {general.politics}",
                    stats_x, name_y - stats_spacing * 4,
                    WHITE,
                    font_size=20,
                    font_name=("SimHei", "Microsoft YaHei"),
                    anchor_x="left"
                )
                
                # 显示所属势力
                arcade.draw_text(
                    f"势力: {general.kingdom_name}",
                    portrait_x, portrait_y - portrait_size // 2 - 15,
                    WHITE,
                    font_size=16,
                    font_name=("SimHei", "Microsoft YaHei"),
                    anchor_x="center"
                )
            
            # 显示分页信息
            total_pages = (len(player_generals) + self.generals_per_page - 1) // self.generals_per_page
            
            arcade.draw_text(
                f"第 {self.current_page + 1} 页 / 共 {total_pages} 页",
                SCREEN_WIDTH // 2, 100,
                WHITE,
                font_size=18,
                font_name=("SimHei", "Microsoft YaHei"),
                anchor_x="center"
            )
        
        # 绘制按钮
        for button in self.buttons:
            button.draw()
        
        # 绘制底部提示
        arcade.draw_text(
            "点击返回按钮返回主菜单",
            SCREEN_WIDTH // 2, 20,
            (200, 200, 200, 150),  # 半透明灰白色
            font_size=16,
            font_name=("SimHei", "Microsoft YaHei"),
            anchor_x="center"
        )
    
    def on_mouse_motion(self, x, y, dx, dy):
        """处理鼠标移动"""
        # 检查按钮悬停
        hovered_button = None
        for button in self.buttons:
            if button.check_mouse_hover(x, y):
                hovered_button = button
                break
        
        # 播放悬停音效
        if hovered_button is not None and hovered_button != self.last_hovered_button:
            arcade.play_sound(self.hover_sound, 0.3)
            self.last_hovered_button = hovered_button
        elif hovered_button is None:
            self.last_hovered_button = None
    
    def on_mouse_press(self, x, y, button, modifiers):
        """处理鼠标点击"""
        # 检查按钮点击
        for i, btn in enumerate(self.buttons):
            if btn.check_mouse_press(x, y):
                arcade.play_sound(self.click_sound, 0.5)
                
                if i == 0:  # 返回按钮
                    main_menu_view = MainMenuView(self.game)
                    self.window.show_view(main_menu_view)
                elif i == 1:  # 上一页按钮
                    self.current_page = max(0, self.current_page - 1)
                elif i == 2:  # 下一页按钮
                    player_generals = self.get_player_generals()
                    total_pages = (len(player_generals) + self.generals_per_page - 1) // self.generals_per_page
                    self.current_page = min(self.current_page + 1, total_pages - 1)
                return
    
    def on_key_press(self, key, modifiers):
        """处理键盘按键事件"""
        if key == arcade.key.ESCAPE:
            main_menu_view = MainMenuView(self.game)
            self.window.show_view(main_menu_view)
        elif key == arcade.key.LEFT:
            # 上一页
            self.current_page = max(0, self.current_page - 1)
        elif key == arcade.key.RIGHT:
            # 下一页
            player_generals = self.get_player_generals()
            total_pages = (len(player_generals) + self.generals_per_page - 1) // self.generals_per_page
            self.current_page = min(self.current_page + 1, total_pages - 1)
    
    def on_text(self, text):
        """处理文本输入事件"""
        pass  # 将领界面不需要处理文本输入

def main():
    """游戏主入口"""
    # 创建游戏资源目录
    if not os.path.exists("resources"):
        os.makedirs("resources")
    
    # 启动游戏窗口
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
    welcome_view = WelcomeView()
    window.show_view(welcome_view)
    arcade.run()

if __name__ == "__main__":
    main() 
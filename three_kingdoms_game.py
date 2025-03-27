#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time
import os
import json
from models.general import General
from models.army import Army, TroopType
from models.kingdom import Kingdom
from models.player import Player
from modules.battle import Battle
from modules.story import Story, Chapter
from modules.game_data import load_game_data

class ThreeKingdomsGame:
    def __init__(self):
        self.player = None
        self.kingdoms = []
        self.generals = []
        self.story = None
        self.chapter = 0
        self.game_running = True
        
    def initialize_game(self):
        """初始化游戏数据"""
        print("正在加载三国演义世界...")
        time.sleep(1)
        
        # 加载游戏数据
        game_data = load_game_data()
        
        # 初始化三个主要势力
        self.kingdoms = [
            Kingdom("魏国", "曹操", "蓝色"),
            Kingdom("蜀国", "刘备", "绿色"),
            Kingdom("吴国", "孙权", "红色")
        ]
        
        # 加载将领数据
        self.generals = game_data["generals"]
        
        # 分配将领到相应的势力
        for general in self.generals:
            for kingdom in self.kingdoms:
                if general.kingdom_name == kingdom.name:
                    kingdom.add_general(general)
        
        # 初始化故事
        self.story = Story()
        
    def display_welcome(self):
        """显示欢迎信息"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("欢迎来到【三国霸业】文字游戏")
        print("公元184年，黄巾起义爆发，天下大乱")
        print("各路英雄豪杰崛起，群雄逐鹿，天下三分")
        print("你将在这乱世中建立霸业，成就一番伟业")
        print("=" * 60)
        time.sleep(2)
    
    def create_player(self):
        """创建玩家角色"""
        print("\n请创建你的角色：")
        name = input("请输入你的名字: ")
        
        print("\n请选择你效忠的势力：")
        print("1. 魏国 - 曹操")
        print("2. 蜀国 - 刘备")
        print("3. 吴国 - 孙权")
        print("4. 自立门户")
        
        choice = int(input("你的选择(1-4): "))
        
        if choice == 4:
            kingdom_name = input("请为你的势力取个名字: ")
            color = "紫色"
            player_kingdom = Kingdom(kingdom_name, name, color)
            self.kingdoms.append(player_kingdom)
        else:
            player_kingdom = self.kingdoms[choice-1]
        
        # 创建玩家角色
        self.player = Player(
            name=name,
            kingdom=player_kingdom,
            leadership=random.randint(70, 95),
            strength=random.randint(70, 95),
            intelligence=random.randint(70, 95),
            politics=random.randint(70, 95),
            charisma=random.randint(70, 95)
        )
        
        # 分配初始军队
        initial_army = Army(
            size=5000,
            morale=80,
            training=70,
            primary_type=TroopType.INFANTRY,
            secondary_type=TroopType.CAVALRY
        )
        
        self.player.armies.append(initial_army)
        
        print(f"\n{name}，欢迎加入三国乱世！")
        time.sleep(1)
    
    def main_menu(self):
        """显示主菜单"""
        while self.game_running:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"== {self.player.name} - {self.player.kingdom.name} ==")
            print(f"当前兵力: {sum(army.size for army in self.player.armies)}")
            print("\n主菜单:")
            print("1. 继续剧情")
            print("2. 查看将领")
            print("3. 管理军队")
            print("4. 进行战斗")
            print("5. 城池管理")
            print("6. 外交联盟")
            print("7. 保存游戏")
            print("8. 退出游戏")
            
            choice = input("\n请选择(1-8): ")
            
            if choice == "1":
                self.progress_story()
            elif choice == "2":
                self.manage_generals()
            elif choice == "3":
                self.manage_armies()
            elif choice == "4":
                self.initiate_battle()
            elif choice == "5":
                self.manage_cities()
            elif choice == "6":
                self.diplomacy()
            elif choice == "7":
                self.save_game()
            elif choice == "8":
                confirm = input("确定要退出游戏吗？(Y/N): ")
                if confirm.upper() == "Y":
                    print("感谢游玩！")
                    self.game_running = False
    
    def progress_story(self):
        """推进游戏剧情"""
        self.story.play_chapter(self.chapter, self.player)
        self.chapter += 1
        input("\n按回车键继续...")
    
    def manage_generals(self):
        """管理将领"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("== 将领管理 ==")
        
        # 显示玩家麾下的将领
        if self.player.generals:
            print("\n你的将领:")
            for i, general in enumerate(self.player.generals, 1):
                print(f"{i}. {general.name} - 统率:{general.leadership} 武力:{general.strength} 智力:{general.intelligence} 政治:{general.politics}")
        else:
            print("\n你目前没有将领。")
        
        print("\n选项:")
        print("1. 招募新将领")
        print("2. 训练将领")
        print("3. 返回主菜单")
        
        choice = input("\n请选择(1-3): ")
        if choice == "3":
            return
        
        # 这里添加招募和训练将领的逻辑
        input("\n开发中... 按回车键返回")
    
    def manage_armies(self):
        """管理军队"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("== 军队管理 ==")
        
        if self.player.armies:
            print("\n你的军队:")
            for i, army in enumerate(self.player.armies, 1):
                print(f"{i}. {army.primary_type.name} - 兵力:{army.size} 士气:{army.morale} 训练:{army.training}")
        else:
            print("\n你目前没有军队。")
        
        print("\n选项:")
        print("1. 招募新兵")
        print("2. 训练军队")
        print("3. 更换兵种")
        print("4. 返回主菜单")
        
        choice = input("\n请选择(1-4): ")
        if choice == "4":
            return
            
        # 这里添加军队管理的逻辑
        input("\n开发中... 按回车键返回")
    
    def initiate_battle(self):
        """发起战斗"""
        # 战斗逻辑将在modules/battle.py中实现
        input("开发中... 按回车键返回")
    
    def manage_cities(self):
        """管理城池"""
        input("开发中... 按回车键返回")
    
    def diplomacy(self):
        """外交系统"""
        input("开发中... 按回车键返回")
    
    def save_game(self):
        """保存游戏"""
        print("正在保存游戏...")
        time.sleep(1)
        print("游戏已保存！")
        input("按回车键继续...")
    
    def run(self):
        """运行游戏"""
        self.display_welcome()
        self.initialize_game()
        self.create_player()
        self.main_menu()

if __name__ == "__main__":
    game = ThreeKingdomsGame()
    game.run() 
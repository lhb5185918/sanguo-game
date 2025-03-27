#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from enum import Enum

class Skill(Enum):
    """将领可拥有的技能枚举"""
    FIRE_ATTACK = "火计"  # 提高火攻效果
    WATER_STRATEGY = "水计"  # 提高水战能力
    AMBUSH = "伏兵"  # 可以设置伏兵
    FORMATION_BREAK = "破阵"  # 克制敌方阵型
    CHARGE = "冲阵"  # 提高骑兵冲锋效果
    IRON_DEFENSE = "铁壁"  # 提高防御能力
    COUNTER = "反击"  # 提高反击成功率
    INSPIRE = "鼓舞"  # 提高军队士气
    LOGISTICS = "辎重"  # 提高行军和补给效率
    SIEGE = "攻城"  # 提高攻城效率
    DUEL = "单挑"  # 提高单挑胜率
    WISDOM = "智谋"  # 提高计谋成功率

class General:
    """将领类，代表游戏中的武将"""
    
    def __init__(self, name, leadership, strength, intelligence, politics, charisma, kingdom_name="未知", image_path=None):
        self.name = name  # 姓名
        self.kingdom_name = kingdom_name  # 所属势力
        self.leadership = leadership  # 统率，影响指挥军队能力
        self.strength = strength  # 武力，影响战斗和单挑能力
        self.intelligence = intelligence  # 智力，影响计谋和策略
        self.politics = politics  # 政治，影响内政和外交
        self.charisma = charisma  # 魅力，影响招募和士气
        self.image_path = image_path  # 将领图像路径
        
        self.level = 1  # 等级
        self.experience = 0  # 经验值
        self.loyalty = 100  # 忠诚度
        self.skills = []  # 技能列表
        self.equipment = []  # 装备
        self.troops_bonus = {}  # 对特定兵种的加成
        
    def __str__(self):
        return f"{self.name} - {self.kingdom_name}"
        
    def add_skill(self, skill):
        """添加技能"""
        if skill not in self.skills and isinstance(skill, Skill):
            self.skills.append(skill)
            return True
        return False
        
    def remove_skill(self, skill):
        """移除技能"""
        if skill in self.skills:
            self.skills.remove(skill)
            return True
        return False
    
    def gain_experience(self, amount):
        """获得经验值"""
        self.experience += amount
        # 检查是否可以升级
        exp_needed = self.level * 100
        if self.experience >= exp_needed:
            self.level_up()
    
    def level_up(self):
        """升级，提升属性"""
        self.level += 1
        self.experience = 0
        
        # 随机提升属性
        attributes = ["leadership", "strength", "intelligence", "politics", "charisma"]
        for _ in range(3):  # 每次升级提升3个随机属性
            attr = random.choice(attributes)
            setattr(self, attr, getattr(self, attr) + random.randint(1, 3))
        
        # 检查是否学习新技能
        if self.level % 5 == 0:  # 每5级有机会学习新技能
            available_skills = [s for s in Skill if s not in self.skills]
            if available_skills:
                new_skill = random.choice(available_skills)
                self.add_skill(new_skill)
                return f"{self.name}学会了新技能: {new_skill.value}！"
        
        return f"{self.name}升级了！当前等级: {self.level}"
    
    def calculate_battle_power(self):
        """计算战斗力"""
        base_power = (self.leadership * 2 + self.strength * 1.5 + 
                      self.intelligence * 1.2 + self.politics * 0.5 + 
                      self.charisma * 0.8)
        
        # 技能加成
        skill_bonus = len(self.skills) * 10
        
        # 等级加成
        level_bonus = self.level * 5
        
        return int(base_power + skill_bonus + level_bonus)
    
    def duel(self, opponent):
        """与另一名将领进行单挑"""
        own_power = self.strength * 0.7 + self.intelligence * 0.3 + random.randint(1, 20)
        
        if Skill.DUEL in self.skills:
            own_power *= 1.25  # 单挑技能加成
            
        opp_power = opponent.strength * 0.7 + opponent.intelligence * 0.3 + random.randint(1, 20)
        
        if Skill.DUEL in opponent.skills:
            opp_power *= 1.25
            
        if own_power > opp_power:
            return True, int(own_power - opp_power)  # 胜利，返回优势值
        else:
            return False, int(opp_power - own_power)  # 失败，返回劣势值 
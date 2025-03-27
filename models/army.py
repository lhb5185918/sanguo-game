#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum, auto
import random

class TroopType(Enum):
    """兵种类型枚举"""
    INFANTRY = "步兵"  # 步兵，基础兵种
    CAVALRY = "骑兵"  # 骑兵，机动性强
    ARCHER = "弓兵"  # 弓箭手，远程攻击
    SPEARMAN = "枪兵"  # 枪兵，克制骑兵
    CROSSBOWMAN = "弩兵"  # 弩兵，强化远程攻击
    SHIELDED = "盾兵"  # 盾兵，防御型
    NAVY = "水军"  # 水军，水战特长
    SIEGE = "攻城兵"  # 攻城兵种

class Terrain(Enum):
    """地形类型枚举"""
    PLAIN = "平原"
    MOUNTAIN = "山地"
    FOREST = "森林"
    RIVER = "河流"
    MARSH = "沼泽"
    CITY = "城池"
    FORT = "关隘"

# 兵种相克关系
TROOP_COUNTERS = {
    TroopType.INFANTRY: {TroopType.ARCHER: 1.2},  # 步兵克制弓兵
    TroopType.CAVALRY: {TroopType.INFANTRY: 1.3},  # 骑兵克制步兵
    TroopType.SPEARMAN: {TroopType.CAVALRY: 1.3},  # 枪兵克制骑兵
    TroopType.ARCHER: {TroopType.SPEARMAN: 1.2},  # 弓兵克制枪兵
    TroopType.CROSSBOWMAN: {TroopType.INFANTRY: 1.2, TroopType.SPEARMAN: 1.2},  # 弩兵克制步兵和枪兵
    TroopType.SHIELDED: {TroopType.ARCHER: 1.5, TroopType.CROSSBOWMAN: 1.3},  # 盾兵克制弓兵和弩兵
    TroopType.NAVY: {},  # 水军没有特定克制
    TroopType.SIEGE: {}  # 攻城兵没有特定克制
}

# 兵种在不同地形的效果
TERRAIN_EFFECTS = {
    TroopType.INFANTRY: {Terrain.PLAIN: 1.0, Terrain.MOUNTAIN: 0.9, Terrain.FOREST: 0.9, Terrain.RIVER: 0.7, Terrain.MARSH: 0.8},
    TroopType.CAVALRY: {Terrain.PLAIN: 1.2, Terrain.MOUNTAIN: 0.6, Terrain.FOREST: 0.7, Terrain.RIVER: 0.5, Terrain.MARSH: 0.6},
    TroopType.ARCHER: {Terrain.PLAIN: 1.0, Terrain.MOUNTAIN: 1.1, Terrain.FOREST: 0.8, Terrain.RIVER: 0.9, Terrain.MARSH: 0.8},
    TroopType.SPEARMAN: {Terrain.PLAIN: 1.0, Terrain.MOUNTAIN: 0.9, Terrain.FOREST: 0.9, Terrain.RIVER: 0.7, Terrain.MARSH: 0.8},
    TroopType.CROSSBOWMAN: {Terrain.PLAIN: 1.0, Terrain.MOUNTAIN: 1.1, Terrain.FOREST: 0.8, Terrain.RIVER: 0.9, Terrain.MARSH: 0.8},
    TroopType.SHIELDED: {Terrain.PLAIN: 1.0, Terrain.MOUNTAIN: 0.9, Terrain.FOREST: 0.9, Terrain.RIVER: 0.7, Terrain.MARSH: 0.7},
    TroopType.NAVY: {Terrain.PLAIN: 0.6, Terrain.MOUNTAIN: 0.5, Terrain.FOREST: 0.5, Terrain.RIVER: 1.5, Terrain.MARSH: 1.2},
    TroopType.SIEGE: {Terrain.PLAIN: 0.9, Terrain.MOUNTAIN: 0.7, Terrain.FOREST: 0.7, Terrain.RIVER: 0.5, Terrain.MARSH: 0.6},
}

class Army:
    """军队类，代表一支部队"""
    
    def __init__(self, size, morale, training, primary_type, secondary_type=None):
        self.size = size  # 兵力数量
        self.morale = morale  # 士气，影响战斗力
        self.training = training  # 训练度，影响战斗表现
        self.primary_type = primary_type  # 主要兵种
        self.secondary_type = secondary_type  # 次要兵种（可选）
        self.secondary_ratio = 0.3 if secondary_type else 0  # 次要兵种占比
        
        # 军队可携带的粮草和补给
        self.food = size * 5  # 每兵5单位粮食
        self.equipment_level = 1  # 装备等级
        
        # 战斗相关属性
        self.fatigue = 0  # 疲劳度
        self.experience = 0  # 战斗经验
        
    def __str__(self):
        if self.secondary_type:
            return f"{self.primary_type.value}/{self.secondary_type.value}混合军 - {self.size}人"
        return f"{self.primary_type.value} - {self.size}人"
    
    def get_battle_power(self, terrain=Terrain.PLAIN, general=None):
        """计算在特定地形下的战斗力，可选将领加成"""
        # 基础战斗力
        base_power = self.size * (self.morale / 100) * (self.training / 100)
        
        # 地形加成
        terrain_factor = TERRAIN_EFFECTS.get(self.primary_type, {}).get(terrain, 1.0)
        if self.secondary_type:
            secondary_terrain_factor = TERRAIN_EFFECTS.get(self.secondary_type, {}).get(terrain, 1.0)
            # 混合计算地形因子
            terrain_factor = terrain_factor * (1 - self.secondary_ratio) + secondary_terrain_factor * self.secondary_ratio
        
        # 装备和经验加成
        equipment_bonus = self.equipment_level * 0.1
        experience_bonus = self.experience * 0.0001  # 小幅度经验加成
        
        # 疲劳度减益
        fatigue_penalty = max(0, 1 - (self.fatigue / 100))
        
        # 将领加成
        general_bonus = 1.0
        if general:
            leadership_bonus = general.leadership * 0.005  # 每点统率增加0.5%战斗力
            general_bonus += leadership_bonus
            
            # 特定兵种加成
            if self.primary_type in general.troops_bonus:
                general_bonus += general.troops_bonus[self.primary_type]
        
        return base_power * terrain_factor * (1 + equipment_bonus + experience_bonus) * fatigue_penalty * general_bonus
    
    def take_casualties(self, amount):
        """承受伤亡"""
        if amount >= self.size:
            self.size = 0
            return True  # 军队被歼灭
        
        self.size -= amount
        
        # 士气降低
        morale_drop = (amount / self.size) * 20
        self.morale = max(10, self.morale - morale_drop)
        
        return False  # 军队仍存在
    
    def merge_army(self, other_army):
        """合并另一支军队"""
        if self.primary_type != other_army.primary_type:
            # 如果主要兵种不同，设置次要兵种
            if not self.secondary_type:
                self.secondary_type = other_army.primary_type
                total_size = self.size + other_army.size
                self.secondary_ratio = other_army.size / total_size
                self.size = total_size
            else:
                # 已有次要兵种，调整比例
                total_size = self.size + other_army.size
                primary_amount = self.size * (1 - self.secondary_ratio)
                secondary_amount = self.size * self.secondary_ratio
                
                if other_army.primary_type == self.secondary_type:
                    secondary_amount += other_army.size
                else:
                    # 三种兵种情况，简化处理，主要保留最多的两种
                    primary_amount += other_army.size
                
                self.size = total_size
                self.secondary_ratio = secondary_amount / total_size
        else:
            # 主要兵种相同，直接合并
            self.size += other_army.size
        
        # 平均士气和训练度
        self.morale = (self.morale * self.size + other_army.morale * other_army.size) / (self.size + other_army.size)
        self.training = (self.training * self.size + other_army.training * other_army.size) / (self.size + other_army.size)
        
        # 合并粮草
        self.food += other_army.food
        
        # 保持疲劳度为两者中较高的
        self.fatigue = max(self.fatigue, other_army.fatigue)
        
        # 累积经验
        self.experience += other_army.experience
    
    def rest(self, days):
        """休整军队，恢复士气和减少疲劳"""
        # 每天恢复5点士气，降低10点疲劳
        self.morale = min(100, self.morale + days * 5)
        self.fatigue = max(0, self.fatigue - days * 10)
        
        # 消耗粮食
        food_consumption = self.size * days
        if food_consumption > self.food:
            # 粮食不足，士气下降
            self.morale = max(10, self.morale - 10)
            self.food = 0
        else:
            self.food -= food_consumption
    
    def train(self, days, general=None):
        """训练军队，提升训练度"""
        base_increase = days * 0.5  # 基础每天提升0.5训练度
        
        # 将领加成
        if general:
            leadership_bonus = general.leadership * 0.01  # 统率加成
            base_increase *= (1 + leadership_bonus)
        
        # 消耗粮食
        food_consumption = self.size * days * 1.2  # 训练消耗更多粮食
        if food_consumption > self.food:
            # 粮食不足，训练效果减半
            base_increase *= 0.5
            self.food = 0
        else:
            self.food -= food_consumption
        
        # 增加疲劳
        self.fatigue = min(100, self.fatigue + days * 5)
        
        # 提升训练度
        self.training = min(100, self.training + base_increase)
    
    def create_unit(self, unit_size):
        """创建一个相同类型但规模较小的军队单位
        
        Args:
            unit_size: 新单位的兵力规模
            
        Returns:
            Army: 新的军队单位实例
        """
        # 创建一个与当前军队属性相同但规模较小的新单位
        unit = Army(
            size=unit_size,
            morale=self.morale,
            training=self.training,
            primary_type=self.primary_type,
            secondary_type=self.secondary_type
        )
        
        # 复制其他相关属性
        unit.secondary_ratio = self.secondary_ratio
        unit.equipment_level = self.equipment_level
        unit.fatigue = self.fatigue
        unit.experience = self.experience
        
        # 按比例分配粮食
        unit.food = int(self.food * (unit_size / self.size)) if self.size > 0 else 0
        
        return unit 
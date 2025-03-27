#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

class Building:
    """建筑类，代表城市中的各种建筑"""
    
    def __init__(self, name, level=1, cost=100, maintenance=10, benefits=None):
        self.name = name  # 建筑名称
        self.level = level  # 建筑等级
        self.cost = cost  # 建造成本
        self.maintenance = maintenance  # 维护成本
        self.benefits = benefits or {}  # 提供的加成
    
    def upgrade(self):
        """升级建筑"""
        self.level += 1
        self.cost = int(self.cost * 1.5)
        self.maintenance = int(self.maintenance * 1.2)
        
        # 升级加成
        for benefit, value in self.benefits.items():
            self.benefits[benefit] = int(value * 1.3)
            
        return self.level

class City:
    """城市类，代表游戏中的一座城池"""
    
    def __init__(self, name, population, prosperity, farms, mines, forts, region):
        self.name = name  # 城市名称
        self.population = population  # 人口
        self.prosperity = prosperity  # 繁荣度
        self.farms = farms  # 农田数量
        self.mines = mines  # 矿山数量
        self.forts = forts  # 城防等级
        self.region = region  # 所属地区
        
        self.owner = None  # 所属势力
        self.governor = None  # 太守/太守将领
        self.garrison = []  # 驻军
        self.loyalty = 80  # 忠诚度
        self.tax_rate = 0.1  # 税率
        self.growth_rate = 0.01  # 人口增长率
        
        # 建筑列表
        self.buildings = {
            "城墙": Building("城墙", level=forts, cost=500, maintenance=50, benefits={"防御": 100 * forts}),
            "粮仓": Building("粮仓", level=1, cost=300, maintenance=30, benefits={"粮食储量": 5000}),
            "集市": Building("集市", level=1, cost=400, maintenance=40, benefits={"商业收入": 100}),
            "兵营": Building("兵营", level=1, cost=500, maintenance=50, benefits={"征兵效率": 10, "训练速度": 5}),
        }
        
        # 资源产出
        self.production = {
            "gold": int(population * 0.1 * prosperity / 100),  # 金钱产出
            "food": farms * 100,  # 粮食产出
            "iron": mines * 20,  # 铁矿产出
            "wood": int(region == "益州" or region == "荆州") * farms * 10,  # 木材产出
        }
        
    def __str__(self):
        return f"{self.name} - 人口: {self.population}, 繁荣度: {self.prosperity}"
    
    def set_owner(self, kingdom):
        """设置城市归属"""
        if self.owner:
            self.owner.remove_city(self)
        
        self.owner = kingdom
        kingdom.add_city(self)
        self.loyalty = max(50, self.loyalty - 20)  # 易主后忠诚度下降
        
        return True
    
    def set_governor(self, general):
        """任命太守"""
        self.governor = general
        
        # 太守的政治属性影响城市发展
        politics_bonus = general.politics / 100
        self.prosperity = min(100, self.prosperity + 5)
        self.loyalty = min(100, self.loyalty + 10)
        self.growth_rate = max(0.01, self.growth_rate + politics_bonus * 0.005)
        
        return True
    
    def add_garrison(self, army):
        """添加驻军"""
        if army not in self.garrison:
            self.garrison.append(army)
            return True
        return False
    
    def remove_garrison(self, army):
        """移除驻军"""
        if army in self.garrison:
            self.garrison.remove(army)
            return True
        return False
    
    def total_garrison_size(self):
        """获取总驻军数量"""
        return sum(army.size for army in self.garrison)
    
    def set_tax_rate(self, rate):
        """设置税率"""
        old_rate = self.tax_rate
        self.tax_rate = max(0.05, min(0.3, rate))  # 限制税率在5%-30%之间
        
        # 税率对忠诚度和繁荣度的影响
        if self.tax_rate > old_rate:
            self.loyalty = max(10, self.loyalty - (self.tax_rate - old_rate) * 100)
            self.prosperity = max(10, self.prosperity - (self.tax_rate - old_rate) * 100)
        elif self.tax_rate < old_rate:
            self.loyalty = min(100, self.loyalty + (old_rate - self.tax_rate) * 50)
            self.prosperity = min(100, self.prosperity + (old_rate - self.tax_rate) * 50)
        
        # 更新金钱产出
        self.update_production()
        
        return self.tax_rate
    
    def expand_farms(self, amount):
        """扩建农田"""
        cost = amount * 200  # 每个农田200金
        
        if self.owner and self.owner.resources["gold"] >= cost:
            self.owner.resources["gold"] -= cost
            self.farms += amount
            
            # 更新粮食产出
            self.production["food"] = self.farms * 100
            
            return True
        return False
    
    def expand_mines(self, amount):
        """扩建矿山"""
        cost = amount * 300  # 每个矿山300金
        
        if self.owner and self.owner.resources["gold"] >= cost:
            self.owner.resources["gold"] -= cost
            self.mines += amount
            
            # 更新矿物产出
            self.production["iron"] = self.mines * 20
            
            return True
        return False
    
    def upgrade_building(self, building_name):
        """升级建筑"""
        if building_name not in self.buildings:
            return False
            
        building = self.buildings[building_name]
        cost = building.cost
        
        if self.owner and self.owner.resources["gold"] >= cost:
            self.owner.resources["gold"] -= cost
            building.upgrade()
            
            # 特殊建筑效果
            if building_name == "城墙":
                self.forts = building.level
            
            return True
        return False
    
    def collect_taxes(self):
        """收税"""
        tax_income = int(self.population * self.tax_rate * self.prosperity / 100)
        
        if self.owner:
            self.owner.resources["gold"] += tax_income
        
        # 税收可能降低忠诚度
        self.loyalty = max(10, self.loyalty - self.tax_rate * 10)
        
        return tax_income
    
    def update_production(self):
        """更新资源产出"""
        self.production = {
            "gold": int(self.population * self.tax_rate * self.prosperity / 100),
            "food": self.farms * 100,
            "iron": self.mines * 20,
            "wood": int((self.region == "益州" or self.region == "荆州") * self.farms * 10),
        }
        
        # 建筑加成
        if "集市" in self.buildings:
            self.production["gold"] += self.buildings["集市"].benefits.get("商业收入", 0)
        
        return self.production
    
    def monthly_update(self):
        """每月更新城市状态"""
        # 人口增长
        growth = int(self.population * self.growth_rate * (self.prosperity / 100))
        self.population += growth
        
        # 忠诚度变化
        loyalty_change = 0
        
        # 太守影响
        if self.governor:
            politics_effect = (self.governor.politics - 50) / 10
            loyalty_change += politics_effect
        
        # 驻军影响
        garrison_size = self.total_garrison_size()
        if garrison_size > self.population * 0.1:
            # 驻军过多会降低忠诚度
            loyalty_change -= (garrison_size / self.population - 0.1) * 10
        elif garrison_size < self.population * 0.02:
            # 驻军太少，治安不足
            loyalty_change -= 5
        else:
            # 适量驻军
            loyalty_change += 1
        
        # 税率影响
        if self.tax_rate > 0.2:
            loyalty_change -= (self.tax_rate - 0.2) * 50
        
        # 繁荣度影响
        prosperity_effect = (self.prosperity - 50) / 25
        loyalty_change += prosperity_effect
        
        # 应用忠诚度变化
        self.loyalty = max(10, min(100, self.loyalty + loyalty_change))
        
        # 繁荣度变化
        prosperity_change = 0
        
        # 税率影响繁荣度
        if self.tax_rate > 0.15:
            prosperity_change -= (self.tax_rate - 0.15) * 30
        else:
            prosperity_change += 1
        
        # 人口密度影响
        ideal_population = self.farms * 1000  # 理想人口
        if self.population > ideal_population * 1.2:
            # 人口过多，资源紧张
            prosperity_change -= (self.population / ideal_population - 1.2) * 10
        
        # 应用繁荣度变化
        self.prosperity = max(10, min(100, self.prosperity + prosperity_change))
        
        # 检查叛乱风险
        if self.loyalty < 30 and random.random() < 0.2:
            return {"event": "rebellion", "message": f"{self.name}忠诚度过低，发生叛乱！"}
        
        # 更新资源产出
        self.update_production()
        
        return {"population_growth": growth, "loyalty_change": loyalty_change, "prosperity_change": prosperity_change}
    
    def recruit_troops(self, amount, troop_type):
        """在城市中征兵"""
        # 检查人口是否足够
        if amount > self.population * 0.05:  # 最多征召5%的人口
            amount = int(self.population * 0.05)
        
        if self.owner:
            new_army = self.owner.recruit_troops(amount, troop_type)
            if new_army:
                self.population -= amount  # 征兵减少人口
                
                # 征兵影响忠诚度
                self.loyalty = max(10, self.loyalty - amount / self.population * 50)
                
                return new_army
        
        return None
    
    def train_garrison(self, days):
        """训练驻军"""
        for army in self.garrison:
            # 尝试找到合适的将领来训练
            trainer = None
            if self.governor and self.governor.leadership > 70:
                trainer = self.governor
            
            army.train(days, trainer)
        
        return True
    
    def get_defense_bonus(self):
        """获取城市防御加成"""
        base_defense = self.buildings.get("城墙").benefits.get("防御", 0)
        terrain_bonus = 1.0
        
        # 地区特殊加成
        if self.region == "益州":
            terrain_bonus = 1.2  # 益州山地多，易守难攻
        elif self.region == "河北":
            terrain_bonus = 1.1  # 河北平原要塞
        
        return base_defense * terrain_bonus 
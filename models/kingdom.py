#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from models.army import Army, TroopType

class Kingdom:
    """势力类，代表游戏中的一个势力/国家"""
    
    def __init__(self, name, leader_name, color):
        self.name = name  # 势力名称
        self.leader_name = leader_name  # 势力领袖名
        self.color = color  # 势力颜色表示
        
        self.cities = []  # 控制的城市
        self.generals = []  # 麾下将领
        self.armies = []  # 拥有的军队
        self.resources = {
            "gold": 1000,  # 金钱
            "food": 5000,  # 粮食
            "iron": 100,  # 铁
            "wood": 200,  # 木材
            "horses": 50,  # 战马
        }
        
        # 外交关系
        self.relations = {}  # 与其他势力的关系，值从-100到100
        self.alliances = []  # 同盟
        self.wars = []  # 正在交战的势力
        
        # 发展相关
        self.tech_level = 1  # 科技水平
        self.population = 0  # 总人口
        self.reputation = 50  # 声望，影响招募和外交
        
    def __str__(self):
        return f"{self.name} - 统治者: {self.leader_name}"
    
    def add_general(self, general):
        """添加将领"""
        if general not in self.generals:
            self.generals.append(general)
            general.kingdom_name = self.name
            return True
        return False
    
    def remove_general(self, general):
        """移除将领"""
        if general in self.generals:
            self.generals.remove(general)
            return True
        return False
    
    def add_city(self, city):
        """添加城市"""
        if city not in self.cities:
            self.cities.append(city)
            city.owner = self
            self.population += city.population
            return True
        return False
    
    def remove_city(self, city):
        """失去城市"""
        if city in self.cities:
            self.cities.remove(city)
            self.population -= city.population
            return True
        return False
    
    def add_army(self, army):
        """添加军队"""
        if army not in self.armies:
            self.armies.append(army)
            return True
        return False
    
    def total_military_power(self):
        """计算总军事实力"""
        return sum(army.size for army in self.armies)
    
    def top_generals(self, count=3):
        """返回实力最强的几名将领"""
        sorted_generals = sorted(self.generals, key=lambda g: g.calculate_battle_power(), reverse=True)
        return sorted_generals[:count]
    
    def declare_war(self, other_kingdom):
        """向另一个势力宣战"""
        if other_kingdom not in self.wars:
            self.wars.append(other_kingdom)
            if other_kingdom in self.alliances:
                self.alliances.remove(other_kingdom)
                other_kingdom.alliances.remove(self)
            
            # 建立敌对关系
            self.relations[other_kingdom.name] = -50
            other_kingdom.relations[self.name] = -50
            
            # 对方也进入战争状态
            if self not in other_kingdom.wars:
                other_kingdom.wars.append(self)
            
            return True
        return False
    
    def make_peace(self, other_kingdom):
        """与另一个势力议和"""
        if other_kingdom in self.wars:
            self.wars.remove(other_kingdom)
            other_kingdom.wars.remove(self)
            
            # 关系略微改善
            self.relations[other_kingdom.name] = max(-20, self.relations.get(other_kingdom.name, 0))
            other_kingdom.relations[self.name] = max(-20, other_kingdom.relations.get(self.name, 0))
            
            return True
        return False
    
    def form_alliance(self, other_kingdom):
        """与另一个势力结盟"""
        if other_kingdom not in self.alliances and other_kingdom not in self.wars:
            self.alliances.append(other_kingdom)
            other_kingdom.alliances.append(self)
            
            # 关系大幅改善
            self.relations[other_kingdom.name] = min(100, (self.relations.get(other_kingdom.name, 0) + 50))
            other_kingdom.relations[self.name] = min(100, (other_kingdom.relations.get(self.name, 0) + 50))
            
            return True
        return False
    
    def break_alliance(self, other_kingdom):
        """解除同盟"""
        if other_kingdom in self.alliances:
            self.alliances.remove(other_kingdom)
            other_kingdom.alliances.remove(self)
            
            # 关系恶化
            self.relations[other_kingdom.name] = max(-20, (self.relations.get(other_kingdom.name, 0) - 30))
            other_kingdom.relations[self.name] = max(-20, (other_kingdom.relations.get(self.name, 0) - 30))
            
            return True
        return False
    
    def collect_tax(self):
        """收税，获取金钱"""
        base_tax = sum(city.population * 0.1 for city in self.cities)
        prosperity_bonus = sum(city.prosperity * 0.01 for city in self.cities)
        
        tax_collected = int(base_tax * (1 + prosperity_bonus))
        self.resources["gold"] += tax_collected
        
        # 税收可能影响声望
        self.reputation -= 1
        
        return tax_collected
    
    def harvest_food(self):
        """收集粮食"""
        base_food = sum(city.farms * 100 for city in self.cities)
        weather_factor = random.uniform(0.8, 1.2)  # 天气因素
        
        food_collected = int(base_food * weather_factor)
        self.resources["food"] += food_collected
        
        return food_collected
    
    def research_tech(self):
        """研究新技术"""
        if self.resources["gold"] >= self.tech_level * 500:
            self.resources["gold"] -= self.tech_level * 500
            self.tech_level += 1
            return True
        return False
    
    def recruit_troops(self, amount, troop_type):
        """招募新兵"""
        cost_per_soldier = {
            TroopType.INFANTRY: 2,
            TroopType.CAVALRY: 5,
            TroopType.ARCHER: 3,
            TroopType.SPEARMAN: 2.5,
            TroopType.CROSSBOWMAN: 4,
            TroopType.SHIELDED: 3.5,
            TroopType.NAVY: 4,
            TroopType.SIEGE: 6
        }
        
        gold_cost = amount * cost_per_soldier.get(troop_type, 2)
        food_cost = amount * 2
        
        # 特殊兵种的额外资源需求
        special_resource = None
        special_amount = 0
        
        if troop_type == TroopType.CAVALRY:
            special_resource = "horses"
            special_amount = amount // 2
        elif troop_type == TroopType.CROSSBOWMAN or troop_type == TroopType.SIEGE:
            special_resource = "wood"
            special_amount = amount // 3
        
        # 检查资源是否足够
        if (self.resources["gold"] >= gold_cost and 
            self.resources["food"] >= food_cost and 
            (not special_resource or self.resources[special_resource] >= special_amount)):
            
            # 扣除资源
            self.resources["gold"] -= gold_cost
            self.resources["food"] -= food_cost
            if special_resource:
                self.resources[special_resource] -= special_amount
            
            # 创建新军队
            new_army = Army(
                size=amount,
                morale=70,
                training=50,
                primary_type=troop_type
            )
            
            self.add_army(new_army)
            return new_army
        
        return None
    
    def monthly_update(self):
        """每月更新，处理常规事务"""
        # 收税
        tax = self.collect_tax()
        
        # 收获粮食
        food = self.harvest_food()
        
        # 军队维护成本
        military_upkeep = sum(army.size * 0.1 for army in self.armies)
        if self.resources["gold"] >= military_upkeep:
            self.resources["gold"] -= military_upkeep
        else:
            # 金钱不足，军队士气降低
            deficit = military_upkeep - self.resources["gold"]
            self.resources["gold"] = 0
            morale_drop = min(20, deficit / 100)
            for army in self.armies:
                army.morale = max(10, army.morale - morale_drop)
        
        # 粮食消耗
        food_consumption = sum(army.size * 0.5 for army in self.armies)
        food_consumption += sum(city.population * 0.1 for city in self.cities)
        
        if self.resources["food"] >= food_consumption:
            self.resources["food"] -= food_consumption
        else:
            # 粮食不足，人口和军队都受影响
            deficit = food_consumption - self.resources["food"]
            self.resources["food"] = 0
            
            # 军队士气大幅下降
            for army in self.armies:
                army.morale = max(10, army.morale - 20)
            
            # 城市繁荣度下降
            starvation_factor = deficit / food_consumption
            for city in self.cities:
                city.prosperity = max(10, city.prosperity - starvation_factor * 10)
                
                # 人口减少
                population_loss = int(city.population * starvation_factor * 0.05)
                city.population = max(100, city.population - population_loss)
                self.population -= population_loss
        
        # 城市发展
        for city in self.cities:
            city.monthly_update()
            
        # 随机事件
        self.random_events()
        
        return {"tax": tax, "food": food}
    
    def random_events(self):
        """随机事件处理"""
        # 可能发生的随机事件，如灾害、叛乱、人才出现等
        event_chance = random.random()
        if event_chance < 0.05:  # 5%概率发生事件
            event_type = random.choice(["disaster", "rebellion", "talent", "windfall"])
            
            if event_type == "disaster":
                # 自然灾害
                affected_city = random.choice(self.cities) if self.cities else None
                if affected_city:
                    severity = random.uniform(0.05, 0.2)
                    affected_city.population = int(affected_city.population * (1 - severity))
                    affected_city.prosperity = max(10, affected_city.prosperity - 20)
                    self.population = sum(city.population for city in self.cities)
                    return f"{affected_city.name}遭遇自然灾害，人口减少，繁荣度下降。"
                    
            elif event_type == "rebellion":
                # 叛乱
                if len(self.cities) > 1 and random.random() < 0.3:
                    rebellious_city = random.choice(self.cities)
                    self.remove_city(rebellious_city)
                    return f"{rebellious_city.name}发生叛乱，城市失守！"
                
            elif event_type == "talent":
                # 人才出现
                # 生成一个随机将领（实现细节略）
                return "一位新的人才出现，寻求加入您的势力。"
                
            elif event_type == "windfall":
                # 意外收获
                resource_type = random.choice(["gold", "food", "iron", "wood", "horses"])
                amount = random.randint(100, 500)
                self.resources[resource_type] += amount
                return f"您的势力发现了{amount}单位的{resource_type}。"
        
        return None 
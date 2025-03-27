#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models.general import General

class Player(General):
    """玩家类，继承自将领，拥有特殊能力和属性"""
    
    def __init__(self, name, kingdom, leadership, strength, intelligence, politics, charisma):
        super().__init__(name, kingdom.name, leadership, strength, intelligence, politics, charisma)
        self.kingdom = kingdom  # 玩家所属势力
        self.armies = []  # 直接控制的军队
        self.fame = 10  # 声望，影响招募和事件
        self.achievement_points = 0  # 成就点数
        self.quests = []  # 当前任务
        self.completed_quests = []  # 已完成任务
        self.title = "普通将领"  # 头衔
        self.items = []  # 持有的物品
    
    def gain_fame(self, amount):
        """获得声望"""
        self.fame += amount
        if self.fame >= 100 and self.title == "普通将领":
            self.title = "知名将领"
        elif self.fame >= 300 and self.title == "知名将领":
            self.title = "著名将领"
        elif self.fame >= 600 and self.title == "著名将领":
            self.title = "一方诸侯"
        elif self.fame >= 1000 and self.title == "一方诸侯":
            self.title = "雄霸一方"
        elif self.fame >= 2000 and self.title == "雄霸一方":
            self.title = "战神"
        
        return self.title if self.title != "普通将领" else None
    
    def add_army(self, army):
        """添加军队到玩家的直接控制下"""
        if army not in self.armies:
            self.armies.append(army)
            return True
        return False
    
    def total_army_size(self):
        """获取玩家直接控制的总兵力"""
        return sum(army.size for army in self.armies)
    
    def add_quest(self, quest):
        """添加新任务"""
        if quest not in self.quests and quest not in self.completed_quests:
            self.quests.append(quest)
            return True
        return False
    
    def complete_quest(self, quest):
        """完成任务"""
        if quest in self.quests:
            self.quests.remove(quest)
            self.completed_quests.append(quest)
            
            # 获得奖励
            self.gain_experience(quest.exp_reward)
            self.gain_fame(quest.fame_reward)
            self.achievement_points += quest.achievement_points
            
            # 如果有物品奖励
            if quest.item_reward:
                self.items.append(quest.item_reward)
            
            return True
        return False
    
    def can_recruit_general(self, general):
        """检查是否能招募特定将领"""
        # 基于声望和魅力计算招募几率
        recruit_chance = (self.fame * 0.1 + self.charisma * 0.5) / 100
        
        # 特殊条件检查（略）
        
        return recruit_chance
    
    def promote(self):
        """晋升，提高在势力中的地位"""
        # 晋升所需成就点
        promotion_cost = {
            "普通将领": 10,
            "知名将领": 30,
            "著名将领": 60,
            "一方诸侯": 100,
            "雄霸一方": 200,
            "战神": 999,  # 已是最高级
        }
        
        if self.achievement_points >= promotion_cost.get(self.title, 0) and self.title != "战神":
            self.achievement_points -= promotion_cost.get(self.title, 0)
            
            # 头衔晋升
            if self.title == "普通将领":
                self.title = "知名将领"
            elif self.title == "知名将领":
                self.title = "著名将领"
            elif self.title == "著名将领":
                self.title = "一方诸侯"
            elif self.title == "一方诸侯":
                self.title = "雄霸一方"
            elif self.title == "雄霸一方":
                self.title = "战神"
            
            # 获得晋升奖励
            self.leadership += 5
            self.strength += 3
            self.intelligence += 3
            self.politics += 3
            self.charisma += 5
            
            return True
        return False
    
    def get_status_report(self):
        """获取玩家状态报告"""
        report = {
            "name": self.name,
            "title": self.title,
            "kingdom": self.kingdom.name,
            "level": self.level,
            "experience": self.experience,
            "fame": self.fame,
            "achievement_points": self.achievement_points,
            "attributes": {
                "leadership": self.leadership,
                "strength": self.strength,
                "intelligence": self.intelligence,
                "politics": self.politics,
                "charisma": self.charisma
            },
            "army_size": self.total_army_size(),
            "armies": [str(army) for army in self.armies],
            "active_quests": len(self.quests),
            "completed_quests": len(self.completed_quests),
            "items": len(self.items)
        }
        
        return report 
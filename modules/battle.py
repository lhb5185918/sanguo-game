#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time
from models.army import Army, TroopType, Terrain, TROOP_COUNTERS

class BattlePhase:
    """战斗阶段枚举"""
    DEPLOYMENT = "部署阶段"
    RANGED = "远程阶段"
    MELEE = "近战阶段"
    PURSUIT = "追击阶段"
    RETREAT = "撤退阶段"

class BattleResult:
    """战斗结果类"""
    def __init__(self, winner, loser, is_decisive, attacker_casualties, defender_casualties, battle_log):
        self.winner = winner  # 胜利方
        self.loser = loser  # 失败方
        self.is_decisive = is_decisive  # 是否决定性胜利
        self.attacker_casualties = attacker_casualties  # 进攻方伤亡
        self.defender_casualties = defender_casualties  # 防守方伤亡
        self.battle_log = battle_log  # 战斗日志
        self.exp_gained = max(10, int((attacker_casualties + defender_casualties) / 100))  # 获得的经验值

class Battle:
    """战斗系统类"""
    
    def __init__(self, attacker_armies, defender_armies, attacker_generals=None, defender_generals=None, terrain=Terrain.PLAIN):
        self.attacker_armies = attacker_armies if isinstance(attacker_armies, list) else [attacker_armies]
        self.defender_armies = defender_armies if isinstance(defender_armies, list) else [defender_armies]
        
        self.attacker_generals = attacker_generals if isinstance(attacker_generals, list) else ([attacker_generals] if attacker_generals else [])
        self.defender_generals = defender_generals if isinstance(defender_generals, list) else ([defender_generals] if defender_generals else [])
        
        self.terrain = terrain
        self.battle_log = []
        self.current_phase = BattlePhase.DEPLOYMENT
        
        # 战斗统计
        self.attacker_casualties = 0
        self.defender_casualties = 0
        self.attacker_morale_loss = 0
        self.defender_morale_loss = 0
        
        # 特殊战术和计谋
        self.attacker_tactics = []
        self.defender_tactics = []
        
    def log(self, message):
        """添加战斗日志"""
        self.battle_log.append(message)
        
    def calculate_army_power(self, armies, generals, is_attacker):
        """计算军队战斗力"""
        total_power = 0
        
        # 分配将领到军队 (简化为均匀分配，实际可以更复杂)
        assigned_generals = []
        if generals:
            assigned_generals = generals[:len(armies)]
            
        for i, army in enumerate(armies):
            # 获取该军队的将领（如果有）
            general = assigned_generals[i] if i < len(assigned_generals) else None
            
            # 计算基本战斗力
            army_power = army.get_battle_power(self.terrain, general)
            
            # 进攻/防守加成
            if is_attacker:
                if self.current_phase == BattlePhase.RANGED and army.primary_type in [TroopType.ARCHER, TroopType.CROSSBOWMAN]:
                    army_power *= 1.2  # 远程阶段弓兵加成
                elif self.current_phase == BattlePhase.MELEE and army.primary_type in [TroopType.INFANTRY, TroopType.SPEARMAN]:
                    army_power *= 1.1  # 近战阶段步兵和枪兵加成
                elif self.current_phase == BattlePhase.PURSUIT and army.primary_type == TroopType.CAVALRY:
                    army_power *= 1.3  # 追击阶段骑兵加成
            else:  # 防守方
                if self.current_phase == BattlePhase.RANGED and army.primary_type == TroopType.SHIELDED:
                    army_power *= 1.3  # 远程阶段盾兵加成
                elif self.terrain == Terrain.FORT or self.terrain == Terrain.CITY:
                    army_power *= 1.25  # 防守关隘或城池加成
                
            # 战术加成
            tactics = self.attacker_tactics if is_attacker else self.defender_tactics
            for tactic in tactics:
                if tactic == "火攻" and self.terrain in [Terrain.FOREST, Terrain.CITY]:
                    if random.random() < 0.3:  # 30%几率触发火攻效果
                        army_power *= 1.5
                        self.log(f"{'进攻方' if is_attacker else '防守方'}成功发动火攻！")
                elif tactic == "埋伏" and self.current_phase == BattlePhase.DEPLOYMENT:
                    if random.random() < 0.4:  # 40%几率触发埋伏效果
                        army_power *= 1.3
                        self.log(f"{'进攻方' if is_attacker else '防守方'}设置了埋伏！")
            
            # 兵种相克关系
            if not is_attacker:  # 只在防守方检查相克关系，以简化计算
                for enemy_army in self.attacker_armies:
                    counter_bonus = TROOP_COUNTERS.get(army.primary_type, {}).get(enemy_army.primary_type, 1.0)
                    if counter_bonus > 1.0:
                        army_power *= counter_bonus
                        self.log(f"{army.primary_type.value}克制{enemy_army.primary_type.value}，获得战斗加成！")
            
            total_power += army_power
            
        return total_power
        
    def conduct_battle_phase(self):
        """进行一个战斗阶段"""
        attacker_power = self.calculate_army_power(self.attacker_armies, self.attacker_generals, True)
        defender_power = self.calculate_army_power(self.defender_armies, self.defender_generals, False)
        
        self.log(f"=== {self.current_phase} ===")
        self.log(f"进攻方战斗力: {int(attacker_power)}")
        self.log(f"防守方战斗力: {int(defender_power)}")
        
        # 计算伤亡率
        power_ratio = attacker_power / defender_power if defender_power > 0 else 10
        
        # 设定基础伤亡率
        base_attacker_casualty_rate = 0.05  # 5%基础伤亡
        base_defender_casualty_rate = 0.05
        
        # 根据战斗力比例调整伤亡率
        if power_ratio > 1:  # 进攻方更强
            defender_casualty_rate = base_defender_casualty_rate * power_ratio
            attacker_casualty_rate = base_attacker_casualty_rate / power_ratio
        else:  # 防守方更强
            defender_casualty_rate = base_defender_casualty_rate / (1/power_ratio)
            attacker_casualty_rate = base_attacker_casualty_rate * (1/power_ratio)
        
        # 战斗阶段特殊调整
        if self.current_phase == BattlePhase.RANGED:
            # 远程阶段对有弓兵的一方有利
            attacker_archers = any(army.primary_type in [TroopType.ARCHER, TroopType.CROSSBOWMAN] for army in self.attacker_armies)
            defender_archers = any(army.primary_type in [TroopType.ARCHER, TroopType.CROSSBOWMAN] for army in self.defender_armies)
            
            if attacker_archers and not defender_archers:
                defender_casualty_rate *= 1.5
                attacker_casualty_rate *= 0.7
            elif defender_archers and not attacker_archers:
                attacker_casualty_rate *= 1.5
                defender_casualty_rate *= 0.7
                
        elif self.current_phase == BattlePhase.PURSUIT:
            # 追击阶段对有骑兵的一方有利
            attacker_cavalry = any(army.primary_type == TroopType.CAVALRY for army in self.attacker_armies)
            
            if attacker_cavalry:
                defender_casualty_rate *= 1.8  # 骑兵追击效果显著
        
        # 计算实际伤亡
        attacker_total_size = sum(army.size for army in self.attacker_armies)
        defender_total_size = sum(army.size for army in self.defender_armies)
        
        # 确保伤亡率不会过高
        attacker_casualty_rate = min(0.3, attacker_casualty_rate)
        defender_casualty_rate = min(0.3, defender_casualty_rate)
        
        attacker_phase_casualties = int(attacker_total_size * attacker_casualty_rate)
        defender_phase_casualties = int(defender_total_size * defender_casualty_rate)
        
        # 更新总伤亡
        self.attacker_casualties += attacker_phase_casualties
        self.defender_casualties += defender_phase_casualties
        
        # 分配伤亡到各个军队
        self.distribute_casualties(self.attacker_armies, attacker_phase_casualties)
        self.distribute_casualties(self.defender_armies, defender_phase_casualties)
        
        self.log(f"进攻方本阶段伤亡: {attacker_phase_casualties}")
        self.log(f"防守方本阶段伤亡: {defender_phase_casualties}")
        
        # 士气变化
        attacker_morale_change = (defender_phase_casualties / defender_total_size * 100 - 
                                attacker_phase_casualties / attacker_total_size * 100)
        defender_morale_change = -attacker_morale_change
        
        self.attacker_morale_loss -= attacker_morale_change
        self.defender_morale_loss -= defender_morale_change
        
        for army in self.attacker_armies:
            army.morale = max(10, min(100, army.morale + int(attacker_morale_change / 2)))
        for army in self.defender_armies:
            army.morale = max(10, min(100, army.morale + int(defender_morale_change / 2)))
        
        # 推进到下一阶段
        if self.current_phase == BattlePhase.DEPLOYMENT:
            self.current_phase = BattlePhase.RANGED
        elif self.current_phase == BattlePhase.RANGED:
            self.current_phase = BattlePhase.MELEE
        elif self.current_phase == BattlePhase.MELEE:
            self.current_phase = BattlePhase.PURSUIT
        elif self.current_phase == BattlePhase.PURSUIT:
            self.current_phase = BattlePhase.RETREAT
        
        # 经验获得
        for army in self.attacker_armies:
            army.experience += 1
        for army in self.defender_armies:
            army.experience += 1
        
        # 将领获得经验
        exp_gain = max(1, int((attacker_phase_casualties + defender_phase_casualties) / 200))
        for general in self.attacker_generals:
            general.gain_experience(exp_gain)
        for general in self.defender_generals:
            general.gain_experience(exp_gain)
        
        # 检查一方是否全军覆没
        attacker_remaining = sum(army.size for army in self.attacker_armies)
        defender_remaining = sum(army.size for army in self.defender_armies)
        
        if attacker_remaining == 0 or defender_remaining == 0:
            return True  # 战斗结束
            
        # 检查一方是否士气崩溃
        attacker_avg_morale = sum(army.morale for army in self.attacker_armies) / len(self.attacker_armies)
        defender_avg_morale = sum(army.morale for army in self.defender_armies) / len(self.defender_armies)
        
        if attacker_avg_morale < 20 or defender_avg_morale < 20:
            return True  # 战斗结束
            
        return False  # 战斗继续
        
    def distribute_casualties(self, armies, total_casualties):
        """将伤亡分配到各个军队"""
        if not armies or total_casualties <= 0:
            return
            
        # 按军队大小比例分配伤亡
        total_size = sum(army.size for army in armies)
        remaining_casualties = total_casualties
        
        for i, army in enumerate(armies):
            if i == len(armies) - 1:  # 最后一支军队
                army_casualties = remaining_casualties
            else:
                army_casualties = int(total_casualties * (army.size / total_size))
                remaining_casualties -= army_casualties
                
            army.take_casualties(army_casualties)
    
    def simulate_battle(self, max_rounds=5):
        """模拟整个战斗过程"""
        self.log("===== 战斗开始 =====")
        self.log(f"地形: {self.terrain.value}")
        
        attacker_size = sum(army.size for army in self.attacker_armies)
        defender_size = sum(army.size for army in self.defender_armies)
        
        self.log(f"进攻方兵力: {attacker_size}")
        attacker_composition = {}
        for army in self.attacker_armies:
            if army.primary_type.value in attacker_composition:
                attacker_composition[army.primary_type.value] += army.size
            else:
                attacker_composition[army.primary_type.value] = army.size
        
        self.log(f"进攻方兵种: {', '.join([f'{troop_type}({size})' for troop_type, size in attacker_composition.items()])}")
        self.log(f"进攻方将领: {', '.join([general.name for general in self.attacker_generals])}" if self.attacker_generals else "进攻方将领: 无")
        
        self.log(f"防守方兵力: {defender_size}")
        defender_composition = {}
        for army in self.defender_armies:
            if army.primary_type.value in defender_composition:
                defender_composition[army.primary_type.value] += army.size
            else:
                defender_composition[army.primary_type.value] = army.size
        
        self.log(f"防守方兵种: {', '.join([f'{troop_type}({size})' for troop_type, size in defender_composition.items()])}")
        self.log(f"防守方将领: {', '.join([general.name for general in self.defender_generals])}" if self.defender_generals else "防守方将领: 无")
        
        self.log("\n战斗开始...\n")
        time.sleep(1)  # 增加戏剧性
        
        # 战前准备：单挑
        if self.attacker_generals and self.defender_generals:
            if random.random() < 0.3:  # 30%几率发生单挑
                attacker_champion = max(self.attacker_generals, key=lambda g: g.strength)
                defender_champion = max(self.defender_generals, key=lambda g: g.strength)
                
                self.log(f"单挑开始！{attacker_champion.name} VS {defender_champion.name}")
                duel_result, advantage = attacker_champion.duel(defender_champion)
                
                if duel_result:
                    self.log(f"{attacker_champion.name}在单挑中战胜了{defender_champion.name}！")
                    # 进攻方士气提升，防守方士气降低
                    for army in self.attacker_armies:
                        army.morale = min(100, army.morale + 10)
                    for army in self.defender_armies:
                        army.morale = max(10, army.morale - 10)
                else:
                    self.log(f"{defender_champion.name}在单挑中战胜了{attacker_champion.name}！")
                    # 防守方士气提升，进攻方士气降低
                    for army in self.defender_armies:
                        army.morale = min(100, army.morale + 10)
                    for army in self.attacker_armies:
                        army.morale = max(10, army.morale - 10)
                
                time.sleep(1)
        
        # 模拟战斗阶段
        battle_ended = False
        rounds = 0
        
        while not battle_ended and rounds < max_rounds:
            battle_ended = self.conduct_battle_phase()
            rounds += 1
            time.sleep(0.5)  # 增加戏剧性
        
        # 判断胜负
        attacker_remaining = sum(army.size for army in self.attacker_armies)
        defender_remaining = sum(army.size for army in self.defender_armies)
        
        attacker_avg_morale = sum(army.morale for army in self.attacker_armies) / len(self.attacker_armies) if self.attacker_armies else 0
        defender_avg_morale = sum(army.morale for army in self.defender_armies) / len(self.defender_armies) if self.defender_armies else 0
        
        # 决定战斗结果
        if attacker_remaining == 0 or attacker_avg_morale < 20:
            # 进攻方战败
            is_decisive = defender_remaining >= defender_size * 0.6  # 如果防守方保存了60%以上的兵力，则为决定性胜利
            self.log("\n===== 战斗结束 =====")
            self.log("防守方获胜！")
            self.log(f"进攻方伤亡: {self.attacker_casualties}")
            self.log(f"防守方伤亡: {self.defender_casualties}")
            
            # 增加疲劳度
            for army in self.defender_armies:
                army.fatigue = min(100, army.fatigue + 30)
            
            return BattleResult(
                winner="defender",
                loser="attacker",
                is_decisive=is_decisive,
                attacker_casualties=self.attacker_casualties,
                defender_casualties=self.defender_casualties,
                battle_log=self.battle_log
            )
        elif defender_remaining == 0 or defender_avg_morale < 20:
            # 防守方战败
            is_decisive = attacker_remaining >= attacker_size * 0.6  # 如果进攻方保存了60%以上的兵力，则为决定性胜利
            self.log("\n===== 战斗结束 =====")
            self.log("进攻方获胜！")
            self.log(f"进攻方伤亡: {self.attacker_casualties}")
            self.log(f"防守方伤亡: {self.defender_casualties}")
            
            # 增加疲劳度
            for army in self.attacker_armies:
                army.fatigue = min(100, army.fatigue + 30)
            
            return BattleResult(
                winner="attacker",
                loser="defender",
                is_decisive=is_decisive,
                attacker_casualties=self.attacker_casualties,
                defender_casualties=self.defender_casualties,
                battle_log=self.battle_log
            )
        else:
            # 战斗不分胜负
            self.log("\n===== 战斗结束 =====")
            self.log("战斗以平局结束！")
            self.log(f"进攻方伤亡: {self.attacker_casualties}")
            self.log(f"防守方伤亡: {self.defender_casualties}")
            
            # 增加疲劳度
            for army in self.attacker_armies:
                army.fatigue = min(100, army.fatigue + 20)
            for army in self.defender_armies:
                army.fatigue = min(100, army.fatigue + 20)
            
            return BattleResult(
                winner=None,
                loser=None,
                is_decisive=False,
                attacker_casualties=self.attacker_casualties,
                defender_casualties=self.defender_casualties,
                battle_log=self.battle_log
            ) 
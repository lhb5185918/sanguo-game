#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models.general import General, Skill
from models.army import TroopType

def load_game_data():
    """加载游戏数据，包括将领、城市等"""
    data = {
        "generals": [],
        "cities": []
    }
    
    # 加载著名将领数据
    data["generals"] = create_famous_generals()
    
    return data

def create_famous_generals():
    """创建三国时期著名将领"""
    generals = []
    
    # 魏国将领
    cao_cao = General(
        name="曹操", 
        leadership=95, 
        strength=80, 
        intelligence=97, 
        politics=90, 
        charisma=85,
        kingdom_name="魏国"
    )
    cao_cao.add_skill(Skill.WISDOM)
    cao_cao.add_skill(Skill.INSPIRE)
    generals.append(cao_cao)
    
    xiahou_dun = General(
        name="夏侯惇", 
        leadership=90, 
        strength=92, 
        intelligence=75, 
        politics=70, 
        charisma=80,
        kingdom_name="魏国"
    )
    xiahou_dun.add_skill(Skill.IRON_DEFENSE)
    xiahou_dun.add_skill(Skill.DUEL)
    generals.append(xiahou_dun)
    
    dian_wei = General(
        name="典韦", 
        leadership=85, 
        strength=97, 
        intelligence=65, 
        politics=60, 
        charisma=75,
        kingdom_name="魏国"
    )
    dian_wei.add_skill(Skill.DUEL)
    generals.append(dian_wei)
    
    xu_chu = General(
        name="许褚", 
        leadership=82, 
        strength=95, 
        intelligence=60, 
        politics=55, 
        charisma=70,
        kingdom_name="魏国"
    )
    xu_chu.add_skill(Skill.DUEL)
    xu_chu.add_skill(Skill.CHARGE)
    generals.append(xu_chu)
    
    zhang_liao = General(
        name="张辽", 
        leadership=92, 
        strength=90, 
        intelligence=80, 
        politics=70, 
        charisma=85,
        kingdom_name="魏国"
    )
    zhang_liao.add_skill(Skill.CHARGE)
    zhang_liao.add_skill(Skill.FORMATION_BREAK)
    generals.append(zhang_liao)
    
    sima_yi = General(
        name="司马懿", 
        leadership=93, 
        strength=65, 
        intelligence=97, 
        politics=90, 
        charisma=80,
        kingdom_name="魏国"
    )
    sima_yi.add_skill(Skill.WISDOM)
    sima_yi.add_skill(Skill.AMBUSH)
    generals.append(sima_yi)
    
    # 蜀国将领
    liu_bei = General(
        name="刘备", 
        leadership=88, 
        strength=75, 
        intelligence=80, 
        politics=95, 
        charisma=98,
        kingdom_name="蜀国"
    )
    liu_bei.add_skill(Skill.INSPIRE)
    generals.append(liu_bei)
    
    guan_yu = General(
        name="关羽", 
        leadership=90, 
        strength=97, 
        intelligence=80, 
        politics=75, 
        charisma=90,
        kingdom_name="蜀国"
    )
    guan_yu.add_skill(Skill.DUEL)
    guan_yu.add_skill(Skill.CHARGE)
    generals.append(guan_yu)
    
    zhang_fei = General(
        name="张飞", 
        leadership=87, 
        strength=96, 
        intelligence=70, 
        politics=65, 
        charisma=85,
        kingdom_name="蜀国"
    )
    zhang_fei.add_skill(Skill.DUEL)
    zhang_fei.add_skill(Skill.INSPIRE)
    generals.append(zhang_fei)
    
    zhao_yun = General(
        name="赵云", 
        leadership=89, 
        strength=95, 
        intelligence=82, 
        politics=75, 
        charisma=85,
        kingdom_name="蜀国"
    )
    zhao_yun.add_skill(Skill.DUEL)
    zhao_yun.add_skill(Skill.CHARGE)
    generals.append(zhao_yun)
    
    ma_chao = General(
        name="马超", 
        leadership=88, 
        strength=94, 
        intelligence=75, 
        politics=70, 
        charisma=82,
        kingdom_name="蜀国"
    )
    ma_chao.add_skill(Skill.CHARGE)
    ma_chao.troops_bonus = {TroopType.CAVALRY: 0.2}
    generals.append(ma_chao)
    
    huang_zhong = General(
        name="黄忠", 
        leadership=85, 
        strength=90, 
        intelligence=72, 
        politics=65, 
        charisma=75,
        kingdom_name="蜀国"
    )
    huang_zhong.add_skill(Skill.DUEL)
    huang_zhong.troops_bonus = {TroopType.ARCHER: 0.2}
    generals.append(huang_zhong)
    
    zhuge_liang = General(
        name="诸葛亮", 
        leadership=95, 
        strength=60, 
        intelligence=100, 
        politics=95, 
        charisma=92,
        kingdom_name="蜀国"
    )
    zhuge_liang.add_skill(Skill.WISDOM)
    zhuge_liang.add_skill(Skill.FIRE_ATTACK)
    zhuge_liang.add_skill(Skill.AMBUSH)
    generals.append(zhuge_liang)
    
    # 吴国将领
    sun_quan = General(
        name="孙权", 
        leadership=90, 
        strength=78, 
        intelligence=88, 
        politics=93, 
        charisma=85,
        kingdom_name="吴国"
    )
    sun_quan.add_skill(Skill.INSPIRE)
    sun_quan.add_skill(Skill.WISDOM)
    generals.append(sun_quan)
    
    zhou_yu = General(
        name="周瑜", 
        leadership=93, 
        strength=80, 
        intelligence=96, 
        politics=85, 
        charisma=89,
        kingdom_name="吴国"
    )
    zhou_yu.add_skill(Skill.WISDOM)
    zhou_yu.add_skill(Skill.FIRE_ATTACK)
    zhou_yu.troops_bonus = {TroopType.NAVY: 0.2}
    generals.append(zhou_yu)
    
    lu_xun = General(
        name="陆逊", 
        leadership=92, 
        strength=75, 
        intelligence=94, 
        politics=88, 
        charisma=85,
        kingdom_name="吴国"
    )
    lu_xun.add_skill(Skill.WISDOM)
    lu_xun.add_skill(Skill.FIRE_ATTACK)
    generals.append(lu_xun)
    
    gan_ning = General(
        name="甘宁", 
        leadership=86, 
        strength=90, 
        intelligence=75, 
        politics=65, 
        charisma=80,
        kingdom_name="吴国"
    )
    gan_ning.add_skill(Skill.AMBUSH)
    gan_ning.troops_bonus = {TroopType.NAVY: 0.15}
    generals.append(gan_ning)
    
    taishi_ci = General(
        name="太史慈", 
        leadership=85, 
        strength=92, 
        intelligence=78, 
        politics=68, 
        charisma=78,
        kingdom_name="吴国"
    )
    taishi_ci.add_skill(Skill.DUEL)
    taishi_ci.troops_bonus = {TroopType.ARCHER: 0.15}
    generals.append(taishi_ci)
    
    huang_gai = General(
        name="黄盖", 
        leadership=87, 
        strength=85, 
        intelligence=82, 
        politics=70, 
        charisma=75,
        kingdom_name="吴国"
    )
    huang_gai.add_skill(Skill.FIRE_ATTACK)
    huang_gai.troops_bonus = {TroopType.NAVY: 0.2}
    generals.append(huang_gai)
    
    # 其他著名将领
    lu_bu = General(
        name="吕布", 
        leadership=93, 
        strength=100, 
        intelligence=70, 
        politics=60, 
        charisma=80,
        kingdom_name="独立"
    )
    lu_bu.add_skill(Skill.DUEL)
    lu_bu.add_skill(Skill.CHARGE)
    lu_bu.troops_bonus = {TroopType.CAVALRY: 0.25}
    generals.append(lu_bu)
    
    diao_chan = General(
        name="貂蝉", 
        leadership=50, 
        strength=40, 
        intelligence=85, 
        politics=92, 
        charisma=100,
        kingdom_name="独立"
    )
    generals.append(diao_chan)
    
    yuan_shao = General(
        name="袁绍", 
        leadership=85, 
        strength=70, 
        intelligence=75, 
        politics=85, 
        charisma=82,
        kingdom_name="河北"
    )
    yuan_shao.add_skill(Skill.INSPIRE)
    generals.append(yuan_shao)
    
    dong_zhuo = General(
        name="董卓", 
        leadership=83, 
        strength=85, 
        intelligence=70, 
        politics=35, 
        charisma=40,
        kingdom_name="凉州"
    )
    dong_zhuo.add_skill(Skill.SIEGE)
    generals.append(dong_zhuo)
    
    return generals

def create_city_data():
    """创建城市数据"""
    cities = [
        {
            "name": "洛阳",
            "population": 80000,
            "prosperity": 80,
            "farms": 50,
            "mines": 20,
            "forts": 2,
            "region": "中原"
        },
        {
            "name": "长安",
            "population": 75000,
            "prosperity": 75,
            "farms": 45,
            "mines": 15,
            "forts": 2,
            "region": "关中"
        },
        {
            "name": "许昌",
            "population": 60000,
            "prosperity": 70,
            "farms": 55,
            "mines": 10,
            "forts": 1,
            "region": "中原"
        },
        {
            "name": "邺城",
            "population": 65000,
            "prosperity": 65,
            "farms": 40,
            "mines": 25,
            "forts": 1,
            "region": "河北"
        },
        {
            "name": "建业",
            "population": 70000,
            "prosperity": 80,
            "farms": 30,
            "mines": 10,
            "forts": 1,
            "region": "江东"
        },
        {
            "name": "成都",
            "population": 68000,
            "prosperity": 75,
            "farms": 60,
            "mines": 15,
            "forts": 1,
            "region": "益州"
        },
        {
            "name": "江陵",
            "population": 55000,
            "prosperity": 70,
            "farms": 50,
            "mines": 5,
            "forts": 1,
            "region": "荆州"
        },
        {
            "name": "下邳",
            "population": 50000,
            "prosperity": 65,
            "farms": 45,
            "mines": 10,
            "forts": 1,
            "region": "徐州"
        }
    ]
    
    return cities 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time

class Chapter:
    """故事章节类"""
    
    def __init__(self, title, intro, events, choices=None, required_level=1):
        self.title = title  # 章节标题
        self.intro = intro  # 章节介绍
        self.events = events  # 章节事件列表
        self.choices = choices or []  # 玩家可选择的选项
        self.required_level = required_level  # 解锁所需等级
        
    def play(self, player):
        """播放章节内容"""
        print(f"\n==== {self.title} ====")
        print(self.intro)
        
        for event in self.events:
            time.sleep(1)
            print(f"\n{event}")
            time.sleep(1.5)
        
        if self.choices:
            print("\n做出你的选择:")
            for i, choice in enumerate(self.choices, 1):
                print(f"{i}. {choice['text']}")
            
            choice_num = int(input("你的选择 (1-{len(self.choices)}): "))
            if 1 <= choice_num <= len(self.choices):
                chosen = self.choices[choice_num - 1]
                print(f"\n{chosen['result']}")
                
                # 执行选择的效果
                if 'effect' in chosen and callable(chosen['effect']):
                    chosen['effect'](player)
                    
                return choice_num
        
        return 0

class Quest:
    """任务类"""
    
    def __init__(self, name, description, objectives, exp_reward, fame_reward, achievement_points=0, item_reward=None):
        self.name = name  # 任务名称
        self.description = description  # 任务描述
        self.objectives = objectives  # 任务目标
        self.exp_reward = exp_reward  # 经验奖励
        self.fame_reward = fame_reward  # 声望奖励
        self.achievement_points = achievement_points  # 成就点数
        self.item_reward = item_reward  # 物品奖励
        self.completed = False  # 是否完成
        
    def __str__(self):
        return f"{self.name}: {self.description}"
    
    def check_completion(self, condition):
        """检查任务是否完成"""
        if condition:
            self.completed = True
            return True
        return False

class Story:
    """游戏剧情类"""
    
    def __init__(self):
        self.chapters = self._init_chapters()
        self.current_chapter = 0
        self.chapter_outcomes = {}  # 记录玩家在各章节的选择
        self.completed_chapters = []
        self.quests = self._init_quests()  # 初始化任务
        
    def _init_chapters(self):
        """初始化游戏章节"""
        chapters = []
        
        # 第一章：黄巾起义
        yellow_turban_chapter = Chapter(
            title="黄巾起义",
            intro="建宁元年(公元168年)，黄巾军揭竿而起，以'苍天已死，黄天当立'为口号，席卷天下。朝廷命各地州郡镇压叛乱...",
            events=[
                "你是一名地方上的小官吏，正值壮年，目睹黄巾军的暴行，决定挺身而出。",
                "当地太守征召勇士组建义军，你毫不犹豫地报名参加。",
                "在一场战斗中，你表现出色，成功击退了一支黄巾军，救下了一个村庄。",
                "你的名声开始在当地传开..."
            ],
            choices=[
                {
                    "text": "加入官军，为朝廷效力",
                    "result": "你加入了官军，在太守麾下效力。太守对你委以重任，给予你一支小队的指挥权。",
                    "effect": lambda player: player.gain_fame(20)
                },
                {
                    "text": "自立队伍，招募乡勇",
                    "result": "你决定自立队伍，招募乡勇保卫家乡。不少当地青壮年响应你的号召，你很快组建了一支小型部队。",
                    "effect": lambda player: (player.gain_fame(15), setattr(player.armies[0], 'size', player.armies[0].size + 500))
                },
                {
                    "text": "投奔一方诸侯",
                    "result": "你听闻刘备、曹操、孙坚等人都在各地起兵抗击黄巾，决定前去投奔一方诸侯。",
                    "effect": lambda player: player.gain_fame(10)
                }
            ],
            required_level=1
        )
        chapters.append(yellow_turban_chapter)
        
        # 第二章：群雄割据
        warlords_chapter = Chapter(
            title="群雄割据",
            intro="黄巾之乱平定后，各地州牧、刺史拥兵自重，不听朝廷调遣。董卓挟持献帝，专权朝政，天下震动...",
            events=[
                "董卓迁都长安，焚烧洛阳，无数百姓流离失所。",
                "各地诸侯纷纷起兵讨伐董卓，关东联军初具规模。",
                "你已经拥有了一定声望，开始考虑自己的未来道路。"
            ],
            choices=[
                {
                    "text": "加入讨董联军",
                    "result": "你决定加入讨董联军，与各路诸侯共同讨伐董卓。联军盟主袁绍对你的加入表示欢迎。",
                    "effect": lambda player: player.gain_fame(25)
                },
                {
                    "text": "独自发展实力",
                    "result": "你认为当前局势混乱，选择暂时独自发展实力，静观其变。你在家乡招募更多兵丁，扩充军备。",
                    "effect": lambda player: (player.gain_fame(15), setattr(player.armies[0], 'size', player.armies[0].size + 1000))
                },
                {
                    "text": "投靠强大势力",
                    "result": "你决定投靠一方强大势力，以求自保和发展。经过考虑，你最终选择了前去投奔。",
                    "effect": lambda player: player.gain_fame(20)
                }
            ],
            required_level=3
        )
        chapters.append(warlords_chapter)
        
        # 第三章：官渡之战
        guandu_chapter = Chapter(
            title="官渡之战",
            intro="建安五年(公元200年)，曹操与袁绍在官渡展开决战。这场战役将决定中国北方的命运...",
            events=[
                "曹操与袁绍两支大军在官渡隔河相望，形势紧张。",
                "曹军虽然兵力不及袁军，但士气高昂，谋士众多。",
                "袁军虽然人多势众，但内部不和，军令不一。",
                "两军相持不下，都在等待战机。"
            ],
            choices=[
                {
                    "text": "支持曹操",
                    "result": "你率军支持曹操。曹操亲自接见了你，对你的到来表示感谢。你被安排在右翼军中，准备接下来的大战。",
                    "effect": lambda player: player.gain_fame(30)
                },
                {
                    "text": "支持袁绍",
                    "result": "你率军支持袁绍。袁绍对你的加入极为重视，将你安排在前锋部队，准备对曹军发起猛攻。",
                    "effect": lambda player: player.gain_fame(30)
                },
                {
                    "text": "保持中立，坐观成败",
                    "result": "你决定保持中立，静观其变。你率军驻扎在官渡周边，随时准备应对局势变化。",
                    "effect": lambda player: (player.gain_fame(15), setattr(player, 'leadership', player.leadership + 5))
                }
            ],
            required_level=5
        )
        chapters.append(guandu_chapter)
        
        # 第四章：三国鼎立
        three_kingdoms_chapter = Chapter(
            title="三国鼎立",
            intro="赤壁之战后，曹操据有北方，孙权盘踞江东，刘备占据荆州，三国鼎立的局面初步形成...",
            events=[
                "曹操统一北方，自封魏王，实力强盛。",
                "孙权继承江东基业，与周瑜等名将共同守卫东吴。",
                "刘备在诸葛亮的辅佐下，开始谋划西蜀之地。",
                "天下初步呈现三足鼎立之势，战火不断。"
            ],
            choices=[
                {
                    "text": "效忠魏国",
                    "result": "你决定效忠曹操建立的魏国。曹操任命你为一方将领，赐予你封地和兵权。",
                    "effect": lambda player: (player.gain_fame(40), setattr(player, 'leadership', player.leadership + 5), setattr(player.armies[0], 'size', player.armies[0].size + 2000))
                },
                {
                    "text": "归顺蜀汉",
                    "result": "你选择归顺刘备建立的蜀汉政权。刘备以礼相待，诸葛亮也对你很是欣赏。",
                    "effect": lambda player: (player.gain_fame(40), setattr(player, 'intelligence', player.intelligence + 5), setattr(player.armies[0], 'size', player.armies[0].size + 1500))
                },
                {
                    "text": "加入东吴",
                    "result": "你投奔孙权的东吴。孙权对你非常器重，授予你要职，委以重任。",
                    "effect": lambda player: (player.gain_fame(40), setattr(player, 'politics', player.politics + 5), setattr(player.armies[0], 'size', player.armies[0].size + 1500))
                },
                {
                    "text": "自立为王",
                    "result": "你决定不臣服于任何一方，而是自立为王，在三国之间开辟属于自己的势力。",
                    "effect": lambda player: (player.gain_fame(50), setattr(player, 'charisma', player.charisma + 10), setattr(player, 'title', "一方诸侯"))
                }
            ],
            required_level=8
        )
        chapters.append(three_kingdoms_chapter)
        
        # 第五章：赤壁之战
        chibi_chapter = Chapter(
            title="赤壁之战",
            intro="建安十三年(公元208年)，曹操南下荆州，率水军八十万直指江东，欲一举吞并江南。孙权与刘备结盟，共同抵抗曹操...",
            events=[
                "曹操大军南下，连破荆州数城，刘表病逝，其子刘琮投降。",
                "刘备携民渡江，与孙权结盟。周瑜、诸葛亮等谋士共同商议迎战之策。",
                "曹军初到江南，水土不服，再加上军中疾病流行，战力有所削弱。",
                "风向对曹军不利，江东联军决定以火攻破敌..."
            ],
            choices=[
                {
                    "text": "参与火攻计划",
                    "result": "你主动请缨，参与周瑜和诸葛亮策划的火攻。在关键时刻，你成功率队引燃曹军战船，为联军立下大功。",
                    "effect": lambda player: (player.gain_fame(45), setattr(player, 'intelligence', player.intelligence + 5))
                },
                {
                    "text": "负责阻截曹军溃兵",
                    "result": "你率军在曹军溃败的必经之路上设伏，成功俘虏了大批曹军士兵，斩杀敌将数名。",
                    "effect": lambda player: (player.gain_fame(40), setattr(player, 'strength', player.strength + 5))
                },
                {
                    "text": "保护后方补给",
                    "result": "你负责守卫联军后方补给线，击退了曹军的多次偷袭，确保了前线的稳定供应。",
                    "effect": lambda player: (player.gain_fame(35), setattr(player, 'leadership', player.leadership + 5))
                }
            ],
            required_level=10
        )
        chapters.append(chibi_chapter)
        
        # 第六章：征讨益州
        yizhou_chapter = Chapter(
            title="征讨益州",
            intro="刘备在诸葛亮的建议下，决定进取益州。刘璋性格懦弱，益州虽大却未善加经营，正是良机...",
            events=[
                "刘备借口援助刘璋抵抗张鲁，率军入蜀。",
                "庞统献计，建议刘备以迅雷不及掩耳之势夺取成都。",
                "刘璋派遣杨怀、高沛率军阻击，被刘备军击败。",
                "刘备军队围攻成都，刘璋最终投降，蜀地落入刘备之手。"
            ],
            choices=[
                {
                    "text": "跟随刘备入蜀",
                    "result": "你追随刘备入蜀，参与了定军山之战，协助黄忠斩杀夏侯渊，为取蜀立下大功。",
                    "effect": lambda player: (player.gain_fame(45), setattr(player, 'strength', player.strength + 5), setattr(player.armies[0], 'size', player.armies[0].size + 2000))
                },
                {
                    "text": "留守荆州",
                    "result": "你被委以重任，留守荆州，抵挡东吴和曹魏的压力，保证刘备后方安全。",
                    "effect": lambda player: (player.gain_fame(40), setattr(player, 'leadership', player.leadership + 5), setattr(player, 'politics', player.politics + 5))
                },
                {
                    "text": "劝说刘璋投降",
                    "result": "你深入成都，向刘璋分析利弊，成功说服他投降，避免了一场血战，刘备非常欣赏你的外交才能。",
                    "effect": lambda player: (player.gain_fame(50), setattr(player, 'intelligence', player.intelligence + 5), setattr(player, 'charisma', player.charisma + 5))
                }
            ],
            required_level=12
        )
        chapters.append(yizhou_chapter)
        
        # 第七章：汉中之战
        hanzhong_chapter = Chapter(
            title="汉中之战",
            intro="汉中位于蜀中咽喉，是进攻中原的门户，也是曹魏进攻蜀汉的必经之地。刘备决定夺取汉中，为北伐中原做准备...",
            events=[
                "刘备命令黄忠、赵云等将领进攻汉中，曹操亲自领兵前来抵抗。",
                "双方在定军山等地多次交战，战况胶着。",
                "法正建议断敌粮道，迫使曹军撤退。",
                "黄忠在定军山一战中斩杀夏侯渊，曹军士气大挫。"
            ],
            choices=[
                {
                    "text": "参与正面战场",
                    "result": "你在定军山之战中表现出色，协助击败曹军主力，立下赫赫战功。",
                    "effect": lambda player: (player.gain_fame(50), setattr(player, 'strength', player.strength + 8), setattr(player, 'leadership', player.leadership + 5))
                },
                {
                    "text": "断敌粮道",
                    "result": "你率轻骑突袭曹军后方，成功切断了曹军的补给线，迫使曹操无奈撤军。",
                    "effect": lambda player: (player.gain_fame(55), setattr(player, 'intelligence', player.intelligence + 5), setattr(player.armies[0], 'training', player.armies[0].training + 10))
                },
                {
                    "text": "设伏击杀敌将",
                    "result": "你在曹军撤退路线上设下埋伏，成功伏击了曹军一支部队，击杀多名敌将。",
                    "effect": lambda player: (player.gain_fame(45), setattr(player.armies[0], 'experience', player.armies[0].experience + 100), setattr(player, 'strength', player.strength + 5))
                }
            ],
            required_level=15
        )
        chapters.append(hanzhong_chapter)
        
        # 第八章：夷陵之战
        yiling_chapter = Chapter(
            title="夷陵之战",
            intro="刘备为报关羽之仇，不顾诸葛亮劝阻，执意东征孙权。吴蜀两国由盟友变成了敌人...",
            events=[
                "关羽北上攻打曹魏，被东吴吕蒙偷袭荆州，最终战死。",
                "刘备悲愤交加，决定东征讨伐孙权，为关羽报仇。",
                "诸葛亮等人多次劝阻，但刘备意已决，率大军出发。",
                "陆逊使用火攻，大败蜀军，刘备被迫撤退，不久病逝于白帝城。"
            ],
            choices=[
                {
                    "text": "追随刘备东征",
                    "result": "你跟随刘备东征，在大军溃败时奋勇掩护，使刘备得以安全撤退。虽然战败，但你的忠诚和勇气获得了刘备的赞赏。",
                    "effect": lambda player: (player.gain_fame(40), setattr(player, 'loyalty', 100), setattr(player, 'strength', player.strength + 5))
                },
                {
                    "text": "支持诸葛亮留守",
                    "result": "你支持诸葛亮的观点，留守成都，保障后方安全。东征失败后，你协助诸葛亮安定朝局，稳定军心。",
                    "effect": lambda player: (player.gain_fame(35), setattr(player, 'intelligence', player.intelligence + 5), setattr(player, 'politics', player.politics + 8))
                },
                {
                    "text": "尝试调解吴蜀关系",
                    "result": "你冒险前往东吴，尝试调解两国关系，虽未能阻止战争，但为日后两国重修于好埋下了伏笔。",
                    "effect": lambda player: (player.gain_fame(50), setattr(player, 'charisma', player.charisma + 10), setattr(player, 'politics', player.politics + 5))
                }
            ],
            required_level=18
        )
        chapters.append(yiling_chapter)
        
        # 第九章：北伐中原
        northern_expedition_chapter = Chapter(
            title="北伐中原",
            intro="刘备病逝，托孤于诸葛亮。诸葛亮为实现先主遗愿，恢复汉室，开始了一系列北伐曹魏的战争...",
            events=[
                "诸葛亮励精图治，政通人和，蜀国国力逐渐恢复。",
                "为联合东吴抗魏，诸葛亮亲自前往东吴，与陆逊达成同盟。",
                "诸葛亮率军出祁山，与魏军大将军司马懿对峙。",
                "双方多次交战，但因粮尽，诸葛亮被迫撤军。"
            ],
            choices=[
                {
                    "text": "随诸葛亮北伐",
                    "result": "你随诸葛亮北伐，在多次战役中表现出色。虽然最终撤军，但你的军事才能得到了诸葛亮的高度认可。",
                    "effect": lambda player: (player.gain_fame(60), setattr(player, 'leadership', player.leadership + 10), setattr(player.armies[0], 'training', player.armies[0].training + 15))
                },
                {
                    "text": "负责军需后勤",
                    "result": "你负责北伐军队的后勤补给，多次组织大规模运粮，确保前线军需充足，为军队作战提供了坚实保障。",
                    "effect": lambda player: (player.gain_fame(55), setattr(player, 'intelligence', player.intelligence + 5), setattr(player, 'politics', player.politics + 5))
                },
                {
                    "text": "镇守边境重地",
                    "result": "你被委派镇守蜀国边境重地，抵挡魏军的多次进攻，保证了北伐军队的侧翼安全。",
                    "effect": lambda player: (player.gain_fame(50), setattr(player, 'strength', player.strength + 5), setattr(player.armies[0], 'morale', player.armies[0].morale + 20))
                }
            ],
            required_level=20
        )
        chapters.append(northern_expedition_chapter)
        
        # 第十章：三分归一
        unification_chapter = Chapter(
            title="三分归一",
            intro="诸葛亮五次北伐，最终因积劳成疾，病逝于五丈原。司马氏篡魏，司马炎废魏帝曹奂，建立晋朝，随后灭吴，三国归于一统...",
            events=[
                "诸葛亮病逝，蜀汉朝政逐渐衰败，最终被魏国司马氏所灭。",
                "魏国司马氏逐渐掌权，司马懿之孙司马炎废黜魏帝，建立晋朝。",
                "晋朝大军压境，东吴独木难支，最终灭亡。",
                "天下重归一统，但战乱的创伤需要时间愈合..."
            ],
            choices=[
                {
                    "text": "归顺晋朝",
                    "result": "你看清大势，主动归顺晋朝。司马炎赏识你的才能，委以重任，你在新的朝代继续发挥自己的才能。",
                    "effect": lambda player: (player.gain_fame(70), setattr(player, 'politics', player.politics + 10), setattr(player, 'title', "晋朝重臣"))
                },
                {
                    "text": "退隐江湖",
                    "result": "你选择功成身退，辞官归隐，在山水之间寄情山水，著书立说，传播三国故事。",
                    "effect": lambda player: (player.gain_fame(60), setattr(player, 'intelligence', player.intelligence + 10), setattr(player, 'title', "隐世名士"))
                },
                {
                    "text": "组织残部抵抗",
                    "result": "你率领残余忠义之士，在偏远地区建立根据地，虽然知道大势已去，但仍然坚持抵抗，成为一段佳话。",
                    "effect": lambda player: (player.gain_fame(80), setattr(player, 'strength', player.strength + 5), setattr(player, 'charisma', player.charisma + 5), setattr(player, 'title', "乱世英雄"))
                },
                {
                    "text": "重建新政权",
                    "result": "你不甘心就此屈服，在混乱中趁机建立自己的势力，虽然规模不大，但在一方土地上成为了实际统治者。",
                    "effect": lambda player: (player.gain_fame(90), setattr(player, 'leadership', player.leadership + 10), setattr(player, 'title', "一方霸主"))
                }
            ],
            required_level=25
        )
        chapters.append(unification_chapter)
        
        return chapters
    
    def _init_quests(self):
        """初始化任务列表"""
        quests = []
        
        # 基础任务
        recruit_quest = Quest(
            name="招兵买马",
            description="招募1000名士兵，组建自己的军队",
            objectives=["招募1000名士兵"],
            exp_reward=100,
            fame_reward=10
        )
        quests.append(recruit_quest)
        
        training_quest = Quest(
            name="训练精兵",
            description="将军队训练度提升到80以上",
            objectives=["提升军队训练度到80"],
            exp_reward=150,
            fame_reward=15
        )
        quests.append(training_quest)
        
        duel_quest = Quest(
            name="武艺切磋",
            description="在单挑中击败一名敌将",
            objectives=["单挑胜利1次"],
            exp_reward=200,
            fame_reward=20,
            achievement_points=1
        )
        quests.append(duel_quest)
        
        battle_quest = Quest(
            name="初试锋芒",
            description="指挥军队取得一场战斗的胜利",
            objectives=["获得战斗胜利1次"],
            exp_reward=250,
            fame_reward=25,
            achievement_points=2
        )
        quests.append(battle_quest)
        
        # 进阶任务
        city_quest = Quest(
            name="据城称雄",
            description="攻占一座城池",
            objectives=["攻占1座城池"],
            exp_reward=500,
            fame_reward=50,
            achievement_points=5
        )
        quests.append(city_quest)
        
        general_quest = Quest(
            name="招贤纳士",
            description="招募3名将领加入你的阵营",
            objectives=["招募3名将领"],
            exp_reward=400,
            fame_reward=40,
            achievement_points=3
        )
        quests.append(general_quest)
        
        alliance_quest = Quest(
            name="结盟强敌",
            description="与一个强大的势力结成同盟",
            objectives=["与1个势力结盟"],
            exp_reward=350,
            fame_reward=35,
            achievement_points=3
        )
        quests.append(alliance_quest)
        
        army_quest = Quest(
            name="千军万马",
            description="扩充军队规模至10000人",
            objectives=["扩充军队至10000人"],
            exp_reward=600,
            fame_reward=60,
            achievement_points=6
        )
        quests.append(army_quest)
        
        # 高级任务
        conquer_quest = Quest(
            name="横扫六合",
            description="攻占10座城池，建立强大势力",
            objectives=["攻占10座城池"],
            exp_reward=1000,
            fame_reward=100,
            achievement_points=10
        )
        quests.append(conquer_quest)
        
        legendary_quest = Quest(
            name="威震华夏",
            description="成为声望达到1000的传奇人物",
            objectives=["声望达到1000"],
            exp_reward=1500,
            fame_reward=150,
            achievement_points=15
        )
        quests.append(legendary_quest)
        
        return quests
    
    def play_chapter(self, chapter_index, player):
        """播放特定章节"""
        if chapter_index < 0 or chapter_index >= len(self.chapters):
            print("无效的章节索引")
            return
            
        if player.level < self.chapters[chapter_index].required_level:
            print(f"需要达到{self.chapters[chapter_index].required_level}级才能进行此章节")
            return
            
        outcome = self.chapters[chapter_index].play(player)
        self.chapter_outcomes[chapter_index] = outcome
        
        if chapter_index not in self.completed_chapters:
            self.completed_chapters.append(chapter_index)
            player.gain_experience(chapter_index * 50 + 100)  # 章节经验奖励
            
        self.current_chapter = chapter_index + 1
        
        return outcome
    
    def get_available_chapters(self, player):
        """获取玩家当前可用的章节"""
        available = []
        for i, chapter in enumerate(self.chapters):
            if player.level >= chapter.required_level:
                available.append((i, chapter.title))
        return available
    
    def get_next_chapter(self, player):
        """获取下一个可用章节"""
        if self.current_chapter < len(self.chapters):
            chapter = self.chapters[self.current_chapter]
            if player.level >= chapter.required_level:
                return self.current_chapter
        
        # 寻找其他未完成的章节
        for i, chapter in enumerate(self.chapters):
            if i not in self.completed_chapters and player.level >= chapter.required_level:
                return i
                
        return None
    
    def get_available_quests(self, player):
        """获取玩家可接的任务"""
        available = []
        for quest in self.quests:
            if quest not in player.quests and quest not in player.completed_quests:
                if quest.name == "横扫六合" and len(player.kingdom.cities) < 3:
                    continue  # 需要至少有3座城市才能接"横扫六合"任务
                elif quest.name == "威震华夏" and player.fame < 500:
                    continue  # 需要至少500声望才能接"威震华夏"任务
                
                available.append(quest)
        return available
    
    def assign_quest(self, player, quest_index):
        """分配任务给玩家"""
        available_quests = self.get_available_quests(player)
        if 0 <= quest_index < len(available_quests):
            quest = available_quests[quest_index]
            player.add_quest(quest)
            return quest
        return None
    
    def check_quest_completion(self, player):
        """检查玩家任务完成情况"""
        completed = []
        
        for quest in player.quests:
            completed_flag = False
            
            # 根据任务类型检查完成条件
            if quest.name == "招兵买马":
                if player.total_army_size() >= 1000:
                    completed_flag = True
            
            elif quest.name == "训练精兵":
                if any(army.training >= 80 for army in player.armies):
                    completed_flag = True
            
            elif quest.name == "初试锋芒":
                # 假设战斗胜利已在别处记录
                if hasattr(player, 'battle_victories') and player.battle_victories > 0:
                    completed_flag = True
            
            elif quest.name == "据城称雄":
                if player.kingdom and len(player.kingdom.cities) > 0:
                    completed_flag = True
            
            elif quest.name == "招贤纳士":
                if len(player.kingdom.generals) >= 3:
                    completed_flag = True
            
            elif quest.name == "千军万马":
                if player.total_army_size() >= 10000:
                    completed_flag = True
            
            elif quest.name == "横扫六合":
                if player.kingdom and len(player.kingdom.cities) >= 10:
                    completed_flag = True
            
            elif quest.name == "威震华夏":
                if player.fame >= 1000:
                    completed_flag = True
            
            # 处理完成的任务
            if completed_flag:
                player.complete_quest(quest)
                completed.append(quest)
        
        return completed 
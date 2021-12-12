#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :menu.py
# @Time      :2021/12/9 13:05
# @Author    :russionbear

import pickle
import os, json, re, colorama, keyboard, random, time
from queue import Queue


MAP_FILEPATH = r'./suitang_map'
SAVE_FILEPATH = r'./suitang_save'

MapMode = {
  "__tip for map": "sea = 1   river = 2   plain = 3   mountain = 4   beach = 5  tree = 6",
  "__tip for person1": "none = 0  sword = 1 arrow = 2 catapult = 3 mount = 4",
  "__tip for person2": "!!!warn:weapons <= troop <= 30000",
  "__tip for person3": {
    "__tip": "",
    "name" : "key",
    "loyal" : "",
    "wise" : "",
    "force" : "",
    "troop" : "",
    "weapons" : "",
    "weaponType" : "",
    "dsc" : ""
  },
  "__tip for persons": "",
  "__tip for city1": "max: Population = 200000  Money = 300000  Treasure = 100",
  "__tip for city2": {
    "__tip": "",
    "loc": "key",
    "header": "",
    "name": "",
    "population": "",
    "perTreasure": "",
    "tax": "",
    "growth": "",
    "natality": "",
    "officer": "",
    "prisoner": "",
    "restTroop": "",
    "weapons": "",
    "money":""
  },
  "__tip for force": {
    "__tip": "",
    "name":  "key",
    "header": "",
    "cities": "type:list"
  },
  "map": [
    [4,3,1,2,5,5,3],
    [3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3]
  ],
  "__run test": "load json",
  "personName": [
    "叶俊友",
    "方经国",
    "宋正真",
    "易志明",
    "廖阳辉",
    "石安澜",
    "熊宏阔",
    "郝子瑜",
    "万修文",
    "刘彭湃",
    "史雨石",
    "杨敏智",
    "丁志业",
    "钱修诚",
    "孟乐安",
    "谢子轩",
    "杨英勋",
    "汤正信",
    "顾俊智",
    "胡华荣",
    "高俊迈",
    "罗高阳",
    "赵敏智",
    "黄浩博",
    "段勇捷",
    "蔡伟志",
    "李俊楚",
    "苏雅懿",
    "卢乐天",
    "贾鹏涛",
    "姚嘉实",
    "萧博文",
    "潘才英",
    "贺阳德",
    "梁雅惠",
    "李泽语",
    "卢永思",
    "杨欣悦",
    "卢飞驰",
    "郝英光",
    "赖乐悦",
    "康博简",
    "邓明辉",
    "苏宏峻",
    "廖良翰",
    "马文乐",
    "郭学林",
    "夏意智",
    "夏咏思",
    "阎文成",
    "侯国兴",
    "朱文宣",
    "戴睿聪",
    "萧玉轩",
    "马绍元",
    "白自强",
    "郝涵衍",
    "杜峻熙",
    "周奇致",
    "白鹏鲸",
    "于雅逸",
    "韩安澜",
    "邱高阳",
    "李才艺",
    "余华晖",
    "马嘉祥",
    "江志行",
    "顾华晖",
    "王和裕",
    "武乐欣",
    "胡高旻",
    "石才良",
    "薛坚成",
    "周祺祥",
    "林景澄",
    "冯阳夏",
    "段志学",
    "潘天路",
    "乔弘方",
    "漕星辰",
    "叶巍然",
    "董光霁",
    "董温茂",
    "田志诚",
    "宋鸿朗",
    "潘文耀",
    "文乐天",
    "夏建安",
    "乔宏放",
    "漕和昶",
    "易彬彬",
    "宋滨海",
    "于修雅",
    "赵泰和",
    "罗向阳",
    "孟修然",
    "顾阳州",
    "许志行",
    "康俊民",
    "周和畅",
    "邓烨华",
    "贺德水",
    "韩嘉荣",
    "崔志新",
    "龚振海",
    "李高达",
    "何博涛",
    "江阳华",
    "李英奕",
    "徐承宣",
    "曹英博",
    "曹飞扬",
    "薛康盛",
    "苏和豫",
    "曹嘉玉",
    "方乐圣",
    "武烨磊",
    "江天工",
    "刘元正",
    "唐逸明",
    "万星华",
    "金鸿博",
    "孙高扬",
    "石乐人",
    "段弘致",
    "徐子瑜",
    "史凯风",
    "宋天和",
    "萧和豫",
    "赵乐水",
    "黄子真",
    "程修德",
    "龚鸿志",
    "朱良畴",
    "邵宏义",
    "谭经国",
    "白俊誉",
    "段宏富",
    "邹立轩",
    "彭心远",
    "易元化",
    "孔昊然",
    "朱越彬",
    "吕伟泽",
    "戴华彩",
    "叶高雅",
    "余经纶",
    "邱鹏鲲",
    "金经义",
    "江英资",
    "石承载",
    "叶鹤轩",
    "邵乐正",
    "傅鸿彩",
    "赖信然",
    "毛英叡",
    "常高歌",
    "范英毅",
    "梁永望",
    "邱季萌",
    "黄高远",
    "薛刚捷",
    "邱雪松",
    "万英逸",
    "袁雅志",
    "梁高畅",
    "王俊哲",
    "彭宏毅",
    "秦泰和",
    "谢雅志",
    "康凯复",
    "钟泰平",
    "赖元德",
    "叶弘方",
    "潘浩初",
    "朱凯歌",
    "蒋嘉茂",
    "谢阳飙",
    "叶鸿祯",
    "萧凯泽",
    "戴飞鸾",
    "阎阳晖",
    "陈子濯",
    "阎勇毅",
    "萧敏才",
    "阎安怡",
    "杜星津",
    "卢展鹏",
    "邵鹏涛",
    "卢飞飙",
    "田元德",
    "侯坚秉",
    "谭敏智",
    "吴涵畅",
    "易弘扬",
    "郑志新",
    "蔡和怡",
    "蔡阳飙",
    "萧祺瑞",
    "冯鸿达"
  ],
  "cityName": [
    "朐故道",
    "项嘉城",
    "化皋州",
    "大东乡",
    "首湖区",
    "淮陟崖",
    "饶华谷",
    "青临村",
    "川农郡",
    "蒙丘峰",
    "平大岛",
    "花河县",
    "定昌坡",
    "汉头镇",
    "泉洋庄",
    "林行堡",
    "棣城港",
    "上兴区",
    "安南港",
    "湖东坡",
    "大桥郡",
    "安鹤堡",
    "湖绥堡",
    "南沧道",
    "门作镇",
    "武新港",
    "镇清区",
    "三清郡",
    "大东堡",
    "安南庄"
  ],
  "forceName": [
    "幻燕联盟",
    "龙兽公国",
    "神翔帝国",
    "暗元国",
    "承赵联邦",
    "玄夏联盟",
    "魔魏联盟",
    "宙辉国",
    "龙兽公国",
    "神元联盟",
    "玄夏国",
    "宙辉国",
    "承赵帝国",
    "暗元公国",
    "魔魏国",
    "天澜公国",
    "承赵联盟",
    "玄夏联邦",
    "魔魏联盟",
    "魔魏公国",
    "玄夏帝国",
    "魔魏帝国",
    "神元国"
  ],
  "auto": False,
  "person": {
    "刘备": {
    "loyal" : 99,
    "wise" : 90,
    "force" : 90,
    "troop" : 20000,
    "weapons" : 20000,
    "weaponType" : 3,
    "dsc" : "奸雄"
    },
    "曹操": {
    "loyal" : 99,
    "wise" : 99,
    "force" : 80,
    "troop" : 2000,
    "weapons" : 2000,
    "weaponType" : 3,
    "dsc" : "英雄"
    },
    "张飞": {
    "loyal" : 99,
    "wise" : 0,
    "force" : 99,
    "troop" : 2000,
    "weapons" : 2000,
    "weaponType" : 3,
    "dsc" : "英雄"
    },
    "关羽": {
    "loyal" : 10,
    "wise" : 0,
    "force" : 99,
    "troop" : 2000,
    "weapons" : 2000,
    "weaponType" : 3,
    "dsc" : "英雄"
    },
    "诸葛亮": {
    "loyal" : 99,
    "wise" : 99,
    "force" : 0,
    "troop" : 2000,
    "weapons" : 2000,
    "weaponType" : 3,
    "dsc" : "英雄"
    }
  },
  "city": {
    "0-0": {
    "name": "许昌",
    "population": 200000,
    "perTreasure": 5.0,
    "officer": ["曹操", "关羽", "诸葛亮"],
    "prisoner": [],
    "restTroop": 0,
    "weapons": {},
    "money":100000
    },
    "1-0": {
    "name": "邺城",
    "population": 200000,
    "perTreasure": 5.0,
    "officer": ["张飞"],
    "prisoner": [],
    "restTroop": 0,
    "weapons": {},
    "money":1000
    },
    "0-1": {
    "name": "成都",
    "population": 200000,
    "perTreasure": 5.0,
    "officer": ["刘备"],
    "restTroop": 0,
    "weapons": {},
    "money":1000
    }
  },
  "force": {
    "魏国": {
    "header": "曹操",
    "cities": ["0-0", "1-0"]
    },
    "蜀国": {
    "header": "刘备",
    "cities": ["0-1"]
    }
  }
}


class Geo:
    sea = 0x1
    mountain = 0x2
    river = 0x3
    plain = 0x4
    # beach = 0x5
    tree = 0x5
    ranges = 1, 6, 2
    color = {
        1: 44,
        2: 43,
        3: 46,
        4: 42,
        # 5: 46,
        5: 41
    }


class Console:
    def __init__(self):
        colorama.init(True)
        self.map_ = []
        self.bg = []
        self.fg = 30
        self.width = 80
        self.height = 60
        self.indent = 0

    def set_bg(self, d0):
        self.bg = d0

    def set_map(self, map_):
        indent = 0
        self.map_ = map_
        for i in map_:
            for j in i:
                # k0 = 0
                # for k in j:
                #     if u'\u4e00' <= k <= u'\u9fa5':
                #         k0 += 2
                #     else:
                #         k0 += 1
                # indent = max(indent, k0)
                indent = max(indent, len(j))
        self.indent = indent + 2
        print(self.indent)

    @staticmethod
    def aligns(s0):
        new_string = ''
        for i in s0:
            codes = ord(i)
            if codes <= 126:
                new_string = new_string + chr(codes + 65248)
            else:
                new_string = new_string + i
        return new_string

    def print_map(self):
        # os.system('mode con cols=%d lines=%d' % (self.height, self.width))
        for i in range(len(self.map_[0])+1):
            # print(f'{str(i-1).center(self.indent)}', end='')
            # print(self.aligns(str(i-1)), end='')
            print(f'{self.aligns(str(i-1)).center(self.indent, "　")}', end='')
        print()
        for i, i1 in enumerate(self.map_):
            # print(f'{str(i).center(self.indent)}', end='')
            # print(self.aligns(str(i), self.indent), end='')
            print(f'{self.aligns(str(i)).center(self.indent, "　")}', end='')
            for j, j1 in enumerate(i1):
                # print(f'\033[1;{Geo.color[self.bg[i][j]]};{self.fg}m{j1.center(self.indent, " ")}', end='')
                # print(f'\033[1;{Geo.color[self.bg[i][j]]};{self.fg}m{self.aligns(j1, self.indent)}', end='')
                print(f'\033[1;{Geo.color[self.bg[i][j]]};{self.fg}m{self.aligns(j1).center(self.indent, "　")}', end='')
            print()

    @staticmethod
    def skim_files(path, rows=3, cols=4):
        gg0 = {'point': 0, 'end': False}
        files = os.listdir(path)
        if not files:
            print('empty')
            return
        length = len(files)
        step = rows * cols
        for i in range(0, length):
            if i and not i % cols:
                print()
            print(files[i], end='\t')
        print()
        print('a:turn left b:turn right esc:back')

        def run(e0: keyboard.KeyboardEvent):
            # global point, end
            # print(e0.name)
            if e0.event_type == 'down':
                if e0.name == 'd':
                    os.system('cls')
                    if gg0['point'] + step + 1 >= length:
                        return
                    gg0['point'] += step
                    os.system('cls')
                    top = gg0['point'] + 12
                    if top > length:
                        top = length
                    it = 0
                    for i in range(gg0['point'], top):
                        print(str(i)+'.'+files[i], end='')
                        it += 1
                        if not it % cols:
                            print()
                    print('page:%d' % ((gg0['point']+step-1)//step))
                elif e0.name == 'a':
                    os.system('cls')
                    if gg0['point'] - step < 0:
                        return
                    gg0['point'] -= step
                    os.system('cls')
                    top = gg0['point'] + 12
                    if top > length:
                        top = length
                    it = 0
                    for i in range(gg0['point'], top):
                        print(str(i)+'.'+files[i], end='')
                        it += 1
                        if not it % cols:
                            print()
                    print('page:%d' % ((gg0['point'] + step - 1) // step))
                elif e0.name == 'esc':
                    os.system('cls')
                    keyboard.unhook_all_hotkeys()
                    gg0['end'] = True

        keyboard.hook(run)
        while not gg0['end']:
            pass
        # keyboard.unhook_all_hotkeys()
        keyboard.unhook_all()

    @staticmethod
    def skim_data(data, step=3):
        if not data:
            print('empty')
            return
        gg0 = {'point': 0, 'end': False}
        keys = list(data.keys())
        length = len(keys)
        for i in keys[:step]:
            print('--' + i + '--')
            print(data[i])
            print()

        print('a:turn left b:turn right esc:back')

        def run(e0: keyboard.KeyboardEvent):
            if e0.event_type == 'down':
                if e0.name == 'd':
                    if gg0['point'] + step + 1 >= length:
                        return
                    os.system('cls')
                    gg0['point'] += step
                    os.system('cls')
                    top = gg0['point'] + step
                    if top > length:
                        top = length
                    for i in range(gg0['point'], top):
                        print('--'+keys[i]+'--')
                        print(data[keys[i]])
                        print()

                    print('page:%d' % ((gg0['point']+step-1)//step))
                elif e0.name == 'a':
                    if gg0['point'] - step < 0:
                        return
                    os.system('cls')
                    gg0['point'] -= step
                    os.system('cls')
                    top = gg0['point'] + step
                    if top > length:
                        top = length
                    for i in range(gg0['point'], top):
                        print('--'+keys[i]+'--')
                        print(data[keys[i]])
                        print()

                    print('page:%d' % ((gg0['point'] + step - 1) // step))
                elif e0.name == 'esc':
                    os.system('cls')
                    keyboard.unhook_all_hotkeys()
                    gg0['end'] = True

        keyboard.hook(run)
        while not gg0['end']:
            pass

        keyboard.unhook_all()


class Top:
    Troops = 20000
    Population = 400000
    Money = 200000
    Treasure = 10
    Loyal = 99
    Wise = 99
    Force = 99


class Weapon:
    none = 0
    sword = 1
    arrow = 2
    catapult = 3
    mount = 4
    ChineseName = {
        none: "徒手",
        sword: "剑",
        arrow: "弓",
        catapult: "攻城车",
        mount: "骑装"
    }
    price = {
        sword: 1,
        arrow: 1,
        catapult: 100,
        mount: 50
    }


class Person:
    def __init__(self):
        # self.id = None
        self.name = ''
        self.dsc = ''
        self.belong = 1

        self.loyal = random.randint(0, Top.Loyal)
        self.wise = random.randint(0, Top.Wise*2)
        self.force = random.randint(0, Top.Force*2)
        self.wise = self.wise // 2 if self.wise > Top.Wise else self.wise
        self.force = self.force // 2 if self.force > Top.Force else self.force

        self.troop = 0
        self.weapons = 0
        self.weaponType = 0

    @classmethod
    def load_obj(cls, d0):
        """
        no name
        :param d0:
        :return:
        """
        obj = cls()
        # int 1, float 2, str 3, list 4, dict 5
        keys = {
            "loyal": 1,
            "wise": 1,
            "force": 1,
            "troop": 1,
            "weapons": 1,
            "weaponType": 1,
            "dsc": 3
        }
        for k, v in keys.items():
            if k not in d0:
                continue

            setattr(obj, k, d0[k])

            if v == 1:
                if not isinstance(d0[k], int):
                    return False
            elif v == 2:
                if not isinstance(d0[k], float):
                    return False
            elif v == 3:
                if not isinstance(d0[k], str):
                    return False
            elif v == 4:
                if not isinstance(d0[k], list):
                    return False
                else:
                    setattr(obj, k, list(d0[k]))
            elif v == 5:
                if not isinstance(d0[k], dict):
                    return False

        return obj

    def obj_info(self):
        info = 'name:{}\tloyal:{}\twise:{}\tforce:{}\tbelong:{}\ntroop:{},weapon:{}-{}\ndsc:{}'
        return info.format(self.name, self.loyal, self.wise, self.force, self.belong, \
                           self.troop, Weapon.ChineseName[self.weaponType], self.weapons, self.dsc)


class City:
    def __init__(self):
        self.name = ''
        self.header = None

        self.population = random.randint(Top.Population//5, Top.Population//2)
        self.perTreasure = random.randint(1, 4)
        self.tax = 0.05
        self.growth = 0.03
        self.natality = 0.01

        self.officer = set()
        self.prisoner = set()
        self.restTroop = Top.Troops
        self.weapons = {}
        self.money = random.randint(1, Top.Money//10)

        self.convey = {}

    def update(self):
        # 控制度
        if self.header.wise > Top.Wise * 0.8:
            self.growth = 0.1
            self.natality = 0.05
            self.tax = 0.002
        elif self.header.wise > 0.6:
            self.growth = 0.5
            self.natality = 0.03
            self.tax = 0.001
        else:
            self.growth = 0.3
            self.natality = 0.02
            self.tax = 0.0005

        # 经济

        self.perTreasure += self.perTreasure * self.growth
        if self.perTreasure > Top.Treasure:
            self.perTreasure = Top.Treasure

        self.money += self.population * self.perTreasure * self.tax
        if self.money > Top.Money:
            self.money = Top.Money
        else:
            self.money = int(self.money)

        # 人口

        self.population += int(self.population * self.natality)
        if self.population > Top.Population:
            self.population = Top.Population

    @classmethod
    def load_obj(cls, d0):
        """
        no officer
        :param d0:
        :return:
        """
        obj = cls()
        # int 1, float 2, str 3, list 4, dict 5
        keys = {
            "name": 3,
            "header": 1,
            "population": 1,
            "perTreasure": 2,
            "officer": 4,
            # "prisoner": 4,
            "restTroop": 1,
            "weapons": 5,
            "money": 1
        }
        if 'officer' not in d0:
            return False
        for k, v in keys.items():
            if k not in d0:
                continue

            setattr(obj, k, d0[k])

            if v == 1:
                if not isinstance(d0[k], int):
                    return False
            elif v == 2:
                if not isinstance(d0[k], float):
                    return False
            elif v == 3:
                if not isinstance(d0[k], str):
                    return False
            elif v == 4:
                if not isinstance(d0[k], list):
                    return False
                else:
                    setattr(obj, k, list(d0[k]))
            elif v == 5:
                if not isinstance(d0[k], dict):
                    return False

        return obj

    def obj_info(self, careful='whneop'):
        """

        :param careful: h:header, n:big number, e:economic, o:officer, p:prisoner
        :return:
        """
        if 'h' in careful:
            header = self.header.name
        else:
            header = "?"

        if 'n' in careful:
            troop = 0
            for i in self.officer:
                troop += i.troop
            population = self.population
            natality = self.natality
            restT = self.restTroop
        else:
            troop = '?'
            population = '?'
            natality = '?'
            restT = '?'

        if 'e' in careful:
            perTreaure = self.perTreasure
            tax = self.tax
            growth = self.growth
            money = self.money
        else:
            perTreaure = "?"
            tax = "?"
            growth = "?"
            money = "?"

        if 'w' in careful:
            weapons = ''
            for k, v in self.weapons.items():
                weapons += '\t' + Weapon.ChineseName[k]+':'+str(v)
        else:
            weapons = '?'

        if 'o' in careful:
            officers = ''
            for i in self.officer:
                officers += i.name + '\t'
        else:
            officers = '?'

        if 'p' in careful:
            conveyPerson = 0

        if 'p' in careful:
            prisoner = ''
            for i in self.prisoner:
                prisoner += i.name + '\t'
        else:
            prisoner = '?'

        info = "name:{}\theader:{}\ttroop:{}\trestTroop:{}\
        \tmoney:{}\nweapons:{}\nofficers:{}\nprisoner:{}\npopulation:{}\
        \tperTreasur:{}\tnatality:{}\ttax:{}\tgrowth:{}".\
            format(self.name, header, troop, restT, money, weapons, officers, prisoner, population, perTreaure, natality, tax, growth)
        return info

    def show_person(self):
        info1 = 'officer:'
        info2 = 'prisoner:'
        it = 1
        for i in self.officer:
            info1 += str(it) + '(' + i.name + ')\t'
            it += 1

        it = 1
        for i in self.prisoner:
            info2 += str(it) + '(' + i.name + ')\t'
            it += 1

        return info1, info2

    def show_convey(self):
        cities = {}
        # for k, v in self.conveyPerson.items():
        #     if k not in cities:
        #         cities[k] = {"officer":''}
        #         for i in v:
        #             cities[k]["officer"] += i.name + '\t'
        #
        # for k, v in self.conveyWeapon.items():
        #     if k not in cities:
        #         cities[k] = {"weapons":""}
        #         for i1, i in v.items():
        #             cities[k]["weapons"] += Weapon.ChineseName[i1] + str(i) + ', '
        # for k, v in self.conveyTroop.items():
        #     if k not in cities:
        #         cities[k] = {"troop": str(v)}
        #
        # for k, v in self.conveyMoney.items():
        #     if k not in cities:
        #         cities[k] = {"mongy": str(v)}

        for k, v in self.convey.items():
            tmp_d = str(k[0]) + '-' + str(k[1])
            cities[tmp_d] = {}
            if 'weapon' in v:
                cities[tmp_d] = {"weapons":""}
                for i1, i in v['weapon'].items():
                    cities[tmp_d]["weapons"] += Weapon.ChineseName[i1] + str(i) + ', '

            if 'officer' in v:
                cities[tmp_d] = {"officer": ''}
                for i in v['officer']:
                    cities[tmp_d]["officer"] += i.name + '\t'

            if 'troop' in v:
                cities[tmp_d]['troop'] = str(v['troop'])

            if 'money' in v:
                cities[tmp_d]['money'] = str(v['money'])

        info = ''
        for k, v in cities.items():
            # tmp_d = str(k[0]) + '-' +str(k[1])
            # info += tmp_d + '\n'
            info += k + '\n'
            for i1, i in v.items():
                info += i1 + ': ' + i + '\n'
            info += '\n'
        return info[:-1]

    def make_outbreak(self):
        for i in self.officer:
            i.troop = i.troop * 4 // 5
            i.weapons = i.weapons * 4 // 5


class Force:
    def __init__(self):
        self.header = 0
        self.cities = set()
        self.name = ""

    @classmethod
    def load_obj(cls, d0):
        """
        no name
        :param d0:
        :return:
        """
        obj = cls()
        # int 1, float 2, str 3, list 4, dict 5
        keys = {
            "header": 3,
            "cities": 4
        }
        for k, v in keys.items():
            if k not in d0:
                return False

            setattr(obj, k, d0[k])

            if v == 1:
                if not isinstance(d0[k], int):
                    return False
            elif v == 2:
                if not isinstance(d0[k], float):
                    return False
            elif v == 3:
                if not isinstance(d0[k], str):
                    return False
            elif v == 4:
                if not isinstance(d0[k], list):
                    return False
                else:
                    setattr(obj, k, list(d0[k]))
            elif v == 5:
                if not isinstance(d0[k], dict):
                    return False

        return obj


class ResManager:
    def __init__(self):
        self.geoMap = []
        self.cities = {}
        self.persons = {}
        self.names = {
            "city": [],
            "person": [],
            "force": []
        }
        # self.otherPersons = {}
        self.forces = {}
        self.myForce = 0
        self.width = self.height = 0
        # self.isOk = False
        self.failed = {}

        self.groups = {}
        self.overed = set()
        self.turn = 1
        self.nowLocation = 1, 1
        self.userSave = {}

        self.attack = {}

    # def load_map(self, filename):
    #     if not os.path.exists(filename):
    #         return False
    #     with open('maps/'+filename, 'rb') as f:
    #         charset = chardet.detect(f.readline())
    #     map_ = []
    #     w = 0
    #     status = ['--map--', '--person--', '--city--', '--force--']
    #     stats = None
    #     with open('maps/'+filename, 'r', encoding=charset['encoding']) as f:
    #         while 1:
    #             s0 = f.readline()
    #             s0 = s0.replace(' ', '')
    #             if not s0:
    #                 break
    #             elif s0[0] == '#':
    #                 continue
    #             elif s0 in status:
    #                 stats = s0
    #                 continue
    #             s0 = s0.split('#')[0]
    #             if s0 == '--map--':
    #                 l0 = s0.split(',')
    #                 tmp = []
    #                 w_1 = 0
    #                 for i in l0:
    #                     i_1 = int(i)
    #                     if Geo.ranges[0] <= i_1 <= Geo.ranges[1]:
    #                         tmp.append(i_1)
    #                     else:
    #                         return False
    #                     w_1 += 1
    #                 if w and w_1 != w:
    #                     return False
    #                 map_.append(tmp)
    #             elif s0 == '--person--':
    #                 pass
    #         if len(map_[0]) <= 0 or len(map_[0]) <= 0:
    #             return False
    #
    #     self.geoMap = map_
    #     self.width, self.height = len(map_[0]), len(map_[0])
    #     return True

    def load_map(self, filepath):
        self.cities.clear()
        self.forces.clear()
        self.persons.clear()
        self.failed.clear()
        if not os.path.exists(filepath):
            print('path error')
            return False
        with open(filepath, 'r', encoding='utf-8') as f:
            top_map = json.load(f)

        # load name and check repeat
        check_key_1 = ['person', 'city', 'force']
        for i in check_key_1:
            self.names[i] = list(set(top_map[i+"Name"]))
            # self.names[i] = top_map[i]
            # if len(self.names[i]) != len(set(self.names[i])):
            #     return False

        self.geoMap = top_map['map']
        self.width, self.height = len(self.geoMap[0]), len(self.geoMap)

        # check geoMap and count effective area for city
        e_area = []
        for i1, i in enumerate(self.geoMap):
            for j1, j in enumerate(i):
                if j < Geo.ranges[0] or j > Geo.ranges[1]:
                    print('geoMap error')
                    return False
                if j <= Geo.ranges[2]:
                    e_area.append((i1, j1))

        if top_map['auto']:
            # effective area
            if len(self.names['city']) > len(e_area):
                self.names['city'] = self.names['city'][:e_area]
            elif len(self.names['city']) < len(e_area):
                random.shuffle(e_area)
                e_area = e_area[0:len(self.names['city'])]
            # make city
            it = iter(self.names['city'])
            for i in e_area:
                obj = City()
                obj.name = it.__next__()
                self.cities[i] = obj
            self.names['city'] = []

            # make person
            if len(self.names['person']) < len(e_area):
                print("map's person aren't enough")
                return False
            bak_person = []
            if len(self.names['person']) > len(e_area) * 4:
                bak_person = self.names['person'][len(e_area) * 4:]
                self.names['person'] = self.names['person'][len(e_area) * 4:]
            s0 = random.sample(range(0, len(self.names['person'])-1), len(e_area)-1)
            s0.sort()
            s0.append(len(self.names['person'])-1)
            begin = 0
            for i1, i in enumerate(e_area):
                print(begin, s0[i1]+1)
                for j in self.names['person'][begin:s0[i1]+1]:
                    obj = Person()
                    obj.name = j
                    self.persons[obj.name] = obj
                    self.cities[i].officer.add(obj)
                begin = s0[i1] + 1
                if not self.cities[i].officer:
                    print(begin, s0)
                for j in self.cities[i].officer:
                    self.cities[i].header = j
                    break
            self.names['person'] = bak_person

            # force
            if len(self.names['force']) > len(e_area):
                self.names['force'] = self.names['force'][:len(e_area)]
            s0 = random.sample(range(0, len(e_area)-1), len(self.names['force'])-1)
            s0.sort()
            s0.append(len(e_area)-1)
            begin = 0
            for i1, i in enumerate(self.names['force']):
                self.forces[i] = Force()
                self.forces[i].name = i
                for j in e_area[begin:s0[i1]+1]:
                    self.cities[j].header.belong = i
                    for k in self.cities[j].officer:
                        k.belong = i
                    self.forces[i].cities.add(j)
                else:
                    obj = Person()
                    obj.name = i + '首领'
                    obj.belong = i
                    if obj.name in self.persons:
                        print("name shouldn't be country name added '首领'")
                        return False
                    self.persons[obj.name] = obj
                    obj.loyal = Top.Loyal
                    self.cities[j].header = obj
                    self.cities[j].officer.add(obj)
                    self.forces[i].header = obj
                begin = s0[i1] + 1

        else:
            for k, v in top_map['person'].items():
                tmp_o = Person.load_obj(v)
                self.persons[k] = tmp_o
                tmp_o.name = k

            for k, v in top_map['city'].items():
                tmp_d = k.split('-')
                tmp_o = City.load_obj(v)
                try:
                    tmp_d = int(tmp_d[0]), int(tmp_d[1])
                    self.cities[tmp_d] = tmp_o
                except KeyError:
                    print("error about city's key")
                    return False

                try:
                    tmp_o.header = self.persons[tmp_o.officer[0]]
                    tmp_of = set()
                    for i in tmp_o.officer:
                        tmp_of.add(self.persons[i])
                    if not tmp_of:
                        print("the person not in person(dict)")
                        return False
                    tmp_o.officer = tmp_of
                except (TypeError, IndexError, KeyError, ValueError):
                    print('error 7fk357f3f')
                    return False

                self.cities[tmp_d] = tmp_o

            for k, v in top_map['force'].items():
                tmp_o = Force.load_obj(v)
                self.forces[k] = tmp_o
                tmp_o.name = k

                tmp_of = set()
                for i in tmp_o.cities:
                    try:
                        tmp_d = i.split('-')
                        tmp_d = int(tmp_d[0]), int(tmp_d[1])
                    except (TypeError, IndexError, ValueError):
                        print('city format error')
                        return False
                    if tmp_d not in self.cities:
                        print('city not in city(dict)')
                        return False
                    tmp_of.add(tmp_d)
                    for j in self.cities[tmp_d].officer:
                        j.belong = k
                    # self.cities[tmp_d].header = j
                tmp_o.cities = tmp_of
                try:
                    tmp_o.header = self.persons[tmp_o.header]
                except KeyError:
                    print('the leader not in person(dict)')
                    return False

            # check number
            cities = 0
            for k, v in self.forces.items():
                cities += len(v.cities)
                for j in v.cities:
                    if self.cities[j].header.belong != k:
                        print("city don't belong to it's force")
                        return False
            c_k = len(self.cities.keys())
            if c_k > cities:
                should_d = []
                for k1, v1 in self.cities.items():
                    if v1.header.belong == '':
                        should_d.append(k1)
                for i in should_d:
                    del self.cities[i]
            elif c_k < cities:
                print('no enough cities(dict)')
                return False

        return True

    def get_person(self):
        # if not self.otherPersons:
        #     return None
        # keys = list(self.otherPersons.keys())
        # obj = keys[random.randint(1, len(keys)-1)]
        # del self.otherPersons[obj.name]
        # self.persons[obj.name] = obj
        # return obj
        if not self.names['person']:
           return None
        obj = Person()
        obj.name = self.names['person'][-1]
        self.names['person'].pop()
        return obj

    def search_force(self, yx):
        for k, v in self.forces.items():
            if yx in v.cities:
                return k

    def search_city(self, obj):
        for k, v in self.cities.items():
            if obj in v.officer:
                return v

    def auto_atk(self):
        force_1 = 0
        force_2 = 0
        troop_1 = 0
        troop_2 = 0
        city = self.cities[self.attack['def']]
        for i in self.attack['atk']:
            force_1 += i.weapons * Weapon.price[i.weaponType] * i.force // 100
            troop_1 += i.troop
        for i in city.officer:
            force_2 += i.weapons * Weapon.price[i.weaponType] * i.force // 100
            troop_2 += i.troop
        force_2 *= city.header.wise * 2.2 * city.header.loyal * 2.2 // Top.Wise // Top.Loyal
        if city.header.wise > 80 and self.attack['money'] < 100 * (city.header.wise-70):
            return 'failed, money is not enough'
        if force_1 < force_2:
            for i in self.attack['atk']:
                p0 = self.search_city(i)
                i.weaponType = 0
                i.weapons = 0
                i.troop = 0
                p0.officer.remove(i)
                city.prisoner.add(i)
            per = troop_1 * 0.4 / troop_2
            for i in city.officer:
                i.troop -= int(i.troop*per)
                if i.troop < 0:
                    i.troop = 0
            if self.forces[self.myForce].header in city.prisoner:
                self.ko(self.myForce, city.header.belong)
            return 'failed, the troop were over'
        else:
            for i in self.attack['atk']:
                i.troop -= int(i.troop*0.3)
                i.weapons = int(i.weapons*0.3)
            for i in city.officer:
                i.weaponType = 0
                i.weapons = 0
                i.troop = 0
            city.prisoner = city.prisoner.union(city.officer)
            city.officer = set(self.attack['atk'])

            for i in self.attack['atk']:
                p0 = self.search_city(i)
                p0.officer.remove(i)
                # i.header = self.attack['atk'][0]
            else:
                city.header = i

            force_3 = self.search_force(self.attack['def'])
            if self.forces[force_3].header in self.cities[self.attack['def']].prisoner:
                self.ko(force_3, self.myForce)

            return 'succeed, occupied the city'

    def update(self):
        for k, v in self.cities.items():
            v.update()
            for k1, v1 in v.convey.items():
                city = self.cities[k1]
                if 'money' in v1:
                    city.money += v1['money']
                if 'troop' in v1:
                    city.restTroop += v1['troop']
                if 'weapon' in v1:
                    for k2, v2 in v1['weapon'].items():
                        if k2 not in city.weapons:
                            city.weapons[k2] = 0
                        city.weapons[k2] += v2
                if 'officer' in v1:
                    if not v1['officer']:
                        continue
                    if v1['officer'][0].belong != city.header.belong:
                        city.prisoner = city.prisoner.union(set(v1['officer']))
                    else:
                        city.officer = city.officer.union(set(v1['officer']))
            v.convey = {}
        self.turn += 1
        self.overed.clear()

    def ko(self, force, who):
        for i in self.forces[force].cities:
            for j in self.cities[i].officer:
                j.belong = who
        self.forces[who].cities = self.forces[who].cities.union(self.forces[force].cities)
        self.failed[force] = self.forces[force]

        for k, v in self.persons.items():
            if v.belong == force:
                v.belong = who

        del self.forces[force]
        print(force+'is game over!')
        if self.myForce == force:
            print('game is over!\n\t往兮一何盛\n\t今兮一何衰\n英雄不过是别人的嫁衣罢了...')
            time.sleep(1000000)
        print('壮士一去兮复不还...')

    @staticmethod
    def load_obj(filepath):
        with open('retention/'+filepath, 'rb') as f:
            return pickle.load(f)


class MainWin:
    def __init__(self):
        if not os.path.exists(MAP_FILEPATH):
            os.mkdir(MAP_FILEPATH)
        if not os.path.exists(SAVE_FILEPATH):
            os.mkdir(SAVE_FILEPATH)

        self.res = ResManager()
        self.__saved = True
        self.floor = 1
        self.console = Console()
        self.filePath = ''
        # self.__queue = Queue(128)
        # self.__qDict = {}

    def run(self):
        while 1:
            if self.floor == 1:
                self.view_1()
            elif self.floor == 2:
                self.view_2()
            elif self.floor == 3:
                self.view_3()
            elif self.floor == 4:
                self.view_4()

    def view_1(self):
        help_info = '''
# input
# "load mapName" to load a new map(-r for a retention) you chosen
# "show maps" to show all maps
# "show retentions" to show all retentions you saved
# "help" to show those info
# "create mapName" to create a map, you can edit it with format '.txt'
# "exit" to exit'''
        while 1:
            input_ = self.hand_cmd(input("-.-:>"))
            if input_[0] == 'exit':
                exit()
            elif input_[0] == 'help':
                print(help_info)
            elif input_[0] == 'show':
                if len(input_) > 1:
                    if input_[1] == 'maps':
                        Console.skim_files(MAP_FILEPATH)
                    elif input_[1] == 'retentions':
                        Console.skim_files(SAVE_FILEPATH)
            elif input_[0] == 'load':
                if len(input_) <= 1:
                    continue
                if input_[1] != '-r':
                    if not os.path.exists(MAP_FILEPATH+'/'+input_[1]):
                        print('path error')
                        continue
                    else:
                        self.res = ResManager()
                        try:
                            rlt = self.res.load_map(MAP_FILEPATH+'/'+input_[1])
                        except OSError:
                            print('map error1')
                            continue
                        if not rlt:
                            print('map error2')
                            continue
                        self.floor = 2
                        self.filePath = input_[1]
                        return
                else:
                    if len(input_) <= 2:
                        continue
                    if not os.path.exists(SAVE_FILEPATH+'/'+input_[2]):
                        print('path error')
                        continue
                    try:
                        with open(SAVE_FILEPATH+'/'+input_[2], 'rb') as f:
                            self.res = pickle.load(f)
                        self.floor = 2
                        self.filePath = input_[2]
                        return
                    except (OSError, pickle.PickleError):
                        print("file error")
            elif input_[0] == 'create':
                if len(input_) < 2:
                    continue
                with open(MAP_FILEPATH+'/'+input_[1], 'w', encoding='utf-8') as f:
                    json.dump(MapMode, f)
                print('created')

    def view_2(self):
        self.console.set_bg(self.res.geoMap)
        tmp_map = [['' for i in range(self.res.width)] for j in range(self.res.height)]
        for k, v in self.res.forces.items():
            for i in v.cities:
                tmp_map[i[0]][i[1]] = k
        for k, v in self.res.cities.items():
            if tmp_map[k[0]][k[1]] == '':
                tmp_map[k[0]][k[1]] = '?'
        self.console.set_map(tmp_map)
        forces = list(self.res.forces.keys())
        while 1:
            self.console.print_map()
            print('choose a force(-1 for back)', end=':\n')
            for i1, i in enumerate(forces):
                if i1 and not i1 % 7:
                    print()
                print(f'{i1}({i})', end=' ')
            try:
                input_ = int(input('\n'))
            except TypeError:
                continue
            if 0 <= input_ < len(forces):
                self.res.myForce = forces[input_]
                self.floor = 3
                break
            elif input_ == -1:
                self.floor = 1
                break

    def view_3(self):
        help_dict = {
            "help": "this menu",
            "save": "save filename\nto save",
            "exit": "",
            "back": "will not save",
            "map": "map [-c] to show map\n-c for showing country name",
            "push": '"push groupName y1-x1 y2-x2 ..." to save many cities at a group'
                    '\npush groupName, y1-x2:y1-x2 to choose cities y1<y<y2,x1<x<x2',
            "show": '"show [-d groupName]" to show all groups you saved\n'
                    '-d to delete group you created',
            "loc": '"loc y-x" to locate a city you chosen',
            "info": '"info [[-g groupName] | -p |-o|-c]" to view a city\n-g for cities in a group\
            ,\n-o to view officers\n-p to view prisoners\n-c to view convey',
            "alt": "alt -w|-p|-r \n-w to allocate weapon\n-p to allocate troop\n-r to allocate random",
            "transfer": "transfer y-x -w|-m|-t|-p\n-w: weapon\n-m: money\n-t: troop\n-p: person",
            "buy": "buy [-p t1:m1 t2:m2 ...]|-i\nbuy weapons\n-i for information",
            "enlist": "enlist number\nmake sure that your money is enough",
            "govern": "govern -a|-b person_id|-s|[-d money person]|-i|-e|-r y-x|-o y-x|-m y-x \n-a appoint a mayor\n-b to break "
                      "sb "
                      "into prison\n-s to "
                      "search a person for you\n-e to enlist a prisoner\n-d to draw a person over your side\n-i for "
                      "information\n-o to start a outbreak\n-m to decrease it's money",
            "atk": "atk y-x groupName|[y1-x1,y2-x2,y3-x3,...] [-auto]\norder cities to attack city located at "
                   "y-x\n-auto for speed",
            "end": "end the turn",
            "who": "who am i"
        }

        while 1:
            inputs = input("-.-:>").split(';')
            for i_i in inputs:
                input_ = self.hand_cmd(i_i)
                if input_[0] == 'save':
                    if len(input_) < 2:
                        if not self.filePath:
                            print('error, no path for saving')
                            continue
                        self.save(self.filePath)
                    else:
                        self.save(input_[1])
                elif input_[0] == 'exit':
                    exit()
                elif input_[0] == 'back':
                    self.floor = 1
                    return
                elif input_[0] == 'help':
                    if len(input_) < 2:
                        print('parameter:')
                        for i1, i in enumerate(list(help_dict.keys())):
                            if i1 and not i1 % 7:
                                print()
                            print(i, end='\t')
                        print()
                        continue
                    try:
                        print(help_dict[input_[1]])
                    except KeyError:
                        print('parameter error')
                elif input_[0] == 'push':
                    if len(input_) < 3:
                        print('error')
                        continue
                    tmp_d = set()
                    if ':' in input_[2]:
                        try:
                            tmp_s0 = input_[2].split(':')
                            tmp_s1 = tmp_s0[0].split('-')
                            tmp_s1 = int(tmp_s1[0]), int(tmp_s1[1])
                            tmp_s2 = tmp_s0[1].split('-')
                            tmp_s2 = int(tmp_s2[0]), int(tmp_s2[1])
                        except (TypeError, IndexError, ValueError):
                            continue
                        r_y, r_x = (1 if tmp_s1[0] < tmp_s2[0]+1 else -1), (1 if tmp_s1[1] < tmp_s2[1]+1 else -1)
                        for i in range(tmp_s1[0], tmp_s2[0]+1, r_x):
                            for j in range(tmp_s2[1], tmp_s2[1]+1, r_y):
                                if self.can_view((i, j)) != -1:
                                    tmp_d.add((i, j))
                    else:
                        for i in input_[2:]:
                            tmp_s0 = i.split('-')
                            try:
                                tmp_s0 = int(tmp_s0[0]), int(tmp_s0[1])
                                if self.can_view(tmp_s0) != -1:
                                    tmp_d.add(tmp_s0)
                            except (TypeError, IndexError, ValueError):
                                continue
                    self.res.groups[input_[1]] = tmp_d
                elif input_[0] == 'show':
                    if len(input_) > 2:
                        if input_[1] != '-d':
                            print('error parameter')
                            continue
                        if input_[2] in self.res.groups:
                            del self.res.groups[input_[2]]
                        continue
                    for k, v in self.res.groups.items():
                        tmp_d = []
                        for j in v:
                            tmp_d.append(str(j[0])+'-'+str(j[1]))
                        print(k+':'+','.join(tmp_d))
                elif input_[0] == 'loc':
                    if len(input_) < 2:
                        print(str(self.res.nowLocation[0])+'-'+str(self.res.nowLocation[1]))
                        continue
                    try:
                        tmp_d = input_[1].split('-')
                        tmp_lc = int(tmp_d[0]), int(tmp_d[1])
                    except (IndexError, TypeError):
                        print('format error')
                        continue
                    if tmp_lc[0] < 0 or tmp_lc[0] >= self.res.height or \
                            tmp_lc[1] < 0 or tmp_lc[1] >= self.res.width:
                        print('error')
                        continue
                    self.res.nowLocation = tmp_lc
                elif input_[0] == 'info':
                    if not self.check(input_, 1):
                        continue
                    if len(input_) < 2:
                        if self.can_view(self.res.nowLocation) == 2:
                            print(self.res.cities[self.res.nowLocation].obj_info())
                        elif self.can_view(self.res.nowLocation) == 1:
                            print(self.res.cities[self.res.nowLocation].obj_info('hno'))
                        elif self.can_view(self.res.nowLocation) == 0:
                            print(self.res.cities[self.res.nowLocation].obj_info('hn'))
                        else:
                            print('no city here')
                        continue
                    elif input_[1] == '-g':
                        if len(input_) < 3:
                            print('error')
                            continue
                        if input_[2] not in self.res.groups:
                            print("name error")
                            continue
                        tmp_d = {}
                        for i in self.res.groups[input_[2]]:
                            if i not in self.res.cities:
                                continue
                            view = self.can_view(i)
                            tmp_k = str(i[0]) + '-' + str(i[1])
                            if view == 0:
                                tmp_d[tmp_k] = self.res.cities[i].obj_info('')
                            elif view == 1:
                                tmp_d[tmp_k] = self.res.cities[i].obj_info('hno')
                            elif view == 2:
                                tmp_d[tmp_k] = self.res.cities[i].obj_info()

                        Console.skim_data(tmp_d, 3)
                    elif input_[1] == '-o':
                        if self.can_view(self.res.nowLocation) < 1:
                            print('not allow')
                            continue
                        tmp_d = {}
                        for i in self.res.cities[self.res.nowLocation].officer:
                            tmp_d[i.name] = i.obj_info()
                        if self.can_view(self.res.nowLocation) == 2:
                            for i in self.res.cities[self.res.nowLocation].prisoner:
                                tmp_d[i.name] = i.obj_info()
                        Console.skim_data(tmp_d, 5)
                    elif input_[1] == '-p':
                        if self.can_view(self.res.nowLocation) < 3:
                            print('not allow')
                            continue

                        tmp_d = {}
                        for i in self.res.cities[self.res.nowLocation].prisoner:
                            tmp_d[i.name] = i.obj_info()
                        Console.skim_data(tmp_d, 5)
                    elif input_[1] == '-c':
                        print(self.res.cities[self.res.nowLocation].show_convey())
                elif input_[0] == 'buy':
                    if len(input_) < 2:
                        continue
                    if self.can_view(self.res.nowLocation) != 2:
                        print('area error')
                        continue
                    if input_[1] == '-i':
                        tmp_info = ''
                        for k, v in Weapon.price.items():
                            tmp_info += str(k)+"("+Weapon.ChineseName[k] + "):$" + str(v) + '\t'
                        print(tmp_info)
                        print(f'local money:{self.res.cities[self.res.nowLocation].money}')
                    elif input_[1] == '-p':
                        if len(input_) < 3:
                            print('error')
                            continue
                        # tmp_info = []
                        # for i in input_[3].split('-'):
                        #     try:
                        #         tmp_info.append(int(i))
                        #     except TypeError:
                        #         print('error')
                        #         break
                        # else:
                        #     try:
                        #         self.buy(tmp_info, int(input_[2]))
                        #     except TypeError:
                        #         print('error')
                        tmp_info = {}
                        tmp_m = 0
                        for i in input_[2:]:
                            tmp_d = i.split('-')
                            try:
                                tmp_d = int(tmp_d[0]), int(tmp_d[1])
                                if tmp_d[1] < 0:
                                    print('error format')
                                    break
                            except (IndexError, TypeError):
                                continue
                            if tmp_d[0] not in Weapon.price:
                                continue
                            if tmp_d[1] == 0:
                                continue
                            tmp_info[tmp_d[0]] = tmp_d[1]
                            tmp_m += tmp_d[1] * Weapon.price[tmp_d[0]]
                            if tmp_m > self.res.cities[self.res.nowLocation].money:
                                print('money is not enough')
                                break
                        else:
                            self.buy(tmp_info)
                elif input_[0] == 'enlist':
                    if self.res.nowLocation in self.res.overed:
                        continue
                    if not self.check(input_):
                        continue
                    try:
                        money = int(input_[1])
                    except TypeError:
                        print('error')
                        continue
                    city = self.res.cities[self.res.nowLocation]
                    if money > city.money or city.population - money < 10000:
                        print('think carefully before action')
                        continue
                    city.population -= money
                    city.money -= money
                    city.restTroop += money
                    print(city.obj_info())
                    self.res.overed.add(self.res.nowLocation)
                elif input_[0] == 'govern':
                    if not self.check(input_):
                        continue
                    if input_[1] == '-s':
                        if self.res.nowLocation in self.res.overed:
                            continue
                        obj = self.res.get_person()
                        if not obj:
                            print("map's repository is empty")
                            continue
                        print(obj.obj_info())
                        obj.belong = self.res.myForce
                        self.res.cities[self.res.nowLocation].officer.add(obj)
                        self.res.overed.add(self.res.nowLocation)
                    elif input_[1] == '-d':
                        try:
                            money = int(input_[2])
                            person = int(input_[3]) - 1
                        except (IndexError, TypeError, ValueError):
                            print('error')
                            continue
                        city = self.res.cities[self.res.nowLocation]
                        if city.money < money:
                            print('poor man!!!')
                            continue
                        ps = list(city.officer)
                        if person < 0 or person >= len(ps):
                            print('error person')
                            continue
                        if ps[person].loyal + money//100 > Top.Loyal:
                            ps[person].loyal = Top.Loyal
                        else:
                            ps[person].loyal += money//100
                        print(ps[person].obj_info())
                    elif input_[1] == '-i':
                        city = self.res.cities[self.res.nowLocation]
                        print('\n'.join(city.show_person()))
                        print(f'money:{city.money}')
                        continue
                    elif input_[1] == '-e':
                        if self.res.nowLocation in self.res.overed:
                            continue
                        city = self.res.cities[self.res.nowLocation]
                        ps = list(city.prisoner)
                        try:
                            person = int(input_[2])
                            obj = ps[person]
                        except (IndexError, TypeError, ValueError):
                            print('error')
                            continue
                        if obj.belong not in self.res.failed and \
                                obj.loyal > Top.Loyal * 0.8 and obj.belong != self.res.myForce:
                            print("a loyal minister, failed")
                            continue
                        obj.belong = self.res.myForce
                        obj.loyal = Top.Loyal // 2
                        city.prisoner.remove(obj)
                        city.officer.add(obj)
                        self.res.overed.add(self.res.nowLocation)
                    elif input_[1] == '-a':
                        if self.res.nowLocation in self.res.overed:
                            continue
                        city = self.res.cities[self.res.nowLocation]
                        ps = list(city.officer)
                        try:
                            person = int(input_[2]) - 1
                            obj = ps[person]
                        except (IndexError, TypeError):
                            print('error')
                            continue
                        city.header = obj
                        self.res.overed.add(self.res.nowLocation)
                    elif input_[1] == '-b':
                        city = self.res.cities[self.res.nowLocation]
                        ps = list(city.officer)
                        if len(ps) == 1:
                            print('error')
                            continue
                        try:
                            person = int(input_[2]) - 1
                            obj = ps[person]
                        except (IndexError, TypeError):
                            print('error')
                            continue
                        if obj == city.header:
                            print('error')
                            continue
                        city.officer.remove(obj)
                        city.prisoner.add(obj)
                    elif input_[1] == '-r':
                        if self.res.nowLocation in self.res.overed:
                            continue
                        if len(input_) < 3:
                            continue
                        tmp_d = input_[2].split('-')
                        try:
                            tmp_d = int(tmp_d[0]), int(tmp_d[1])
                        except TypeError:
                            print('format error')
                            continue
                        if tmp_d not in self.res.cities \
                                or tmp_d in self.res.forces[self.res.myForce].cities:
                            continue
                        if self.res.forces[self.res.cities[tmp_d].header.belong].header in self.res.cities[tmp_d].officer:
                            print('failed')
                            continue
                        if self.res.cities[tmp_d].header.loyal <= Top.Wise * 0.5:
                            if self.res.cities[self.res.nowLocation].header.loyal > Top.Wise * 0.5:
                                self.res.search_force(tmp_d).cities.remove(tmp_d)
                                self.res.forces[self.res.myForce].add(tmp_d)
                                city = self.res.cities[tmp_d]
                                obj = city.header
                                obj.belong = self.res.myForce
                                obj.loyal -= 20
                                if obj.loyal < 0:
                                    obj.loyal = 0
                                city.officer.remove(obj)
                                city.prisoner = city.prisoner.union(city.officer)
                                self.res.overed.add(self.res.nowLocation)
                                print('succeed')
                                continue
                        print('failed')
                    elif input_[1] == '-o':
                        if self.res.nowLocation in self.res.overed:
                            continue
                        if len(input_) < 3:
                            continue
                        tmp_d = input_[2].split('-')
                        try:
                            tmp_d = int(tmp_d[0]), int(tmp_d[1])
                        except (TypeError, ValueError):
                            print('format error')
                            continue
                        if tmp_d not in self.res.cities \
                                or tmp_d in self.res.forces[self.res.myForce].cities:
                            continue

                        city = self.res.cities[tmp_d]
                        if city.header.wise < Top.Wise * 0.8 and \
                                self.res.cities[self.res.nowLocation].header.wise - 10 > city.header.wise and\
                                random.randint(0, 1) != 0:
                            city.make_outbreak()
                            self.res.overed.add(self.res.nowLocation)
                            print('succeed')
                            continue
                        self.res.overed.add(self.res.nowLocation)
                        print('failed')
                    elif input_[1] == '-m':
                        if self.res.nowLocation in self.res.overed:
                            continue
                        if len(input_) < 3:
                            continue
                        tmp_d = input_[2].split('-')
                        try:
                            tmp_d = int(tmp_d[0]), int(tmp_d[1])
                        except (TypeError, TypeError):
                            print('format error')
                            continue
                        if tmp_d not in self.res.cities \
                                or tmp_d in self.res.forces[self.res.myForce].cities:
                            continue

                        city = self.res.cities[tmp_d]
                        if city.header.wise < Top.Wise * 0.8 and \
                                self.res.cities[self.res.nowLocation].header.wise - 10 > city.header.wise and\
                                random.randint(0, 2) != 0:
                            city.money = int(city.money*0.6)
                            self.res.overed.add(self.res.nowLocation)
                            print('succeed')
                            continue
                        self.res.overed.add(self.res.nowLocation)
                        print('failed')
                elif input_[0] == 'alt':
                    if self.check(input_):
                        self.allocate(input_[1])
                elif input_[0] == 'transfer':
                    if not self.check(input_, 3):
                        continue
                    tmp_d = input_[1].split('-')
                    try:
                        tmp_d = int(tmp_d[0]), int(tmp_d[1])
                    except (ValueError, IndexError):
                        print('format error')
                        continue
                    if tmp_d not in self.res.forces[self.res.myForce].cities:
                        print('error area')
                        continue
                    if abs(tmp_d[0]-self.res.nowLocation[0]) + abs(tmp_d[1]-self.res.nowLocation[1]) != 1:
                        print('area error')
                        continue
                    city = self.res.cities[self.res.nowLocation]
                    # tgt = self.res.cities[tmp_d]
                    if tmp_d not in city.convey:
                        city.convey[tmp_d] = {}

                    if input_[2] == '-w':
                        tmp_data = {}
                        for k, v in city.weapons.items():
                            print(Weapon.ChineseName[k]+f" rest:{v}")
                            while 1:
                                nu = input()
                                try:
                                    if int(nu) > v or int(nu) < 0:
                                        print('error')
                                    else:
                                        if nu:
                                            tmp_data[k] = int(nu)
                                        break
                                except ValueError:
                                    break
                        if 'weapon' not in city.convey[tmp_d]:
                            city.convey[tmp_d]['weapon'] = {}
                        for k, v in tmp_data.items():
                            city.weapons[k] -= v
                            if city.weapons[k] <= 0:
                                del city.weapons[k]
                            if k in city.convey[tmp_d]['weapon']:
                                city.convey[tmp_d]['weapon'][k] += v
                            else:
                                city.convey[tmp_d]['weapon'][k] = v

                    elif input_[2] == '-p':
                        tmp_data = []
                        length = len(city.officer)
                        for i in city.officer:
                            length -= 1
                            if not length:
                                break
                            print(i.obj_info)
                            print('input "enter" to ignore')
                            if input() == '':
                                continue
                            tmp_data.append(i)
                            city.officer.remove(i)
                            if city.header == i:
                                for i_2 in city.officer:
                                    city.header = i_2
                                    break
                        if 'officer' not in city.convey[tmp_d]:
                            city.convey[tmp_d]['officer'] = []
                        city.convey[tmp_d]['officer'].extend(tmp_data)
                        # city.convey[tmp_d]['officer'] = set(city.convey[tmp_d]['officer'])

                    elif input_[2] == '-t':
                        print(f"rest troop: {city.restTroop}")
                        try:
                            nu = int(input())
                            if nu > city.restTroop:
                                nu = city.restTroop
                            if nu <= 0:
                                continue
                        except ValueError:
                            print('error')
                            continue
                        if 'troop' not in city.convey[tmp_d]:
                            city.convey[tmp_d]['troop'] = 0
                        city.convey[tmp_d]['troop'] += nu
                        city.restTroop -= nu

                    elif input_[2] == '-m':
                        print(f"rest money: {city.money}")
                        try:
                            nu = int(input())
                            if nu > city.money:
                                nu = city.money
                            if nu <= 0:
                                continue
                        except ValueError:
                            print('error')
                            continue
                        if 'money' not in city.convey[tmp_d]:
                            city.convey[tmp_d]['money'] = 0
                        city.convey[tmp_d]['money'] += nu
                        city.money -= nu
                elif input_[0] == 'atk':
                    # if not self.check(input_, 3):
                    #     continue
                    if len(input_) < 3:
                        continue
                    try:
                        tmp_d = input_[1].split('-')
                        tmp_d = int(tmp_d[0]), int(tmp_d[1])
                        if tmp_d not in self.res.cities or \
                                tmp_d in self.res.forces[self.res.myForce].cities:
                            raise IndexError
                    except (IndexError, TypeError, ValueError):
                        print('error')
                        continue
                    auto = 0
                    if '-auto' in input_:
                        if len(input_) < 4:
                            continue
                        input_.remove('-auto')
                        auto += 1

                    to_atk = []
                    if input_[2] in self.res.groups:
                        for i in self.res.groups:
                            if self.can_view(i) == 2 and abs(i[0]-tmp_d[0]) + abs(i[1]-tmp_d[1]) == 1:
                                if len(self.res.cities[i].officer) > 1 and i not in self.res.overed:
                                    to_atk.append(self.res.cities[i])
                    else:
                        for i in input_[2:]:
                            tmp_d1 = i.split('-')
                            try:
                                tmp_d1 = int(tmp_d1[0]), int(tmp_d1[1])
                            except (IndexError, TypeError, ValueError):
                                continue

                            if tmp_d1 in self.res.forces[self.res.myForce].cities and \
                                    abs(tmp_d1[0]-tmp_d[0]) + abs(tmp_d1[1]-tmp_d[1]) == 1:
                                if len(self.res.cities[tmp_d1].officer) > 1 and \
                                        tmp_d1 not in self.res.overed:
                                    to_atk.append(self.res.cities[tmp_d1])

                    if not to_atk:
                        print('empty group...')
                        continue

                    persons = []
                    joined = []
                    money = 0
                    it = 0
                    for i in to_atk:
                        tmp_data = list(i.officer)
                        tmp_data.remove(i.header)
                        persons.extend(tmp_data)
                        # print(persons)
                        money += i.money

                    length = len(persons)
                    if not length:
                        print('no person can join the wae')
                        continue
                    while 1:
                        os.system('cls')
                        print(persons[it].obj_info())
                        input_1 = input(
                            "join the war?\n'enter' for yes, 'end' to finish,'d' to next, 'a' to back\n")
                        if input_1 == 'end':
                            break
                        if input_1 == 'a':
                            it = (it - 1 + length) % length
                            continue
                        elif input_1 == 'd':
                            it = (it + 1 + length) % length
                            continue
                        if input_1 == '':
                            joined.append(persons.pop(it))
                            length -= 1
                            if not length:
                                break
                    if not joined:
                        print('error')
                        continue
                    while 1:
                        input_1 = input(f'rest money:{money}\ncost:')
                        try:
                            input_1 = int(input_1)
                            if input_1 < 0 or input_1 > money:
                                raise TypeError
                        except (TypeError, ValueError):
                            continue
                        break
                    per = input_1 / money
                    for i in to_atk:
                        i.money -= int(per * money)
                        if i.money < 0:
                            i.money = 0
                    self.res.attack['atk'] = joined
                    self.res.attack['money'] = input_1
                    self.res.attack['def'] = tmp_d
                    if not auto:
                        print('function error, ask developer')
                        self.floor = 4
                        return
                    else:
                        print(self.res.auto_atk())
                elif input_[0] == 'end':
                    self.res.update()
                    tmp_map = [['' for i in range(self.res.width)] for j in range(self.res.height)]
                    for k, v in self.res.forces.items():
                        for i in v.cities:
                            tmp_map[i[0]][i[1]] = k
                    self.console.set_map(tmp_map)
                    self.console.print_map()
                    print(f'round {self.res.turn}')
                elif input_[0] == 'map':
                    if len(input_) > 1:
                        if input_[1] != '-c':
                            continue

                        tmp_map = [['' for i in range(self.res.width)] for j in range(self.res.height)]
                        for k, v in self.res.forces.items():
                            for i in v.cities:
                                tmp_map[i[0]][i[1]] = k
                        self.console.set_map(tmp_map)
                    else:
                        tmp_map = [['' for i in range(self.res.width)] for j in range(self.res.height)]
                        for k, v in self.res.cities.items():
                            tmp_map[k[0]][k[1]] = v.name + '（' + v.header.belong[0] + "）"
                        self.console.set_map(tmp_map)
                    self.console.print_map()
                elif input_[0] == 'who':
                    print(f'force:{self.res.myForce}\theader:{self.res.forces[self.res.myForce].header.name}')

    def view_4(self):
        """
        暂时没写好
        :return:
        """
        self.floor = 3

    def hand_cmd(self, s0):
        self.__saved = False
        input_ = re.sub(' +', ' ', s0)
        if input_[-1] == ' ':
            input_ = input_[:-1]
        cmc = input_.split(' ')
        if not cmc:
            return False
        cmc[0] = cmc[0].lower()
        # if cmc[0] == 'exit':
        #     if not self.__saved and '-f' not in cmc:
        #         input_ = input("exit without save?(tip: input yes to save)\n")
        #         if input_ == 'yes':
        #             self.save()
        #     print('\nbye')
        #     exit()
        return cmc

    def save(self, f):
        if os.path.exists(SAVE_FILEPATH+'/'+f):
            if input("overwrite?(y/n)") == 'y':
                pass
                # with open(SAVE_FILEPATH+'/'+f, 'wb') as f:
                #     f.write(pickle.dumps(self.res))
                # print('saved')
            else:
                return
        else:
            with open(SAVE_FILEPATH+'/'+f, 'wb') as f:
                f.write(pickle.dumps(self.res))
        print('saved')

    def can_view(self, loc):
        """

        :param loc:
        :return: 2:all, 1:officer, 0:none, -1 error
        """
        # if self.__queue.full():
        #     del self.__qDict[self.__queue.get()]
        # if loc in self.__qDict:
        #     return loc
        if loc not in self.res.cities:
            return -1
        if loc in self.res.forces[self.res.myForce].cities:
            return 2
        # for i in self.res.cities[loc].persons:
        #     if i.belong == self.res.myForce:
        #         return 1
        # else:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for i in directions:
            y, x = i[0] + loc[0], i[1] + loc[1]
            if (y, x) in self.res.forces[self.res.myForce].cities:
                return 1
        return 0

    # def buy(self, types, money):
    #     if self.res.cities[self.res.nowLocation].money < money:
    #         print('you are so poor!!!-.-!!!')
    #         return
    #     if not types:
    #         print('error')
    #         return
    #     per = money / sum(types)
    #     cost = 0
    #     info = ''
    #     for i in types:
    #         goods = per * i // Weapon.price[i]
    #         cost += goods * Weapon.price[i]
    #         if i not in self.res.cities[self.res.nowLocation].weapons:
    #             self.res.cities[self.res.nowLocation].weapons[i] = goods
    #         else:
    #             self.res.cities[self.res.nowLocation].weapons[i] += goods
    #         info += str(goods) + ' ' + Weapon.ChineseName[i] + '\t'
    #     info += '\n were bought, cost $' + str(cost)
    #     self.res.cities[self.res.nowLocation].money -= cost
    #     print(info)

    def buy(self, g0):
        print('bought:')
        city = self.res.cities[self.res.nowLocation]
        for k, v in g0.items():
            if k not in city.weapons:
                city.weapons[k] = 0
            city.weapons[k] += v
            city.money -= Weapon.price[k] * v
            print(f'{Weapon.ChineseName[k]}:{v}', end=' ')
        print()

    def allocate(self, p0):
        if p0 == '-r':
            city = self.res.cities[self.res.nowLocation]
            for i in city.officer:
                need = Top.Troops - i.troop
                if city.restTroop > need:
                    city.restTroop -= need
                    i.troop += need
                else:
                    i.troop += city.restTroop
                    city.restTroop = 0

            for i in city.officer:
                if i.weaponType != 0:
                    if i.weaponType not in city.weapons:
                        continue
                    needs = i.troop - i.weapons
                    needs = needs if needs >= 0 else 0
                    if city.weapons[i.weaponType] > needs:
                        i.weapons += needs
                        city.weapons[i.weaponType] -= needs
                    else:
                        i.weapons += city.weapons[i.weaponType]
                        del city.weapons[i.weaponType]
            keys = list(city.weapons.keys())
            keys.sort(key=lambda a: city.weapons[a])
            for i in city.officer:
                if i.weaponType not in city.weapons and i.weaponType != Weapon.none:
                    continue
                if i.troop <= i.weapons:
                    continue

                needs = i.troop - i.weapons
                needs = needs if needs >= 0 else 0
                if city.weapons[i.weaponType] > needs:
                    i.weapons += needs
                    city.weapons[i.weaponType] -= needs
                else:
                    i.weapons += city.weapons[i.weaponType]
                    del city.weapons[i.weaponType]
        elif p0 == '-w':
            city = self.res.cities[self.res.nowLocation]
            persons = list(city.officer)
            it = 0
            length = len(persons)
            while 1:
                os.system('cls')
                print(persons[it].obj_info())
                tmp_info = 'weapon:'
                print(f"money:{city.money}\trest weapons:")
                for k, v in city.weapons.items():
                    tmp_info += str(k) + "(" + Weapon.ChineseName[k] + "):" + str(v) + '\t'
                print(tmp_info)
                input_ = input("which to equip?\tformat:type-amount\n'0' to finish,'d' to next, 'a' to back\n")
                if input_ == '0':
                    break
                if input_ == 'a':
                    it = (it - 1 + length) % length
                    continue
                elif input_ == 'd':
                    it = (it + 1 + length) % length
                    continue
                tmp_d = input_.split('-')
                try:
                    tmp_d = int(tmp_d[0]), int(tmp_d[1])
                    if tmp_d[0] not in Weapon.price or tmp_d[1] < 0 \
                            or tmp_d[1] > city.weapons[tmp_d[0]]:
                        raise TypeError
                except (TypeError, IndexError, ValueError):
                    print('format error')
                    continue
                if Top.Troops < tmp_d[1]:
                    tmp_d = tmp_d[0], Top.Troops
                # if tmp_d[1] > city.weapons[tmp_d[0]]:
                #     print("think carefully before your action")
                #     continue
                # if persons[it].weaponType != Weapon.none:
                city.weapons[persons[it].weaponType] += persons[it].weapons
                persons[it].weaponType = tmp_d[0]
                persons[it].weapons = tmp_d[1]
                city.weapons[tmp_d[0]] -= tmp_d[1]
                it = (it + 1 + length) % length
        elif p0 == '-p':
            city = self.res.cities[self.res.nowLocation]
            persons = list(city.officer)
            it = 0
            length = len(persons)
            while 1:
                os.system('cls')
                print(persons[it].obj_info())
                print(f"rest troop:{city.restTroop}")
                input_ = input("'0' to finish,'d' to next, 'a' to back")
                if input_ == '0':
                    break
                if input_ == 'a':
                    it = (it - 1 + length) % length
                    continue
                elif input_ == 'd':
                    it = (it + 1 + length) % length
                    continue
                try:
                    nu = int(input_)
                    if nu > city.restTroop:
                        print('troop is not enough')
                        continue
                    if nu > Top.Troops:
                        nu = Top.Troops
                    city.restTroop += persons[it].troop
                    city.restTroop -= nu
                    persons[it].troop = nu

                except (TypeError, IndexError, ValueError):
                    print('format error')
                    continue

                it = (it + 1 + length) % length

    def check(self, input_, n=2):
        if len(input_) < n:
            return False
        if self.can_view(self.res.nowLocation) == -1:
            print('area error')
            return False
        return True


if __name__ == "__main__":
    # MainWin().run()
    # Console.skim_files(SAVE_FILEPATH)
    # exObj = MainWin()
    # exObj.res.load_map(MAP_FILEPATH+'/'+'map.json')
    # exObj.floor = 3
    # exObj.res.myForce = '魏国'
    # exObj.console.set_bg(exObj.res.geoMap)
    # exObj.res.names['person'].append('典韦')
    # exObj.run()
    MainWin().run()
    pass

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :forTest.py
# @Time      :2021/11/8 14:13
# @Author    :russionbear
import sys
import os, re, random
from queue import Queue
import pickle, shutil
import ctypes
import xlrd
import colorama


# class Parameter:
#     def __init__(self):


class TOOL:
    p = {}

    @staticmethod
    def view_obj(obj):
        l0 = obj.__dict__
        # print(obj.__dict__)
        for i in l0:
            print('%s:%s' % (i, obj.__dict__[i]))

    @classmethod
    def get_param(cls, filepath):
        tables = xlrd.open_workbook(filepath)
        data = {}
        for i in tables.sheet_names():
            data[i] = {}
            table = tables.sheet_by_name(i)
            for j in range(1, table.nrows):
                tmp_index = table.cell_value(j, 0)
                data[i][tmp_index] = {}
                for k in range(1, table.ncols):
                    data[i][tmp_index][table.cell_value(0, k)] = table.cell_value(j, k)

        cls.p = data


TOOL.get_param(r'E:\Date_code\py_data\policyGame\army.xlsx')


class Cache:
    Max = 128

    def __init__(self):
        self.buffer = {}
        self.queue = Queue(Cache.Max)

    def has(self, id0):
        return id0 in self.buffer

    def put(self, n0):
        if n0.id in self.buffer:
            return
        self.buffer[n0.id] = n0
        self.queue.put(n0.id)
        if self.queue.full():
            tmp = self.queue.get()
            del self.buffer[tmp.id]
            self.save_obj(tmp)

    def get(self, id0):
        if id0 in self.buffer:
            return self.buffer[id0]
        return None

    def clear(self):
        while not self.queue.empty():
            tmp = self.queue.get()
            del self.buffer[tmp.id]
            self.save_obj(tmp)

    @staticmethod
    def save_obj(obj):
        path = obj.filePath + '/__obj__'
        with open(path, 'wb') as f:
            f.write(pickle.dumps(obj))


CACHE = Cache()
TRANSMIT_SPEED = 20

# person


class Root:
    low = 50
    mid = 150
    high = 300

    def __init__(self):
        self.pBless = 0
        self.pEvil = 0
        self.pWit = 0


class Ability:
    def __init__(self):
        self.hr = 0
        self.argue = 0
        self.military = 0
        self.protocol = 0
        self.finance = 0
        self.subtlety = 0


# class Relative:
#     clanElder = 0x1
#     parent = 0x2
#     child = 0x3
#     brother = 0x4
#     grandparent = 0x5
#     grandchild = 0x6
#     uncle = 0x7
#     nephew = 0x8
#
#     def __init__(self):
#         pass


class Person(Root):
    pSoldier = 0x1
    pTrader = 0x2
    pOfficial = 0x3
    pGang = 0x4
    pPolice = 0x5
    pClanElder = 0x6
    pTraveller = 0x7

    RName = 0x1
    RTRust = 0x2

    def __init__(self):
        super(Person, self).__init__()
        self.id = 0
        self.name = 0
        self.age = 0
        self.sex = 0

        self.health = 0
        self.hometown = 0

        # self.relatives = Relative()
        # self.friends = set()
        # self.branch = set()
        # self.header = 0
        #
        # self.ability = Ability()
        #
        # self.profession = 0
        # self.group = set()
        # self.prestige = {}
        # self.collections = []
        # self.properties = set()

        self.loc = 0
        self.belong = 0

    def set_header(self, p0):
        pass


class Crowd:

    def __init__(self):
        self.persons = 0
        self.blessing = 0
        self.evil = 0


# all blow are about person
#
#
# class Weather:
#     # wind
#     WNo = 0x1
#     WWave = 0x2
#     WFlag = 0x3
#     WJam = 0x4
#     WTree = 0x5
#     WHouse = 0x6
#
#     # temperature
#     TBone = 0x1
#     TIce = 0x2
#     TCold = 0x3
#     TCool = 0x4
#     TWarm = 0x5
#     THot = 0x6
#     Ts = [1, 2, 3, 4, 5, 6]
#
#     # dampness
#     MWater = 0x1
#     MDamp = 0x2
#     MWet = 0x3
#     MMid = 0x4
#     MLittle = 0x5
#     MDraught = 0x6
#
#     # sun
#     SDock = 0x1
#     SWind = 0x2
#     SShine = 0x3
#     SHot = 0x4
#     SSafe = 0x5
#
#     dust = 0x4
#
#     def __init__(self):
#         # 0, + 8
#         # 暂不控制
#         self.windDirection = 1
#         self.windStrength = 1
#         self.sunshine = 3
#         self.pollution = {}
#
#         self.temperature = 0
#         # plant,lake, river, sea, tem
#         self.moisture = 3
#
#     def add(self, n, strength):
#         pass
#
#     def update(self, type_, n):
#         pass
#
#     @staticmethod
#     def get_weather_name(self, obj):
#         pass
#
#
# class Geo:
#     # 地质
#     LQSoft = 0x1
#     LQClay = 0x2
#     LQSand = 0x3
#     LQHardI = 0x4
#     LQHardII = 0x5
#     LQHardIII = 0x6
#
#     LQs = [1, 2, 3, 4, 5, 6]
#
#     # 依海拔分类
#     LADeepSea = 0x1
#     LAShallow = 0x2
#     LAPlain = 0x3
#     LAHill = 0x4
#     LAMountain = 0x5
#     LAPlateau = 0x6
#     LAs = [(-21000, -300), (-299, 0), (1, 300), (301, 1200), (1201, 3000), (3001, 8848)]
#
#     # 地貌
#     LFSea = 0x1
#     LFRiver = 0x2
#     LFWetland = 0x3
#     LFLake = 0x4
#
#     LFLava = 0x5
#     LFVolcano = 0x6
#
#     LFGlacier = 0x7
#
#     # 坡度
#     LSPlain = 0x1
#     LSHill = 0x2
#     LSMountain = 0x3
#
#     # 低中高纬
#     LOLow = 0x1
#     LOMid = 0x2
#     LOHigh = 0x3
#
#     def __init__(self):
#         self.altitude = 0
#         self.slope = 0
#         self.lq = {
#             Geo.LQSoft: 100,
#             Geo.LQClay: 0,
#             Geo.LQSand: 0,
#             Geo.LQHardI: 0,
#             Geo.LQHardII: 0,
#             Geo.LQHardIII: 0,
#         }
#         # 暂在考虑中
#         self.lf = 0
#         self.location = 0
#         pass
#
#     def hand_lq(self, type_, n=80):
#         # for i, j in self.lq.items():
#         #     self.lq[i] /= (100 - n)
#         # self.lq[type_] += 80
#         pass
#
#     @staticmethod
#     def get_type_altitude(h):
#         for i1, i in enumerate(Geo.LAs):
#             if i[0] < h < i[1]:
#                 return i1+1
#         return 0
#
#
# class Resource:
#     PMoss = 0x1
#     PGrass = 0x2
#     PBush = 0x3
#     PTree = 0x4
#     PJungle = 0x5
#     Ps = [1, 2, 3, 4, 5]
#
#     AArctic = 0x2
#     ADessert = 0x1
#     APlain = 0x3
#     ATree = 0x4
#     AJungle = 0x5
#
#     def __init__(self):
#         self.water = 1
#         # self.plant = {
#         #     Resource.PMoss: 100,
#         #     Resource.PGrass: 0,
#         #     Resource.PBush: 0,
#         #     Resource.PTree: 0,
#         #     Resource.PJungle: 0
#         # }
#         self.plant = 0
#         # 特殊物品
#         self.drug = {}
#         # 同plant属性
#         self.animal = 1
#         self.ore = 1
#         self.gas = 1


# class Building:
#     BDwelling = 0x1
#     BProduce = 0x2
#     BProcess = 0x3
#     BCulture = 0x5
#     BMark = 0x6
#
#     BService = 0xb
#     BMilitary = 0xa
#
#     TFarm = 5
#     TPark = 10
#     TWork = 20
#     TRoom = 40
#     Ts = [0, TFarm, TPark, TWork, TRoom]
#
#     # person
#     # group
#
#     def __init__(self):
#         self.id = 0, 0
#         self.name = 0
#         self.exFuncs = set()
#
#         self.tName = 0
#         self.areas = 1
#         self.height = 10
#         self.capacity = 100
#
#         # __stockholder__ owned by people if is -1
#         # could be a person or a group
#         self.owner = {}
#
#         self.manager = 0
#         self.dwellers = set()
#         self.storages = set()
#         # self.groups = set()
#         # self.person = set()
#
#         # self.limitation = set()
#         # self.watchdog = 0
#
#     def set_limitation(self):
#         pass
#
#     @staticmethod
#     def find_building():
#         '''produce'''
#         BFarmland = 0x3
#         BTreeFarm = 0x4
#         BLogging = 0x6
#         BPasture = 0x1
#         BMine = 0x16
#         BRare = 0x2
#         BGas = 0x17
#
#         BFactory = 0x22
#
#         BBank = 0x33
#         BSchool = 0x34
#         BLaboratory = 0x35
#         BBar = 0x37
#
#         BTemple = 0x2
#         BChurch = 0x3
#         BStadium = 0x5
#         #
#         BCasino = 0x6
#
#         '''process'''
#         GBasic = 0x11
#         GLuxury = 0x12
#         GTool = 0x13
#         GWeapon = 0x14
#
#         '''server'''
#
#         TRoad = 0x1
#         TTrain = 0x2
#         THighway = 0x3
#         TShip = 0x4
#         TPlane = 0x5
#
#         NPost = 0x1
#         NPhone = 0x2
#         NEmail = 0x3
#         NNet = 0x4
#
#         '''army'''
#         BStronghold = 0x1
#         BStorage = 0x2


class Storage:
    # SPearls = 0x1
    # SMoney = 0x2
    #
    # SFood = 0x11
    # SWood = 0x12
    # SBest = 0x13
    # SMine = 0x14
    # SGas = 0x15
    # SRare = 0x16
    # SMedicine = 0x17
    #
    # SBasic = 0x18
    # SLuxury = 0x19
    # STool = 0x1a
    GMoney = 0x1
    GMax = 1000

    # SWeapon = 0x4

    def __init__(self):
        self.id = 0
        self.data = {}
        self.cost = {}
        # self.loc = 0

    def add(self, type_, nu, p0=0):
        rest = self.get_rest()
        if rest <= 0:
            return nu
        if type_ not in self.data:
            self.data[type_] = 0
            self.cost[type_] = 0
        self.data[type_] += rest if rest < nu else nu
        self.cost[type_] = TOOL.p['weapon'][type_]['stg_cost']
        return nu - self.data[type_]

    def get(self, type_):
        return self.data[type_]

    def decrease(self, type_, nu):
        self.data[type_] -= nu

        tmp = - self.data[type_]
        if tmp > 0:
            del self.data[type_]
            del self.cost[type_]
        return tmp

    def set(self, type_, nu, p0=0):
        self.data[type_] = nu
        self.cost[type_] = nu

    def empty(self):
        return bool(self.data)

    def get_rest(self):
        rst = 0
        for k, v in self.data.items():
            rst += self.cost[k] * v
        return self.GMax - rst

    def gain(self, s0):
        for k, v in s0.data.items():
            self.add(k, v)


class News:
    pass


# class Group:
#     gOfficial = 0x1
#     gTrader = 0x2
#     gTroop = 0x3
#     gGang = 0x4
#     gPolice = 0x5
#     gClan = 0x6
#     gTravel = 0x7
#
#     def __init__(self):
#         self.leader = 0
#         self.usage = 0
#         self.all = set()


class Unit:
    SWeak = 100
    SNormal = 150
    SStrong = 200
    SMaster = 300

    DFamine = 0x1
    DFlood = 0x2
    DFire = 0x3
    DCivilWar = 0x4
    DRevolution = 0x5
    DHeresy = 0x6
    DDefect = 0x7

    WPopulation = 0x11
    WPerson = 0x12
    WWeapon = 0x13
    WJoker = 0x14
    WKing = 0x15
    WEconomy = 0x16
    WDefence = 0x17

    Cap = 1000
    Ceiling = 1000

    def __init__(self):
        self.id = 0
        self.belong = 0
        self.data = set()
        self.loc = 0

        self.header = 0, 1
        self.persons = set()

        self.force = {}
        self.ships = 0

        self.spirit = 100
        self.top_spirit = self.SWeak

        self.storage = Storage()

        self.isGarrison = False
        self.isForSupply = False
        self.restA = 3

    def move(self, loc, rest):
        regU.move(self.id, self.loc, loc)
        self.restA = rest

    def has(self, id_):
        return id_ in self.data

    def add(self, id_):
        self.data.add(id_)
        regP.get(id_).belong = self.header

    def remove(self, id_):
        self.data.remove(id_)

    def set_loc(self, loc):
        self.loc = loc

    def tostring(self, mode=0):
        """

        :param mode:
        :return:
        """
        info = ''
        if mode == 0:
            info = 'id:'+str(self.id)+'\theader:'+regP.get(self.header).name+'\tbelong:'+str(self.belong)+'\n'
            info += 'loc:'+str(self.loc)
        return info

    #

    def set_for_supply(self):
        self.isForSupply = True

    def support(self, mount, type_, nu):
        pass

    def get_atk(self, type_=0):
        """

        :param type_: 0:short, 1:median, 2:long
        :return:
        """
        rlt = 0
        s0 = ['atk_short', 'atk_mid', 'atk_long']
        for t, sp in self.force:
            t_rlt = 0
            for k, v in sp:
                t_rlt += TOOL.p['weapon'][k][s0[type_]] * v
            t_rlt *= 1 + TOOL.p['weapon'][t][s0[type_]]
            rlt += t_rlt

        return rlt

    def hurt(self, type_, nu):
        s0 = ['def_short', 'def_mid', 'def_long']

        total = 0
        for t, sp in self.force.items():
            for k, v in sp:
                total += v
        per = nu / total

        should_d = set()
        for t, sp in self.force.items():
            mount_rate = 1 - TOOL.p['weapon'][t][s0[type_]]
            should_2 = set()
            for k, v in sp:
                needs = round(v * per * (1-TOOL.p['weapon'][k][s0[type_]]) * mount_rate)
                if needs >= v:
                    should_2.add(k)
                else:
                    self.force[t][k] -= needs
            for i in should_d:
                del self.force[t][i]
            if not self.force[t]:
                should_d.add(t)

        for i in should_d:
            del self.force[i]

        return bool(self.force)

    def gather(self):
        rlt = {}
        for t, sp in self.force.items():
            p0 = 0
            for k, v in sp.items():
                if k not in rlt:
                    rlt[k] = 0
                rlt[k] += v
                p0 += v
            rlt[t] = p0

        if 'none' in rlt:
            del rlt['none']

        for k, v in rlt.items():
            cs = TOOL.p['weapon'][k]['people']
            rlt[k] = (rlt[k]+cs-1)//cs
        return rlt

    def discipline(self):
        self.spirit += int(self.spirit * 0.1)
        if self.spirit > self.top_spirit:
            self.spirit = self.top_spirit

    def set_garrison(self, t0=True):
        if not self.restA:
            return False
        self.isGarrison = t0
        self.restA -= 1
        return True

    def get_duration(self):
        rlt = 0
        for t, sp in self.force.items():
            rlt = max(rlt, TOOL.p['weapon'][t]['duration'])
        return rlt

    def can_compact(self):
        return regM.get(self.loc[0], self.loc[1]).city == 0

    def compact_city(self):
        regC.get(regM.get(self.loc[0], self.loc[1]).city).compacted()


'''can be deleted'''
# class Industry(Root):
#     def __init__(self):
#         super(Industry, self).__init__()
#         self.population = 0
#         self.buildings = {}
#         self.capacity = 0
#         self.persons = 0
#         self.money = 0
#         self.retire_rate = 0.2
#         self.work_rate = 0.3
#
#     def pay(self, type_, nu):
#         pass
#
#     def delivery(self, type_, nu):
#         pass
#
#
# class Law:
#     def __init__(self):
#         self.lBirth = 0
#
#
# class IDwell(Industry):
#     def __init__(self):
#         super(IDwell, self).__init__()
#         self.iId = 0
#
#         self.newChild = 0
#         self.oldChild = 0
#         self.older = 0
#         self.vagrant = 0
#
#         self.birth = 0
#         self.death = 0
#         self.img = 9
#
#         self.bliss = 100
#
#         self.needs = Storage()
#
#     def pay(self, type_, nu):
#         pass
#
#     def update(self, population):
#         self.population = self.population - int(population*self.death) + \
#                           int(population*self.birth) - int(population * self.img)
#         if self.population < 0:
#             self.population = 0
#         self.older -= int(population*self.death)
#         if self.older < 0:
#             self.older = 0
#         self.vagrant += self.oldChild
#         self.vagrant -= int(population * self.img)
#         if self.vagrant < 0:
#             self.vagrant = 0
#         self.oldChild = self.newChild
#         self.newChild = int(population*self.birth)
#         self.needs.set(Storage.SBasic, population)
#
#
# class IOfficial(Industry):
#     # road, hospital, gym
#     server = 0x1
#     mark = 0x2
#     culture = 0x3
#
#     def __init__(self):
#         self.iId = 0
#         super(IOfficial, self).__init__()
#         self.header = 0
#         self.storage = Storage()
#
#     def pay(self, type_, nu):
#         pass
#
#     def delivery(self, type_, nu):
#         pass
#
#
# class ISchool(Industry):
#     CProduce = 0x1
#     CProcess = 0x2
#     CPolice = 0x3
#     CTrader = 0x4
#
#     def __init__(self):
#         super(ISchool, self).__init__()
#         self.iId = 0
#         self.leader = 0
#
#         class Course:
#             def __init__(self):
#                 self.nowSkill = 0
#                 self.skill = 0
#                 self.teachers = 0
#                 self.students = 0
#                 self.restP = 0
#
#                 self.salary = 0
#                 self.price = 0
#                 self.tax = 0
#                 self.workTime = 24
#                 self.weight = 20
#
#         self.cProduce = Course()
#         self.cProcess = Course()
#         self.cPolice = Course()
#         self.cTrader = Course()
#         self.cOfficial = Course()
#
#         self.index = [self.cProduce, self.CProcess, self.CPolice, self.cTrader, self.cOfficial]
#
#         self.needs = Storage()
#
#     def pay(self, type_, nu):
#         pass
#
#     def count_need(self, nu):
#         needs = self.capacity - self.population
#         if self.work_rate * self.population < needs:
#             needs = self.work_rate * self.population
#         if needs >= nu:
#             return nu
#         else:
#             needs
#
#     def enlist(self, nu):
#         for i in self.index:
#             i.students += int(i.weight*nu)
#             self.population += int(i.weight*nu)
#
#     def count_gain(self, nu):
#         needs = 0
#         # for i in self.index:
#         #     needs += self.
#
#
# class IProduce:
#     def __init__(self):
#         self.iId = 0
#         self.retire_rate = 0
#
#         class Good(Industry):
#             def __init__(self):
#                 super(Good, self).__init__()
#                 self.salary = 0
#                 self.price = 0
#                 self.tax = 0
#                 self.workTime = 24
#                 self.skill = 0
#                 self.stopped = False
#                 # self.resP = 0
#
#         self.food = Good()
#         self.wood = Good()
#         self.medicine = Good()
#         self.best = Good()
#         self.mine = Good()
#         self.water = Good()
#         self.gas = Good()
#         self.index = [self.food, self.wood, self.medicine, self.best, self.mine, self.water, self.gas]
#
#         self.goods = Storage()
#
#     def pay(self, type_, nu):
#         pass
#
#     def delivery(self, type_, nu):
#         pass
#
#     def update(self):
#         for i in self.index:
#             i.population -= int(i.population*self.retire_rate)
#             if not i.stopped:
#                 i.money -= i.population * i.salary
#                 if i.money <= 0:
#                     i.stopped = True
#
#
# class IProcess:
#     def __init__(self):
#         self.iId = 0
#         self.retire_rate = 0
#
#         class Good(Industry):
#             def __init__(self):
#                 super(Good, self).__init__()
#                 self.salary = 0
#                 self.price = 0
#                 self.tax = 0
#                 self.workTime = 24
#                 self.skill = 0
#                 self.resP = 0
#
#         self.basic = Good()
#         self.luxury = Good()
#         self.tool = Good()
#         self.weapon = Good()
#         self.index = [self.basic, self.luxury, self.tool, self.weapon]
#
#         self.goods = Storage()
#
#     def pay(self, type_, nu):
#         pass
#
#     def delivery(self, type_, nu):
#         pass
#
#     def update(self):
#         for i in self.index:
#             i.population -= int(i.population*self.retire_rate)
#             if not i.stopped:
#                 i.money -= i.population * i.salary
#                 if i.money <= 0:
#                     i.stopped = True
#
#
# class IPolice(Industry):
#     ONone = 0x1
#     OPolite = 0x2
#     ORude = 0x3
#     OFirm = 0x4
#     ONoLow = 0x5
#
#     def __init__(self):
#         super(IPolice, self).__init__()
#         self.iId = 0
#         self.leader = 0
#         self.order = 0
#
#         self.salary = 0
#         self.skill = 0
#         self.restP = 0
#
#         self.tScout = 0
#         self.tHandle = 0
#
#         self.groups = set()
#         # self.force = 0
#         # self.weapons = set()
#
#     def update(self):
#         self.money -= self.population * self.salary
#
#
# class IGang(Industry):
#
#     def __init__(self):
#         super(IGang, self).__init__()
#         self.iId = 0
#         self.topOne = 0
#         self.locGroups = set()
#         self.outGroups = set()
#         self.low = Law()
#         self.news = News()
#
#
# class ITrader(Industry):
#     def __init__(self):
#         super(ITrader, self).__init__()
#         self.iId = 0
#         self.leader = 0
#         self.consumer = {}
#         self.producer = {}
#
#     def register(self, id_, type_, nu):
#         if type_ not in self.producer:
#             self.producer[type_] = {}
#         self.producer[type_][id_] = nu
#         total = 0
#         for k, v in self.producer[type_].items():
#             total += v
#         self.producer[type_]["__total__"] = total
#
#     def buy(self, id_, type_, nu):
#         if type_ not in self.consumer:
#             self.consumer[type_] = {}
#         self.consumer[type_][id_] = nu
#         total = 0
#         for k, v in self.consumer[type_].items():
#             total += v
#         self.consumer[type_]["__total__"] = total
# 


class Block:
    GSea = 0x1
    GRock = 0x2
    GBeach = 0x3
    GMountain = 0x4
    GHill = 0x5
    GPlain = 0x4
    GLake = 0x6

    WRain = 0x1
    WWind = 0x2
    WCloud = 0x3
    WHot = 0x4
    WCold = 0x5
    WMist = 0x6

    REasy = 0x1
    RRoad = 0x2
    RHighway = 0x3
    RTrail = 0x4

    RWater = 0x1
    RWood = 0x2
    RAnimal = 0x3
    ROre = 0x4
    RGas = 0x5
    RDrug = 0x6

    def __init__(self):
        self.id = 0, 0
        self.name = '海口'
        self.belong = 0, 0

        self.geo = 0
        self.river = 0

        self.resource = set()
        self.weather = set()
        self.road = set()

        self.city = 0
        self.groups = set()
        self.storage = Storage()

    def update(self):
        pass

    def tostring(self, mode=0):
        """

        :param mode:
        :return:
        """
        info = ''
        if mode == 0:
            info = 'id:'+str(self.id)+'\tname:'+self.name+'\tbelong:'+str(self.belong)+'\n'
        return info
    # def __del__(self):
    #     print("it's del")


class City(Root):
    BProducer = 0x1
    BFactory = 0x2
    BShipyard = 0x3

    BAirport = 0x4
    BHarbor = 0x5

    BStronghold = 0x11

    BMarker = 0x21
    BBanker = 0x22

    BWell = 0x23
    BPublic = 0x24

    MaxFreeSpace = 20

    TopMoney = 1000000
    PerProduce = 100

    # DFamine = 0x1
    # DFlood = 0x2
    # DFire = 0x3
    # DCivilWar = 0x4
    # DRevolution = 0x5
    # DHeresy = 0x6
    # DDefect = 0x7
    #
    # WPopulation = 0x11
    # WPerson = 0x12
    # WWeapon = 0x13
    # WJoker = 0x14
    # WKing = 0x15
    # WEconomy = 0x16
    # WDefence = 0x17

    def __init__(self):
        super(City, self).__init__()
        self.id = 0
        self.loc = 0, 0
        self.freeSpace = 10
        self.ctrlForce = 0.1
        self.header = 0

        self.buildings = set()
        self.factories = 0
        self.specialities = set()
        self.dwellings = 0

        self.population = 0
        self.perTreasure = 0
        self.tax = 0.05
        self.growth = 0.03

        self.persons = set()

        self.produceQueue = {}
        self.storage = Storage()

        self.money = 0

        # self.law = Law()

        # self.iDwell = IDwell()
        # self.iOfficial = IOfficial()
        # self.iSchool = ISchool()
        # self.iProduce = IProduce()
        # self.iProcess = IProcess()
        # self.iTrader = ITrader()
        # self.iPolice = IPolice()
        # self.iGang = IGang()
        # self.index = [self.iDwell, self.iOfficial, self.iSchool, self.iProduce, self.iProcess, self.iTrader, self.iPolice, self.iGang]
        #
        # self.news = News()

    def can_produce(self):
        l0 = list(self.specialities)
        for k, v in TOOL.p['weapon'].items():
            if v['profrom'] in self.buildings and v['special'] == 1:
                l0.append(k)
        return l0

    def produce(self, type_, nu):
        class Product:
            def __init__(self):
                self.number = nu
                self.target = nu * TOOL.p['weapon'][type_]['cost']
                self.now = 0
                self.weight = 1

        self.produceQueue[type_] = Product()

    def set_priority(self, type_, p):
        self.produceQueue[type_].weight = p

    def near_sea(self):
        geo = regM.get(self.loc[0], self.loc[1]).geo
        if geo in [Block.GBeach, Block.GLake]:
            return True
        else:
            return False

    def build(self, type_, nu=1):
        if type_ == self.BFactory:
            self.factories += 1
        elif type_ == City.BWell:
            self.dwellings += nu
        else:
            self.buildings.add(type_)

    def remove_build(self, type_, nu=1):
        if type_ == self.BFactory:
            self.factories -= 1
            if self.factories <= 0:
                self.buildings.remove(type_)
        elif type_ == City.BWell:
            self.dwellings -= nu
            if self.dwellings <= 0:
                self.buildings.remove(type_)

    def can_expand(self):
        return self.MaxFreeSpace - self.freeSpace - len(self.buildings)

    def expand_block(self, v):
        self.freeSpace += v

    def send(self, obj):
        pass

    def transport(self, s0, tgt, user):
        can = regS.can_transport(self.loc, tgt)
        if can > 0:
            regS.set_tsp(s0, self.loc, tgt, user)

    def compacted(self):
        self.population = int(self.population * 0.9)
        self.ctrlForce = 0.1

    def placate(self):
        if self.money > self.population * self.perTreasure / 2:
            self.money -= self.population * self.perTreasure // 2
            self.ctrlForce += 0.1
            if self.ctrlForce > 1:
                self.ctrlForce = 1.0
            return True
        return False

    def update(self):
        # 控制度
        if self.ctrlForce < 0.2:
            self.growth = -abs(self.growth)
            self.tax = -abs(self.tax)
        elif self.ctrlForce < 0.6:
            self.growth = 0.01
            self.tax = 0.001
            if regP.get(self.header):
                if regP.get(self.header).pWit > Root.high:
                    self.ctrlForce += 0.1
                if regP.get(self.header).pWit > Root.mid:
                    self.ctrlForce += 0.05
        else:
            self.growth = 0.03
            self.tax = 0.01
            if regP.get(self.header):
                if regP.get(self.header).pWit > Root.high:
                    self.ctrlForce += 0.1
                if regP.get(self.header).pWit > Root.mid:
                    self.ctrlForce += 0.05
            if self.ctrlForce > 1:
                self.ctrlForce = 1.0

        # 经济
        th = 1

        if not self.produceQueue:
            th *= 1.2

        self.money += self.population * th * self.perTreasure // 100

        self.perTreasure = self.perTreasure*self.tax

        # 人口

        self.population = int(self.population * self.growth)
        if self.population > self.dwellings * 1000:
            self.population = self.dwellings * 1000

        # 人才
        if self.BPublic in self.buildings:
            vt = 20
        else:
            vt = 100
        if random.randint(1, vt) == 1:
            obj = Person()
            obj.pBless = self.pBless + random.randint(1, 20) - 10
            obj.pEvil = self.pBless + random.randint(1, 20) - 10
            obj.pWit = self.pBless + random.randint(1, 20) - 10

            self.persons.add(obj)
            if len(self.persons) > 30:
                self.persons.pop()

        # 生产
        ws = 0
        for k, v in self.produceQueue.items():
            ws += v.weight
        per = self.factories * self.perTreasure / ws
        should_d = set()
        for k, v in self.produceQueue.items():
            v.now += per * v.weight
            if v.now > v.target:
                should_d.add(k)
                self.storage.add(k, v.number)

    def unload(self, s0):
        self.storage.gain(s0)
        self.tax = - 0.05
        self.growth = - 0.05

    # person

    def add(self, cur):
        self.persons.add(cur)

    def remove(self, cur):
        self.persons.remove(cur)

    # def update(self):
    #     population = 0
    #     bless = evil = wit = 0
    #     for i in range(7):
    #         tmp = self.get_industry(i)
    #         population += tmp.population
    #         bless += tmp.pBless
    #         evil += tmp.pEvil
    #         wit += tmp.pWit
    #     self.pWit = wit/population
    #     self.pEvil = evil/population
    #     self.pBless = bless/population
    #     # people
    #     self.iDwell.update(population)
    #
    #     # school
    #     needs = self.iSchool.count_need(self.iDwell.oldChild)
    #     self.iDwell -= needs
    #     self.iSchool.enlist(needs)
    #
    # def get_industry(self, id_):
    #     return self.index[id_]


class Region:
    def __init__(self, filepath=0):
        self.id = 0, 0
        self.belong = 0, 0
        self.rId = 0
        self.name = 'haikou'
        self.data = set()
        # self.data = []
        # self.filePath = filepath

    def add(self, obj):
        if len(self.data) > 128:
            return False
        self.data.add(obj.id)
        self.data.belong = self.id
        return True

    def remove(self, id0):
        # if id0 in self.data:
        #     self.data.remove(id0)
        #     path = self.filePath+'/'+str(id0)
        #     if len(os.listdir(path)) > 1:
        #         f = self.get(id0)
        #         for i_1 in f.data:
        #             f.get(i_1).belong = self.id
        #             if f.id[1] == -1:
        #                 continue
        #             f.filePath = self.filePath + '/' + str(f.id)
        #             Region.open_room(f.filePath)
        #             Region.save_obj(f)
        #     shutil.rmtree(self.filePath+'/'+str(id0))
        #
        #     if id0 in self.buffer:
        #         del self.buffer[id0]
        #         self.buffer_set.remove(id0)
        #         self.buffer_queue.queue.clear()
        self.data.remove(id0)

    def has(self, id0):
        return id0 in self.data

    def list(self):
        return list(self.data)

    def tostring(self, mode=0):
        """

        :param mode:
        :return:
        """
        info = ''
        if mode == 0:
            info = 'id:' + str(self.id) + '\tname:' + self.name + '\tbelong:' + str(self.belong) + '\n'
        return info

    # def get(self, cur):
    #     if CACHE.has(cur):
    #         return CACHE.get(cur)
    #     elif cur[1] == -1:
    #         if not rgdBlock.has(cur[0]):
    #             return None
    #         return rgdBlock.get(cur=cur[0])
    #     else:
    #         path = self.filePath+'/'+str(cur)
    #         tmp = Region.load_obj(path)
    #
    #         CACHE.put(tmp)
    #
    #         return tmp

    # def modify_path(self, path):
    #     self.filePath = path
    #     for i_1 in self.data:
    #         if i_1[1] == -1:
    #             continue
    #         tmp = self.get(i_1)
    #         tmp.modify_path(path+'/'+str(tmp.id))

    # def add(self, cur, name, data=[]):
        # if cur[1] == -1:
        #     obj = rgdBlock.get(cur=cur[0])
        # else:
        #     path = self.filePath+'/'+str(cur)
        #     Region.open_room(path)
        #     obj = Region.load_obj(path)
        #     for i_1 in data:
        #         if self.has(i_1):
        #             self.get(i_1).belong = cur
        #             if i_1[1] != -1:
        #                 shutil.move(self.get(i_1).filePath, path+'/')
        #
        # obj.id = cur
        # obj.name = name
        # obj.belong = self.id
        #
        # self.data.add(cur)
        #
        # if cur[1] != -1:
        #     Region.save_obj(obj)
        #
        # CACHE.save_obj(self)

    # @staticmethod
    # def open_room(filepath):
    #     if os.path.exists(filepath):
    #         for f in os.listdir(filepath):
    #             try:
    #                 shutil.rmtree(filepath+'/'+f)
    #             except NotADirectoryError:
    #                 os.remove(filepath+'/'+f)
    #     else:
    #         os.mkdir(filepath)
    #
    # @staticmethod
    # def load_obj(filepath):
    #     '''
    #
    #     :param filepath:
    #     :return: Region
    #     '''
    #     path = filepath+'/__obj__'
    #     if os.path.exists(path):
    #         with open(path, 'rb') as f:
    #             return pickle.load(f)
    #     else:
    #         tmp = Region(filepath)
    #
    #         with open(path, 'wb') as f:
    #             f.write(pickle.dumps(tmp))
    #
    #         tmp.filePath = filepath
    #         return tmp


class Force(Region):
    def __init__(self, filepath):
        super(Force, self).__init__(filepath)
        self.regionRank = {
            0: '',
            1: '',
            2: '',
            3: '',
            4: '',
            5: '',
            6: '',
            7: '',
        }
        self.lows = set()
        self.header = 0

        self.master = 0
        self.minion = 0
        # self.RM = RegManager()


class TopRegion(Region):
    def __init__(self, filepath):
        super(TopRegion, self).__init__(filepath)


class RegeditNu:
    rankB = 0x0
    rank1 = 0x1
    rank2 = 0x2
    rank3 = 0x3
    rank4 = 0x4
    rank5 = 0x5
    rank6 = 0x6
    rank7 = 0x7
    rank8 = 0x8
    rank9 = 0x9

    unit = 0xa
    building = 0xb
    storage = 0xc
    person = 0xd
    city = 0xe

    def __init__(self, filename):
        self.restNu = {}
        self.nowNu = {}
        for i in range(1, 0xe):
            self.restNu[i] = set()
            self.nowNu[i] = 0

        self.restNu[-1] = set()
        self.nowNu[-1] = 0
        self.fileName = filename

    def get(self, type_):
        if len(self.restNu[type_]):
            return self.restNu[type_].pop()
        else:
            self.nowNu[type_] += 1
            return self.nowNu[type_]

    # 暂不考虑溢出处理
    def rec(self, type_, nu):
        self.restNu[type_].add(nu)
        # if len(self.restNu[type_]) > 128:

    @staticmethod
    def load_obj(filepath):
        path = filepath+'/__obj__'
        if os.path.exists(filepath):
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    return pickle.load(f)
            else:
                for i_1 in os.listdir(filepath):
                    shutil.rmtree(i_1)

                tmp = RegeditNu(filepath)
                with open(path, 'wb') as f:
                    f.write(pickle.dumps(tmp))
                return tmp
        else:
            os.mkdir(filepath)
            tmp = RegeditNu(filepath)
            with open(path, 'wb') as f:
                f.write(pickle.dumps(tmp))
            return tmp

    @staticmethod
    def save_obj(obj):
        with open(obj.filePath+'/__obj__', 'wb') as f:
            f.write(pickle.dumps(obj))


rgdNu = RegeditNu.load_obj('run/regeditNu')


class Regedit(Cache):
    def __init__(self, filepath):
        super(Regedit, self).__init__()
        self.filePath = filepath
        self.top = 0
        self.removed = 0
        self.remove_point = 0

    def resize(self, rows, cols):
        if os.path.exists(self.filePath):
            shutil.rmtree(self.filePath)
        os.mkdir(self.filePath)

    def get(self, cur):
        if cur in self.buffer:
            return self.buffer[cur]
        elif not self.has(cur):
            return
        else:
            with open(self.filePath+'/'+str(cur), 'rb') as f:
                tmp = pickle.load(f)

            self.put(tmp)

            return tmp

    def add(self, belong, name, type_):
        id_ = rgdNu.get(type_)
        obj = Region()
        obj.belong = belong
        obj.id = id_, type_
        obj.name = name
        path = self.filePath+'/'+str(obj.id)
        with open(path, 'wb') as f:
            f.write(pickle.dumps(obj))
        return obj

    def remove(self, ids):
        """

        :param ids: list
        :return:
        """
        for cur in ids:
            if self.has(cur):
                os.remove(self.filePath+'/'+str(cur))
                self.removed += 1
                rgdNu.rec(cur[1], cur[0])

        self.clear()
        self.remove_point = 0

    def has(self, cur):
        return os.path.exists(self.filePath+'/'+str(cur))

    def get_nu(self):
        if not self.removed:
            self.top += 1
            return self.top - 1
        else:
            for i in range(self.remove_point, self.top):
                if self.has(i):
                    self.removed -= 1
                    self.remove_point = i + 1
                    return i

    @classmethod
    def load_obj(cls, filepath):
        path = filepath + '/__obj__'
        if os.path.exists(filepath):
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    tmp = pickle.load(f)
            else:
                for i_1 in os.listdir(filepath):
                    os.remove(filepath+'/'+i_1)
                    # shutil.rmtree(i_1)

                tmp = cls(filepath)
                del tmp.queue

                with open(path, 'wb') as f:
                    f.write(pickle.dumps(tmp))
                # if os.path.exists(filepath+'/__removed__'):
                #     shutil.rmtree(filepath+'/__removed__')
                # os.mkdir(filepath+'/__removed__')

        else:
            os.mkdir(filepath)
            tmp = cls(filepath)
            del tmp.queue

            with open(path, 'wb') as f:
                f.write(pickle.dumps(tmp))
            # if os.path.exists(filepath+'/__removed__'):
            #     shutil.rmtree(filepath+'/__removed__')
            # os.mkdir(filepath+'/__removed__')

        tmp.queue = Queue(Cache.Max)
        return tmp

    @staticmethod
    def save_obj(obj):
        path = obj.filePath + '/' + str(obj.id)

        with open(path, 'wb') as f:
            f.write(pickle.dumps(obj))


class RgdBlock(Regedit):
    def __init__(self, size: tuple):
        super(RgdBlock, self).__init__('run/region0')

        self.height, self.width = size
        self.resize(size[0], size[1])

    def resize(self, rows, cols):
        super(RgdBlock, self).resize(rows, cols)
        new_length = rows * cols
        for i in range(new_length):
            with open(self.filePath+'/'+str((i, RegeditNu.rankB)), 'wb') as f:
                tmp = Block()
                tmp.id = i, RegeditNu.rankB
                tmp.belong = 1, 9
                f.write(pickle.dumps(tmp))
        self.height, self.width = rows, cols

    def get(self, cur=-1, **kwargs) -> Block:
        # print(len(self.buffer_set))
        if cur == -1:
            cur = kwargs['y'] * self.width + kwargs['x'], RegeditNu.rankB
        if cur[0] >= self.width * self.height:
            raise IndexError
        return super(RgdBlock, self).get(cur)

    def has(self, cur):
        return super(RgdBlock, self).has(cur)


class RegManager:
    def __init__(self):
        self.regeditS = {}
        for i in range(0, 10):
            path = 'run/region'+str(i) + '/__obj__'
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    self.regeditS[i] = pickle.load(f)
                    self.regeditS[i].queue = Queue(Cache.Max)
                    if self.regeditS[i].buffer:
                        print(self.regeditS[i])
                        raise OSError
            else:
                print('error path:', path)
                raise OSError

    def domain(self, rows, cols):
        # top region
        print(self.create((1, 10), RegeditNu.rank9, 'top', []))
        if rows * cols <= 128:
            return
        # county
        r = 0
        while r < rows:
            row1, row2 = r, random.randint(4, 9) + r
            if row2 >= rows:
                row2 = rows - 1
            r = row2 + 1

            c = 0
            while c < cols:
                col1, col2 = c, random.randint(4, 9) + c
                if col2 >= cols:
                    col2 = cols - 1
                c = col2 + 1

                data = []
                for i in range(row1, row2+1):
                    for j in range(col1, col2+1):
                        data.append((i * rows + j, RegeditNu.rankB))

                self.create((1, 9), RegeditNu.rank1, 'county', data)

        if rows * cols <= 10000:
            return

        # status
        r = 0
        while r < rows:
            row1, row2 = r, random.randint(50, 99) + r
            if row2 >= rows:
                row2 = rows - 1
            r = row2 + 1

            c = 0
            while c < cols:
                col1, col2 = c, random.randint(50, 99) + c
                if col2 >= cols:
                    col2 = cols - 1
                c = col2 + 1

                data = []

                for i in range(row1, row2+1):
                    id1 = self.regeditS[0].get(i, col1).belong[0]
                    id2 = self.regeditS[0].get(i, col2).belong[0]
                    for j in range(id1, id2+1):
                        data.append((RegeditNu.rank1, j))

                self.create((1, 9), RegeditNu.rank2, 'county', data)

        if rows * cols <= 1000000:
            return
        # province
        r = 0
        while r < rows:
            row1, row2 = r, random.randint(500, 999) + r
            if row2 >= rows:
                row2 = rows - 1
            r = row2 + 1

            c = 0
            while c < cols:
                col1, col2 = c, random.randint(500, 999) + c
                if col2 >= cols:
                    col2 = cols - 1
                c = col2 + 1

                data = []

                for i in range(row1, row2 + 1):
                    id1 = self.regeditS[0].get(i, col1).belong[0]
                    id2 = self.regeditS[0].get(i, col2).belong[0]
                    id1 = self.get(id1[0], id1[1]).belong[0]
                    id2 = self.get(id2[0], id2[1]).belong[0]
                    for j in range(id1, id2 + 1):
                        data.append((RegeditNu.rank1, j))

                self.create((1, 9), RegeditNu.rank3, 'county', data)

        if rows * cols // 10000 <= 10000:
            print('生命所不能承受的范围')
            raise OSError

    def map_with(self):
        return self.regeditS[0].width

    @staticmethod
    def resize(rows, cols):
        for i in range(0, 10):
            path = 'run/region'+str(i)
            if os.path.exists(path):
                shutil.rmtree(path)
            os.mkdir(path)

        regedit = {
            0: RgdBlock((rows, cols)),
        }
        for i in range(1, 10):
            regedit[i] = Regedit('run/region'+str(i))

        for i in range(0, 10):
            path = 'run/region'+str(i)
            del regedit[i].queue
            with open(path+'/__obj__', 'wb') as f:
                f.write(pickle.dumps(regedit[i]))

    def has(self, cur, type_):
        return self.regeditS[type_].has((cur, type_))

    def search(self, cur):
        end = []
        for i_1 in range(8, 0, -1):
            if self.has(cur, i_1):
                end.append((cur, i_1))
        return end

    def get(self, cur, type_) -> Region:
        return self.regeditS[type_].get((cur, type_))

    def create(self, belong, type_, name, data):
        """
        :param belong:
        :param type_: belong[1] > type_ > 0
        :param name:
        :param data: will not be checked
        :return:
        """
        if 0 < type_ < belong[1]:
            obj = self.regeditS[type_].add(belong, name, type_)
            for i in data:
                obj.add(self.get(i[0], i[1]))

            return True

        return False

    def remove(self, ids):
        rlt = {}
        for cur in ids:
            obj1 = self.get(cur[0], cur[1])
            obj2 = self.get(obj1.belong[0], obj1.belong[1])
            for i in obj1.data:
                obj2.add(self.get(i[0], i[1]))
            if cur[1] in rlt:
                rlt[cur[1]].add(cur)
            else:
                rlt[cur[1]] = set()
                rlt[cur[1]].add(cur)

        for k, v in rlt.items():
            self.regeditS[k].remove(v)

    def list(self, cur, mode=0):
        """

        :param cur: 0 < cur[1] < 9
        :param mode:1:name;2:nu;0:name+nu
        :return:
        """
        rlt = []
        if cur[1] <=0 or cur [1] >=9:
            print('path error')
            return []
        obj1 = self.get(cur[0], cur[1])
        if not obj1:
            print('has no such path')
            return
        for i in obj1.data:
            obj2 = self.get(i[0], i[1])
            if mode == 1:
                tmp = obj2.name
            else:
                tmp = chr(ord('a') + obj2.id[1]) + str(obj2.id[0])
                if mode == 3:
                    tmp = obj2.name + tmp
            rlt.append(tmp)

        return rlt

    def belong_to(self, cur, type_, obj=None):
        if not obj:
            obj = self.get(cur, type_)
        id_ = obj.id
        while id_[1] < RegeditNu.rank8:
            id_ = self.get(id_[0], id_[1]).belong

        return id_


class RegUnit(Regedit):
    def __init__(self):
        super(RegUnit, self).__init__('run/units')

    def add(self, belong, name, type_):
        return

    def create(self, p0, loc, belong=(RegeditNu.rank9, 0)):
        """

        :param p0:
        :param loc: should have spare space
        :param belong:
        :return:
        """
        obj = Unit(p0)
        obj.belong = belong
        obj.id = rgdNu.get(RegeditNu.unit), RegeditNu.unit
        path = self.filePath + '/' + str(obj.id)
        with open(path, 'wb') as f:
            f.write(pickle.dumps(obj))
        if belong != (RegeditNu.rank9, 0):
            obj2 = self.get(belong)
            obj2.add(obj)

        regM.get(loc, RegeditNu.rankB).gTroop.add(obj.id)

        return obj

    def move(self, id_, o_loc, n_loc):
        regM.get(o_loc, RegeditNu.rankB).gTroop.add(id_)
        regM.get(n_loc, RegeditNu.rankB).gTroop.remove(id_)
        self.get(id_).set_loc(n_loc)

    def remove(self, ids):
        for id_ in ids:
            loc = self.get(id_)
            regM.get(loc.loc, RegeditNu.rankB).gTroop.remove(id_)
            self.get(loc.belong).remove(id_)
        super(RegUnit, self).remove(ids)

    def chg_belong(self, id_, belong):
        obj = self.get(id_)
        obj.belong = belong
        self.get(obj.belong).remove(id_)
        self.get(belong).add(id_)


class RegCity(Regedit):
    def __init__(self):
        super(RegCity, self).__init__('run/cities')


class RegNews(Regedit):
    def __init__(self):
        super(RegNews, self).__init__('run/news')


class RegNewsMng:
    def __init__(self):
        self.regeditS = {}
        for i in range(0, 10):
            path = 'run/news/'+str(i) + '/__obj__'
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    self.regeditS[i] = pickle.load(f)
                    self.regeditS[i].queue = Queue(Cache.Max)
                    if self.regeditS[i].buffer:
                        print(self.regeditS[i])
                        raise OSError
            else:
                print('error path:', path)
                raise OSError


class RegStorage(Regedit):
    MaxConvey = 3
    MaxConveyCost = 3

    def __init__(self):
        super(RegStorage, self).__init__('run/storages')
        self.convey = {}

    def set_tsp(self, obj: Storage, cur, tgt, user, end=-2):
        if end == -2:
            end = self.can_transport(cur, tgt)
            if end == -1:
                raise IndexError
        now = 0
        if obj.id in self.convey:
            now = -self.convey[obj.id]['now']

        self.convey[cur] = {
            "now": now,
            "end": end,
            "target_id": tgt,
            "user": user,
            'obj': obj
        }

    def update(self):
        should_d = []
        for k, v in self.convey.items():
            v['now'] += self.MaxConvey
            if v['now'] > v['end']:
                ##### waiting: news ####
                regC.get(regM.get(v['target_id']).city).unload(v['obj'])

        for i in should_d:
            del self.convey[i]

    @staticmethod
    def can_transport(cur, tgt):
        flag1 = regM.belong_to(cur[0], cur[1])
        flag2 = regM.belong_to(tgt[0], tgt[1])
        flags = [flag1, flag2]
        w = regM.map_with()
        y1, x1 = flag1[0]//w, flag1[0] % w
        y2, x2 = flag2[0]//w, flag2[0] % w
        q = max(abs(y1-y2), abs(x1-x2))
        for i in range(1, q+1):
            x = int((x2-x1)/q*i)
            y = int((y2-y1)/q*i)
            if regM.belong_to(y * w + x, RegeditNu.rankB) not in flags:
                return -1
        return int(((y1-y2)**2+(x2-x1)**2)**0.5)


class RegPerson(Regedit):
    MaxConvey = 5

    def __init__(self):
        super(RegPerson, self).__init__('run/persons')
        self.convey = {}

    def has(self, cur):
        return cur in self.convey

    def set_tsp(self, cur, tgt, tgt_, user):
        loc = self.get(cur).loc
        w = regM.map_with()
        y1, x1 = loc[0]//w, loc[0] % w
        y2, x2 = tgt[0]//w, tgt[0] % w
        now = 0
        if cur in self.convey:
            now = -self.convey[cur]['now']

        self.convey[cur] = {
            "now": now,
            "end": abs(y1-y2) + abs(x1-x2),
            "target_loc": tgt,
            "target_obj": tgt_,
            "user": user
        }

    def update(self):
        should_d = []
        for k, v in self.convey.items():
            v['now'] += self.MaxConvey
            if v['now'] > v['end']:
                ##### waiting: news ####
                self.get(v[k]).loc = v['target_loc']
                if v['target_obj'][1] == RegeditNu.city:
                    regC.get(v['target_obj']).add(k)
                elif v['target_obj'][1] == RegeditNu.unit:
                    regU.get(v['target_obj']).add(k)

        for i in should_d:
            del self.convey[i]

    def make_person(self, bless, evil, wit, ranges) -> Person:
        pass

    @classmethod
    def load_obj(cls, filepath):
        return super(RegPerson, cls).load_obj(filepath)


# RegManager.resize(10, 10)
regM = RegManager()
regM.domain(10, 10)
regG = Regedit.load_obj('run/groups')
regN = Regedit.load_obj('run/news')
regP = RegPerson.load_obj('run/persons')
regU = RegUnit.load_obj('run/units')
regC = RegCity.load_obj('run/cities')
regS = RegStorage.load_obj('run/transports')

# class RegeditForce(Regedit):
#     def __init__(self):
#         super(RegeditForce, self).__init__('run/forces/')


class RgdBuilding(Regedit):
    pass


class RgdGroup(Regedit):
    pass


class RgdPerson(Regedit):
    pass


class GameCore:
    def __init__(self):
        self.blocks = RgdBlock((10, 10))


class MapBuilder:
    def __init__(self, size):
        # self.size = size
        # self.tmpMap = self.make_map_random0bit(size)
        # self.tmpMap = self.handle_map_scattered(self.tmpMap)
        # self.print(self.tmpMap)
        #
        # map_1 = self.fill_map(self.tmpMap)
        # self.print(map_1)
        # self.print(self.handle_map_scattered(map_1))
        # 
        # map_2 = self.fill_map(self.tmpMap, True)
        # self.print(map_2)
        # self.print(self.handle_map_scattered(map_2))
        # self.print(self.make_map_altitude(size))
        self.print(self.make_map_altitude0ladder((5, 5), [1, 1, 1, 1, 1, 1]), site=6)
        pass

    @staticmethod
    def make_map_random(size, vq=500):
        map_ = [[0 for i in range(size[1])] for j in range(size[0])]
        for i in range(size[0]):
            for j in range(size[1]):
                if random.randint(1, 1000) <= vq:
                    map_[i][j] = 1

        return map_

    @staticmethod
    def make_map_random0bit(size, vq=400, b1=109, b2=1000, rq=800):
        map_ = [[0 for i in range(size[1])] for j in range(size[0])]
        for i in range(size[0]):
            for j in range(size[1]):
                r1 = r2 = 1001
                while r1 > 1000:
                    r1 = random.randint(1, 1000+rq)
                while r2 > 1000:
                    r2 = random.randint(1, 1000+rq)
                r1 = r1 < vq
                r2 = r2 < vq
                r3 = random.randint(1, 1000)
                if r3 > b2:
                    r1 = not r1
                elif r3 > b1:
                    r1 = r1 or r2
                else:
                    r1 = r1 and r2
                if r1:
                    map_[i][j] = 1
                else:
                    map_[i][j] = 0

        return map_

    @staticmethod
    def make_map_altitude0queue(size):
        map_ = [[None for i1 in range(size[0])] for j in range(size[1])]
        rlt = set()
        drct = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        queue = set()
        queue.add((0, 0))

        while queue:
            tem_q = set()
            rlt = rlt.union(queue)

            for i in queue:
                if random.randint(1, 5) >= 3:
                    map_[i[0]][i[1]] = 1
                else:
                    map_[i[0]][i[1]] = 0

                for j in drct:
                    y, x = i[0] + j[0], i[1] + j[1]
                    if x < 0 or y < 0 or y >= size[0] or x >= size[1]:
                        continue
                    if map_[y][x] == None and (y, x) not in rlt:
                        tem_q.add((y, x))

            queue.clear()
            queue = queue.union(tem_q)
            tem_q.clear()

        return map_

    @staticmethod
    def make_map_altitude0ladder(size, ladder):
        sum_ = sum(ladder)
        n = size[0] * size[1] / sum_

        for i in range(len(ladder)):
            ladder[i] = int(n*ladder[i])

        for i in enumerate(ladder):
            if i[1] == 0:
                ladder[i[0]] = -1

        sum_ = 0
        for i in range(1, len(ladder)+1):
            if ladder[-i] == -1:
                continue
            ladder[-i] += sum_
            sum_ = ladder[-i]

        if sum_ < size[0] * size[1]:
            ladder[0] += size[0] * size[1] - sum_

        queue = []
        map_ = []
        rlt = set()
        for i in range(size[0]):
            tmp = []
            for j in range(size[1]):
                queue.append((i, j))
                tmp.append(0)
            map_.append(tmp)

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        prior = []
        for i1, i in enumerate(ladder):
            if i == -1:
                continue
            tem_l = []
            for j in range(i):
                if prior:
                    cur = random.randint(0, len(prior)-1)
                    prior.pop(cur)
                else:
                    cur = random.randint(0, len(queue)-1)
                # map_[queue[cur][0]][queue[cur][1]] = i1
                # map_[queue[cur][0]][queue[cur][1]] =\
                    # random.randint(Geo.LAs[i1][0], Geo.LAs[i1][1])
                tem_l.append(queue[cur])
                queue.pop(cur)
            MapBuilder.print(map_, site=6)

            if i1 != 0:
                prior.clear()
                rlt = rlt.union(set(queue))

                for k1 in rlt:
                    for k2 in directions:
                        y, x = k2[0] + k1[0], k2[1] + k1[1]
                        if y < 0 or x < 0 or y >= size[0] or x >= size[1] or\
                                (y, x) in rlt:
                            continue
                        prior.append((y, x))
                # print('border', sorted(prior))
                prior = list(set(tem_l).difference(set(prior)))
                # print('no_border', (sorted(prior)))

            rlt.union(queue)

            queue.clear()
            queue.extend(tem_l)
            tem_l.clear()

        return map_

    @staticmethod
    def fill_map(pre_map, center=False, compare=None):
        if not compare:
            compare = lambda a: a == 1

        map_ = [i[:] for i in pre_map]
        print(len(map_))

        rlt = set()
        size = len(map_), len(map_[0])
        drct = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        queue = set()
        for i in range(size[0]):
            if not compare(map_[i][0]):
                queue.add((i, 0))

            if not compare(map_[i][-1]):
                queue.add((i, size[1] - 1))

        for i in range(1, size[1]-1):
            if not compare(map_[0][i]):
                queue.add((0, i))

            if not compare(map_[-1][i]):
                queue.add((size[0]-1, i))

        while queue:
            tem_q = set()
            rlt = rlt.union(queue)

            for i in queue:
                for j in drct:
                    y, x = i[0] + j[0], i[1] + j[1]
                    if x < 0 or y < 0 or y >= size[0] or x >= size[1]:
                        continue
                    if not compare(map_[y][x]) and (y, x) not in rlt:
                        tem_q.add((y, x))

            queue.clear()
            queue = queue.union(tem_q)
            tem_q.clear()

        if center:
            for i in range(size[0]):
                for j in range(size[1]):
                    if (i, j) not in rlt:
                        map_[i][j] = 1
        else:
            for i in rlt:
                map_[i[0]][i[1]] = 1
        print(len(map_))
        return map_

    @staticmethod
    def handle_map_scattered(pre_map, compare=None):
        if not compare:
            compare = lambda a: a == 1
        size = len(pre_map), len(pre_map[0])
        map_ = [j[:] for j in pre_map]
        directions = [(0, 1), (-1, 0), (1, 0), (0, -1)]
        for i in range(0, size[0]):
            for j in range(0, size[1]):
                can = 0
                if not compare(map_[i][j]):
                    continue
                for k in directions:
                    y, x = i + k[0], j + k[1]
                    if y < 0 or x < 0 or y >= size[0] or x >= size[1]:
                        continue
                    if compare(map_[y][x]):
                        can += 1
                if can <= 1:
                    map_[i][j] = 0

        return map_

    @staticmethod
    def make_snack(pre_map):
        size = len(pre_map), len(pre_map[0])
        # map_ = [i[:] for i in pre_map]
        map_ = [[0 for i in range(size[1])] for j in range(size[0])]

    @staticmethod
    def not_map(map_):
        rlt = []
        for i in map_:
            tmp = []
            for j in i:
                if j == 0:
                    c = 1
                else:
                    c = 0
                tmp.append(c)
            rlt.append(tmp)
        return rlt

    @staticmethod
    def print(map_, contrary=False, site=3):
        if contrary:
            for i in map_:
                for j in i:
                    if j == 0:
                        print(("%-"+str(site)+"d") % j, end='')
                    else:
                        print(("%-"+str(site)+"c") % ' ', end='')
                print()
        else:
            for i in map_:
                for j in i:
                    if j != 0:
                        print(("%-"+str(site)+"d") % j, end='')
                    else:
                        print(("%-"+str(site)+"c") % ' ', end='')
                print()
        print()


class MapInit:
    def __init__(self, size, date=None, dimension: tuple=None):
        map_ = RgdBlock(size)
        # self.dimension(map_, (-89, 89))
        # self.altitude0slope(map_)
        # self.landform(map_)

        self.print(map_, lambda a: a.weather.temperature)

        # self.print(map_, lambda a: a.geo.)

    # @staticmethod
    # def land0quality(map_: RgdBlock):
    #     vt = len(Geo.LQs) - 1
    #     for i in range(map_.width*map_.height):
    #         for j in Geo.LQs:
    #             map_.get(cur=i).geo.lq[j] = 0
    #         map_.get(cur=i).geo.lq[random.randint(0, vt)] = 100
    #
    # @staticmethod
    # def altitude0slope(map_: RgdBlock, sea=250, shadow=300, plain=700, mountain=950, plateau=1000):
    #     # sea=250, shadow=50, plain=400, mountain=250, plateau=50
    #     # mark = MapBuilder.make_mpa_altitude((map_.height, map_.width))
    #     for i in range(map_.height):
    #         for j in range(map_.width):
    #             n = random.randint(1, 1000)
    #             if n <= sea:
    #                 map_.get(i, j).geo.altitude = -random.randint(1, 20)
    #             elif n <= shadow:
    #                 map_.get(i, j).geo.altitude = -random.randint(21, 8848)
    #             elif n <= plain:
    #                 map_.get(i, j).geo.altitude = random.randint(0, 300)
    #             elif n <= mountain:
    #                 map_.get(i, j).geo.altitude = random.randint(301, 2000)
    #             elif n <= plateau:
    #                 map_.get(i, j).geo.altitude = random.randint(2001, 8848)
    #                 # 更新土质
    #                 map_.get(i, j).geo.hand_lq(80)
    #
    #             slope = random.randint(1, 10)
    #             if slope < 4:
    #                 map_.get(i, j).geo.slope = slope
    #             else:
    #                 high = map_.get(i, j).geo.altitude
    #                 if abs(high) <= 300:
    #                     map_.get(i, j).geo.slope = Geo.LSPlain
    #                 elif abs(high) <= 3000:
    #                     map_.get(i, j).geo.slope = Geo.LSHill
    #                 else:
    #                     map_.get(i, j).geo.slope = Geo.LSMountain
    #
    #     fill_map = MapBuilder.fill_map(MapInit.to_bit(map_, compare=lambda a: a.geo.altitude >= 0))
    #
    #     # 盆地 海边？
    #     for i in range(map_.height):
    #         for j in range(map_.width):
    #             if fill_map[i][j] == 0 and map_.get(i, j).geo.altitude < 300:
    #                 map_.get(i, j).geo.altitude = -random.randint(1, 300)
    #
    #
    #     # plain -300, 300
    #     # hill 301, 3000
    #     for i in range(map_.height):
    #         for j in range(map_.width):
    #             slope = random.randint(1, 10)
    #             if slope < 4:
    #                 map_.get(i, j).geo.slope = slope
    #             else:
    #                 high = map_.get(i, j).geo.altitude
    #                 if abs(high) <= 300:
    #                     map_.get(i, j).geo.slope = Geo.LSPlain
    #                 elif abs(high) <= 3000:
    #                     map_.get(i, j).geo.slope = Geo.LSHill
    #                 else:
    #                     map_.get(i, j).geo.slope = Geo.LSMountain

    # @staticmethod
    # def landform(map_: RgdBlock, river=100, lake=200, wetland=250, volcano=300):
    #     directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    #
    #     fill_map = MapBuilder.fill_map(MapInit.to_bit(map_, compare=lambda a: a.geo.altitude >= 0), True)
    #     MapBuilder.print(fill_map)
    #
    #     # count hollow
    #     hollow_0 = set()
    #     hollow_1 = set()
    #     hollow_2 = set()
    #     hollows = []
    #     for i in range(map_.height):
    #         for j in range(map_.width):
    #             if fill_map[i][j] == 0:
    #                 continue
    #             should = []
    #             for k in directions:
    #                 x, y = k[0] + j, k[1] + i
    #                 if x < 0 or y < 0 or x >= map_.width or y >= map_.height:
    #                     continue
    #                 elif fill_map[y][x] == 0:
    #                     # should = -1
    #                     break
    #                 elif map_.get(i, j).geo.altitude >= map_.get(y, x).geo.altitude:
    #                     should.append((y, x))
    #             else:
    #                 if not should:
    #                     hollow_0.add((i, j))
    #                 elif len(should) == 1:
    #                     hfg = ((i, j), should[0])
    #                     hollow_1.add(hfg)
    #                 elif len(should) == 2:
    #                     if should[0][0] + should[1][0] == y * 2 and\
    #                             should[0][1] + should[1][1] == x * 2:
    #                         continue
    #                     hfg = ((i, j), should[0], should[1])
    #                     hollow_2.add(hfg)
    #
    #     for i in hollow_0:
    #         tmp = set()
    #         tmp.add(i)
    #         hollows.append(tmp)
    #
    #     while 1:
    #         can_out = True
    #         delete = []
    #         for i in hollow_1:
    #             for j in range(len(hollows)):
    #                 if i[1] in hollows[j]:
    #                     hollows[j].add(i[0])
    #                     delete.append(i)
    #                     can_out = False
    #         for i in delete:
    #             hollow_1.remove(i)
    #         delete.clear()
    #
    #         for i in hollow_2:
    #             for j in range(len(hollows)):
    #                 if i[1] in hollows[j] and i[2] in hollows[j]:
    #                     hollows[j].add(i[0])
    #                     can_out = False
    #                     delete.append(i)
    #         for i in delete:
    #             hollow_2.remove(i)
    #         delete.clear()
    #
    #         if can_out:
    #             break
    #
    #     # hollows.sort(key=lambda a: len(a))
    #     # river, lake, wetland
    #     for i in hollows:
    #         cur = random.randint(1, 1000)
    #         if cur <= river:
    #             for j in i:
    #                 map_.get(j[0], j[1]).geo.lf = Geo.LFRiver
    #         elif cur <= lake:
    #             for j in i:
    #                 map_.get(j[0], j[1]).geo.lf = Geo.LFLake
    #         elif cur <= wetland:
    #             for j in i:
    #                 map_.get(j[0], j[1]).geo.lf = Geo.LFWetland
    #
    #     # ###### check ###### #
    #     # count = 0
    #     # rlt = set()
    #     # for i in hollows:
    #     #     count += len(i)
    #     #     for j in i:
    #     #         rlt.add(j)
    #     # print(count, len(rlt))
    #     # print(hollows)
    #     # return
    #
    #     del hollows, hollow_1, hollow_2, hollow_0
    #     # 火山
    #     hill_0 = set()
    #     hill_1 = set()
    #     hill_2 = set()
    #     hills = []
    #     for i in range(map_.height):
    #         for j in range(map_.width):
    #             if fill_map[i][j] == 0:
    #                 continue
    #             should = []
    #             for k in directions:
    #                 x, y = k[0] + j, k[1] + i
    #                 if x < 0 or y < 0 or x >= map_.width or y >= map_.height:
    #                     continue
    #                 elif fill_map[y][x] == 0:
    #                     continue
    #                 elif map_.get(i, j).geo.altitude < map_.get(y, x).geo.altitude:
    #                     should.append((y, x))
    #             else:
    #                 if not should:
    #                     hill_0.add((i, j))
    #                 elif len(should) == 1:
    #                     hfg = ((i, j), should[0])
    #                     hill_1.add(hfg)
    #                 elif len(should) == 2:
    #                     if should[0][0] + should[1][0] == y * 2 and\
    #                             should[0][1] + should[1][1] == x * 2:
    #                         continue
    #                     hfg = ((i, j), should[0], should[1])
    #                     hill_2.add(hfg)
    #
    #     for i in hill_0:
    #         tmp = set()
    #         tmp.add(i)
    #         hills.append(tmp)
    #
    #     while 1:
    #         can_out = True
    #         delete = []
    #         for i in hill_1:
    #             for j in range(len(hills)):
    #                 if i[1] in hills[j]:
    #                     hills[j].add(i[0])
    #                     delete.append(i)
    #                     can_out = False
    #         for i in delete:
    #             hill_1.remove(i)
    #         delete.clear()
    #
    #         for i in hill_2:
    #             for j in range(len(hills)):
    #                 if i[1] in hills[j] and i[2] in hills[j]:
    #                     hills[j].add(i[0])
    #                     can_out = False
    #                     delete.append(i)
    #         for i in delete:
    #             hill_2.remove(i)
    #         delete.clear()
    #
    #         if can_out:
    #             break
    #
    #     for i in hills:
    #         cur = random.randint(0, 1000)
    #         if cur <= volcano - wetland:
    #             tmp = list(i)
    #             tmp.sort(key=lambda a: map_.get(a[0], a[1]).geo.altitude)
    #             map_.get(tmp[-1][0], tmp[-1][1]).geo.lf = Geo.LFVolcano
    #             for j in tmp[:-1]:
    #                 map_.get(j[0], j[1]).geo.lf = Geo.LFLava
    #
    #     # ###### check ###### #
    #     # count = 0
    #     # rlt = set()
    #     # for i in hills:
    #     #     if len(i) > 2:
    #     #         count += len(i)
    #     #     for j in i:
    #     #         rlt.add(j)
    #     # print(count, len(rlt))
    #     # print(hills)
    #     # return
    #
    #     # 纬度
    #     ''''''

    # @staticmethod
    # def dimension(map_: RgdBlock, dimension=(0, 0)):
    #     # wind, sun, steam,
    #     # 30, 60, 90
    #     reference = [-90, -60, -30, 30, 60, 90]
    #     sections = []
    #     ladders = []
    #     for i in enumerate(reference):
    #         if dimension[0] < i[1]:
    #             sections.append((dimension[0], i[1]))
    #             for j in range(i[0]+1, len(reference)):
    #                 if reference[j] >= dimension[1]:
    #                     sections.append((reference[j-1], dimension[1]))
    #                     break
    #                 else:
    #                     sections.append((reference[j-1], reference[j]))
    #             break
    #     if sections[-1][0] > sections[-1][1]:
    #         tmp = (sections[-2][0], sections[-1][1])
    #         sections.pop(-1)
    #         sections.pop(-1)
    #         sections.append(tmp)
    #     for i in sections:
    #         ladders.append(i[1]-i[0])
    #     if len(sections) == 1 and sections[0][0] == sections[0][1]:
    #         ladders = [(0, map_.height)]
    #     else:
    #         n = map_.height/sum(ladders)
    #         max_c = 0
    #         for i in enumerate(ladders):
    #             ladders[i[0]] = round(ladders[i[0]] * n)
    #             if ladders[i[0]] > ladders[max_c]:
    #                 max_c = i[0]
    #         ladders[max_c] += map_.height - sum(ladders)
    #         max_c = 0
    #         for i in enumerate(ladders):
    #             ladders[i[0]] = max_c, i[1] + max_c
    #             max_c += i[1]
    #
    #     for i, j in zip(ladders, sections):
    #         max_c = max(abs(j[0]), abs(j[1]))
    #         print(max_c)
    #         if max_c > 60:
    #             interval = 0, 1, Geo.LOHigh, 0, 1
    #         elif max_c > 30:
    #             interval = 1, 3, Geo.LOMid, 2, 3
    #         else:
    #             interval = 4, 5, Geo.LOLow, 3, 4
    #         for k in range(i[0], i[1]):
    #             for p in range(map_.width):
    #                 map_.get(k, p).weather.temperature =\
    #                     Weather.Ts[random.randint(interval[0], interval[1])]
    #                 map_.get(k, p).geo.location = interval[2]
    #                 map_.get(k, p).resource.plant =\
    #                     Resource.Ps[random.randint(interval[3], interval[4])]
    #                 map_.get(k, p).resource.animal =\
    #                     Resource.Ps[random.randint(interval[3], interval[4])]

        #     print(i, j)
        # print(ladders)
        # print(sections)

    @staticmethod
    def resource0weather(map_: RgdBlock, ore=200, gas=200):
        for i in range(map_.width * map_.height):
            cur1 = random.randint(1, 1000)
            if cur1 > ore:
                cur1 = 0
            else:
                cur1 %= 6
            map_.get(cur=i).resource.ore = cur1
            cur1 = random.randint(1, 1000)
            if cur1 > gas:
                cur1 = 0
            else:
                cur1 %= 6
            map_.get(cur=i).resource.gas = cur1

    @staticmethod
    def people(map_: RgdBlock, low=50, mid=500, high=200, top=250):
        #
        pass

    @staticmethod
    def mark():
        pass

    @staticmethod
    def to_bit(pre_map: RgdBlock, compare=None):
        if not compare:
            pass
        map_ = []
        for i in range(pre_map.height):
            tmp_map = []
            for j in range(pre_map.width):
                tmp_map.append(int(compare(pre_map.get(i, j))))
            map_.append(tmp_map)
        return map_

    @staticmethod
    def print(map_: RgdBlock, func):
        if not func:
            func = lambda a: a
        for i in range(map_.height):
            for j in range(map_.width):
                print('%-6s' % str(func(map_.get(i, j))), end='')
            print()

    @staticmethod
    def simple_army(map_: RgdBlock):
        # for i in range(25):
        #     tRegion.add((i, -1), 'test')
        # Region.save_obj(tRegion)
        # data = []
        # for i in range(0, 13):
        #     data.append((i, -1))
        # tRegion.add((1, 8), 'test', data)
        # data.clear()
        # for i in range(13, 25):
        #     data.append((i, -1))
        # tRegion.add((2, 8), 'testtt', data)
        pass


# MapInit.simple_army(rgdBlock)
'''
前景色   背景色         颜色
---------------------------
30              40             黑色
31              41              红色
32             42              绿色
33             43              黃色
34             44              蓝色
35             45              紫红色
36             46              青蓝色
37             47              白色

显示方式           意义
-------------------------
0                终端默认设置
1                高亮显示
4                使用下划线
5                闪烁
7                反白显示
8                不可见
'''


class Console:
    def __init__(self):
        colorama.init(True)
        self.map_ = []
        self.colors = []
        self.width = 80
        self.height = 60
        self.indent = 0

    def set_map(self, map_, color=None):
        indent = 0
        self.map_ = map_
        if not color:
            self.colors = [[None for i in map_[0]] for i in map_]
        else:
            self.colors = color
        for i in map_:
            for j in i:
                indent = max(indent, len(str(j)))
        self.indent = indent

    def print_map(self):
        os.system('mode con cols=%d lines=%d' % (self.height, self.width))
        for i, i1 in enumerate(self.map_):
            for j, j1 in enumerate(i1):
                color = '' if not self.colors[i][j] else \
                    '\033[1;{};{}m'.format(self.colors[i][j][0], self.colors[i][j][1])
                text = ('{:-'+str(self.indent)+'}').format(j)
                print(color+text, end='')
            print()


class AI:
    @staticmethod
    def ctrl_unit(u0: Unit):
        pass


class Role:
    def __init__(self, nickname, job):
        self.nickname = nickname
        self.force = 1
        self.job = job
        self.__workspace = 'j0'
        # self.__hand_path('../../123')
        # print(self.__hand_path('../'))
        # print(tRegion.data)
        pass

    def run(self):
        saved = True
        while 1:
            input_ = input("["+self.nickname+"]# ")
            input_ = re.sub(' +', ' ', input_)
            if input_[-1] == ' ':
                input_ = input_[:-1]
            cmc = input_.split(' ')
            if cmc[0] == 'exit':
                if not saved and '-f' not in cmc:
                    input_ = input("exit without save?(tip: input yes for save)\n")
                    if input_ == 'yes':
                        self.save()
                print('\nbye')
                break
            elif hasattr(self, cmc[0]):
                eval('self.'+cmc[0]+"(cmc[1:])")

    def lscmds(self):
        print(self.__doc__)

    def save(self):
        print('saved')

    def speed(self):
        pass

    def loc(self, l0):
        if not l0:
            print(self.__workspace)
        else:
            try:
                if l0[0][-1] == '/':
                    cur = ord(l0[0][0]) - ord('a'), int(l0[0][1:-1])
                else:
                    cur = ord(l0[0][0]) - ord('a'), int(l0[0][1:])
            except ValueError:
                print('error format for path')
                return
            cur = cur[1], cur[0]
            if regM.has(cur[0], cur[1]):
                if l0[0][-1] == '/':
                    print(regM.list(cur))
                else:
                    self.__workspace = chr(ord('a')+cur[0]) + str(cur[1])
                return True
            else:
                print('has no such region')

    def view(self, l0):
        if l0[0]:
            try:
                cur = int(l0[0][1:]), ord(l0[0][0]) - ord('a')
            except ValueError:
                print('error format for path')
                return
            if regM.has(cur[0], cur[1]):
                obj = regM.get(cur[0], cur[1])
                print(obj.tostring())

    # def loc(self, l0):
    #     if not l0:
    #         print(self.__workspace)
    #         return
    #     path = self.__hand_path(l0[0])
    #     if not path:
    #         print('error3grr')
    #         return
    #     if path[0][-1] == '/':
    #         if len(path[1].data) < 128:
    #             end_data = list(path[1].data)
    #         else:
    #             mark = 128
    #             end_data = []
    #             for i in path[1].data:
    #                 end_data.append(i)
    #                 mark -= 1
    #                 if mark == 0:
    #                     break
    #         # rlt = []
    #         # for i in end_data:
    #         #
    #
    #     else:
    #         self.__workspace = path[0]

    # def __hand_path(self, s0):
    #     if s0 == '/':
    #         return '/', tRegion
    #     if s0[0] == '/':
    #         full_path = s0
    #     elif s0[0:2] == './':
    #         full_path = self.__workspace + s0[1:]
    #     elif s0[0:3] == '../':
    #         can_back = self.__workspace.count('/')
    #         if self.__workspace == '/':
    #             can_back = 0
    #         should_back = str(re.search('^(../)+', s0)).count('../')
    #         if should_back >= can_back:
    #             full_path = s0[should_back*3-1:]
    #         else:
    #             p_s_1 = self.__workspace.split('/')
    #             full_path = '/'.join(p_s_1[0:can_back-should_back+1]) + s0[should_back*3-1:]
    #     else:
    #         full_path = self.__workspace + '/' + s0
    #
    #     if full_path[1] == '/':
    #         full_path = full_path[1:]
    #
    #     # legal
    #
    #     p_s_1 = full_path.split('/')[1:]
    #     f = tRegion
    #     for i_1 in p_s_1:
    #         try:
    #             id0 = (int(i_1[1:]), ord(i_1[0])-ord('a'))
    #         except ValueError:
    #             return False
    #         if f.has(id0):
    #             f = f.get(id0)
    #         else:
    #             return False
    #
    #     return full_path, f


class RoleOfficial(Role):
    def search(self):
        pass

    def news(self):
        pass


class RoleCommander(Role):
    def __init__(self, nickname, job):
        super(RoleCommander, self).__init__(nickname, job)

    def army(self, l0):
        if len(l0) == 0:
            print('')
            return
        if l0[0] == 'v':
            pass

    def __view_army(self):
        pass

    def mov(self, l0):
        pass


'''
    view,  army, /force/province/status/block
    loc /force/province/status/block
'''


if __name__ == "__main__":
    import time
    start_time = time.time()
    # print(regM.regeditS[RegeditNu.rank9].data)
    # exit()
    print(regM.has(0, RegeditNu.rankB), 'fdfdf')
    # RoleCommander('1', 2).run()
    exTmp = RoleCommander('bear', 8)
    exTmp.run()

    print(time.time() - start_time)
    pass


from PIL import Image
import numpy
from typing import Any, Dict, List, Set, Tuple
import math

import networkx
import random


class Information:
    CODE: Dict[int, str] = {
        0x1: "city_no_people",
        0x2: "city_hunger",
        0x3: "city_no_tax_building",
        0x4: "sciencse_no_money",
        0x5: "arsenal_no_money"
    }

    def __init__(self, code) -> None:
        # self.type: int = 0
        self.code: int = code
        self.msg: str = self.CODE[code]

################################# weapon ###################################


class _WEngine:
    def __init__(self) -> None:
        self.type = ""  # land sea air
        self.moveCostTable: Dict[int, int]

    def can_fly(self):
        pass

    def can_sail(self):
        pass


class WeaponAtr:
    """
    aiRole = sea|land|air, launch, atk, far, bomb, ac, logistics
    """

    def __init__(self) -> None:
        self.engine: _WEngine = None
        # sea|land|air, launch, atk, far, bomb, ac, logistics
        self.aiRole = -1, -1

        self.maxBullet: int
        self.bulletId: int
        self.maxOil: int
        self.oilId: int
        self.weaponFactory: 'WeaponFactory' = None


class WeaponFactory:
    def __init__(self) -> None:
        # storage
        self.weapons: Dict[int, WeaponAtr] = {}
        self.engine: Dict[str, _WEngine]
        self.atkTable: Dict[int, Dict[int, int]]


class GoodsBlueprint:
    BP: Dict[int, 'GoodsBlueprint']

    def __init__(self) -> None:
        self.id: int = 0
        self.name = ''
        self.weaponAtr: None | WeaponAtr = None
        self.steps = 0
        self.labor = 0
        self.money = 0
        self.people = 0

    @classmethod
    def load_data(cls):
        pass

    @classmethod
    def make_weapon_factory(cls):
        return WeaponFactory()

############################ force ####################################
# ability


class Ability:
    def __init__(self) -> None:
        self.body = 0
        self.manage = 0
        self.research = 0


# person
class Person(Ability):
    def __init__(self) -> None:
        super.__init__()
        self.kind = 100
        self.evil = 100

        self.aq = 100
        self.character: Tuple[str, str]
        self.belong = None
        self.name: str = ""


class PersonFactory:
    @classmethod
    def make_person(cls):
        return Person()

# group


class Group(Ability):
    usedFor: str = None

    def __init__(self) -> None:
        self.id = 0
        self.header: Person = None
        self.staff: List[Person] = []
        self.belong: 'Group' = None
        self.loc: Tuple[int, int] = -1, -1


class GroupCommander(Group):
    usedFor: str = "commander"

    def __init__(self) -> None:
        super.__init__()
        # 性质：地下组织/起义军，军队，警察, 旅游队，间谍队
        self.troops: List[Troop] = []
        self.captains: Dict[int, TroopCaptain] = {}


class GroupMinister(Group):
    usedFor: str = "minister"

    def __init__(self) -> None:
        super().__init__()
        self.cities: List[City] = []
        self.weaponBluprint: set = set()
        self.money = 0


class GroupKing(Group):
    usedFor: str = "king"

    def __init__(self) -> None:
        super().__init__()
        self.countryName: str = None
        self.minister: GroupMinister = None
        self.commanders: List[GroupCommander] = []
        self.subKings: List[GroupKing] = []

        self.commands = None


class GroupFactory:
    COUNTRY_NAME: Set[str] = set()

    @classmethod
    def make_coutry(cls, header=None, country_name: str = None, cities: List['City'] = [], bp: List['GoodsBlueprint'] = []):
        king = GroupKing()
        if country_name is not None and country_name in cls.COUNTRY_NAME:
            return None
        king.countryName = country_name
        if header is None:
            king.header = PersonFactory.make_person()
        king.staff = [PersonFactory.make_person()
                      for i in range(random.randint(4, 12))]
        minister = GroupMinister()
        king.minister = minister
        minister.header = PersonFactory.make_person()
        minister.staff = [PersonFactory.make_person()
                          for i in range(random.randint(0, 5))]
        minister.cities = cities
        minister.weaponBluprint = bp


# troop 多兵种司令，非战区总司令
# 侦查视野
# 移动
# 战斗系统
# 战略单位：支援补给，超远程，海军，空军，陆军
class TroopCaptain(Group):
    def __init__(self, force_rate, force_structure) -> None:
        super().__init__()
        self.target = ""

        self.forceRate: float = force_rate
        self.storage: Dict[int, int] = {}
        self.packages: List['Package'] = []
        # should be update in time
        self.forceStructure: Dict[int, int] = force_structure
        self.weaponFactory: 'WeaponFactory'

        self.underSeaForces: List['Troop'] = []
        self.atkSeaForces: List['Troop'] = []
        self.farAtkSeaForces: List['Troop'] = []

        self.atkLandForces: List['Troop'] = []
        self.farAtkLandForces: List['Troop'] = []
        self.launchLandForces: List['Troop'] = []

        self.__troopListDict: Dict[Tuple[str, str], List['Troop']] = {}

        self.__troopListDict[('sea', 'atk')] = self.atkSeaForces
        self.__troopListDict[('sea', 'far')] = self.farAtkSeaForces
        self.__troopListDict[('sea', 'under')] = self.underSeaForces

        self.__troopListDict[('land', 'atk')] = self.atkLandForces
        self.__troopListDict[('land', 'far')] = self.farAtkLandForces
        self.__troopListDict[('land', 'launch')] = self.launchLandForces

        self.deployed = False

        self.add_troop(force_rate, force_structure)

    def deploy(self, cover_map: numpy.ndarray):
        pass

    def add_troop(self, force, force_structure: Dict[int, int]):
        r = sum(force_structure.values()) / \
            (sum(force_structure)+sum(self.forceStructure.values()))
        self.forceRate = self.forceRate * (1-r) + force * r
        for k, v in force_structure.items():
            self.forceStructure[int(k)] = self.forceStructure.get(
                int(k), 0) + v
            troops = self.__troopListDict[self.weaponFactory.weapons[int(
                k)].aiRole]
            troops.sort(key=lambda a: a.endurance)
            for i in troops:
                need = 100 - i.endurance
                if need > v:
                    v = 0
                    i.endurance += v
                    break
                i.endurance = 100
                v -= need
            else:
                if v == 0:
                    continue
                for i in range(v//100):
                    troops.append(
                        Troop(self, self.weaponFactory.weapons[int(k)], 100, 0, 0))
                    v -= 100
                if v > 0:
                    troops.append(
                        Troop(self, self.weaponFactory.weapons[int(k)], v, 0, 0))

    def add_storage(self, storage):
        for k, v in storage.items():
            self.storage[int(k)] = self.storage.get(int(k), 0) + v

    def supply(self):
        storage = self.storage
        for k, v in self.__troopListDict.items():
            for i in v:
                weaponAtr = i.weaponAtr
                n_t = weaponAtr.bulletId
                n_v = weaponAtr.maxBullet - i.bullet
                n_t_2 = weaponAtr.oilId
                n_v_2 = weaponAtr.maxOil = i.oil
                #
                if n_t in storage:
                    if storage[int(n_v)] > n_v:
                        storage[int(n_v)] -= n_v
                        i.bullet += n_v
                    else:
                        i.bullet += storage[int(n_v)]
                        del storage[int(n_v)]
                #
                if n_t_2 in storage:
                    if storage[int(n_v_2)] > n_v_2:
                        storage[int(n_v_2)] -= n_v_2
                        i.bullet += n_v_2
                    else:
                        i.bullet += storage[int(n_v_2)]
                        del storage[int(n_v_2)]

    def transport(self):
        should_pop = []
        for i1, i in enumerate(self.packages):
            if i.restSteps <= 0:
                if i.storage is not None:
                    self.add_storage(i.storage)
                if i.persons is not None:
                    self.staff.extend(i.persons)
                should_pop.append(i1)
            i.restSteps -= 1
        for i in should_pop[::-1]:
            self.packages.pop(i1)

    def add_pkg(self, pkg):
        self.packages.append(pkg)


class Troop:
    def __init__(self, belong, weapon, endurance, oil, bullect) -> None:
        self.belong: 'TroopCaptain' = belong
        self.loc: Tuple[int, int] = -1, -1
        self.weaponAtr: "WeaponAtr" = weapon
        self.endurance = endurance  # self.maxEndurance = 100
        self.oil = oil
        self.bullet = bullect
        self.loading: None | List['Troop'] = None
        self.supply: None | Dict[int, int] = None


########################### 建筑 ##########################
class Building:
    usedfor: str = ""

    def __init__(self) -> None:
        self.id: int = 0
        self.cityId: int = 0
        self.loc: Tuple[int, int] = None
        # self.force: Dict[int, Person | Group] = {}  # key=0 为特殊
        self.groups: List[Group | Person] = []


class Living(Building):
    usedfor: str = "living"

    def __init__(self, p, luxury_r=1, max_p=10**6) -> None:
        super().__init__()
        self.maxPopulation = max_p
        self.population = p
        self.popuGrowthRate = 0.001

        self.workEfficiency = 1
        self.workTime = 0.6
        self.restLabor = 0

        self.lastDemandedTick: int = 0

        self.luxuryRate = luxury_r
        self.taxRate = 0.01

    def update(self, tick, city: "City"):
        # 人口
        self.restLabor = 0
        self.population = int(self.popuGrowthRate *
                              self.population) + self.population
        if self.population < 0:
            self.population = 0
            return
        if self.population > self.maxPopulation:
            self.population = self.maxPopulation

        buildingCache = city.buildingCache
        # 基本需求
        self.restLabor = self.workEfficiency * self.workTime * self.population
        if buildingCache.factoryBase is not None:
            if not buildingCache.factoryBase.isError:
                self.restLabor -= buildingCache.factoryBase.count_labor(
                    self.population)
                self.lastDemandedTick = tick

        # 饥饿
        if tick > self.lastDemandedTick:
            self.population -= int(0.001 *
                                   self.lastDemandedTick * self.population)
            self.restLabor = 0
            return

        # 经济税收
        if buildingCache.factoryLuxury is not None:
            tax = 0
            lu_n = self.population * self.luxuryRate
            la_n = buildingCache.factoryLuxury.count_labor(lu_n)
            if la_n > self.restLabor:
                lu_n = int(lu_n*self.restLabor/la_n)
                self.restLabor = 0
            else:
                self.restLabor -= la_n
            tax = lu_n * self.taxRate
            if city.belong is not None:
                city.belong.money += tax

    def get_labor(self, v) -> None | int:
        if v > self.restLabor:
            return self.restLabor
        self.restLabor -= v


class Factory(Building):
    usedfor: str = "factory"

    def __init__(self, labor_r) -> None:
        super().__init__()
        self.laborRatio: int = labor_r
        self.isError = False

    def count_labor(self, v):
        return math.ceil(v/self.laborRatio)


class Arsenal(Factory):
    usedfor: str = "arsenal"

    def __init__(self, labor_r) -> None:
        super().__init__(labor_r)
        # self.money = 0
        # self.demand: Dict[int, int] = {}
        self.storage: Dict[int, int] = {}
        # 生产武器需要初始资金
        # self.produce: Dict[int, Dict[int, int]] = {}
        self.produce: Dict[int, Tuple[int, int, int]]

    def update(self, tick, city: "City"):
        living = city.buildingCache.living
        keys = list(self.produce.keys())
        reslabor = living.restLabor
        needs = [self.produce[k][1] - self.produce[k][2] for k in keys]
        if reslabor >= sum(needs):
            labors = needs
        else:
            n = reslabor / sum(needs)
            labors = [int(n*i) for i in needs]
        living.get_labor(sum(labors))

        for k, v in zip(keys, labors):
            tb = self.produce[k]
            tb = tb[0], tb[1], tb[2] + v
            self.produce[k] = tb
            # self.produce[k][2] += v
            if tb[1] <= tb[2]:
                self.storage[k] = self.storage.get(k, 0) + tb[0]
                del self.produce[k]

        base_storage = city.buildingCache.militaryBase.storage
        if base_storage is not None:
            for k, v in self.storage.items():
                base_storage[int(k)] = base_storage.get(int(k), 0) + v
            self.storage = {}

    def add_storage(self, s: Dict[int, int]):
        for k, v in s.items():
            self.storage[int(k)] = self.storage[int(k)]

class MilitaryBase(Building):
    usedfor: str = "militay"

    def __init__(self) -> None:
        super().__init__()
        self.hasHarbor = False
        self.hasAirport = False
        self.storage: Dict[int, int] = {}

        self.money = 0
        self.soldierAccount = 0
        self.soldierForceValue = 0
        self.soldierForcePrice = 0

        self.troops: List[Troop] = []
        self.ariForces: List[Troop] = []

    def update(self, tick, city):
        if self.money < self.soldierForcePrice:
            return
        forces = self.money // self.soldierForcePrice
        self.money -= forces * self.soldierForcePrice
        self.soldierForceValue += forces


class Laboratory(Building):
    usedfor: str = "laboratory"

    def __init__(self) -> None:
        super().__init__()
        self.money = 0
        self.blueprints: Dict[int, Tuple[int, int, int]] = {}

    def update(self, tick, city: "City"):
        keys = list(self.blueprints.keys)
        keys.sort()
        minister = city.belong
        if minister is None:
            return
        for i in keys:
            tb = self.blueprints[int(i)]
            if self.money < tb[0]:
                break
            tb = tb[0], tb[1], tb[2] + 1
            if tb[1] == tb[2]:
                minister.weaponBluprint.add(int(i))
                del self.blueprints[int(i)]
            else:
                self.blueprints[int(i)] = tb


# 运输：group, person, storage
class Package:
    def __init__(self) -> None:
        self.comeFrom: Tuple[int, int, int] = None  # cityId, buildingId
        self.comeTo: Tuple[int, int, int] = None
        self.storage: Dict[int, int] = None
        self.groups: List[Group] = None
        self.persons: List[Person] = None
        self.restSteps: int = 0


# 城市
class BuildingCache:
    def __init__(self) -> None:
        self.living: Living = None
        self.factoryBase: Factory = None
        self.factoryLuxury: Factory = None
        self.factoryWeapon: Arsenal = None
        self.factoryScience: Laboratory = None
        self.militaryBase: MilitaryBase = None

    def update(self, tick, city):
        self.living.update(tick, city)
        if self.factoryScience:
            self.factoryScience.update(tick, city)
        if self.factoryWeapon:
            self.factoryWeapon.update(tick, city)
        if self.militaryBase:
            self.militaryBase.update(tick, city)


class City:
    def __init__(self,
                 base_ratio,
                 luxury_ratio,
                 arsenal_ratio,
                 max_p, p,
                 luxury_rate,
                 has_luxury, has_arsenal, has_science, has_military
                 ) -> None:
        # self.id: int = -1
        self.pos: Tuple[int, int] = -1, -1
        self.belong: GroupMinister = None

        self.buildings: Dict[int, Building] = {}
        self.buildingCache: BuildingCache = BuildingCache()

        self.packages: List[Package] = []

        self.defenseLevel: int = 5
        self.defenseEndurance: int = 10

        it = 0
        self.buildingCache.living = Living(p, luxury_rate, max_p)
        self.buildings[it] = self.buildingCache.living
        it += 1
        self.buildingCache.factoryBase = Factory(base_ratio)
        self.buildings[it] = self.buildingCache.factoryLuxury
        if has_luxury:
            it += 1
            self.buildingCache.factoryLuxury = Factory(luxury_ratio)
            self.buildings[it] = self.buildingCache.factoryLuxury
        if has_arsenal:
            it += 1
            self.buildingCache.factoryWeapon = Arsenal(arsenal_ratio)
            self.buildings[it] = self.buildingCache.factoryWeapon
        if has_science:
            it += 1
            self.buildingCache.factoryScience = Laboratory()
            self.buildings[it] = self.buildingCache.factoryScience
        if has_military:
            it += 1
            self.buildingCache.militaryBase = MilitaryBase()
            self.buildings[it] = self.buildingCache.militaryBase

    def add_pak(self, pkg: Package):
        self.packages.append(pkg)

    def update(self, tick):
        self.buildingCache.update(tick)

###################################################################


class RoadNet:
    def __init__(self) -> None:
        self.roadMap: numpy.ndarray = None
        self.roadMapDict: Dict[Tuple[int, int], set] = {}
        self.minLandRoadId = 2
        self.minSeaLineId: int = None

        # source target weight, road
        self.landRoad: Dict[Tuple[int, int],
                            Dict[Tuple[int, int], Tuple[int, List[Tuple[int, int]]]]] = {}
        self.seaRoad: Dict[Tuple[int, int],
                           Dict[Tuple[int, int], Tuple[int, List[Tuple[int, int]]]]] = {}
        self.airRoad: Dict[Tuple[int, int],
                           Dict[Tuple[int, int], Tuple[int, int]]] = {}

        self.blockadeRoad: Set[Tuple[int, int, int, int, int]] = set()
        self.G = networkx.Graph()
        self.roadTable: Dict[Tuple[int, int, int, int],
                             List[Tuple[int, int]]] = {}
        self.roadWeightTable: Dict[Tuple[int, int, int, int], int] = {}

    def init_road_net(self, map_size, land_roads, land_roads_w, sea_roads, sea_roads_w):
        self.airRoad.clear()
        self.landRoad.clear()
        self.seaRoad.clear()
        self.blockadeRoad.clear()

        for k, v in land_roads.items():
            for k1, v1 in v.items():
                if k < k1:
                    first, second = k, k1
                else:
                    first, second = k1, k

                if first not in self.landRoad:
                    self.landRoad[first] = {}
                if second in self.landRoad[first]:
                    # continue
                    raise IndexError()
                if first != k:
                    v1.reverse()
                self.landRoad[first][second] = (land_roads_w[k][k1], v1)

        for k, v in sea_roads.items():
            for k1, v1 in v.items():
                if k < k1:
                    first, second = k, k1
                else:
                    first, second = k1, k

                if first not in self.seaRoad:
                    self.seaRoad[first] = {}
                if second in self.seaRoad[first]:
                    raise IndexError()
                if first != k:
                    v1.reverse()
                self.seaRoad[first][second] = (sea_roads_w[k][k1], v1)
                # self.seaRoad.add((first[0], first[1], second[0], second[1]))

        # land
        self.G.clear()
        for k, v in self.landRoad.items():
            for k1, v1 in v.items():
                self.G.add_edge(k, k1, weight=v1[0])

        T1 = networkx.minimum_spanning_tree(self.G)
        T2 = networkx.maximum_spanning_tree(self.G)

        # sea
        self.G.clear()
        for k, v in self.seaRoad.items():
            for k1, v1 in v.items():
                self.G.add_edge(k, k1, weight=v1[0])

        T3 = networkx.minimum_spanning_tree(self.G)
        T4 = networkx.maximum_spanning_tree(self.G)

        edges = {}
        for i in [T1, T2, T3, T4]:
            for j in i.edges():
                if j[0] < j[1]:
                    first = j[0]
                    second = j[1]
                else:
                    first = j[1]
                    second = j[0]

                # if first in self.landRoad:
                #     if second in self.landRoad[first]:
                #         del self.landRoad[first][second]
                # else:
                #     if second in self.seaRoad[first]:
                #         del self.seaRoad[first][second]
                if first not in edges:
                    edges[first] = {}

                edges[first][second] = None

        self.G.clear()
        should_del = []
        for k, v in self.landRoad.items():
            if k not in edges:
                should_del.append(k)
                continue
            should_del_1 = []
            for k1, v1 in v.items():
                if k1 not in edges[k]:
                    should_del_1.append(k1)
                else:
                    self.G.add_edge(k, k1, weight=v1[0])
            for i in should_del_1:
                del v[i]
        for i in should_del:
            del self.landRoad[i]

        should_del.clear()
        for k, v in self.seaRoad.items():
            if k not in edges:
                should_del.append(k)
                continue
            should_del_1 = []
            for k1, v1 in v.items():
                if k1 not in edges[k]:
                    should_del_1.append(k1)
                else:
                    self.G.add_edge(k, k1, weight=v1[0])
            for i in should_del_1:
                del v[i]
        for i in should_del:
            del self.seaRoad[i]

        self.roadMap = numpy.zeros(map_size, dtype=numpy.int32)
        road_id = self.minLandRoadId
        for k, v in self.landRoad.items():
            for k1, v1 in v.items():
                for r in v1[1]:
                    if self.roadMap[r[0], r[1]] != 0:
                        self.roadMap[r[0], r[1]] = 1
                        if r not in self.roadMapDict:
                            self.roadMapDict[r] = set()
                        self.roadMapDict[r].add(road_id)
                    else:
                        self.roadMap[r[0], r[1]] = numpy.int32(road_id)
                road_id += 1
        self.minSeaLineId = road_id
        for k, v in self.seaRoad.items():
            for k1, v1 in v.items():
                for r in v1[1]:
                    if self.roadMap[r[0], r[1]] != 0:
                        self.roadMap[r[0], r[1]] = 1
                        if r not in self.roadMapDict:
                            self.roadMapDict[r] = set()
                        self.roadMapDict[r].add(road_id)
                    else:
                        self.roadMap[r[0], r[1]] = numpy.int32(road_id)
                road_id += 1

    def update_graph(self):
        pass

    def get_pos_road(self, source, target, weight=False):
        if source > target:
            first = target
            second = source
        else:
            first = source
            second = target

        key = (first[0], first[1], second[0], second[1])
        if key not in self.roadTable:
            try:
                self.roadTable[key] = networkx.shortest_path(
                    self.G, first, second)
                weights = []
                for i1, i in enumerate(self.roadTable[key][1:]):
                    first1 = i
                    second2 = self.roadTable[key][i1-1]
                    if first1 > second2:
                        tmp = first1
                        first1 = second2
                        second2 = tmp
                    v = self.landRoad[first1][second2]
                    weights.append(v)
                self.roadWeightTable[key] = sum(weights)
            except:
                self.roadWeightTable[key] = None
                self.roadTable[key] = None

        if weight:
            return self.roadWeightTable[key]

        if source == first:
            return self.roadTable[key]
        else:
            return self.roadTable[key][::-1]


class MapBaseTool:
    @staticmethod
    def load_height_map(file_path, size, ladder: list) -> numpy.ndarray:
        """
        ladder: key can't little than 2
        """
        ladder = sorted(ladder)
        if 255 not in ladder:
            raise ValueError()
            ladder.append(255)

        image_raw = Image.open(file_path)
        image_raw = image_raw.resize(size)

        # convert image to black and white
        image_height = image_raw.convert('L')

        array_height = numpy.array(image_height)
        for i in numpy.nditer(array_height, op_flags=['readwrite']):
            v = int(i)
            for j in ladder:
                if v <= j:
                    i += numpy.uint8(j-v)
                    break

        return array_height

    @staticmethod
    def find_seas(d_in: numpy.ndarray, sea_v):
        """
        sea_v can't have zero
        make test: numpy.zeros((10, 10), dtype=numpy.uint8)
        progress: sea=1, land=0
        return:land=0, sea>=2
        """
        d0 = d_in.copy()
        width, height = d0.shape[1], d0.shape[0]

        # 海：1， 陆地： 0
        for i in numpy.nditer(d0, op_flags=["readwrite"]):
            if int(i) in sea_v:
                i *= numpy.uint8(0)
                i += numpy.uint8(1)
            else:
                i &= numpy.uint8(0)

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        def fs_search(x, y, id_):
            queue = set([(x, y)])
            d0[y, x] = id_
            while len(queue):
                x_, y_ = queue.pop()
                for i in directions:
                    n_x, n_y = x_ + i[0], y_ + i[1]
                    if n_x < 0 or n_x >= width or n_y < 0 or n_y >= height or d0[n_y, n_x] != 1:
                        continue

                    d0[n_y, n_x] = numpy.uint8(id_)
                    queue.add((n_x, n_y))

        global_id = 2
        for y in range(d0.shape[0]):
            for x in range(d0.shape[1]):
                v = d0[y, x]
                if v != 1:
                    continue
                fs_search(x, y, global_id)
                global_id += 1

        return d0

    @staticmethod
    def count_sealand(hm: numpy.ndarray, sea_v: set) -> numpy.ndarray:
        """
        Return[np.ndarray...]:sealand[sea<-1,land>1], land[land >1], sea[sea>1]
        """
        array_sea = MapBaseTool.find_seas(hm, sea_v)

        array_land = array_sea.copy()
        array_land[array_land == 0] = 1  # sea type
        array_land = MapBaseTool.find_seas(array_land, set([1]))
        array_sl = numpy.zeros(hm.shape, numpy.int32)
        for l, s, sl in zip(
            numpy.nditer(array_land, op_flags=['readwrite']),
            numpy.nditer(array_sea, op_flags=['readwrite']),
            numpy.nditer(array_sl, op_flags=['readwrite'])
        ):
            v_l = int(l)
            v_s = int(s)
            if v_l * v_s != 0 or v_l + v_s == 0:
                raise ValueError()
            if v_l != 0:
                sl += numpy.int32(v_l)
            else:
                sl += numpy.int32(-v_s)

        # print(array_sea)
        # print(array_land)
        # print(array_sl)
        return array_sl, array_land, array_sea

    @staticmethod
    def find_true_sea(sl: numpy.ndarray, sea_area=0.2, near_border=True):
        """
        zero: land
        """
        S_all = sl.shape[0] * sl.shape[1]
        _ck, _cv = numpy.unique(sl, return_counts=True)
        counts = {}
        for i1, i in enumerate(_ck):
            counts[i] = _cv[i1]
        seas = set()

        if near_border:
            for i in range(sl.shape[0]):
                v = sl[i, 0]
                if v != 0:
                    seas.add(v)
                v = sl[i, sl.shape[1]-1]
                if v != 0:
                    seas.add(v)

            for i in range(1, sl.shape[1]-1):
                v = sl[0, i]
                if v != 0:
                    seas.add(v)
                v = sl[sl.shape[0]-1, i]
                if v != 0:
                    seas.add(v)

        sea_area_nu = sea_area if sea_area >= 1 else sea_area * S_all

        for k, v in counts.items():
            if v >= sea_area_nu:
                seas.add(k)

        return seas, set([k for k in counts.keys() if k not in seas])

    @staticmethod
    def init_city_random(hm: numpy.ndarray, geo_r: Dict[int, Tuple[float, float] | None]):
        cities = []
        geo_w = {}
        for k, v in geo_r.items():
            if v is None:
                geo_w[k] = 0
            else:
                geo_w[k] = v[0] + random.random() * (v[1]-v[0])
        for y in range(hm.shape[0]):
            for x in range(hm.shape[1]):
                p = random.random()
                if p < geo_w[int(hm[y, x])]:
                    cities.append((y, x))

        return cities

    @staticmethod
    def make_road_net(
        hm: numpy.ndarray,
        cities: set,
        geo_w: Dict[int, int],
        array_land: numpy.ndarray | None,
        sea_v: set
    ):
        land_roads: Dict[Tuple[int, int], Dict[Tuple[int, int], int]] = {}
        land_roads_w = {}
        sea_roads: Dict[Tuple[int, int], Dict[Tuple[int, int], int]] = {}
        sea_roads_w = {}

        def get_area_map(x, y, e_area: numpy.ndarray):
            area_map = numpy.zeros(hm.shape, numpy.int32)
            q: List[Tuple[int, int]] = [(y, x)]
            q_s = set([(y, x)])

            height, width = area_map.shape[0], area_map.shape[1]
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            while q:
                y, x = q.pop()
                q_s.remove((y, x))

                w = area_map[y, x]

                for i in directions:
                    n_y, n_x = y+i[0], x+i[1]
                    # format
                    if n_y < 0 or n_x < 0 or n_y >= height or n_x >= width:
                        continue

                    # effective erea
                    if not e_area[n_y, n_x]:
                        continue

                    v = area_map[n_y, n_x]

                    new_v = w + geo_w[int(hm[n_y, n_x])]

                    if v == 0 or new_v < v:
                        area_map[n_y, n_x] = new_v
                        if (n_y, n_x) in q_s:
                            continue
                        q.append((n_y, n_x))
                        q_s.add((n_y, n_x))

            return area_map

        def get_road_by_area(area_map: numpy.ndarray, source, target):
            """
            y, x
            """
            road = [target]
            y, x = target
            v = area_map[target[0], target[1]]
            width, height = area_map.shape[1], area_map.shape[0]
            direactions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            is_last_d_h = True
            while v:
                for i in direactions:
                    n_y, n_x = y + i[0], x + i[1]
                    if n_y < 0 or n_x < 0 or n_y >= height or n_x >= width:
                        continue
                    if area_map[n_y, n_x] == 0:
                        continue

                    if (n_y, n_x) == source:
                        road.append(source)
                        road.reverse()
                        return road
                    if area_map[n_y, n_x] == v - 1:
                        v -= 1
                        y, x = n_y, n_x
                        road.append((n_y, n_x))

                        if (i[0] == 0) == is_last_d_h:
                            direactions.reverse()
                            is_last_d_h = not is_last_d_h

                        break

            print(road, source, target, '\n', area_map)

        array_sea = MapBaseTool.find_seas(hm, sea_v)
        if array_land is None:
            array_sea = MapBaseTool.find_seas(hm, sea_v)

            array_land = array_sea.copy()
            array_land[array_land == 0] = 1  # sea type
            array_land = MapBaseTool.find_seas(array_land, set([1]))

        # update array_sea
        #//################ hm is modified here !!!! ################
        should_be_sea = []
        # print(list(sea_v)[0])
        __sea_v = numpy.uint8(list(sea_v)[0])
        for i in cities:
            for d in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_y, new_x = i[0] + d[0], i[1] + d[1]
                if new_y <= 0 or new_x <= 0 or new_y >= hm.shape[0] or new_x >= hm.shape[1]:
                    continue
                v = hm[new_y, new_x]
                if int(v) in sea_v:
                    should_be_sea.append((new_y, new_x))

        array_sea_2 = array_sea.copy()
        for i in should_be_sea:
            array_sea_2[i[0], i[1]] = __sea_v
        # array_sea_2 = MapBaseTool.find_seas(hm, water_v)

        # land
        print('count land road...')
        for l_m in numpy.unique(array_land):
            land_cities = [i for i in cities if array_land[i[0], i[1]] == l_m]
            e_area = array_land.copy()
            e_area[e_area != l_m] = 0
            e_area[e_area == l_m] = 1
            e_area = numpy.array(e_area, dtype=numpy.bool_)
            for i_c, c in enumerate(land_cities):
                area_map = get_area_map(c[1], c[0], e_area)
                land_roads[c] = {}
                land_roads_w[c] = {}
                for c_t in land_cities[i_c+1: len(land_cities)]:
                    land_roads[c][c_t] = get_road_by_area(area_map, c, c_t)
                    if len(land_roads[c][c_t]) == 2:
                        land_roads_w[c][c_t] = 1
                    else:
                        land_roads_w[c][c_t] = area_map[c_t[0], c_t[1]]

        # sea
        print('count sea road...')
        for l_m in numpy.unique(array_sea_2):
            land_cities = [i for i in cities if array_sea_2[i[0], i[1]] == l_m]
            e_area = array_sea_2.copy()
            e_area[e_area != l_m] = 0
            e_area[e_area == l_m] = 1
            e_area = numpy.array(e_area, dtype=numpy.bool_)
            for i_c, c in enumerate(land_cities):
                area_map = get_area_map(c[1], c[0], e_area)
                sea_roads[c] = {}
                sea_roads_w[c] = {}
                for c_t in land_cities[i_c+1: len(land_cities)]:
                    sea_roads[c][c_t] = get_road_by_area(area_map, c, c_t)
                    if len(sea_roads[c][c_t]) == 2:
                        sea_roads_w[c][c_t] = 1
                    else:
                        sea_roads_w[c][c_t] = area_map[c_t[0], c_t[1]]

        # conbine, stand
        should_del = []
        for k, v in sea_roads.items():
            for k1, v1, in v.items():
                try:
                    if set(v1) == set(land_roads[k][k1]):
                        should_del.append((k, k1))
                        continue
                except:
                    pass
                try:
                    if set(v1) == set(land_roads[k1][k]):
                        should_del.append((k, k1))
                except:
                    pass

        for i in should_del:
            del sea_roads[i[0]][i[1]]
            del sea_roads_w[i[0]][i[1]]

        roadNet = RoadNet()
        roadNet.init_road_net(
            (hm.shape[0], hm.shape[1]), 
            land_roads, land_roads_w, sea_roads, sea_roads_w
        )
        # return land_roads, land_roads_w, sea_roads, sea_roads_w
        return roadNet


class GeoNodeSet:
    def __init__(self, id_, name, cost, color=(0, 0, 0), range_=None, issea=None) -> None:
        self.id: int = id_
        self.name: str = name
        self.cost: int = cost
        self.color: Any = color
        self.cityRateRange: Tuple[float, float] | None = range_
        self.isSea: bool | None = issea


class GameRule:
    def __init__(self) -> None:
        self.modifyCity = False


class PowerSystem:
    def __init__(self) -> None:
        self.personName: Set[str] = set()
        self.countryName: Set[str] = set()

        self.__groupIds: Set[int] = set()

        self.countries: Dict[int, 'GroupKing'] = {}
        self.subCountries: Dict[int, 'GroupKing'] = {}
        self.ministers: Dict[int, 'GroupMinister'] = {}
        self.commanders: Dict[int, 'GroupCommander'] = {}
        self.troopCaptains: Dict[int, 'TroopCaptain'] = {}
        self.persons: Dict[int, "Person"] = {}
        self.armyMap: numpy.ndarray
        self.armyMapDict: Dict[int, List['Troop']] = {}

    def make_coutry(self, city: 'City', header=None, country_name: str = None, cities: List['City'] = [], bp: List['GoodsBlueprint'] = []):
        king = GroupKing()
        if country_name is not None and country_name in self.countryName:
            return None
        self.countryName.add(country_name)
        king.countryName = country_name
        if header is None:
            king.header = self.make_person()

        king.staff = [self.make_person() for i in range(random.randint(4, 12))]
        king.id = self.__get_one_group_id()
        king.loc = city.pos

        minister = GroupMinister()
        king.minister = minister
        minister.header = self.make_person()
        minister.staff = [self.make_person()
                          for i in range(random.randint(0, 5))]
        minister.cities = cities
        minister.weaponBluprint = bp
        minister.id = self.__get_one_group_id()
        minister.loc = city.pos
        minister.belong = king
        for i in cities:
            i.belong = minister
        city.buildingCache.living.groups.append(king)
        city.buildingCache.living.groups.append(minister)

    def make_person(self):
        return Person()

    def make_troop_captain(self, belong, loc, force, weapons):
        troopCaptain = TroopCaptain(force, weapons)
        troopCaptain.belong = belong
        troopCaptain.loc = loc

    def get_country_name(self):
        import time
        return str(time.time())

    def __get_one_group_id(self):
        while True:
            king_id = random.randint(100, 2**12)
            if king_id in self.__groupIds:
                continue
            self.__groupIds.add(king_id)
            break
        return king_id


class MapBase:
    def __init__(self) -> None:
        self.geoNodes: Dict[int, GeoNodeSet] = {}
        self.heightMap: numpy.ndarray
        self.seaLandMap: numpy.ndarray
        self.bigSeaLand: Set[int]
        # 0==sea, 1==empty land, >1==country==cityId
        self.countryMap: numpy.ndarray
        # key >=2
        self.cityIdDict: Dict[int, City] = {}

        self.cityDict: Dict[Tuple[int, int], City] = {}
        self.roadNet: RoadNet
        self.gameRule = GameRule()
        self.powerSystem = PowerSystem()
        self.weaponFactory = WeaponFactory()

    def __update_pkg(self):
        for city in list(self.cityDict.values()):
            should_pop = []
            for i1, i in enumerate(city.packages):
                if i.restSteps <= 0:
                    if i.comeTo[:2] == city.pos:
                        building = city.buildings[i.comeTo[1]]
                        if i.storage is not None:
                            building.add_storage(i.storage)
                        if i.persons is not None:
                            for j in i.persons:
                                building.groups.append(j)
                        if i.groups is not None:
                            for j in i.groups:
                                building.groups.append(j)
                    else:
                        road = self.roadNet.get_pos_road(
                            city.pos, i.comeTo[:2])
                        if road is not None:
                            i.restSteps = self.roadNet.get_pos_road(
                                city.pos, i.comeTo[:2], weight=True)
                            # self.cities[self.posIdDict[road[1]]].add_pak(i)
                            self.cityDict[road[1]].add_pak(i)
                    should_pop.append(i1)
                    continue
                i.restSteps -= 1
            for i in should_pop[::-1]:
                city.packages.pop(i)

    # self.cityDict 变为了set类型
    def load(self, filepath, mapsize, geonodes: List[GeoNodeSet], sea_area=0.2, near_border=True):
        self.geoNodes.clear()
        for i in geonodes:
            self.geoNodes[i.id] = i

        # 地形图
        self.heightMap = MapBaseTool.load_height_map(
            filepath, mapsize, [i.id for i in geonodes])

        # 划分陆地，海洋
        sl, l, s = MapBaseTool.count_sealand(
            self.heightMap, set([i.id for i in geonodes if i.isSea]))
        self.seaLandMap = sl

        # 确定 大陆 岛屿，海洋 湖泊
        bsl1 = MapBaseTool.find_true_sea(l, sea_area, near_border)
        bsl2 = MapBaseTool.find_true_sea(s, sea_area, near_border)
        self.bigSeaLand = bsl1[0] | bsl2[0]

        # init cities
        geo_r = {}
        for i in geonodes:
            geo_r[i.id] = i.cityRateRange
        city_pos = set(MapBaseTool.init_city_random(self.heightMap, geo_r))

        # init road net
        geo_w = {}
        sea_v = set([i.id for i in geonodes if i.isSea == True])
        # water_v = set([i for i in geonodes if i.isSea is not None])
        for i in geonodes:
            geo_w[i.id] = i.cost
        self.roadNet = MapBaseTool.make_road_net(self.heightMap, city_pos, geo_w, l, sea_v)
        self.cityDict = city_pos

        # country map
        return self

    # self.cityDict 变回了init中声明的类型
    def init_city(self,
                  max_p_r, p_rate_r, luxury_rate_r, 
                  base_ratio_r, luxury_ratio_r, arsenal_ratio_r,
                  has_luxury_r, has_arsenal_r, has_science_r, has_military_r):
        city_pos = list(self.cityDict)
        if len(city_pos) >= 2 ** 12:
            raise MemoryError("城市数量>= 2^12")
        self.cityDict = {}
        for i in city_pos:
            __max_p = random.randint(*max_p_r)
            city = City(
                random.randint(*base_ratio_r),
                random.randint(*luxury_ratio_r),
                random.randint(*arsenal_ratio_r),
                __max_p,
                int(random.uniform(*p_rate_r)*__max_p),
                random.uniform(*luxury_rate_r),
                random.random() < random.uniform(*has_luxury_r),
                random.random() < random.uniform(*has_arsenal_r),
                random.random() < random.uniform(*has_science_r),
                random.random() < random.uniform(*has_military_r),
            )
            city.pos = i
            self.cityDict[i] = city
        self.cityIdDict = {}

        __pos_id_dict = {}
        for i1, i in enumerate(list(self.cityDict.values())):
            self.cityIdDict[i1+2] = i
            __pos_id_dict[i.pos] = i1+2

        # 划分领土
        city_pos = set(self.cityDict)
        # sea_v = set([i[0] for i in self.geoNodes.items() if i[1].isSea])
        country_mp = self.seaLandMap.copy()
        country_mp[country_mp < 0] = 0
        country_mp[country_mp != 0] = 1
        country_mp = country_mp.astype(numpy.int16)
        # print(country_mp)

        # deep = True
        height, width = country_mp.shape[0], country_mp.shape[1]
        for border_r in range(min(self.heightMap.shape[0], self.heightMap.shape[1])):
            should_remove = set()
            for pos in city_pos:
                pos_1 = set([(border_r, 0), (-border_r, 0)])
                for y in range(1-border_r, border_r):
                    x = border_r - y
                    pos_1.add((y, x))
                    pos_1.add((y, -x))
                __should_remove = True
                for i in pos_1:
                    y, x = pos[0] + i[0], pos[1] + i[1]
                    if y < 0 or x < 0 or x >= width or y >= height:
                        continue
                    # v = country_mp[y, x]
                    if country_mp[y, x] != 1:
                        continue
                    tmp_pos_v = __pos_id_dict[pos]
                    for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        n_y, n_x = y + d[0], x + d[1]
                        if n_y < 0 or n_x < 0 or n_y >= height or n_x >= width:
                            continue
                        if country_mp[n_y, n_x] == tmp_pos_v:
                            break
                    else:
                        if border_r != 0:
                            continue

                    country_mp[y, x] = tmp_pos_v
                    __should_remove = False

                if __should_remove:
                    should_remove.add(pos)

            # print(should_remove)
            city_pos = city_pos - should_remove
            # if deep:
            #     print(country_mp)
            #     deep = False
            if len(city_pos) == 0:
                break
        self.countryMap = country_mp

    def init_country(self,
                     force_r, technique_r, army_nu_r, city_army_r_r
                     ):
        # 选出首都位置，划分城市
        account_force = force_r if force_r > 1 else force_r * \
            len(self.cityDict)
        if account_force > len(self.cityDict):
            account_force = len(self.cityDict)
        account_force = int(account_force)
        capital = random.sample(list(self.cityDict), account_force)
        cityed = set(capital)
        country_city = [set([i]) for i in capital]
        should_pass = set()
        while True:
            old_len = len(cityed)
            for i1, i in enumerate(country_city):
                _city_node = None
                _city_weight = None
                for j in i:
                    for k, v in dict(self.roadNet[j]).items():
                        if k in cityed:
                            continue
                        if _city_weight is None:
                            _city_node = k
                            _city_weight = v['weight']
                        elif v['weight'] < _city_weight:
                            _city_node = k
                            _city_weight = v['weight']
                if _city_node is None:
                    should_pass.add(i1)
                else:
                    i.add(_city_node)
                    cityed.add(_city_node)

            if len(cityed) == old_len:
                rest_city = set(self.cityDict) - cityed
                for i in rest_city:
                    country_city[random.randint(0, len(country_city))].add(i)
                break

        # 分配势力
        tcnq_keys = list(GoodsBlueprint.BP.keys())
        for i in range(account_force):
            self.powerSystem.make_coutry(
                capital[i],
                country_name=self.powerSystem.get_country_name(),
                cities=list(country_city[i]),
                bp=random.sample(tcnq_keys, len(tcnq_keys)*int(technique_r))
            )

        # 分配军队 陆军
        city_army_r = random.uniform(city_army_r_r)
        _froce_v = set(
            [k for k, v in self.weaponFactory.weapons.items() if v.aiRole[0] == "land"])
        _force_pool_n = math.ceil(army_nu_r[1]/len(_froce_v))
        force_pool = []
        for i in range(_force_pool_n):
            force_pool.extend(tcnq_keys)

        for k, v in self.cityDict.items():
            if random.random() > city_army_r and k not in capital:
                continue
            tmp_weapons = {}
            tmp_weapon_keys = random.sample(
                force_pool, random.randint(army_nu_r))
            for i in tmp_weapon_keys:
                tmp_weapons[int(i)] = tmp_weapons.get(int(i), 0) + 100
            self.powerSystem.make_troop_captain(
                v.belong.belong.header, k, 1, tmp_weapons)


########################## game controller ############################

class GameController:
    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    __TEST_PATH = r"/home/king/Downloads/2020013113291021.jpg"
    __HEIGHT_PATH = r'/home/king/w/my-game/XEngine/tests/test.png'
    __CITY_PATH = r'/home/king/w/my-game/XEngine/tests/test_city.png'

    __GEO_NODE_SET = [
        GeoNodeSet(100, "sea", 1, issea=True),
        GeoNodeSet(150, "stand", 1, range_=[0.04, 0.07], issea=False),
        GeoNodeSet(200, "plain", 1, range_=[0.06, 0.12]),
        GeoNodeSet(255, "mountain", 2, range_=[0.01, 0.03]),
    ]
    v = MapBase().load(__TEST_PATH, (15, 15), __GEO_NODE_SET)
    # plt.figure(1, figsize=(8,5))
    v.init_city(
        (100000, 1000000), (0.5, 0.9), (0, 1), (3, 5), (1, 2), (1, 2), 
        (0.5, 1), (0.3, 0.9), (0.3, 0.9), (0.1, 1)
    )
    v.init_country()

    print(v.cityDict)
    print(v.countryMap)
    networkx.draw(v.roadNet.G, node_color='lightblue',
                  with_labels=True,
                  node_size=50)

    # nx.draw()

    plt.show()

        # max_p_r, p_rate_r, luxury_rate_r,
        #           base_ratio_r, luxury_ratio_r,
        #           has_luxury_r, has_science_r, has_military_r):

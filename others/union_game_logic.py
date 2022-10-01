# 

# from itertools import count
import os
import random
import re
from typing import Any, Dict, List, Set, Tuple, TypeVar
import pandas
# from GameMapBase import MapBase, MapBaseTool
import json
import yaml
import sys
import numpy
from PIL import Image
import networkx
import heapq

TAny = TypeVar("TAny")

def CAST(v, t: TAny) -> TAny:
    return v


class GameObject:
    CLS_DICT: Dict[str, Any]

    def __init__(self, obj) -> None:
        GameObject.CLS_DICT[obj.__class__.__name__]
        

########################## param setting ###########################

class SetCityModel:
    def __init__(self) -> None:
        self.livingBlocks:int = 1
        self.produceBlocks:int = 1
        self.manufactureBlocks:int = 1

        self.storageBlocks: int = 1
        self.militaryStorageBlocks: int = 1
        self.buildHarbor = False
        self.roadQuality: int = 0
        self.wallDefenseValue: int = None


class SetTroopModel:
    def __init__(self) -> None:
        self.name: str = None
        self.footmen: int = None
        self.cavalry: int = None


# class SetBuilding:
#     def __init__(self) -> None:
#         self.id: int = None
#         self.name: str = None
#         self.buildResourceEnv: str = None
#         self.costMoney = None
#         # self.perBuildFrom: Dict[str, int] = None
#         # self.progressLen: int = None
#         self.short: str = None
#         self.costMoney: int = None
#         self.blocks: int = None
#         self.callName: str = None
        
#         self.industry_type: str = None
#         self.industry_rate: int = None
#         self.industry_base: str = None
#         self.living_populication: int = None
#         self.living_tax: int = None
#         self.business_rate: int = None
#         self.production_type: Set[str] = None
#         self.traffic: Set[str] = None
#         self.military_defense: int = None
#         self.military_attack: int = None
#         self.isStorage: True | None = None

#     def types(self):
#         rlt = set()
#         if self.industry_type is not None:
#             rlt.add('industry')
#         if self.living_populication is not None:
#             rlt.add("living")
#         if self.business_rate is not None:
#             rlt.add("business")
#         if self.production_type is not None:
#             rlt.add("production")
#         if self.traffic is not None:
#             rlt.add("traffic")
#         if self.military_attack is not None:
#             rlt.add("military")
#         return rlt


class SetUnit:
    def __init__(self) -> None:
        self.id: int = None
        self.name: str = None
        self.buildBuildingEnv: str = None
        self.perBuildFrom: Dict[str, int] = None
        self.progressLen: int = None
        self.short: str = None
        self.canLoad: bool = None
        self.move_atr: str = None
        self.move_v: int = None
        self.atk_atr: str = None
        self.atk_v: int = None
        self.def_atr: str = None
        self.def_v: int = None
        self.view_atr: str = None
        self.view_v: int = None


class SetResource:
    def __init__(self) -> None:
        self.name: str = None
        self.id: int = None
        self.callName: str = None
        self.perBuildFrom: Dict[str, int] = None
        self.progressLen:int = None
        self.perLabor: int = None
        self.sellMoney: int = 0


class SetGeoNode:
    def __init__(self) -> None:
        self.name = None
        self.id = None
        self.callName: str = None

        self.globalCost: int = None
        self.engineCost: Dict[str, int] = None
        
        self.heightThreshold: int = None
        self.isSea: bool | None = None
        self.globalColor: Any = None

        self.cityRateRange: Tuple[float, float] = None
        self.resourceRange: Dict[int, float] = None


class SetGeneral:
    def __init__(self) -> None:
        pass

    def load_from_d(self, d0):
        for k, v in d0.items():
            setattr(self, k, v)


class GameSetting:
    def __init__(self) -> None:
        self.settingFileRoot: str = ''
        self.mapSize: Tuple[int, int] = None
        self.groupAmount: int = 2

        # unit
        self.units: List[SetUnit] = []
        self.__unitNameDict = {}
        self.__unitIdDict = {}
        # resource
        self.resource: List[SetResource] = []
        self.__resourceIdDict = {}
        self.__resourceNameDict = {}

        # geo node
        self.geoNode: List[SetGeoNode] = []
        self.__geoNodeIdDict = {}
        self.__geoNodeNameDict = {}

        # city model
        self.cityModel: List[SetCityModel] = []
        self.__cityIdModel = {}
        self.__cityNameModel = {}

        # troop model
        self.troopModel: List[SetTroopModel] = []
        self.__troopIdModel = {}
        self.__troopNameModel = {}

        # building model
        # self.cityModel: Dict[str, SetCityModel] = {}
        # self.troopGroupModel: Dict[str, SetTroopModel] = {}
        self.perBlockPopulication: int = 10000
        self.perBlockStorageValue: int = 100
        self.perBlockArmyStorageValue: int = 100
        self.perBlockCost: int = 10
        self.perWallDefenseCost: int = 100
        self.harborCost: int = 1000
        self.perRoadCost: int = 1000
        self.turmoilScale: int = 1000
        self.perRestLabourCost: float = 1
        self.cityMaxFindPerson: int = 10
        self.cityMaxInitMoney: int = 1000

    @staticmethod
    def check_integrity(b: object):
        keys = list(b.__class__().__dict__.keys())
        for i in keys:
            if i.find('_'+b.__class__.__name__+'__') != -1:
                continue
            try:
                getattr(b, i)
            except:
                return i

    @classmethod
    def load_from_data(self, s0):
        pass

    def load_data_from_local(self, root_path):
        obj_dict = {
            'geo_node.csv': [SetGeoNode, self.geoNode, self.__geoNodeIdDict, self.__geoNodeNameDict],
            'unit.csv': [SetUnit, self.units, self.__unitIdDict, self.__unitNameDict],
            "resource.csv": [SetResource, self.resource, self.__resourceIdDict, self.__resourceNameDict],
            "city_model.csv": [SetCityModel, self.cityModel, self.__cityIdModel, self.__cityNameModel],
            "troop_model.csv": [SetTroopModel, self.troopModel, self.__troopIdModel, self.__troopNameModel]
        }
        for path, tb in obj_dict.items():
            C, container, id_container, name_container = tb
            data_frame = pandas.read_csv(os.path.join(root_path, path))
            keys = list(data_frame.keys())
            keys.remove("drop")
            it_id = 10
            for i in data_frame.iterrows():
                if i[1]['name'] is numpy.NAN:
                    continue
                if i[1]['drop'] is not False:
                    continue
                c = C()
                for k in keys:
                    k_v = i[1][k]

                    if k_v is numpy.NAN:
                        k_v = None

                    if type(k_v) == str:
                        # print(type(k))
                        if k_v[0] == "{":
                            try:
                                k_v = json.loads(k_v.replace('“', '"').replace('”', '"'))
                            except:
                                # print("dict error", k_v, k_v[1]=='')
                                pass
                        
                        elif k_v[0] == '[':
                            __is_set = None
                            try:
                                __is_set = (k_v[1] == ' ')
                                __is_tuple = (k_v[2] == " ")
                                k_v = json.loads(k_v)
                            except:
                                pass
                            
                            if __is_tuple:
                                k_v = tuple(k_v)

                            elif __is_set == True:
                                k_v = set(k_v)

                    else:
                        if k_v is numpy.NAN:
                            k_v = None
                    c.__setattr__(k, k_v)
                    # print(f'key={k},value={k_v}, {type(k_v)}, {k_v is numpy.NAN}')
                c.id = it_id
                if 'id' not in keys:
                    it_id += 1
                    
                container.append(c)
                id_container[c.id] = c
                name_container[c.name] = c
            check_rlt = self.check_integrity(container[0])
            if check_rlt is not None:
                print(container[0].__dict__)
                print('csv error:',path, check_rlt)
                exit(0)

        # drop firstly
        with open(os.path.join(root_path, 'test.yml'), 'r', encoding='utf-8') as f:
            yaml_data = yaml.load(f, Loader=yaml.FullLoader)

        # self.buildingGroupModel = yaml_data['building_model']
        # self.troopGroupModel = yaml_data['troop_model']
        
    # def get_building(self, id_=None, name=None)->SetBuilding:
    #     if id_ is not None:
    #         return self.__buildingIdDict[id_]
    #     return self.__buildingNameDict[name]

    def unit_types(self) -> List[str]:
        return [i.id for i in self.units]

    def get_unit(self, id_=None, name=None)->SetUnit:
        if id_ is not None:
            return self.__unitIdDict[id_]
        return self.__unitNameDict[name]

    def get_resource(self, id_=None, name=None)->SetResource:
        if id_ is not None:
            return self.__resourceIdDict[id_]
        return self.__resourceNameDict[name]

    def get_geo_node(self, id_=None, name=None) -> SetGeoNode:
        if id_ is not None:
            return self.__geoNodeIdDict[id_]
        return self.__geoNodeNameDict[name]

    def get_city_model(self, id_=None, name=None) -> SetCityModel:
        if id_ is not None:
            return self.__cityIdModel[id_]
        return self.__cityNameModel[name]

    def get_troop_model(self, id_=None, name=None) -> SetTroopModel:
        if id_ is not None:
            return self.__troopIdModel[id_]
        return self.__troopNameModel[name]

    #######
    def get_name(self, type_):
        pass

    def free_name(self, type_, name):
        pass

    def combat_judge(self):
        pass




########################  natural  ####################### 



class PersonNatural:
    ff = 0


class CityNatural:
    ff = 0


###########################  ############################## 


class Person:
    def __init__(self) -> None:
        self.id: int = 0
        self.kind = 100
        self.evil = 100

        self.aq = 100
        # 主，强硬，软弱，......印象决策
        self.character: Set[int]

        self.belong = None
        self.name: str = ""
        self.nowLoc: Tuple[int, Any] |"Group"

    def auto_init(self):
        self.kind = random.randint(0, 100)
        self.evil = random.randint(0, 100)
        self.aq = random.randint(self.kind, 100)


# group
class GroupBase:
    def __init__(self) -> None:
        self.id = 0
        self.groupName: str = ''
        self.header: Person
        self.belong: Group| None
        # 低于0.2必反，低于0.4随机反，低于0.6等待一个理由
        self.loyalty: float = 1
        self.staff: List['Person'] = []

# 
class GroupTransaction:
    def __init__(self) -> None:
        # [宣战，讲和]，[入盟，毁梦]，[索取/请求 物资/人物/军队/资金]

        pass


class Group(GroupBase):
    def __init__(self) -> None:
        super().__init__()
        self.loc: 'Troop'
        self.ministers: Set['Person'] = set()
        self.commanders: Set['Person'] = set()

        self.subGroups: List['Group'] = []
        self.troops: List['Troop'] = []
        self.cities: List["City"] = []

        self.money: int  = -1

        # self.campGroup: str = ""
        # self.enemies: Set[int] = set()
        self.unionShip: Dict[int, float] = {}
        self.secondHeader: List['Person'] = []
        self.transaction: GroupTransaction

        self.aiMilitaryMoneyRate: float = 0.5
        self.aiCityMoneyWeight: Dict[int, float] = {}

class Troop(GroupBase):
    def __init__(self) -> None:
        super().__init__()
        self.loc: Tuple[int, int] | City
        # self.bullect:int
        # self.oil:int
        # self.units: Dict[int, int]
        # self.resource: Dict[int, int]
        self.units: Dict[int, int] = {}
        self.groups: Set[Group]|None = None
        self.troopModel: SetTroopModel = None
        self.target: Tuple['City', str] = None
        self.shouldSupply = False
        # self.sourceCity: int = None


# 
########################### building ############################## 


class CityAtrLiving:
    def __init__(self) -> None:
        self.group: Dict['Person', float] = {}
        self.blocks: int = 100
        self.populication: int = 0
        self.standardCitizen: 'Person' = Person()
        self.talentedPerson: Set['Person'] = set()


class CityAtrProduce:
    def __init__(self) -> None:
        self.produceType: Set[int] = set()
        self.resource: Set['int'] = set()
        self.group: Dict["Person", float] = {}
        self.blocks: int = 1
        self.workEfficiency: float = 1

        self.produceWeight: Dict[int, float] = {}


class CityAtrManufacture:

    def __init__(self) -> None:
        self.produceType: Set[int] = set()
        self.group: Dict["Person", float] = {}
        self.blocks: int = 1
        # self.workEfficiency: float = 1
        self.productQuality: float = 1

        # type, number  ; all, per, restLen
        self.produceQueue: Dict[Tuple[int, int], Tuple[Dict[int, int], Dict[int, int], int]] = {}
        self.blockedQueue: Dict[Tuple[int, int], int] = {}


class CityAtrMarket:
    def __init__(self) -> None:
        self.group: Dict["Person", float] = {}
        self.tradeCitySet: Dict[int, int|None] = {}
        # self.innerProfitRate: float
        # self.outerProfitRate: float
        self.profitRate: float = 1


class CityAtrStorage:
    def __init__(self) -> None:
        self.blocks: int = 0
        self.militaryBlocks: int = 0
        self.produceStorage: Dict[int, int] = {}
        self.produceStorageWeight: Dict[int, float]
        self.manufactureStorage: Dict[int, int] = {}


class CityAtrTraffic:
    def __init__(self) -> None:
        self.roadLen: int = 1
        self.roadQuality: float = 1
        self.perRoadCost: int = 10
        self.hasHarbor: bool = False


class CityAtrMilitary:
    def __init__(self) -> None:
        self.wallDefenseValue = 100
        self.defenseRate: float
        self.attackRate: float
        self.innerTroops: Set["Troop"] = set()
        self.supplyTroops: Dict['Troop', int] = set()


class CityAtrUnder:
    def __init__(self) -> None:
        self.group: Dict["Person", float] = {}

        self.underGroup: Dict["Person", float] = {}
        self.spies: Set['Person'] = set()
        self.turmoilRate: float = 1
        self.prison: Set['Person'] = {}


class City:

    def __init__(self) -> None:
        self.id:int = None
        self.name: str
        self.belong: str = None

        self.politicianGroup: Dict["Person", float] = {}
        self.aiMoney: int = 0
        self.aiCityModel: str = 'default'
        self.groupUpdateCache: Set[str] = set()
        self.aiFindPerson = False
        self.character = set()

        # 注意命名规则
        self.livingArea = CityAtrLiving() # 1
        self.produceArea = CityAtrProduce() # 2
        self.manufactureArea = CityAtrManufacture() # 3
        self.marketArea = CityAtrMarket() # 4
        self.trafficArea = CityAtrTraffic() # 5
        self.militaryArea = CityAtrMilitary() # 6
        self.underArea = CityAtrUnder() # 7
        self.storageArea = CityAtrStorage() # 8
        self.__areaCache = {
            # CityAtrLiving.__name__: self.livingArea,
            # CityAtrProduce.__name__: self.produceArea,
            # CityAtrManufacture.__name__: self.manufactureArea,
            # CityAtrMarket.__name__: self.marketArea,
            # CityAtrTraffic.__name__: self.trafficArea,
            # CityAtrMilitary.__name__: self.militaryArea,
            # CityAtrStorage.__name__: self.
        }

        for k, v in self.__dict__.items():
            if re.match(r'[^_].*Area$', k) is not None:
                self.__areaCache[v.__class__.__name__] = v

    # 设置好 aiMoney, all group, aiCityModel
    def auto_init(self):
        self.update_city_group()
        self.update_by_model()

    def get_area_by_obj(self, obj: TAny) -> TAny:
        return self.__areaCache[obj.__class__.__name__]

    def update_by_model(self, gameSetting: "GameSetting"):
        if self.aiCityModel is None:
            return

        city_model = gameSetting.get_city_model(name=self.aiCityModel)
        d0 = [
            (city_model.livingBlocks, self.livingArea),
            (city_model.produceBlocks, self.produceArea),
            (city_model.manufactureBlocks, self.manufactureArea),
            (city_model.storageBlocks, self.storageArea)
        ]
        d0_rlt = []

        for new_blocks, area in d0:
            can_go = True
            if new_blocks is None:
                can_go = False
            else:
                rest_blocks = new_blocks - area.blocks
                cost_money = gameSetting.perBlockCost * rest_blocks
                if rest_blocks <=0 or cost_money > self.aiMoney:
                    can_go = False

            if can_go:
                area.blocks += rest_blocks
                self.aiMoney -= cost_money
                d0_rlt.append(True)
            else:
                d0_rlt.append(False)

        if d0_rlt[0]:
            city_model.livingBlocks = None
        if d0_rlt[1]:
            city_model.produceBlocks = None
        if d0_rlt[2]:
            city_model.manufactureBlocks = None
        if d0_rlt[3]:
            city_model.storageBlocks = None

        self.livingArea.populication = self.livingArea.blocks * gameSetting.perBlockPopulication
        self.storageArea.militaryBlocks = city_model.militaryStorageBlocks

        # wall
        can_go = True
        if city_model.wallDefenseValue is None:
            can_go = False
        else:
            rest_blocks = city_model.wallDefenseValue - self.militaryArea.wallDefenseValue
            cost_money = gameSetting.perWallDefenseCost * rest_blocks
            if rest_blocks <=0 or cost_money > self.aiMoney:
                can_go = False

        if can_go:
            self.militaryArea.wallDefenseValue += rest_blocks
            self.aiMoney -= cost_money
            city_model.wallDefenseValue = None

        # harbor
        if city_model.buildHarbor is None or self.trafficArea.hasHarbor:
            pass
        elif gameSetting.harborCost > self.aiMoney:
            pass
        else:
            self.trafficArea.hasHarbor = True
            self.aiMoney -= gameSetting.harborCost
            city_model.buildHarbor = None

        # road
        if city_model.roadQuality is None:
            pass
        elif city_model.roadQuality <= self.trafficArea.roadQuality:
            pass
        else:
            cost_money = (city_model.roadQuality - self.trafficArea.roadQuality) * gameSetting.perRoadCost * self.trafficArea.roadLen
            if cost_money <= self.aiMoney:
                self.aiMoney -= cost_money
                self.trafficArea.roadQuality = city_model.roadQuality
                city_model.roadQuality = None

        model_keys = list(city_model.__dict__.values())
        if model_keys.count(None) == len(model_keys):
            self.aiCityModel = None

    def update_city_group(self):
        for i in self.groupUpdateCache:
            if i == CityAtrLiving.__name__:
                person = self.livingArea.standardCitizen
                kind = evil = aq = 0
                for k, v in self.livingArea.group.items():
                    kind += k.kind * v
                    evil += k.evil * v
                    aq += k.aq * v
                person.kind = kind
                person.aq = aq
                person.evil = evil

            elif i == CityAtrProduce.__name__:
                aq = sum([k.aq * v for k, v in self.produceArea.group.items()])
                self.produceArea.workEfficiency = aq / 50
            
            elif i == CityAtrManufacture.__name__:
                aq = sum([k.aq * v for k, v in self.manufactureArea.group.items()])
                self.manufactureArea.productQuality = aq / 100

            elif i == CityAtrMarket.__name__:
                aq = sum([k.aq * v for k, v in self.marketArea.group.items()])
                self.marketArea.profitRate = aq

            elif i == CityAtrUnder.__name__:
                aq = sum([k.aq * v for k, v in self.underArea.group.items()])
                self.underArea.turmoilRate = 1 - aq


############################## mapbase ################################


if False:
    class RoadNet:
        def __init__(self) -> None:
            self.roadMap: numpy.ndarray = None
            self.roadMapDict: Dict[Tuple[int, int], set] = {}
            self.minLandRoadId = 2
            self.minSeaLineId: int = None

            # source target weight, road
            self.landRoad: Dict[
                Tuple[int, int], Dict[Tuple[int, int], Tuple[int, List[Tuple[int, int]]]]
            ] = {}
            self.seaRoad: Dict[
                Tuple[int, int], Dict[Tuple[int, int], Tuple[int, List[Tuple[int, int]]]]
            ] = {}
            self.airRoad: Dict[Tuple[int, int], Dict[Tuple[int, int], Tuple[int, int]]] = {}

            self.blockadeRoad: Set[Tuple[int, int, int, int, int]] = set()
            self.G = networkx.Graph()
            self.roadTable: Dict[Tuple[int, int, int, int], List[Tuple[int, int]]] = {}
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
                    self.roadTable[key] = networkx.shortest_path(self.G, first, second)
                    weights = []
                    for i1, i in enumerate(self.roadTable[key][1:]):
                        first1 = i
                        second2 = self.roadTable[key][i1 - 1]
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

else:
    class RoadNet:
        def __init__(self) -> None:
            self.landRoadWeight: Dict[Tuple[int, int], int] = {}
            # self.blockedCity: Set[int] = set()
            self.G = networkx.Graph()

        # land_roads_w 应该被 key[0] < key[1]
        def init_road_net(self, land_roads_w: Dict[Tuple[int, int], int]):
            for k, v in land_roads_w.items():
                self.G.add_edge(k[0], k[1], weight=v)
            self.landRoadWeight = land_roads_w

        def block_city(self, city_id):
            self.G.remove_node(city_id)

        def unblock_city(self, city_id):
            for keys, v in self.landRoadWeight.items():
                if city_id in keys:
                    self.G.add_edge(keys[0], keys[1], v)

        def weight(self, src, trg):
            first, second = src, trg
            if first > second:
                first = trg
                second = src
            if (first, trg) not in self.landRoadWeight:
                return None
            return self.landRoadWeight[(first, second)]

class MapBaseTool:
    @staticmethod
    def load_height_map(file_path, size, ladder: list) -> numpy.ndarray:
        """
        ladder: key can't little than 2, don't need sorted
        """
        ladder = sorted(ladder)
        if 255 not in ladder:
            raise ValueError()
            ladder.append(255)

        image_raw = Image.open(file_path)
        image_raw = image_raw.resize(size)

        # convert image to black and white
        image_height = image_raw.convert("L")

        array_height = numpy.array(image_height)
        for i in numpy.nditer(array_height, op_flags=["readwrite"]):
            v = int(i)
            for j in ladder:
                if v <= j:
                    i += numpy.uint8(j - v)
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
                    if (
                        n_x < 0
                        or n_x >= width
                        or n_y < 0
                        or n_y >= height
                        or d0[n_y, n_x] != 1
                    ):
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
    def count_sealand(hm: numpy.ndarray, sea_v: set) -> Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]:
        """
        Return[np.ndarray...]:sealand[sea<-1,land>1], land[land >1], sea[sea>1]
        """
        array_sea = MapBaseTool.find_seas(hm, sea_v)

        array_land = array_sea.copy()
        array_land[array_land == 0] = 1  # sea type
        array_land = MapBaseTool.find_seas(array_land, set([1]))
        array_sl = numpy.zeros(hm.shape, numpy.int32)
        for l, s, sl in zip(
            numpy.nditer(array_land, op_flags=["readwrite"]),
            numpy.nditer(array_sea, op_flags=["readwrite"]),
            numpy.nditer(array_sl, op_flags=["readwrite"]),
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
                v = sl[i, sl.shape[1] - 1]
                if v != 0:
                    seas.add(v)

            for i in range(1, sl.shape[1] - 1):
                v = sl[0, i]
                if v != 0:
                    seas.add(v)
                v = sl[sl.shape[0] - 1, i]
                if v != 0:
                    seas.add(v)

        sea_area_nu = sea_area if sea_area >= 1 else sea_area * S_all

        for k, v in counts.items():
            if v >= sea_area_nu:
                seas.add(k)

        return seas, set([k for k in counts.keys() if k not in seas])

    @staticmethod
    def init_city_random(
        hm: numpy.ndarray, geo_r: Dict[int, Tuple[float, float] | None]
    ):
        cities = []
        geo_w = {}
        for k, v in geo_r.items():
            if v is None:
                geo_w[k] = 0
            else:
                geo_w[k] = v[0] + random.random() * (v[1] - v[0])
        for y in range(hm.shape[0]):
            for x in range(hm.shape[1]):
                p = random.random()
                __v = int(hm[y, x])
                if __v not in geo_w:
                    continue
                if p < geo_w[__v]:
                    cities.append((y, x))

        return cities

    @staticmethod
    def make_road_net_random(
        hm: numpy.ndarray,
        cities: set,
        geo_w: Dict[int, int],
        array_land: numpy.ndarray | None,
        sea_v: set,
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
                    n_y, n_x = y + i[0], x + i[1]
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

            print(road, source, target, "\n", area_map)

        array_sea = MapBaseTool.find_seas(hm, sea_v)
        if array_land is None:
            array_sea = MapBaseTool.find_seas(hm, sea_v)

            array_land = array_sea.copy()
            array_land[array_land == 0] = 1  # sea type
            array_land = MapBaseTool.find_seas(array_land, set([1]))

        # update array_sea
        # //################ hm is modified here !!!! ################
        should_be_sea = []
        # print(list(sea_v)[0])
        __sea_v = numpy.uint8(list(sea_v)[0])
        for i in cities:
            for d in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_y, new_x = i[0] + d[0], i[1] + d[1]
                if (
                    new_y <= 0
                    or new_x <= 0
                    or new_y >= hm.shape[0]
                    or new_x >= hm.shape[1]
                ):
                    continue
                v = hm[new_y, new_x]
                if int(v) in sea_v:
                    should_be_sea.append((new_y, new_x))

        array_sea_2 = array_sea.copy()
        for i in should_be_sea:
            array_sea_2[i[0], i[1]] = __sea_v
        # array_sea_2 = MapBaseTool.find_seas(hm, water_v)

        # land
        print("count land road...")
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
                for c_t in land_cities[i_c + 1 : len(land_cities)]:
                    land_roads[c][c_t] = get_road_by_area(area_map, c, c_t)
                    if len(land_roads[c][c_t]) == 2:
                        land_roads_w[c][c_t] = 1
                    else:
                        land_roads_w[c][c_t] = area_map[c_t[0], c_t[1]]

        # sea
        print("count sea road...")
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
                for c_t in land_cities[i_c + 1 : len(land_cities)]:
                    sea_roads[c][c_t] = get_road_by_area(area_map, c, c_t)
                    if len(sea_roads[c][c_t]) == 2:
                        sea_roads_w[c][c_t] = 1
                    else:
                        sea_roads_w[c][c_t] = area_map[c_t[0], c_t[1]]

        # conbine, stand
        should_del = []
        for k, v in sea_roads.items():
            for (
                k1,
                v1,
            ) in v.items():
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
            (hm.shape[0], hm.shape[1]), land_roads, land_roads_w, sea_roads, sea_roads_w
        )
        # return land_roads, land_roads_w, sea_roads, sea_roads_w
        return roadNet

    @staticmethod
    def make_road_net(country_map: numpy.ndarray):
        crossing = set()
        v1, v2, v3 = country_map[0, 0], country_map[1, 0], country_map[0, 1]
        if v1 != 0:
            if v2 != 0 and v2 != v1:
                crossing.add((v1, v2) if v1 < v2 else (v2, v1))
            if v3 != 0 and v3 != v1:
                crossing.add((v1, v3) if v1 < v3 else (v3, v1))

        for y in range(1, country_map.shape[0]):
            for x in range(1, country_map.shape[1]):
                v1, v2, v3 = country_map[y, x], country_map[y-1, x], country_map[y, x-1]
                if v1 == 0:
                    continue
                if v2 != 0 and v2 != v1:
                    crossing.add((v1, v2) if v1 < v2 else (v2, v1))
                if v3 != 0 and v3 != v1:
                    crossing.add((v1, v3) if v1 < v3 else (v3, v1))

        vs = numpy.unique(country_map)
        __vs_d = {}
        for i in vs:
            __vs_d[int(i)] = round(numpy.sum(country_map==i) ** 0.5)
        __road_w = {}
        for i in crossing:
            __road_w[i] = __vs_d[i[0]] + __vs_d[i[1]]
        roadNet = RoadNet()
        roadNet.init_road_net(__road_w)
        return roadNet

    @staticmethod
    def find_road_by_astar(cost_map: numpy.ndarray, start_p, target_p):
        """cost_map < 0: forbidden"""

        q_q = []
        road = []
        local_map = numpy.zeros(cost_map.shape, dtype=cost_map.dtype)
        start_p = start_p[0], start_p[1], 0, (abs(start_p[0]-target_p[0])+abs(start_p[1]-start_p[1]))
        # start_p = ((0, (abs(start_p[0]-target_p[0])+abs(start_p[1]-start_p[1]))), start_p)
        height, width = cost_map.shape[0], cost_map.shape[1]
        heapq.heappush(q_q, ((start_p[2]+start_p[3], start_p[3]), start_p))
        # local_map[start_p[0], start_p[1]] = start_p[2]

        # deep = 20
        while True:
            if len(q_q) == 0:
                break

            now_p = heapq.heappop(q_q)
            # print('now_p', now_p)
            # deep -= 1
            # if deep <=0:
            #     break

            if local_map[now_p[1][0], now_p[1][1]] !=0:
                continue

            local_map[now_p[1][0], now_p[1][1]] = now_p[1][2]

            road.append(now_p[1][:2])

            if now_p[1][:2] == target_p:
                break

            for d in [(1, 0), (-1,0), (0, 1), (0, -1)]:
                new_y, new_x = d[0] + now_p[1][0], d[1] + now_p[1][1]
                if new_y < 0 or new_x < 0 or new_y >= height or new_x >= width:
                    continue
                elif cost_map[new_y, new_x] < 0:
                    continue
                
                new_p = new_y, new_x, now_p[1][2]+cost_map[new_y, new_x], (abs(target_p[0]-new_y)+abs(target_p[1]-new_x))
                can_go = False
                if local_map[new_y, new_x] == 0:
                    can_go = True
                elif local_map[new_y, new_x] < new_p[2]:
                    can_go = True
                if can_go:
                    if ((new_p[2]+new_p[3], new_p[3]), new_p) in q_q:
                        print(True)
                    heapq.heappush(q_q, ((new_p[2]+new_p[3], new_p[3]), new_p))

        if road[-1] != target_p:
            return
        return road

    @staticmethod
    def find_raod_by_oil(cost_map: numpy.ndarray, start_p, target_p, oil):
        pass


class GeoNodeSet:
    def __init__(
        self, id_, name, cost, resource_range,  color=(0, 0, 0), range_=None, issea=None
    ) -> None:
        self.id: int = id_
        self.name: str = name
        self.cost: int = cost
        self.color: Any = color
        self.cityRateRange: Tuple[float, float] | None = range_
        self.isSea: bool | None = issea
        self.resourceRange: Dict[int, float] = resource_range


class MapBase:
    def __init__(self) -> None:
        # self.geoNodes: Dict[int, GeoNodeSet] = {}

        self.heightMap: numpy.ndarray
        self.seaLandMap: numpy.ndarray
        self.globalCostMap: numpy.ndarray
        self.bigSeaLand: Set[int]
        # 0==sea, 1==empty land, >1==country==cityId
        self.countryMap: numpy.ndarray
        # key >=2
        self.cities: Dict[Tuple[int, int], int] = {}
        self.roadNet: RoadNet
        self.resourceDict: Dict[Tuple[int, int], Set[int]] = {}

    # self.cityDict 变为了set类型
    def load(
        self,
        filepath,
        mapsize,
        geonodes: List[SetGeoNode],
        sea_area=0.2,
        near_border=True,
    ):
        # self.geoNodes.clear()
        # for i in geonodes:
        #     self.geoNodes[i.id] = i
        geonode_dict: Dict[int, SetGeoNode] = {}
        for i in geonodes:
            geonode_dict[i.heightThreshold] = i

        # 地形图
        self.heightMap = MapBaseTool.load_height_map(
            filepath, mapsize, [i.heightThreshold for i in geonodes]
            #[i.id for i in geonodes]
        )

        # 划分陆地，海洋
        sl, l, s = MapBaseTool.count_sealand(
            self.heightMap, set([i.heightThreshold for i in geonodes if i.isSea])
            # set([i.id for i in geonodes if i.isSea])
        )
        self.seaLandMap = sl

        # 确定 大陆 岛屿，海洋 湖泊
        bsl1 = MapBaseTool.find_true_sea(l, sea_area, near_border)
        bsl2 = MapBaseTool.find_true_sea(s, sea_area, near_border)
        self.bigSeaLand = bsl1[0] | bsl2[0]

        # init cities
        geo_r = {}
        # for i in geonodes:
        #     geo_r[i.id] = i.cityRateRange
        for i in geonodes:
            if i.cityRateRange is None:
                continue
            geo_r[i.heightThreshold] = i.cityRateRange

        # print(geo_r, 'geo')
        city_pos = set(MapBaseTool.init_city_random(self.heightMap, geo_r))

        ## 划分领土
        if len(city_pos) >= 2**12:
            raise MemoryError("城市数量>= 2^12")

        __pos_id_dict = {}
        for i1, i in enumerate(city_pos):
            __pos_id_dict[i] = i1 + 2

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
                for y in range(1 - border_r, border_r):
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

        self.cities = __pos_id_dict
        # road
        self.roadNet = MapBaseTool.make_road_net(country_mp)

        # resource
        for y in range(self.heightMap.shape[0]):
            for x in range(self.heightMap.shape[1]):
                v = self.heightMap[y, x]
                __resource = set()
                # for k, v in self.geoNodes[v].resourceRange.items():
                # for k, v in geonodes[int]
                for k, v in geonode_dict[v].resourceRange.items():
                    if random.random() > v:
                        __resource.add(int(k))
                if len(__resource) == 0:
                    continue
                self.resourceDict[(y, x)] = __resource
        
        # global cost map
        self.globalCostMap = numpy.zeros(self.heightMap.shape, dtype=numpy.int8)
        for hm, gcm in zip(
            numpy.nditer(self.heightMap, op_flags=["readwrite"]),
            numpy.nditer(self.globalCostMap, op_flags=["readwrite"])
        ):
            gcm += numpy.int8(geonode_dict[int(hm)].globalCost)
        
        return self


class LogisticsSys:
    def __init__(self) -> None:
        self.data: Dict[Tuple[int, int], Dict[int, Tuple[List[Tuple[Person, Any, int]], set|None, dict]]] = {}

    def send(self, from_city: int, to_city: int, person: Tuple["Person", Any]=None, troops: set=None, resource: dict=None):
        pass

    def get_by_update(self) -> Dict[int, Tuple[List[Tuple[Person, Any, int]], set|None, dict]]:
        pass


class GameContext(MapBase):
    CLS_DICT: Dict[str, Any] = {}

    def __init__(self) -> None:
        super().__init__()
        self.class_dict: Dict[str, Any] = {}

        self.gameSetting: GameSetting
        self.logisticsSys: LogisticsSys = LogisticsSys()

        self.cities: Dict[int, 'City'] = {}
        self._cityPosDict: Dict[Tuple[int, int], 'City'] = {}

        self.persons: Dict[int, 'Person'] = {}

        self.groups: Dict[int, "Group"] = {}

        self.troops: Dict[int, "Troop"] = {}
        self._troopPosDict: Dict[Tuple[int, int], 'City'] = {}
        self.tradeRecord: Dict[int, 'ActionTradeWithGroup'] = {}

    def auto_init(self):
        group_amount = self.gameSetting.groupAmount
        # register class
        register_cls = [
            City, CityAtrLiving, CityAtrManufacture,
            CityAtrMarket, CityAtrProduce, CityAtrMilitary,
            CityAtrStorage, CityAtrTraffic, CityAtrUnder,
            Person, Troop, Group
        ]
        for i in register_cls:
            self.class_dict[i.__name__] = i

        self.load(self.gameSetting.settingFileRoot, self.gameSetting.mapSize, 
            sorted(self.gameSetting.geoNode, key=lambda a: a.heightThreshold)
        )
        # init cities
        __cities = []
        for pos, id_ in list(self.cities.items()):
            city = self.make_city(pos)
            # del self.cities[city.id]
            city.id = id_
            # self.cities[id_] = city
            __cities.append(city)
            city.aiCityModel = 'default'
            city.aiMoney = sys.maxsize
            p_nu = random.randint(1, 3)
            for i in range(p_nu):
                person = self.make_person()
                person.nowLoc = city.id, City
                city.politicianGroup[person] = 1 / p_nu
            
            for cls in [CityAtrLiving, CityAtrProduce, CityAtrManufacture, CityAtrMarket, CityAtrUnder]:
                p_nu = random.randint(1,4)
                for i in range(p_nu):
                    person = self.make_person()
                    person.nowLoc = city.id, cls
                    city.get_area_by_obj(cls()).group[person] = 1 / p_nu

            city.update_city_group()
            city.update_by_model(self.gameSetting)
            city.aiMoney = random.randint(0, self.gameSetting.cityMaxInitMoney)

            # 城市内军队
            troop = self.make_troop()
            person = self.make_person()
            person.nowLoc = troop
            troop.header = person
            troop.loc = city
            city.militaryArea.innerTroops.add(troop)

        self.cities.clear()
        for i in __cities:
            i: City
            self.cities[i.id] = i

        # init group
        group_amount = group_amount if len(self.cities) >= group_amount else len(self.cities)
        l_order = [i for i in range(1, len(self.cities))]
        # print(group_amount, l_order)
        l_order = random.sample(l_order, group_amount-1)
        l_order.append(len(self.cities))
        l_order.insert(0, 0)
        l_order.sort()
        for i in l_order[:-1]:
            power = self.make_group()
            __cities = [j + 2 for j in range(i, l_order[i+1])]
            for city in __cities:
                for trp in self.cities[city].militaryArea.innerTroops:
                    trp.belong = power
                    power.troops.append(trp)
                    power.commanders.add(trp.header)
                self.cities[city].belong = power
                power.cities.append(self.cities[city])
            loc_city = random.choice(__cities)
            power.loc = list(self.cities[loc_city].militaryArea.innerTroops)[0]
            p_nu = random.randint(1, 5)
            for _i in range(p_nu):
                person = self.make_person()
                person.nowLoc = power
                power.ministers.add(person)
            power.money = random.randint(100, 10000)
        
    def __get_one_uniqe_id(self, d0): # ?lock
        while True:
            _id = random.randint(100, 2**12)
            if _id in d0:
                continue
            break
        return _id

    def make_city(self, pos):
        city = City()
        city_id = self.__get_one_uniqe_id(self.cities)
        self.cities[city_id] = city
        city.id = city_id
        city.name = str(city_id)
        self._cityPosDict[pos] = city
        return city

    def make_group(self, header=None, belong=None):
        group = Group()
        group.id = self.__get_one_uniqe_id(set(self.groups).union(self.cities))
        if header is None:
            group.header = self.make_person()
        else:
            group.header = header

        group.belong = belong
        return group

    def make_person(self):
        person = Person()
        person.id = self.__get_one_uniqe_id(self.persons)
        person.name = f"p{person.id}"
        return person

    def make_troop(self, header=None, belong=None):
        troop = Troop()
        troop.id = self.__get_one_uniqe_id(set(self.groups).union(self.cities))
        troop.header = header if header is not None else self.make_person()
        troop.belong = belong
        return troop

    def make_trade(self):
        person = ActionTradeWithGroup()
        person.tradeId = self.__get_one_uniqe_id(self.tradeRecord)
        self.tradeRecord[person.tradeId] = person
        return person

    ### update
    def update_city(self, city: "City"):
        if city.aiFindPerson:
            pass
        city.update_by_model(self.gameSetting)
        city.update_city_group()
        # labour
        labours = city.livingArea.populication
        labours = int(city.produceArea.workEfficiency * labours) * city.produceArea.blocks

        # produce and rest labour
        storage_total = self.gameSetting.perBlockStorageValue * (city.storageArea.blocks - city.storageArea.militaryBlocks)
        produce_storage = city.storageArea.produceStorage
        rest_labour = 0
        for k, v in city.produceArea.produceWeight.items():
            k = str(k)
            labour_tmp = int(labours * v)
            perLabor = self.gameSetting.get_resource(id_=k).perLabor
            produce_storage[k] = produce_storage.get(k, 0) + labour_tmp // perLabor
            if produce_storage[k] > storage_total[k]:
                rest_labour += int((storage_total[k] - produce_storage[k]) / perLabor)

        # money
        city.aiMoney += int(labours * city.marketArea.profitRate)  # turmoil
        if random.random() > city.underArea.turmoilRate/self.gameSetting.turmoilScale:
            city.aiMoney - city.aiMoney // 5
        rest_labour_money = int(rest_labour * self.gameSetting.perRestLabourCost)
        city.aiMoney += rest_labour_money
        try:
            rest_labour_m_p = rest_labour_money // len(city.marketArea.tradeCitySet)
        except ZeroDivisionError:
            rest_labour_m_p = 0

        if rest_labour_m_p != 0:
            for i in city.marketArea.tradeCitySet:
                self.cities[i].aiMoney += rest_labour_m_p
        
        # manufacture
        manufacture_storage = city.storageArea.manufactureStorage
        rest_units = city.storageArea.militaryBlocks * self.gameSetting.perBlockArmyStorageValue
        rest_units -= sum(city.storageArea.manufactureStorage.values())
        should_del = []
        manufacture_blocks = city.manufactureArea.blocks
        for pos, l0 in city.manufactureArea.produceQueue.items():
            if l0[2] == 0:
                if rest_units - pos[1] <= 0:
                    continue
                manufacture_storage[pos[0]] = manufacture_storage.get(pos[0], 0) + pos[1]
                should_del.append(pos)
                continue
            
            if manufacture_blocks <= 0:
                continue
            manufacture_blocks -= 1

            for k, v in l0[1].items():
                if produce_storage.get([int(k)], 0) < v:
                    break
            else:
                city.manufactureArea.produceQueue[pos] = (l0[0], l0[1], l0[2]-1)
                for k, v in l0[1].items():
                    produce_storage[int(k)] -= v
        for i in should_del:
            del city.manufactureArea.produceQueue[i]

        # supply
        supply_troops = city.militaryArea.supplyTroops
        # for troop in supply_troops:
        #     if supply_troops
        #     supply_troops[troop] -= 1
        #     if troop.shouldSupply:


    def __count_cost_map(self, engine):
        pass

    def update_troop(self, troop: "Troop"):
        pass

    def tick(self):
        for city in self.cities.values():
            self.update_city(city)

    @classmethod
    def register_cls(cls):
        register_cls = [
            City, CityAtrLiving, CityAtrManufacture,
            CityAtrMarket, CityAtrProduce, CityAtrMilitary,
            CityAtrStorage, CityAtrTraffic, CityAtrUnder
        ]
        for i in register_cls:
            cls.CLS_DICT[i.__name__] = i

############################# controller #############################

########### about view
# about city
# about country
# about troop
# find

########## about operation
############################ net package / action ##########################

class Action:
    def __init__(self) -> None:
        pass


class ActionTransit:
    def __init__(self) -> None:
        self.personIds: List[int] = None
        self.troopIds: List[int] = None
        self.resource: Dict[int, int] = None
        self.fromCity: int
        self.comeCity: int

    def check(self):
        pass


class ActionTransitCity:
    def __init__(self) -> None:
        self.fromCity: int
        self.toCity: int
    
    def check(self):
        pass


class ActionApointPerson:
    def __init__(self) -> None:
        self.personId: "Person"
        self.to: str
        self.weight: float

############### city

class ActionSetCityTask:
    def __init__(self) -> None:
        self.cityId: int
        self.model: str = None
        self.findPerson: bool = None
        self.produceWeight: Dict[int, float] = None
        self.manufactureQueue: List[Tuple[int, int]] = None
        self.tradeCities: List[int] = None
        self.supplyTroops: List[int] = None


############### troop

class ActionSetTroop:
    def __init__(self) -> None:
        self.troopId: int = None
        self.locCityId: int = None
        self.headerId: int = None
        self.groupName: str = None
        self.staffIds: List[int] = None
        self.groupIds: List[int] = None
        self.troopModel: SetTroopModel = None
        self.target: Tuple[int, str] = None


############### group

class ActionSetGroup:
    def __init__(self) -> None:
        self.groupId: int = None
        self.groupName: str = None
        self.headerId: int = None
        self.staffIds: List[int] = None
        self.ministers: List[int] = None
        self.commanders: List[int] = None
        self.troops: List[int] = None
        self.cities: List[int] = None
        # self.unionShip: Dict[int, float] = None
        self.secondHeader: List[int] = None
        self.aiMilitaryMoneyRate: float = None
        self.aiCityMoneyWeight: Dict[int, float] = None
        self.subGroups: List[int] = None
        self.drop: bool = None


class ActionTradeWithGroup:
    def __init__(self) -> None:
        self.fromId: int
        self.groupId: int
        self.tradeId: int

        self.cities: List[int] = None
        self.troops: List[int] = None
        self.persons: List[int] = None
        self.money: int = None
        self.resource: Dict[int, int] = None
        self.groups: List[int] = None

        self.costCities: List[int] = None
        self.costTroops: List[int] = None
        self.costPersons: List[int] = None
        self.costMoney: int = None
        self.costResource: Dict[int, int] = None
        self.costGroups: List[int] = None


class ActionTradeWithGroupRlt:
    def __init__(self) -> None:
        self.tradeId: int
        self.isOk: bool


############################ game server ##########################
class GameLocalServer:
    def __init__(self) -> None:
        self.gameContext: GameContext = GameContext()
        self.gameContext.gameSetting = GameSetting()
        self.gameContext.gameSetting.load_data_from_local('data')

    def handle_action(self):
        pass

    def send_action(self):
        pass


class GameManager:
    def __init__(self) -> None:
        self.gameContext: GameContext = GameContext()
        self.gameContext.gameSetting = GameSetting()
        self.gameContext.gameSetting.load_data_from_local('data')

    def init_power(self):
        pass

    ############################ view ##########################

    ########################### handle #########################

    # 运输
    def transit(self, from_city: "City", to_city: "City", person: Tuple["Person", Any]=None, troops: set=None, resource: dict=None):
        pass

    # 人事
    def apoint(self, city: "City", person: "Person", weight, form_=None, to=None):
        pass

    def drop_person(self, city: "City", person: "Person", where):
        pass

    # 城市-经济
    def set_city_model(self, model=None, find_person=None):
        pass

    def set_manufacture_q(self, q: List[Tuple[int, int]]):
        pass

    def add_to_trade(self, source, target, up=None):
        pass

    # 军队
    def make_troop(self, city: "City", model, header: "Person"):
        pass

    def set_troop_cmder(self, troop: "Troop", ):
        pass

    def set_troop_model(self):
        pass

    def set_troop_source(self):
        pass

    def set_troop_target(self):
        pass

    # 政治
    def split_group(self, person):
        pass

    def delete_group(self, group):
        pass

    def allocate_cities(self, cities: set, old_group: "Group", new_group: "Group"):
        pass

    def allocate_troops(self, troops: Set['Troop'], old_group: "Group", new_group: "Group"):
        pass

    def allocate_persons(self, persons: Set['Person'], old_group: "Group", new_group: "Group"):
        pass

    def in_camp(self):
        pass

    def out_camp(self):
        pass

    def ask_from_group(self):
        pass

    def buy_from_group(self):
        pass

    def send_to_group(self):
        pass

    def change_stituation(self):
        pass

    # 

    def move_all_in_city(self):
        pass


if __name__ == "__main__":
    gm = GameManager()
    # print(gm.gameContext.gameSetting.__dict__)

    __TEST_PATH = r"/home/king/Downloads/2020013113291021.jpg"
    # __HEIGHT_PATH = r"/home/king/w/my-game/XEngine/tests/test.png"
    # __CITY_PATH = r"/home/king/w/my-game/XEngine/tests/test_city.png"

    gm.gameContext.gameSetting.settingFileRoot = __TEST_PATH
    gm.gameContext.gameSetting.mapSize = (15, 15)
    gm.gameContext.auto_init()
    gc = gm.gameContext
    gc.tick()
    while True:
        ipt = input("$: ")
        try:
            print(eval(ipt))
        except:
            print('error')

# min road Q
# gather resource
# trade up don't make anything
# 初始化参数 ;参数有id
# 取消仓库限制
# Excel非法字符 "
# 不得创建销毁城市
# 不能任命到市外战斗区
# a* 并不是最优，而是最快

###### 关于客户端，服务端 传输
## gameSetting 不即时更新

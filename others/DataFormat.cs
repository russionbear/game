using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Soup
{


    public class DataFormat
    {
        // Start is called before the first frame update
        //public void Test()
        //{
        //    //序列化成对象

        //    Studet student = JsonConvert.DeserializeObject<Studet>(json);
        //    //输出:张三
        //    Console.WriteLine(student.name);
        //    //序列化成
        //    resultJson = JsonConvert.SerializeObject(student);
        //    Console.WriteLine(resultJson);


        //}
    }

    #region game setting, params
    // param setting
    class SetCityModel
    {
        int livingBlocks;
        int produceBlocks;
        int manufactureBlocks;

        int storageBlock1;
        int militaryStorageBlocks;
        int buildHarbor = -1;
        int roadQuality = 0;
        int wallDefenseValue = -1;
    }

    class SetTroopModel
    {
        string name;
        int footment;
        int cavalry;
    }

    class SetUnit
    {
        int id;
        string name;
        string buildBuildingEnv;
        Dictionary<string, int> perBuildFrom;
        int progressLen;
        string introduction;
        bool canLoad;
        string move_atr;
        int move_v;
        string atk_atr;
        int atk_v;
        string def_atr;
        int def_v;
        string view_atr;
        int view_v;
    }


    class SetResource
    {
        string name;
        int id;
        string callName;
        Dictionary<string, int> perBuildFrom;
        int progressLen;
        int perLabor;
        int sellMoney;
    }


    class SetGeoNode
    {
        string name;
        int id;
        string callName;

        int globalCost;
        Dictionary<string, int> engineCost;


        int heightThreshold;
        bool isSea;
        int globalColor;

        (float, float) cityRateRange;
        Dictionary<int, int> resourceRange;
    }


    class SetGeneral
    {

        //public SetGeneral LoadFromData()
        //{
        //    for k, v in d0.items():

        //        setattr(int  k, v)
        //        return this;
        //}
    }

    class SetGenerics<T>
    {
        List<T> generics;
        private Dictionary<string, T> genericsNameDict;
        private Dictionary<int, T> genericsIdDict;
    }


    class GameSetting
    {
        string settingFileRoot;
        (int, int) mapSize;
        int groupAmount;
        //region 储存参数
        // unit
        List<SetUnit> units;
        private Dictionary<string, SetUnit> unitNameDict;
        private Dictionary<int, SetUnit> unitIdDict;
        // resource
        List<SetResource> resource;
        private Dictionary<int, SetResource> resourceIdDict;
        private Dictionary<string, SetResource> resourceNameDict;

        //
        // geo node
        List<SetGeoNode> geoNode;
        private Dictionary<int, SetGeoNode> geoNodeIdDict;
        private Dictionary<string, SetGeoNode> geoNodeNameDict;

        // city model
        List<SetCityModel> cityModel;
        private Dictionary<int, SetCityModel> cityModelIdDict;
        private Dictionary<string, SetCityModel> cityModelNameDict;

        // troop model
        List<SetTroopModel> troopModel;
        private Dictionary<int, SetTroopModel> troopModelIdDict;
        private Dictionary<string, SetTroopModel> troopModelNameDict;

        // unit, resource, geonode, citymodel, troopmodel
        //private List<Object> settingBlock;
        //endregion

        int perBlockPopulication;
        int perBlockStorageValue;
        int perBlockArmyStorageValue;
        int perBlockCost;
        int perWallDefenseCost;
        int harborCost;
        int perRoadCost;
        int turmoilScale;
        int perRestLabourCost;
        int cityMaxFindPerson;
        int cityMaxInitMoney;

        private List<string> personNames;
        private List<string> cityNames;
        private List<string> groupNames;

        public static GameSetting LoadData(string s0)
        {
            return JsonConvert.DeserializeObject<GameSetting>(s0);
        }

        //region 获取参数的方法
        public SetUnit GetUnit(int id)
        {
            return unitIdDict[id];
        }
        public SetUnit GetUnit(string name)
        {
            return unitNameDict[name];
        }

        public SetResource GetResource(int id)
        {
            return resourceIdDict[id];
        }
        public SetResource GetResource(string name)
        {
            return resourceNameDict[name];
        }

        public SetGeoNode GetGeoNode(int id)
        {
            return geoNodeIdDict[id];
        }
        public SetGeoNode GetGeoNode(string name)
        {
            return geoNodeNameDict[name];
        }


        public SetCityModel GeoCityModel(int id)
        {
            return cityModelIdDict[id];
        }
        public SetCityModel GetCityModel(string name)
        {
            return cityModelNameDict[name];
        }

        public SetTroopModel GetTroopModel(int id)
        {
            return troopModelIdDict[id];
        }
        public SetTroopModel GetTroopModel(string name)
        {
            return troopModelNameDict[name];
        }


        //endregion

        public string GetPersonName()
        {
            int index = Random.Range(0, personNames.Count - 1);
            string rlt = personNames[index];
            personNames.RemoveAt(index);
            return rlt;
        }

        public void FreePersonName(string name)
        {
            personNames.Add(name);
        }

        public string GetCityName()
        {
            int index = Random.Range(0, cityNames.Count - 1);
            string rlt = cityNames[index];
            cityNames.RemoveAt(index);
            return rlt;
        }

        public void FreeCityName(string name)
        {
            cityNames.Add(name);
        }


        ////
        //    def get_name(self, type_):
        //        pass

        //    def free_name(self, type_, name):
        //        pass

        //    def combat_judge(self):
        //        pass
    }

    #endregion

    class Person
    {
        int id;
        int kind;
        int evil;

        int aq;
        // 主，强硬，软弱，......印象决策
        List<int> character;

        int belong;
       string name;
        (int, int) nowLoc;
       //int nowLoc: Tuple[int, Any] |"Group"


        public void AutoInit()
        {
            belong = 0;
            kind = (int)Random.Range(0, 100);
            evil = (int)Random.Range(0, 100);
            aq = (int)Random.Range(kind, 100);
        }
    }



// group
class GroupBase
    {
        int id;
        int groupName;
        Person person;
        int belong;
        // 低于0.2必反，低于0.4随机反，低于0.6等待一个理由
        float loyalty;
        List<Person> staff;
    }

// 
class GroupTransaction
    {
        // [宣战，讲和]，[入盟，毁梦]，[索取/请求 物资/人物/军队/资金]

    }


class Group: GroupBase
    {
        // troop id
        int loc;

        List<Person> ministers;
        List<Person> commanders;

        List<Group> subGroups;
        List<Troop> troops;
        List<City> cities;

        int money;

        // int money: int  = -1

        Dictionary<int, int> unionShip;
        List<Person> secondHeader;
        GroupTransaction transaction;
        float aiMilitaryRate;
        Dictionary<int, float> aiCityMoneyWeight;

       //int aiMilitaryMoneyRate: float = 0.5
       //int aiCityMoneyWeight: Dict[int, float] = { }
    }

class Troop: GroupBase
    {
        //int loc: Tuple[int, int] | City
        (int, int) loc;
        Dictionary<int, int> units;
        List<Group> groups;
        SetTroopModel troopModel;
        (int, string) target;
        bool shouldSupply;
    }


    class CityAtrLiving
    {
        Dictionary<Person, int> group;
        int blocks;

        int populication;
        Person standardCitizen;
        List<Person> talentedPerson;
    }


class CityAtrProduce
    {
        List<int> resource;
        List<int> produceType;
        Dictionary<Person, float> group;
        float workEfficiency;
        int blocks;
        Dictionary<int, float> produceWeight;

    }


class CityAtrManufacture
    {
        Dictionary<Person, float> group;
        int blocks;
        float productQuality;
        Dictionary<(int, int), (Dictionary<int, int>, Dictionary<int, int>, int)> produceQueue;
        Dictionary<(int, int), int> blockedQueue;
    }


class CityAtrMarket
    {
        Dictionary<Person, float> group;
        Dictionary<int, int> tradeCitySet;
        float profitRate;
    }


class CityAtrStorage
    {
        int blocks;
        Dictionary<int, int> produceStorage;
        Dictionary<int, int> manufactureStorage;
    }


class CityAtrTraffic
    {
        int roadLen;
        // int roadQuality: float = 1
        float roadQuality;
        int perRoadCost;
        bool hasHarbor;
    }


class CityAtrMilitary
    {
        int wallDefenseValue;
        float defenseRate;
        float attackRate;

        List<Troop> innerTroops;
        Dictionary<Troop, int> supplyTroops;
    }


class CityAtrUnder
    {
        Dictionary<Person, float> group;
        Dictionary<Person, float> underGrou;

        List<Person> spies;
        float turmoilRate;
        List<Person> prison;
    }


class City
    {

        int id;
        string name;
        int belong;

        Dictionary<Person, float> politicianGroup;
        int aiMoney;
        string aiCityModel;
        //int aiCityModel: str = 'default'
        List<string> groupUpdateCache;
        bool aiFindPerson;
        List<string> characters;


        //(CityAtrLiving, CityAtrProduce, CityAtrManufacture, CityAtrMarket, CityAtrTraffic, CityAtrMilitary, CityAtrUnder, CityAtrStorage) cityArea;

        CityAtrLiving livingArea; // 1
        CityAtrProduce produceArea; // 2
        CityAtrManufacture manufactureArea; // 3
        CityAtrMarket marketArea; // 4
        CityAtrTraffic trafficArea; // 5
        CityAtrMilitary militaryArea; // 6
        CityAtrUnder underArea; // 7
        CityAtrStorage storageArea; // 8
                                    //int __areaCache = {
                                    //     // CityAtrLiving.__name__:int livingArea,
                                    //     // CityAtrProduce.__name__:int produceArea,
                                    //     // CityAtrManufacture.__name__:int manufactureArea,
                                    //     // CityAtrMarket.__name__:int marketArea,
                                    //     // CityAtrTraffic.__name__:int trafficArea,
                                    //     // CityAtrMilitary.__name__:int militaryArea,
                                    //     // CityAtrStorage.__name__:int 
                                    // }

        //for k, v inint __dict__.items():
        //            if re.match(r'[^_].*Area$', k) is not None:
        //               int __areaCache[v.__class__.__name__] = v

    }


    class RoadNet
    {
        Dictionary<(int, int), int> landRoadWeight;
//        List<int> landRoadWeight: Dict[Tuple[int, int], int] = {}
//// List<int> blockedCity: Set[int] = set()
//List<int> G = networkx.Graph()

//// land_roads_w 应该被 key[0] < key[1]
//def init_road_net(self, land_roads_w: Dict[Tuple[int, int], int]) :
//            for k, v in land_roads_w.items():
//                List<int> G.add_edge(k[0], k[1], weight = v)
//            List<int> landRoadWeight = land_roads_w

//        def block_city(self, city_id) :
//            List<int> G.remove_node(city_id)

//        def unblock_city(self, city_id) :
//            for keys, v in List<int> landRoadWeight.items():
//                if city_id in keys:
//List<int> G.add_edge(keys[0], keys[1], v)

          int weight(int src, int trg)
        {
            int first = src, second = trg;
            if (first > second)
            {
                first = trg;
                second = src;
            }
            if (landRoadWeight.ContainsKey((first, second)))
            {
                return landRoadWeight[(first, second)];
            }
            return -1;
        }
    }


    class MapBaesTool
    {

    }

    class Matrix<T>
    {
        T[,] data;
        public Matrix(int rows, int cols)
        {
            data = new T[rows, cols];
        }
    }


    //class MapBase
    //{
    //    //private Matrix4x4 matrix;


    //    //uint d0[][] ;
    //}


class LogisticsSys
    {
        List<(int , ActionTransit )> data;
    //    List<int> data: Dict[Tuple[int, int], Dict[int, Tuple[List[Tuple[Person, Any, int]], set|None, dict]]] = {}

        public void Send(ActionTransit pkg, int val)
        {
            data.Add((val, pkg));
        }

        public List<ActionTransit> GetByUpdate()
        {
            List<ActionTransit> rlt = new List<ActionTransit>();
            List<(int, ActionTransit)> newData = new List<(int, ActionTransit)>();
            for (int i = 0; i < data.Count; i++)
            {
                if (data[i].Item1 == 0)
                {
                    rlt.Add(data[i].Item2);
                }
                else
                {
                    newData.Add((data[i].Item1 - 1, data[i].Item2));
                }
            }
            return rlt;
        }
    }

    class GameContext
    {

        //List<int> heightMap: numpy.ndarray
        //List<int> seaLandMap: numpy.ndarray
        //List<int> globalCostMap: numpy.ndarray
        //List<int> bigSeaLand: Set[int]
        //// 0==sea, 1==empty land, >1==country==cityId
        //List<int> countryMap: numpy.ndarray
        //// key >=2
        //List<int> cities: Dict[Tuple[int, int], int] = { }
        //List<int> roadNet: RoadNet
        //List<int> resourceDict: Dict[Tuple[int, int], Set[int]] = { }

        //    Dictionary<int>
        //     List<int> cities: Dict[int, 'City'] = { }
        //     List<int> _cityPosDict: Dict[Tuple[int, int], 'City'] = { }

        //List<int> persons: Dict[int, 'Person'] = { }

        //List<int> groups: Dict[int, "Group"] = { }

        //List<int> troops: Dict[int, "Troop"] = { }
        //List<int> _troopPosDict: Dict[Tuple[int, int], 'City'] = { }
        //List<int> tradeRecord: Dict[int, 'ActionTradeWithGroup'] = { }

        Matrix<byte> heightMap;
        Matrix<byte> seaLandMap;
        Matrix<byte> globalCostMap;
        Matrix<byte> bigSeaLand;
        Matrix<byte> coutryMap;
        Dictionary<(int, int), List<int>> resourceDict;

        GameSetting gameSetting;

        // 上面的是在游戏不可变属性，下则可变
        LogisticsSys LogisticsSys;
        Dictionary<int, City> cities;
        Dictionary<int, Person> persons;
        Dictionary<int, Group> groups;
        Dictionary<int, Troop> troops;
        Dictionary<int, ActionTradeWithGroup> tradeRecord;
    }

    //public class PriorityQueue
    //{
    //    private List<Node> nodeList = new List<Node>();

    //    // 堆节点
    //    private class Node
    //    {
    //        //数据
    //        public object data { get; set; }

    //        public int val { get; set; }

    //        public Node(object data, int val)
    //        {
    //            this.data = data;
    //            this.val = val;
    //        }
    //    }

    //    public PriorityQueue()
    //    {
    //        nodeList.Add(null);
    //    }

    //    //获取队列数据数量
    //    public int GetCount()
    //    {
    //        return nodeList.Count - 1;
    //    }

    //    /// <summary>
    //    /// 添加数据
    //    /// </summary>
    //    /// <returns>The push.</returns>
    //    /// <param name="data">数据实体.</param>
    //    /// <param name="val">堆中根据此值来对数据进行比较.</param>
    //    public void Push(object data, int val)
    //    {
    //        nodeList.Add(new Node(data, val));

    //        //up
    //        Up(nodeList.Count - 1);
    //    }

    //    //取出数据
    //    public object Out()
    //    {
    //        if (nodeList.Count <= 1) return null;
    //        Node node = nodeList[1];
    //        nodeList[1] = nodeList[nodeList.Count - 1];
    //        nodeList.RemoveAt(nodeList.Count - 1);
    //        Down(1);
    //        return node.data;
    //    }

    //    //上浮
    //    private void Up(int addindex)
    //    {
    //        //父节点是否存在，并进行判断是否需要上浮
    //        if (addindex > 1 && (nodeList[addindex / 2].val > nodeList[addindex].val))
    //        {
    //            Node node = nodeList[addindex / 2];
    //            nodeList[addindex / 2] = nodeList[addindex];
    //            nodeList[addindex] = node;
    //            //递归 继续上浮
    //            Up(addindex / 2);
    //        }
    //    }

    //    //下沉
    //    private void Down(int index)
    //    {
    //        int targetIndex = 0;
    //        //左孩子是否存在
    //        if (index * 2 < nodeList.Count)
    //        {
    //            targetIndex = index * 2;
    //        }
    //        else
    //        {
    //            return;
    //        }
    //        //右孩子是否存在，如果存在与左孩子进行比较，去较小的一个
    //        if (targetIndex + 1 < nodeList.Count &&
    //           nodeList[targetIndex].val > nodeList[targetIndex + 1].val)
    //        {
    //            targetIndex += 1;
    //        }

    //        //与孩子进行比较
    //        if (nodeList[index].val < nodeList[targetIndex].val)
    //        {
    //            return;
    //        }

    //        //下沉
    //        Node node = nodeList[index];
    //        nodeList[index] = nodeList[targetIndex];
    //        nodeList[targetIndex] = node;

    //        //递归 继续下沉
    //        Down(targetIndex);
    //    }

    //}

    class Action
    {

    }

class ActionTransit
    {
        List<int> personIds;
        List<int> troopIds;
        Dictionary<int, int> resource;
        int fromCity;
        int comeCity;
    }


    class ActionTransitCity
    {
        int fromCity;
        int toCity;
    }


class ActionApointPerson
    {
        Person personId;
        string to;
        float weight;
    }

// city

class ActionSetCityTask
    {
        int cityId;
        string model;
        bool findPerson;
        Dictionary<int, float> produceWeigh;
        List<(int, int)> manufactureQueue;
        List<int> tradeCities;
        List<int> supplyTroops;
    }


// troop

class ActionSetTroop
    {
        int troopId;
        int locCityId;
        int headerId;
        string groupName;
        List<int> staffIds;
        List<int> groupIds;
        SetTroopModel troopModel;
        (int, string) target;
    }


// group

class ActionSetGroup
    {
        int groupId;
        string groupName;
        int headerId;
        List<int> staffIds;
        List<int> ministers;
        List<int> commanders;
        List<int> troops;
        List<int> cities;
        List<int> secondHeader;
        float aiMilitaryMoneyRate;
        Dictionary<int, float> aiCityMoneyWeight;
        List<int> subGroups;
        bool drop;
    }


class ActionTradeWithGroup
    {

        int fromId;
        int groupId;
        int tradeId;

        List<int> cities;
        List<int> troops;
        List<int> persons;
        List<int> money;
        List<int> resource;
        List<int> groups;

        List<int> costCities;
        List<int> costTroops;
        List<int> costPersons;
        int costMoney;
        Dictionary<int, int> costResource;
        List<int> costGroups;
    }


class ActionTradeWithGroupRlt
    {
        int tradeId;
        bool isOk;
    }


// game server //
class GameLocalServer
    {
        GameContext gameContext;

        //List<int> gameContext: GameContext = GameContext()
        //List<int> gameContext.gameSetting = GameSetting()
        //List<int> gameContext.gameSetting.load_data_from_local('data')
    }

    //def handle_action(self):
    //    pass

    //def send_action(self) :
    //    pass


}


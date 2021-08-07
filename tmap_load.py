#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :tmap_load.py
# @Time      :2021/7/22 16:06
# @Author    :russionbear
'''
(i, j)低i行, 第j列
'''
import time

from PyQt5.Qt import *
from PyQt5 import QtGui
from PyQt5 import QtCore
import functools
import sys
from map_load import DW , Geo, VMap, resource

# class QApp(QApplication):
#     def __init__(self):
#         super(QApp, self).__init__(sys.argv)
#         self.forbiden = False
#     def notify(self, a0: QtCore.QObject, a1: QtCore.QEvent) -> bool:
#         if not self.forbiden or a1.type() not in [QMouseEvent, QKeyEvent]:
#             return super(QApp, self).notify(a0, a1)
#
#     def timerGo(self, m):
#         self.forbiden = True
#         self.timer = QTimer()
#         self.timer.start(m)
#         self.timer.timeout.connect(self.timerStop)
#
#     def timerStop(self):
#         self.forbiden = False
#         self.timer.deleteLater()
#         # self.killTimer(self.timer)

qapp = QApplication(sys.argv)
# qapp = QApp()

class TMap(VMap):
    def initUI(self, name='test1', parent=None, block=(100, 100), winSize=(800, 800), brother=None):
        super(TMap, self).initUI(name, parent, block, winSize, brother)
        self.circle.deleteLater()
        del self.circled, self.circleStatus
        self.showFullScreen()
        self.canMove = (True if self.mapBlockSize[0]*self.mapSize[0] > self.width() else False,
                               True if self.mapBlockSize[1]*self.mapSize[1]>self.height() else False)
        x, y = (self.width()-self.mapBlockSize[0]*self.mapSize[0])//2, (self.height()-self.mapBlockSize[1]*self.mapSize[1])//2
        self.mapMove(x, y, True)

        #命令类型：存活多少单位，存活指定单位，防御某个建筑，存活多少建筑，拖住多少回合，回合内击杀，阻拦多少单位，阻拦某个单位，
        # 回合内消灭多少单位/资金，占领指挥部，消灭敌方，不消灭敌方某单位
        self.users = [{'flag':'red', 'enemy':['blue'], 'action':'right', 'command_bg':'会战', 'command':'消灭敌方', \
                       'outcome':0, 'money':99999, 'hero':'google', 'header_loc':None, 'canBeGua':False, 'bout':1, 'exp':2}, \
                      {'flag':'blue', 'enemy':['red'], 'action':'left', 'command_bg':'会战', 'command':'消灭敌方', \
                       'outcome':0, 'money':0, 'hero':'warhton', 'header_loc':None, 'canBeGua':False, 'bout':1, 'exp':2}]
        self.user = self.users[0]
        self.globalData = {'income':1000}
        self.bout = 1
        self.tUser = {'flag':'red'}

        self.costMap = None
        self.dwChoosed = None
        self.targetChoosed = None
        self.areaToChoose = []
        self.planToSupply = []
        self.roadsToChoose = {'point':0, 'roads':[], 'layers':[]}
        self.targetsToChoose = {'choosed':None, 'layers':[]}
        self.planToUnload = {'layers':[], 'data':[], 'loc':None}   # [[k:记录, odk2：可选落地点, 0：是否落地]]
        self.actionTreeList = [None, 'areashowed', 'pathshowed', 'targetshowed', 'gtargetshowed', 'unloadingshow']
        self.choose_status = None  # None, areashowd, pathshowed, targetshowd, gtargetshowed, unloadshow
        self.dwChoosedStatus = 'move'
        self.shouldShow = []

        self.dwsListWidget = None

        self.choosePathMenu = QFrame(self)
        layout_choosePath = QBoxLayout(QBoxLayout.TopToBottom)
        self.choose_btn_waiting = QPushButton('待命')
        self.choose_btn_waiting.clicked.connect(functools.partial(self.dwCpu,'waiting'))
        layout_choosePath.addWidget(self.choose_btn_waiting)
        self.choose_btn_attacking = QPushButton('攻击')
        self.choose_btn_attacking.clicked.connect(functools.partial(self.dwCpu,'attack'))
        layout_choosePath.addWidget(self.choose_btn_attacking)
        self.choose_btn_stealth = QPushButton('隐身')
        self.choose_btn_stealth.clicked.connect(functools.partial(self.dwCpu,'stealth'))
        layout_choosePath.addWidget(self.choose_btn_stealth)
        self.choose_btn_occupy = QPushButton('占领')
        self.choose_btn_occupy.clicked.connect(functools.partial(self.dwCpu,'occupy'))
        layout_choosePath.addWidget(self.choose_btn_occupy)
        self.choose_btn_loading = QPushButton('搭载')
        self.choose_btn_loading.clicked.connect(functools.partial(self.dwCpu,'loading'))
        layout_choosePath.addWidget(self.choose_btn_loading)
        self.choose_btn_unloading = QPushButton('卸载')
        self.choose_btn_unloading.clicked.connect(functools.partial(self.dwCpu,'unload'))
        layout_choosePath.addWidget(self.choose_btn_unloading)
        self.choose_btn_laymine = QPushButton('布雷')
        self.choose_btn_laymine.clicked.connect(functools.partial(self.dwCpu,'laymine'))
        layout_choosePath.addWidget(self.choose_btn_laymine)
        self.choose_btn_buy = QPushButton('计划补给')
        self.choose_btn_buy.clicked.connect(functools.partial(self.dwCpu,'buy'))
        layout_choosePath.addWidget(self.choose_btn_buy)
        self.choosePathMenu.setLayout(layout_choosePath)
        self.choosePathMenu.show()
        self.choosePathMenu.hide()

        self.unloadMenu = QFrame(self)
        layout_choosePath = QBoxLayout(QBoxLayout.TopToBottom)
        self.unloadMenuItems = []
        for i in range(5):
            tem_btn = QPushButton('完成')
            tem_btn.track = None
            layout_choosePath.addWidget(tem_btn)
            tem_btn.clicked.connect(functools.partial(self.dwCpu,'unloading', tem_btn))
            tem_btn.show()
            self.unloadMenuItems.append(tem_btn)
        self.unloadMenu.setLayout(layout_choosePath)
        self.unloadMenu.show()
        self.unloadMenu.hide()

        self.rightMenu = QFrame(self)
        layout_choosePath = QBoxLayout(QBoxLayout.TopToBottom)
        tem_action = QPushButton('胜利条件')
        tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'beforevictory'))
        layout_choosePath.addWidget(tem_action)
        tem_action = QPushButton('兵力')
        tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'forces'))
        layout_choosePath.addWidget(tem_action)
        # tem_action = QPushButton('读取记录')
        # tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'read'))
        # layout_choosePath.addWidget(tem_action)
        tem_action = QPushButton('保存记录')
        tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'save'))
        layout_choosePath.addWidget(tem_action)
        tem_action = QPushButton('退出')
        tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'exit'))
        layout_choosePath.addWidget(tem_action)
        tem_action = QPushButton('回合结束')
        tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'end'))
        layout_choosePath.addWidget(tem_action)
        self.rightMenu.setLayout(layout_choosePath)
        self.rightMenu.show()
        self.rightMenu.hide()
        self.canRightMenuShow = True

        self.Head = QFrame(self)
        self.Head.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.Head_head = QLabel(self.Head)
        self.Head_head.setPixmap(QPixmap(resource.find({'usage':'hero', 'name':self.user['hero']})['pixmap']).scaled(80, 80))
        self.Head_exp = QProgressBar(self.Head)
        self.Head_exp.setMaximum(int(resource.basicData['hero_f'][self.user['hero']]['max_energy']))
        self.Head_exp.setAlignment(Qt.AlignVCenter)
        self.Head_exp.valueChanged.connect(self.proValueChange)
        self.Head_exp.setValue(self.user['exp'])
        self.Head_name = QLabel(self.user['hero'])
        self.Head_money = QLabel('$'+str(self.user['money']))
        head_font = QFont('宋体', 20)
        head_font.setBold(True)
        self.Head_money.setFont(head_font)
        self.Head_name.setFont(head_font)
        self.Head.setStyleSheet('border-radius:5px;background-color:'+self.user['flag']+';')
        head_layout = QBoxLayout(QBoxLayout.LeftToRight)
        head_layout_ = QBoxLayout(QBoxLayout.TopToBottom)
        head_layout_.addWidget(self.Head_name)
        head_layout_.addWidget(self.Head_money)
        head_layout_.addWidget(self.Head_exp)
        head_layout.addWidget(self.Head_head)
        head_layout.addLayout(head_layout_)
        self.Head.setLayout(head_layout)
        self.Head.move(0, 0)
        self.Head.show()
        self.Head.raise_()

        self.infoView = QListWidget(self)
        self.infoView.show()
        self.infoView.hide()
        self.isCtrlDown = False

        self.isRun = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerStop)

        self.dwUpdater = QTimer(self)
        self.dwUpdater.timeout.connect(self.myUpdate)
        self.dwUpdater.start(1400)
        actions = {}
        for i in self.users:
            actions[i['flag']] = i['action']
        for i in self.pointer_dw:
            for j in i:
                if j:
                    j.doBody(actions[j.track['flag']])

        self.childWindow = QWidget()
        self.childWindow.setWindowModality(Qt.ApplicationModal)

        self.commands = []

    def judgement(self, dw:DW, endP, command):
        if not endP or not self.pointer_dw[endP[0]][endP[1]]:
            return
        self.isRun = False
        # 没有播放声音##################%%%%%%
        # time.sleep(0.2)
        self.isRun = True
        beginP = dw.mapId
        enemy = self.pointer_dw[endP[0]][endP[1]]
        ###此处忽略英雄加成
        at1 = float(resource.basicData['gf'][dw.track['name']][enemy.track['name']]) * \
              (float(resource.basicData['gfGeo_g'][dw.track['name']][self.pointer_geo[beginP[0]][beginP[1]].track['name']])/100 + 1) * \
              ((100-float(resource.basicData['gfGeo_f'][enemy.track['name']][self.pointer_geo[endP[0]][endP[1]].track['name']]))/100)
        at2 = float(resource.basicData['gf'][enemy.track['name']][dw.track['name']]) * \
              (float(resource.basicData['gfGeo_g'][enemy.track['name']][self.pointer_geo[endP[0]][endP[1]].track['name']])/100 + 1) * \
              ((100-float(resource.basicData['gfGeo_f'][dw.track['name']][self.pointer_geo[beginP[0]][beginP[1]].track['name']]))/100)
        if float(resource.basicData['gf'][enemy.track['name']]['gf_mindistance']) > 1 :
            at2 = 0
        elif enemy.bullect == 0:
            at2 = 0
        blood2 = enemy.bloodValue - at1 * dw.bloodValue /10
        blood2 = 0 if round(blood2) <= 0 else round(blood2, 1)
        blood1 = dw.bloodValue - at2 * blood2 /10
        blood1 = 0 if round(blood1) <= 0 else round(blood1, 1)
        dw1 = {}
        dw2 = {}
        if blood1 == 0 and blood2 == 0:
            dw.deleteLater()
            enemy.deleteLater()
            self.pointer_dw[beginP[0]][beginP[1]] = None
            self.pointer_dw[endP[0]][endP[1]] = None
            dw1['isAlive'] = False
            dw2['isAlive'] = False
            print('all has beng!!!!!!!')
        elif blood1 == 0:
            dw.deleteLater()
            self.pointer_dw[beginP[0]][beginP[1]] = None
            print('dw has beng!!!!')
            enemy.doBlood(blood2)
            dw1['isAlive'] = False
            dw2 = enemy.makeTrack()
        elif blood2 == 0:
            enemy.deleteLater()
            self.pointer_dw[endP[0]][endP[1]] = None
            print('enemy has beng!!!!')
            dw.doBlood(blood1)
            dw.doBody(self.user['action']+'G')
            dw.moved = True
            dw1 = dw.makeTrack()
            dw2['isAlive'] = False
        else:
            print('nothing has beng!!!')
            dw.doBlood(blood1)
            enemy.doBlood(blood2)
            dw.doBody(self.user['action']+'G')
            dw.moved = True
            dw1 = dw.makeTrack()
            dw2 = enemy.makeTrack()
        command['dw1'] = dw1
        command['dw2'] = dw2

    def timerStop(self):
        # if self.user['flag'] == self.tUser['flag']:
        if 1:
            if self.dwChoosedStatus == 'waiting':
                self.dwChoosed.doBody(self.user['action']+'G')
                self.dwChoosed.moved = True
                road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                command = {'type':self.dwChoosedStatus, 'road':road}
                self.commands.append(command)
            ### 非tUser单位只能由命令修改
            elif self.dwChoosedStatus == 'encounter':
                self.dwChoosed.doBody(self.user['action']+'G')
                self.dwChoosed.moved = True
                road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                command = {'type':self.dwChoosedStatus, 'road':road}
                self.commands.append(command)
            elif self.dwChoosedStatus == 'stealth':
                self.dwChoosed.doBody(self.user['action']+'G')
                if self.choose_btn_stealth.text() == '下潜':
                    self.dwChoosed.isDiving = not self.dwChoosed.isDiving
                else:
                    self.dwChoosed.isStealth = not self.dwChoosed.isStealth
                self.dwChoosed.moved = True
                road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                command = {'type':self.dwChoosedStatus, 'road':road}
                self.commands.append(command)
            elif self.dwChoosedStatus == 'attacking':
                if self.dwChoosed.mapId[1] + 1 == self.targetsToChoose['choosed'][1]:
                    self.dwChoosed.doBody('right')
                elif self.dwChoosed.mapId[1] - 1 == self.targetsToChoose['choosed'][1]:
                    self.dwChoosed.doBody('left')
                road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                command = {'type':self.dwChoosedStatus, 'road':road}
                self.judgement(self.dwChoosed, self.targetsToChoose['choosed'], command)
                self.commands.append(command)
            elif self.dwChoosedStatus == 'occupy':
                self.dwChoosed.occupied += round(self.dwChoosed.bloodValue)
                road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                command = {'type':self.dwChoosedStatus, 'road':road, 'occupy':self.dwChoosed.occupied}
                self.commands.append(command)
                if self.dwChoosed.occupied >= 20 :
                    dw = self.pointer_geo[self.dwChoosed.mapId[0]][self.dwChoosed.mapId[1]]
                    track = resource.find({'usage':'build', 'name':dw.track['name'], 'flag':self.user['flag']})
                    dw.change(track=track)
                    self.dwChoosed.occupied = 0
                self.dwChoosed.doBody(self.user['action']+'G')
                self.dwChoosed.moved = True
            elif self.dwChoosedStatus == 'loading':
                com = {}
                actions = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                com['hafuman'] = resource.findHafuman(self.dwChoosed.track['base64'])
                com['oil'] = self.dwChoosed.oil
                com['pixmap'] = self.dwChoosed.track['pixmap']
                com['bullect'] = self.dwChoosed.bullect
                com['blood'] = self.dwChoosed.bloodValue
                com['moved'] = False
                com['occupied'] = 0
                com['name'] = self.dwChoosed.track['name']
                com['cursor'] = len(self.pointer_dw[actions[-1][0]][actions[-1][1]].loadings)
                self.pointer_dw[actions[-1][0]][actions[-1][1]].loadings.append(com)
                self.pointer_dw[actions[0][0]][actions[0][1]] = None
                self.dwChoosed.deleteLater()
                road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                command = {'type':self.dwChoosedStatus, 'road':road}
                self.commands.append(command)
                print(self.pointer_dw)
            elif self.dwChoosedStatus == 'unloading':
                notDel = []
                print(self.planToUnload)
                dws = []
                for i in self.planToUnload['data']:
                    if i[2]:
                        print('is counting')
                        del i[0]['cursor'], i[0]['pixmap'], i[0]['name']
                        track = resource.findByHafuman(i[0]['hafuman'])
                        track.update(i[0])
                        dw = DW(self)
                        dw.initUI(track, i[2])
                        self.pointer_dw[i[2][0]][i[2][1]] = dw
                        dw.setGeometry(self.pointer_geo[i[2][0]][i[2][1]].geometry())
                        dw.moved = True
                        dw.oil = float(resource.basicData['gf'][track['name']]['oil'])
                        dw.bullect = float(resource.basicData['gf'][track['name']]['bullect'])
                        dw.show()
                        dw.raise_()
                        dw.doBody(self.user['action']+'G')
                        dws.append(dw.makeTrack())
                    else:
                        notDel.append(int(i[0]['cursor']))
                newloadings = []
                for i1, i in enumerate(self.dwChoosed.loadings):
                    if i1 in notDel:
                        newloadings.append(i)
                self.dwChoosed.loadings = newloadings
                self.dwChoosed.moved = True
                self.dwChoosed.doBody(self.user['action']+'G')
                road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                command = {'type':self.dwChoosedStatus, 'road':road, 'loadings':newloadings.copy(), 'dws':dws}
                self.commands.append(command)
                print(len(self.commands), self.commands)

            for i in self.shouldShow:
                i.show()
            self.isRun = True
            self.clear(None)
            self.timer.stop()
        else:
            pass

    def timerGo(self, m):
        self.isRun = False
        self.timer.start(m)

    def collectMap(self):
        map = {}
        map['map'] = []
        geos = iter(self.findChildren(Geo))
        for i in range(self.mapSize[1]):
            com = []
            for j in range(self.mapSize[0]):
                tem = geos.__next__()
                com.append(int(resource.findHafuman(tem.track['base64'])))
            map['map'].append(com)

        dws = []
        for i in self.findChildren(DW):
            com = {}
            com['hafuman'] = resource.findHafuman(i.track['base64'])
            com['axis'] = i.mapId
            com['oil'] = i.oil
            com['bullect'] = i.bullect
            com['blood'] = i.bloodValue
            com['moved'] = i.moved
            com['occupied'] = i.occupied
            dws.append(com)
        map['dw'] = dws
        self.map.update(map)
        # print(self.map)
        return self.map

    def suppliesCount(self):
        dwName = None
        geoName = None
        if self.dwChoosed.track['name'] == 'transport':
            dwName = 'transport'
            geoName = 'factory'
        elif self.dwChoosed.track['name'] == 'transportship':
            dwName = 'transportship'
            geoName = 'shipyard'

        e1 = []
        e2 = []
        for i in self.findChildren(Geo):
            if i.track['usage'] == 'build':
                if i.track['flag'] == self.user['flag'] and \
                        i.track['name'] == geoName:
                    e1.append(i)
        for i in self.findChildren(DW):
            if i.track['flag'] == self.user['flag'] and \
                    i.track['name'] == dwName and \
                    not i.moved:
                e2.append(i)
        if not e2 or not e1:
            print('here', e1, e2)
            return False
        tem_data_1 = {}
        for i1, i in enumerate(e2):
            costMap = self.costAreaCount(i)
            tem_data_1[str(i1)] = {'dws':[], 'geos':[]}
            for j1, j in enumerate(e2):
                if j1 == i1:
                    continue
                roads = self.roadCount(i, j.mapId, costMap)
                if roads:
                    cost = resource.basicData['move'][self.dwChoosed.track['name']]['move_distance']
                    oil = float(cost) if float(cost) <= self.dwChoosed.oil else self.dwChoosed.oil
                    for k in roads[0][1:]:
                        oil -= float(resource.basicData['move'][self.dwChoosed.track['name']][self.pointer_geo[k[0]][k[1]].track['name']])
                    if oil < 0:
                        continue
                else:
                    continue
                tem_data_1[str(i1)]['dws'].append((str(j1), len(roads[0])))
            for j1, j in enumerate(e1):
                roads = self.roadCount(i, j.mapId, costMap)
                if roads:
                    cost = resource.basicData['move'][self.dwChoosed.track['name']]['move_distance']
                    oil = float(cost) if float(cost) <= self.dwChoosed.oil else self.dwChoosed.oil
                    for k in roads[0][1:]:
                        oil -= float(resource.basicData['move'][self.dwChoosed.track['name']][
                                         self.pointer_geo[k[0]][k[1]].track['name']])
                    if oil < 0:
                        continue
                else:
                    continue
                tem_data_1[str(i1)]['geos'].append((str(j1), len(roads[0])))
            # tem_data_1[str(i1)]['dws'] = sorted(tem_data_1[str(i1)]['dws'], key=lambda arg:arg[1])
            tem_data_1[str(i1)]['geos'] = sorted(tem_data_1[str(i1)]['geos'], key=lambda arg:arg[1])
        end = []
        def supplyRoad(point, cache=[]):
            here_cache = cache[:]
            if point not in cache:
                here_cache.append(point)
            else:
                return
            if tem_data_1[point]['geos']:
                here_cache.append(tem_data_1[point]['geos'][0][0])
                end.append(here_cache)
                return
            for i in tem_data_1[point[0]]['dws']:
                supplyRoad(i[0], here_cache)
        for i1, i in enumerate(e2):
            if i == self.dwChoosed:
                supplyRoad(str(i1))
                break
        if not end:
            return False
        tend = []
        for i in end:
            for j in i[:-1]:
                tend.append(e2[int(j)].mapId)
                # print(e2[int(j)].mapId, end='')
            tend.append(e1[int(i[-1])].mapId)
            # print('\n', e1[int(i[-1])].mapId)
        self.planToSupply = tend
        return True

    def costAreaCount(self, dw:DW):
        '''-1:error, -2:不可停留， -3：运输车'''
        self.collectMap()
        cost = resource.basicData['move'][dw.track['name']]['move_distance']
        oil = float(cost) if float(cost) <= dw.oil else dw.oil
        if oil <= 0:
            return
        tem_map = []

        for i in self.map['map']:
            tem_map.append(i[:])
        for i, i1 in enumerate(tem_map):
            for j, j1 in enumerate(tem_map[i]):
                geo_name = resource.findByHafuman(str(j1))['name']
                tem_map[i][j] = int(resource.basicData['move'][dw.track['name']][geo_name])

        for j in self.users:
            if j['flag'] == dw.track['flag']:
                for i in self.findChildren(DW):
                    if i.track['flag'] in j['enemy'] and not i.isHidden():
                    # if i.track['flag'] != dw.track['flag']:
                        tem_map[i.mapId[0]][i.mapId[1]] = 99
                break
        # for i in tem_map:
        #     for j in i:
        #         print(j, ' ', end='')
        #     print()
        return tem_map

    def areaCount(self, dw:DW, costMap=None):
        cost = resource.basicData['move'][dw.track['name']]['move_distance']
        oil = float(cost) if float(cost) <= dw.oil else dw.oil

        tem_map = costMap if costMap else self.costAreaCount(dw)
        rows = len(tem_map)
        cols = len(tem_map[0])
        tem_area = [[-1 for i in range(cols)] for j in range(rows)]
        directions = [(1, 0), (-1, 0), (0, -1), (0, 1)]

        def area(beginP, oil):
            tem_area[beginP[0]][beginP[1]] = oil
            for i in directions:
                x, y = beginP[0]+i[0], beginP[1]+i[1]
                if x <0 or x >= rows or  y < 0 or y >= cols:
                    continue
                if tem_area[x][y] == -1 and oil - tem_map[x][y] >= 0:
                    area((x, y), oil - tem_map[x][y])
                elif tem_area[x][y] != -1 and oil - tem_map[x][y] > tem_area[x][y]:
                    area((x, y), oil - tem_map[x][y])
        area(dw.mapId, oil)
        # for i in tem_area:
        #     for j in i:
        #         print(j, ' ', end='')
        #     print()
        return tem_area

    def roadCount(self, dw:DW, last, costMap=None):
        print(last)
        if not costMap:
            print('roadCount error')
            return
        cost = resource.basicData['move'][dw.track['name']]['move_distance']
        oil = float(cost) if float(cost) <= dw.oil else dw.oil
        tem_map = costMap

        cols = len(tem_map[0])
        rows = len(tem_map)
        directions = [(1, 0), (-1,0), (0, -1), (0, 1)]
        end = []
        def road(beginP, endP, length, hasgo=[]):
            hasgo_ = hasgo[:]
            length_ = length - tem_map[beginP[0]][beginP[1]]
            hasgo_.append((beginP[0], beginP[1]))
            if length < 0:
                return
            if beginP[0] == endP[0] and beginP[1] == endP[1]:
                end.append(hasgo_[:])
                return
            for i in directions:
                x, y = beginP[0] + i[0], beginP[1]+i[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
                    continue
                if (x, y) not in hasgo:
                    road((x, y), endP, length_, hasgo_)

        road(dw.mapId, last, oil)
        return sorted(end, key=lambda arg: len(arg))

    ####有点特殊
    def findTarget(self, dw:DW, endP, moved=False):
        ###移动攻击 判断
        if resource.basicData['gf'][dw.track['name']]['attackAftermove'] == '0' and moved:
            return True
        max = resource.basicData['gf'][dw.track['name']]['gf_maxdistance']
        if max == 0 or dw.bullect == 0:
            return True
        min = resource.basicData['gf'][dw.track['name']]['gf_mindistance']
        x1, y1 = endP
        rows = len(self.map['map'])
        cols = len(self.map['map'][0])
        directions = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        # contain = []
        self.targetsToChoose['choosed'] = []
        for k in range(int(min), int(max)+1):
            for j in range(k+1):
                for i in directions:
                    x, y = x1 + j*i[0], y1 + (k - j)*i[1]
                    if x < 0 or x >= rows or y < 0 or y >= cols or ( (x, y) in self.targetsToChoose['choosed'] ):
                        continue
                    if self.pointer_dw[x][y]:
                        # print(self.pointer_dw[x][y].track['flag'], self.user['enemy'])
                        if self.pointer_dw[x][y].track['flag'] in self.user['enemy'] and not self.pointer_dw[x][y].isHidden():
                            if float(resource.basicData['gf'][dw.track['name']][self.pointer_dw[x][y].track['name']]) > 0:
                                self.targetsToChoose['choosed'].append((x, y))
                                # isEmpty = False
        return not self.targetsToChoose['choosed']

    '''
        waiting,  stealt, attacking, occupy, loading, unloading, bulld, buied, laymine
    '''
    #移动打断 待修改
    def dwCpu(self, type=None, data=None):
        if type == 'showarea':
            costMap = data
            # count = 0
            inner_map = self.areaCount(self.dwChoosed, costMap)
            # print(inner_map)
            for i1, i in enumerate(inner_map):
                for j1, j in enumerate(i):
                    if j != -1:
                        circle = QFrame(self)
                        circle.mapId = i1, j1
                        circle.setStyleSheet('border-radius:5px;border:3px solid rgb(0, 200,0)')
                        circle.show()
                        circle.setGeometry(self.pointer_geo[i1][j1].geometry())
                        self.areaToChoose.append(circle)
            #             count += 1
            # if count == 0:
            #     return False
            # return True
        ###巨型坦克+树林 = bug
        elif type == 'showpath':
            for j in self.areaToChoose:
                j.hide()
            for j in self.roadsToChoose['roads'][self.roadsToChoose['point']]:
                circle = QFrame(self)
                circle.setStyleSheet('border-radius:5px;border:3px solid rgb(100, 100,200)')
                circle.show()
                circle.setGeometry(self.pointer_geo[j[0]][j[1]].geometry())
                self.roadsToChoose['layers'].append(circle)
        ####待改进
        elif type == 'showgftargets':
            a0 = data
            for i in self.findChildren(DW):
                if i.geometry().contains(a0.pos()):
                    end = []
                    max = resource.basicData['gf'][i.track['name']]['gf_maxdistance']
                    if max == 0 or i.bullect == 0:
                        return True
                    min = resource.basicData['gf'][i.track['name']]['gf_mindistance']
                    x1, y1 = i.mapId[0], i.mapId[1]
                    rows = len(self.map['map'])
                    cols = len(self.map['map'][0])
                    directions = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

                    for k in range(int(min), int(max) + 1):
                        for j in range(k + 1):
                            for i in directions:
                                x, y = x1 + j * i[0], y1 + (k - j) * i[1]
                                if x < 0 or x >= rows or y < 0 or y >= cols or (x, y) in end:
                                    continue
                                end.append((x, y))
                    for i in end:
                        circle = QFrame(self)
                        circle.setStyleSheet('border-radius:5px;border:3px solid rgb(200, 0,0)')
                        circle.show()
                        circle.raise_()
                        circle.setGeometry(self.pointer_geo[i[0]][i[1]].geometry())
                        circle.mapId = self.pointer_geo[i[0]][i[1]].mapId
                        self.targetsToChoose['layers'].append(circle)

                    return True
            return False
        elif type == 'waiting':
            self.dwChoosedStatus = 'waiting'
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            self.dwChoosed.mapId = tuple(road[-1])
            self.animeMove(road)
        elif type == 'stealth':
            self.dwChoosedStatus = 'stealth'
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            self.dwChoosed.mapId = tuple(road[-1])
            self.animeMove(road)
        elif type == 'attack':
            self.dwChoosedStatus = 'attacking'
            for j in self.targetsToChoose['choosed']:
                circle = QFrame(self)
                circle.setStyleSheet('border-radius:5px;border:3px solid rgb(200, 0,0)')
                circle.show()
                circle.setGeometry(self.pointer_geo[j[0]][j[1]].geometry())
                circle.mapId = j[0], j[1]
                self.targetsToChoose['layers'].append(circle)
            for i in self.roadsToChoose['layers']:
                i.hide()
            self.choosePathMenu.hide()
            self.choose_status = 'targetshowed'
        elif type == 'attacking':
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            self.dwChoosed.mapId = tuple(road[-1])
            for i in self.targetsToChoose['layers']:
                if tuple(i.mapId) != self.targetsToChoose['choosed']:
                    i.hide()
            self.animeMove(road)
        elif type == 'occupy':
            self.dwChoosedStatus = 'occupy'
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            self.dwChoosed.mapId = tuple(road[-1])
            for i in self.targetsToChoose['layers']:
                if tuple(i.mapId) != self.targetsToChoose['choosed']:
                    i.hide()
            self.animeMove(road)
        elif type == 'loading':
            self.dwChoosedStatus = 'loading'
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            # self.dwChoosed.mapId = tuple(road[-1])
            for i in self.targetsToChoose['layers']:
                if tuple(i.mapId) != self.targetsToChoose['choosed']:
                    i.hide()
            self.animeMove(road)
        elif type == 'unload':
            self.choose_status = 'unloadingshow'
            points = []
            for i in self.planToUnload['data']:
                for j in i[1]:
                    if j not in points:
                        points.append(j)
            for i in points:
                circle = QFrame(self)
                circle.setStyleSheet('border-radius:5px;border:3px solid rgb(200, 0,0)')
                circle.show()
                circle.setGeometry(self.pointer_geo[i[0]][i[1]].geometry())
                circle.mapId = i
                circle.isBlack = False
                self.planToUnload['layers'].append(circle)
            for i in self.roadsToChoose['layers']:
                i.hide()
            self.choosePathMenu.hide()
        elif type == 'unloading':
            # self.dwChoosedStatus = 'unloading'
            self.unloadMenu.hide()
            if not data.track:
                self.dwChoosedStatus = 'unloading'
                road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                self.dwChoosed.mapId = tuple(road[-1])
                self.animeMove(road)
            else:
                for i in self.planToUnload['data']:
                    if i[0] == data.track:
                        i[2] = self.planToUnload['loc']
                        # print(i[2])
                        data.hide()
                        for j in self.planToUnload['layers']:
                            if tuple(j.mapId) == tuple(self.planToUnload['loc']):
                                j.isBlack = True
                                j.setStyleSheet('border-radius:5px;border:3px solid rgb(0, 0, 0)')
                            else:
                                for k in self.planToUnload['data']:
                                    if tuple(j.mapId) in k[1] and not k[2]:
                                        break
                                else:
                                    j.setStyleSheet('border-radius:5px;border:3px solid rgb(0, 0, 0)')
                                    j.isBlack = True
                        for j in self.planToUnload['layers']:
                            if not j.isBlack:
                                break
                        else:
                            self.dwChoosedStatus = 'unloading'
                            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                            self.dwChoosed.mapId = tuple(road[-1])
                            self.animeMove(road)
                        break
                # print()
        elif type == 'showbuild':
            self.dwsListWidget = QListWidget()
            self.dwsListWidget.setWindowModality(QtCore.Qt.ApplicationModal)
            self.dwsListWidget.itemDoubleClicked.connect(self.dwCpu)
            self.dwsListWidget.setWindowTitle('选择单位')
            self.dwsListWidget.setFixedSize(300, 300)
            keys = resource.basicData['geo']['canbuild'][data]
            tem_end = []
            for i in resource.findAll({'usage':'dw', 'flag':self.user['flag'], 'action':'left'}):
                if i['name'] == 'delete':
                    continue
                if resource.basicData['money']['classify'][i['name']] in keys or i['name'] in keys:
                    money = resource.basicData['money']['money'][i['name']]
                    text = resource.basicData['money']['chineseName'][i['name']]+'\t\t'+money+'$'
                    tem_end.append((i['pixmap'], text, i['name'], float(money)))
            tem_end = sorted(tem_end, key=lambda arg:arg[3])
            for i in tem_end:
                QListWidgetItem(QIcon(i[0]), i[1], self.dwsListWidget).name = i[2]
            self.dwsListWidget.show()
            self.dwChoosedStatus = 'builddw'
        ###原地购买
        elif isinstance(type, QListWidgetItem):
            if self.dwChoosedStatus == 'builddw':
                if self.user['money'] < float(resource.basicData['money']['money'][type.name]):
                    self.dwsListWidget.setWindowTitle('资金不足')
                else:
                    dw = DW(self)
                    dw.initUI({'usage':'dw', 'name':type.name, 'flag':self.user['flag'], 'action':self.user['action']+'G'}, self.dwChoosed)
                    dw.setGeometry(self.pointer_geo[self.dwChoosed[0]][self.dwChoosed[1]].geometry())
                    self.pointer_dw[self.dwChoosed[0]][self.dwChoosed[1]] = dw
                    dw.moved = True
                    dw.show()
                    dw.raise_()
                    self.dwsListWidget.close()
                    self.user['money'] -= float(resource.basicData['money']['money'][type.name])
                    self.user['outcome'] += float(resource.basicData['money']['money'][type.name])
                    #%%%%%%%
                    command = {'type':'builddw', 'flag':self.user['flag'], 'dw':dw.makeTrack(), 'user':self.user.copy()}
                    self.commands.append(command)

            # elif self.dwChoosedStatus == 'buy':
            #
        elif type == 'buy':
            self.dwChoosedStatus = 'buy'
            self.dwsListWidget = QWidget()
            self.dwsListWidget.setWindowModality(QtCore.Qt.ApplicationModal)
            layout = QFormLayout()
            self.dwsListWidget.setWindowTitle('选择单位')
            self.dwsListWidget.setFixedSize(300, 300)
            keys = resource.basicData['geo']['canbuild']['factory' if self.dwChoosed.track['name'] == 'transport' else 'shipyard']
            tem_end = []
            for i in resource.findAll({'usage': 'dw', 'flag': self.user['flag'], 'action': 'left'}):
                if i['name'] == 'delete':
                    continue
                if resource.basicData['money']['classify'][i['name']] in keys or i['name'] in keys:
                    money = resource.basicData['money']['money'][i['name']]
                    text = resource.basicData['money']['chineseName'][i['name']] + '\t\t' + money + '$'
                    tem_end.append((i['pixmap'], text, i['name'], float(money)))
            tem_end = sorted(tem_end, key=lambda arg: arg[3])
            for i in tem_end:
                tem_btn = QPushButton(QIcon(i[0]), i[1])
                tem_btn.setStyleSheet("border:none;")
                tem_btn.setFocusPolicy(Qt.NoFocus)
                tem_spin = QSpinBox()
                tem_spin.setMaximum(self.user['money'])
                tem_spin.name = i[2]
                tem_spin.money = i[3]
                layout.addRow(tem_btn, tem_spin)
            tem_btn_1 = QPushButton('确定')
            tem_bnt_2 = QPushButton("取消")
            tem_bnt_2.clicked.connect(functools.partial(self.dwCpu, 'buied', 'quit'))
            tem_btn_1.clicked.connect(functools.partial(self.dwCpu, 'buied', 'sure'))
            layout.addRow(tem_btn_1, tem_bnt_2)
            self.dwsListWidget.setLayout(layout)
            self.dwsListWidget.show()
            self.choosePathMenu.hide()
            self.choose_status = None

        elif type == 'buied':
            if data == 'sure':
                # print(self.plan)
                end = {}
                all = 0
                for i in self.dwsListWidget.findChildren(QSpinBox):
                    price = float(i.value())
                    if price:
                        end[i.name] = price
                        all += price
                if all > self.user['money']:
                    self.dwsListWidget.setWindowTitle('资金不足')
                elif all == 0:
                    self.clear(None)
                    self.dwsListWidget.close()
                else:
                    for i, j in end.items():
                        if i in self.dwChoosed.supplies:
                            self.dwChoosed.supplies[i] += end[i]
                        else:
                            self.dwChoosed.supplies[i] = end[i]
                    self.dwsListWidget.close()
                    dws = []
                    for i in self.planToSupply[:-1]:
                        self.pointer_dw[i[0]][i[1]].doBody(self.user['action']+'G')
                        self.pointer_dw[i[0]][i[1]].moved = True
                        dws.append(self.pointer_dw[i[0]][i[1]].mapId)

                    command = {'type':'buied', 'flag':self.user['flag'], 'supplies':self.dwChoosed.supplies.copy(), 'dws':dws, 'user':self.user.copy()}
                    self.commands.append(command)

                    self.clear(None)
                    self.dwsListWidget.close()

            elif data == 'quit':
                self.clear(None)
                self.dwsListWidget.close()

        else:
            print(type, data)

    def dwCommandCpu(self, road, type, data=None):
        if type == 'waiting':
            pass

    ##只能被tUser调用哦
    def animeMove(self, actions):
        inter_time = 200
        directions = [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        cols = len(self.map['map'][0])
        rows = len(self.map['map'])
        self.shouldShow = []
        for i1, i in enumerate(actions):
            tem_dw = self.pointer_dw[i[0]][i[1]]
            if tem_dw:
                if tem_dw.track['flag'] in self.user['enemy'] and i1 != len(actions) -1:
                    actions = actions[0:i1]
                    self.dwChoosedStatus = 'encounter'
                    break
            for j in directions:
                x, y = i[0]+j[0], i[1]+j[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
                    continue
                tem_dw = self.pointer_dw[x][y]
                if tem_dw:
                    if tem_dw.track['flag'] in self.user['enemy'] and tem_dw.isHidden() and tem_dw not in self.shouldShow:
                        self.shouldShow.append(tem_dw)

        group = QSequentialAnimationGroup(self)
        for i in range(len(actions[:-1])):
            self.dwChoosed.raise_()
            tem_anime = QPropertyAnimation(self.dwChoosed, b'pos', self)
            tem_anime.setStartValue(self.pointer_geo[actions[i][0]][actions[i][1]].pos())
            tem_anime.setEndValue(self.pointer_geo[actions[i+1][0]][actions[i+1][1]].pos())
            tem_anime.setDuration(inter_time)
            if i == 0:
                tem_anime.setEasingCurve(QEasingCurve.InQuad)
            group.addAnimation(tem_anime)
        for i in self.roadsToChoose['layers']:
            i.hide()
        self.choosePathMenu.hide()
        if len(actions) != 1:
            self.dwChoosed.occupied = 0
            if self.dwChoosedStatus != 'loading':
                self.pointer_dw[actions[0][0]][actions[0][1]] = None
                self.pointer_dw[actions[-1][0]][actions[-1][1]] = self.dwChoosed

        if actions[-1][1] > actions[0][1]:
            self.dwChoosed.doBody('right')
        elif actions[-1][1] < actions[0][1]:
            self.dwChoosed.doBody('left')
        group.start()
        self.timerGo((len(actions)-1)*inter_time)
        # qapp.timerGo(len(actions)*inter_time)

    def clear(self, toChooseStatus):
        if toChooseStatus == 'return':
            if self.choose_status == 'unloadingshow':
                for i in self.planToUnload['layers']:
                    i.hide()
                self.choosePathMenu.show()
                self.choosePathMenu.raise_()
                self.unloadMenu.hide()
                self.choose_status = 'pathshowed'
            elif self.choose_status == 'targetshowed':
                for i in self.targetsToChoose['layers']:
                    i.hide()
                self.choosePathMenu.show()
                self.choosePathMenu.raise_()
                self.choose_status = 'pathshowed'
            elif self.choose_status == 'pathshowed':
                for i in self.roadsToChoose['layers']:
                    i.hide()
                for i in self.areaToChoose:
                    i.show()
                self.choosePathMenu.hide()
                self.choose_status = 'areashowed'
            elif self.choose_status == 'areashowed':
                self.clear(None)
            return
        elif toChooseStatus == None:
            for i in [self.areaToChoose, self.roadsToChoose['layers'], self.targetsToChoose['layers'], self.planToUnload['layers']]:
                for j in i:
                    j.deleteLater()
            self.dwChoosed = None
            self.areaToChoose = []
            self.roadsToChoose = {'point':0, 'roads':[], 'layers':[]}
            self.targetsToChoose = {'choosed':None, 'layers':[]}
            self.choosePathMenu.hide()
            self.planToUnload = {'layers': [], 'data': [], 'loc': None}
            self.unloadMenu.hide()
        elif toChooseStatus == 'areashowed':
            for i in [self.roadsToChoose['layers'], self.targetsToChoose['layers'], self.planToUnload['layers']]:
                for j in i:
                    j.deleteLater()
            for i in self.areaToChoose:
                i.show()
            self.roadsToChoose = {'point':0, 'roads':[], 'layers':[]}
            self.targetsToChoose = {'choosed':None, 'layers':[]}
            self.choosePathMenu.hide()
            self.planToUnload = {'layers': [], 'data': [], 'loc': None}
            self.unloadMenu.hide()
        elif toChooseStatus == 'pathshowed':
            for i in [self.targetsToChoose['layers'], self.planToUnload['layers']]:
                for j in i:
                    j.deleteLater()
            for i in self.roadsToChoose['layers']:
                i.show()
            self.targetsToChoose = {'choosed':None, 'layers':[]}
            self.choosePathMenu.show()
            self.choosePathMenu.raise_()
            self.planToUnload = {'layers': [], 'data': [], 'loc': None}
            self.unloadMenu.hide()
        self.choose_status = toChooseStatus

    '''选择， 移动， 缩放'''
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self.isRun:
            return
        self.canRightMenuShow = True
        self.rightMenu.hide()

        # if self.isCtrlDown:
        #     for i in self.findChildren(DW):
        #         if i.geometry().contains(a0.pos()):
        #             for j in self.infoView.children():
        #                 j.deleteLater()
        #             self.infoView.addItem(QListWidgetItem(QIcon(resource.find({'usage':'dw2', 'name':'oil'})['pixmap']), 'oil\t'+str(i.oil)))
        #             self.infoView.addItem(QListWidgetItem(QIcon(resource.find({'usage':'dw2', 'name':'bullect'})['pixmap']), 'bullect\t'+str(i.bullect)))
        #             for j in i.loadings:
        #                 self.infoView.addItem(QListWidgetItem(QIcon(j['pixmap']), j['name']))
        #             for j1, j in i.supplies.items():
        #                 self.infoView.addItem(QListWidgetItem(j1+'\t$'+str(j)))
        #             self.infoView.move(a0.pos())
        #             self.infoView.show()
        #             self.infoView.raise_()
        #             break
        #     return

        if a0.button() == 1 and not self.hasMove:
            if self.choose_status == None: #0:
                self.clear(None)
                for i in self.findChildren(DW):
                    if i.track['flag'] in self.user['enemy'] and i.isHidden():
                        continue
                    if i.contains(a0.pos()):
                        self.dwChoosed = i
                        self.costMap = self.costAreaCount(i)
                        self.dwCpu('showarea', self.costMap)
                        self.choose_status = 'areashowed'
                        break
                else:
                    tem_dw = self.childAt(a0.pos())
                    if hasattr(tem_dw, 'track'):
                        if tem_dw.track['usage'] == 'build':
                            if tem_dw.track['flag'] == self.user['flag'] and tem_dw.track['name'] in ['factory', 'shipyard', 'airport']:
                                self.clear(None)
                                self.dwChoosed = tuple(tem_dw.mapId)
                                self.dwCpu('showbuild', tem_dw.track['name'])
                            else:
                                self.clear(None)
                        else:
                            self.clear(None)
                    else:
                        self.clear(None)

            elif self.choose_status == 'areashowed': #1: user want to choose a tartget to show paths
                for i in self.areaToChoose:
                    if i.geometry().contains(a0.pos()):
                        self.targetsToChoose['choosed'] = tuple(i.mapId)
                        for j in self.choosePathMenu.findChildren(QPushButton):
                            j.hide()
                        self.choose_btn_waiting.show()

                        #过滤 敌方单位，已移动过的单位
                        if self.dwChoosed.moved or self.dwChoosed.track['flag'] != self.user['flag']:
                            self.clear(None)
                            return

                        ###补给计划
                        if tuple(self.dwChoosed.mapId) == tuple(i.mapId):
                            if 'transport' in self.dwChoosed.track['name']:
                                if self.suppliesCount():
                                    if self.dwChoosed.moved:
                                        self.dwCpu('buy')
                                    else:
                                        self.choose_btn_buy.show()
                            ###原地布雷
                            elif resource.basicData['money']['canlaymine'][self.dwChoosed.track['name']] == '1':
                                self.choose_btn_laymine.show()

                        tem_dw = self.pointer_dw[i.mapId[0]][i.mapId[1]]           #####应小心改变它的值 ,可能值为：运输单位，None，隐形敌方单位
                        if tem_dw:
                            if tem_dw.track['flag'] in self.user['enemy'] and tem_dw.isHidden():
                                tem_dw = None

                        ###占领
                        if self.pointer_geo[i.mapId[0]][i.mapId[1]].track['usage'] == 'build' and \
                                resource.basicData['money']['classify'][self.dwChoosed.track['name']] == 'foot':
                            if self.pointer_geo[i.mapId[0]][i.mapId[1]].track['flag'] in self.user['enemy'] or \
                                    self.pointer_geo[i.mapId[0]][i.mapId[1]].track['flag'] == 'none':
                                self.choose_btn_occupy.show()

                        ###攻击
                        if (resource.basicData['gf'][self.dwChoosed.track['name']]['attackAftermove'] == '0' and \
                            tuple(self.dwChoosed.mapId) == tuple(i.mapId)) or \
                                resource.basicData['gf'][self.dwChoosed.track['name']]['attackAftermove'] == '1':
                            tem_end = self.findTarget(self.dwChoosed, i.mapId)
                            if not tem_end:
                                self.choose_btn_attacking.show()

                        ###隐身
                        if resource.basicData['money']['canstealth'][self.dwChoosed.track['name']] == '1':
                            if self.dwChoosed.isStealth:
                                self.choose_btn_stealth.setText('显身')
                            else:
                                self.choose_btn_stealth.setText('隐身')
                            self.choose_btn_stealth.show()
                        if resource.basicData['money']['candiving'][self.dwChoosed.track['name']] == '1':
                            if self.dwChoosed.isDiving:
                                self.choose_btn_stealth.setText('上浮')
                            else:
                                self.choose_btn_stealth.setText('下潜')
                            self.choose_btn_stealth.show()
                        ####装载
                        if tem_dw and tuple(i.mapId) != tuple(self.dwChoosed.mapId):
                            if tem_dw.track['name'] in \
                                    resource.basicData['money']['canloading'][tem_dw.track['name']] or\
                                resource.basicData['money']['classify'][self.dwChoosed.track['name']] in \
                                    resource.basicData['money']['canloading'][tem_dw.track['name']]:
                                if len(tem_dw.loadings) < int(resource.basicData['money']['canloading'][tem_dw.track['name']][0:1]):
                                    for j in self.choosePathMenu.findChildren(QPushButton):
                                        j.hide()
                                    self.choose_btn_loading.show()
                                else: #过滤装满的单位
                                    continue
                            else:##过滤 友方己方单位
                                continue
                        ####卸载
                        if self.dwChoosed.loadings:
                            self.planToUnload['data'] = []
                            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                            cols = len(self.map['map'][0])
                            rows = len(self.map['map'])
                            for k in self.dwChoosed.loadings:
                                for j in self.planToUnload['data']:
                                    if j[0] == k:
                                        break
                                else:
                                    odk2 = []
                                    for j in directions:
                                        x, y = i.mapId[0]+j[0], i.mapId[1] + j[1]
                                        if x >= 0 and x < rows and  y >= 0 and y < cols:
                                            if int(resource.basicData['move'][k['name']][self.pointer_geo[x][y].track['name']]) < 99 and not self.pointer_dw[x][y]:
                                                odk2.append((x, y))
                                    if odk2:
                                        self.planToUnload['data'].append([k, odk2, False])
                            if self.planToUnload['data']:
                                self.choose_btn_unloading.show()
                                for j in self.unloadMenuItems:
                                    j.hide()
                                for j1, j in enumerate(self.planToUnload['data']):
                                    self.unloadMenuItems[j1].setText(resource.basicData['money']['chineseName'][j[0]['name']]+'('+str(j[0]['cursor']+1)+')')
                                    self.unloadMenuItems[j1].setIcon(QIcon(j[0]['pixmap']))
                                    self.unloadMenuItems[j1].track = j[0]


                        #####显示路径
                        self.roadsToChoose['roads'] = self.roadCount(self.dwChoosed, i.mapId, self.costMap)
                        self.dwCpu('showpath')

                        ###显示菜单
                        x1, y1 = a0.x(), a0.y()
                        if x1 + self.choosePathMenu.width()>self.width():
                            x1 = self.width() - self.choosePathMenu.width()
                        if y1 + self.choosePathMenu.height()>self.height():
                            y1 = self.height() - self.choosePathMenu.height()
                        self.choosePathMenu.move(x1, y1)
                        self.choosePathMenu.show()
                        self.choosePathMenu.raise_()
                        self.choose_status = 'pathshowed'# 2
                        break
                else:
                    self.clear(None)

            elif self.choose_status == 'targetshowed':#3:
                for i in self.targetsToChoose['layers']:
                    if i.geometry().contains(a0.pos()):
                        self.targetsToChoose['choosed'] = i.mapId
                        self.dwCpu('attacking')
                        break
                else:
                    self.clear(None)
                    self.choosePathMenu.hide()

            elif self.choose_status == 'unloadingshow':
                for i in self.planToUnload['layers']:
                    if i.geometry().contains(a0.pos()) and not i.isBlack:
                        for j in self.unloadMenuItems:
                            j.hide()
                        self.planToUnload['loc'] = i.mapId
                        for j in self.unloadMenuItems:
                            for k in self.planToUnload['data']:
                                if k[0] == j.track:
                                    if tuple(i.mapId) in k[1] and not k[2]:
                                        j.show()
                        self.unloadMenuItems[-1].show()
                        x1, y1 = a0.x(), a0.y()
                        if x1 + self.unloadMenu.width() > self.width():
                            x1 = self.width() - self.unloadMenu.width()
                        if y1 +self.unloadMenu.height() > self.height():
                            y1 = self.height() - self.unloadMenu.height()
                        self.unloadMenu.move(x1, y1)
                        self.unloadMenu.show()
                        self.unloadMenu.raise_()
                        break
                    elif i.isBlack:
                        continue
                else:
                    self.clear(None)

            else:
                self.clear(None)
                self.rightMenu.hide()
                self.choosePathMenu.hide()

        elif a0.button() == 2:
            if self.choose_status == None:
                self.hasMove = a0.pos()
                self.clear(None)
            else:
                self.clear('return')

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self.isRun:
            return

        if a0.button() == 2:
            if self.hasMove:
                if self.canRightMenuShow:
                    if not self.dwCpu('showgftargets', a0):
                        x, y = a0.x(), a0.y()
                        if a0.x() + self.rightMenu.width() > self.width():
                            x = self.width() - self.rightMenu.width()
                        if a0.y() + self.rightMenu.height() > self.height():
                            y = self.height() - self.rightMenu.height()
                        self.rightMenu.move(x, y)
                        self.rightMenu.show()
                        self.rightMenu.raise_()
            self.hasMove = None

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self.isRun:
            return
        self.canRightMenuShow = False
        if not self.hasMove:
            return
        x, y = a0.x() - self.hasMove.x(), a0.y() - self.hasMove.y()
        self.hasMove = a0.pos()
        if self.pointer_geo[0][0].x() + x >= 0 or \
                self.pointer_geo[-1][-1].x() + x <= self.width() - self.mapBlockSize[0]:
            x=0
        if self.pointer_geo[0][0].y() + y >= 0 or \
                self.pointer_geo[-1][-1].y() + y <= self.height() - self.mapBlockSize[1]:
            y=0
        for i, i1 in enumerate(self.pointer_geo):
            for j, j1 in enumerate(i1):
                j1.move(x+j1.x(), y+j1.y())
                if self.pointer_dw[i][j]:
                    self.pointer_dw[i][j].move(x+self.pointer_dw[i][j].x(), y+self.pointer_dw[i][j].y())

    def wheelEvent(self, a0: QtGui.QWheelEvent=None) -> None:
        if not self.isRun:
            return
        if self.choose_status != 'pathshowed':
            return
        isUp = a0 if isinstance(a0, int) else -a0.angleDelta().y()
        if (isUp < 0 and self.roadsToChoose['point'] == 0) or (isUp > 0 and self.roadsToChoose['point'] == len(self.roadsToChoose['roads']) -1):
            return
        for i in self.roadsToChoose['layers']:
            i.deleteLater()
        self.roadsToChoose['layers'] = []
        self.roadsToChoose['point'] += -1 if isUp <0 else 1
        for j in self.roadsToChoose['roads'][self.roadsToChoose['point']]:
            circle = QFrame(self)
            circle.setStyleSheet('border-radius:5px;border:3px solid rgb(100, 100,200)')
            circle.show()
            circle.setGeometry(self.pointer_geo[j[0]][j[1]].geometry())
            self.roadsToChoose['layers'].append(circle)
        x1, y1 = a0.x(), a0.y()
        if x1 + self.unloadMenu.width() > self.width():
            x1 = self.width() - self.unloadMenu.width()
        if y1 + self.unloadMenu.height() > self.height():
            y1 = self.height() - self.unloadMenu.height()
        self.unloadMenu.move(x1, y1)
        self.choosePathMenu.show()
        self.choosePathMenu.raise_()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Control:
            self.isCtrlDown = True

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Control:
            self.isCtrlDown = False
            self.infoView.hide()

    def canTransport(self, dw:DW, p):
        tem_e = self.pointer_dw[p[0]][p[1]]
        if  tem_e:
            if 'transport' in tem_e.track['name'] and tem_e.track['transport']:
                if dw.track['name'] in ['footmen', 'gunnery'] and tem_e.track['name'] == 'transport':
                    return True
                elif dw.track['name'] in ['footmen', 'gunnery'] and tem_e.track['name'] == 'transportShip':
                    return True
        return False
        # else:
        #     return True

    def moveToDw(self, dw:DW=None):
        # dw = self.findChild(DW)
        x, y = self.width()/2 - dw.x(), self.height()/2 - dw.y()
        if self.pointer_geo[0][0].x() + x >= 0:
            x = -self.pointer_geo[0][0].x()
        elif self.pointer_geo[-1][-1].x() + x <= self.width() - self.mapBlockSize[0]:
            x = self.width() - self.mapBlockSize[0] - self.pointer_geo[-1][-1].x()
        if self.pointer_geo[0][0].y() + y >= 0:
            y = -self.pointer_geo[0][0].y()
        elif self.pointer_geo[-1][-1].y() + y <= self.height() - self.mapBlockSize[1]:
            y = self.height() - self.mapBlockSize[1] - self.pointer_geo[-1][-1].y()
        x, y = x if self.canMove[0] else 0, y if self.canMove[1] else 0
        anime_group = QParallelAnimationGroup(self)
        for i, i1 in enumerate(self.pointer_geo):
            for j, j1 in enumerate(i1):
                # j1.move(x+j1.x(), y+j1.y())
                tem_anime = QPropertyAnimation(j1, b'pos', self)
                tem_anime.setStartValue(j1.pos())
                tem_anime.setEndValue(QPoint(x+j1.x(), y+j1.y()))
                tem_anime.setDuration(400)
                anime_group.addAnimation(tem_anime)
                if self.pointer_dw[i][j]:
                    # self.pointer_dw[i][j].move(x+self.pointer_dw[i][j].x(), y+self.pointer_dw[i][j].y())
                    tem_anime2 = QPropertyAnimation(self.pointer_dw[i][j], b'pos', self)
                    tem_anime2.setStartValue(self.pointer_dw[i][j].pos())
                    tem_anime2.setEndValue(QPoint(x + self.pointer_dw[i][j].x(), y + self.pointer_dw[i][j].y()))
                    tem_anime2.setDuration(400)
                    anime_group.addAnimation(tem_anime2)
        anime_group.start()

    def running(self):
        pass

    def isVictory(self):
        newusers = []
        for i in self.users:
            if i['header_loc']:
                tem = self.pointer_geo[i['header_loc'][0]][i['header_loc'][1]]
                if tem.track['flag'] != i['flag']:
                    for j in self.findChildren(DW):
                        if j.track['flag'] == i['flag']:
                            j.change(tem.track['flag'])
                    for j in self.findChildren(Geo):
                        if j.track['usage'] == 'build':
                            if j.track['flag'] == tem.track['flag']:
                                j.change(track=resource.find({'usgae':'build', 'name':j.track['name'], 'flag':tem.track['flag']}))
                else:
                    newusers.append(i)
            else:
                for j in self.findChildren(DW):
                    if j.track['flag'] == i['flag']:
                        i['canBeGua'] = True
                        newusers.append(i)
                        break
                else:
                    if not i['canBeGua']:
                        newusers.append(i)

        self.users = newusers
        # print(self.users)
        for i in self.users:
            if i['flag'] == self.tUser['flag']:
                break
        else:
            print('你输了')
            time.sleep(99999)
        dws = {}
        for i in self.users:
            if not i['canBeGua']:
                dws[i['flag']] = 1
            else:
                dws[i['flag']] = 0
        for i in self.findChildren(DW):
            dws[i.track['flag']] += 1
        if len(dws) <= 1:
            print(dws[0]['flag'],' is victory!\ngame is already over!')
            sys.exit()
        return False

    def chooseRightMenu(self, data):
        self.collectMap()
        self.childWindow.deleteLater()
        self.childWindow = QWidget()
        self.childWindow.setWindowModality(Qt.ApplicationModal)
        layout = QBoxLayout(QBoxLayout.TopToBottom, self.childWindow)
        if data == 'beforevictory':
            self.childWindow.setWindowTitle('胜利条件')
            tem_1 = QLabel('战斗背景：'+self.user['command_bg'])
            tem_1.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(tem_1)
            tem_1 = QLabel('战斗目标：'+self.user['command'])
            tem_1.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(tem_1)
            tem_1 = QPushButton('忍气吞声地接受。。。')
            tem_1.clicked.connect(self.childWindow.close)
            layout.addWidget(tem_1)
            self.childWindow.setLayout(layout)
            self.childWindow.show()
            self.childWindow.setMinimumSize(200, 200)
        elif data == 'forces':##此处忽略军队价值
            self.childWindow.setWindowTitle('兵力')
            rows = [i['flag'] for i in self.users]
            cols = ['本回合支出', '收入', '剩余资金', '军队数量', '步兵类占比', '车辆类占比', '海军占比', '空军占比']
            area = QTableWidget(self.childWindow)
            area.setColumnCount(len(cols))
            area.setRowCount(len(rows))
            for i, j in enumerate(cols):
                area.setHorizontalHeaderItem(i, QTableWidgetItem(j))
            for i, j in enumerate(rows):
                area.setVerticalHeaderItem(i, QTableWidgetItem(j))
            for i, j in enumerate(rows):
                for k in self.users:
                    if k['flag'] == j:
                        area.setItem(i, 2, QTableWidgetItem(str(k['money'])))
                        area.setItem(i, 0, QTableWidgetItem(str(k['outcome'])))
                        break
                income = 0
                for k in self.findChildren(Geo):
                    if k.track['usage'] == 'build':
                        if k.track['flag'] == j:
                            income += self.globalData['income']
                area.setItem(i, 1, QTableWidgetItem(str(income)))
                total = dw1 = dw2 = dw3 = dw4 = 0
                for k in self.findChildren(DW):
                    if k.track['flag'] == j:
                        total += 1
                        if resource.basicData['money']['classify'][k.track['name']] == 'foot':
                            dw1 += 1
                        elif resource.basicData['money']['classify'][k.track['name']] == 'track':
                            dw2 += 1
                        elif resource.basicData['money']['classify'][k.track['name']] == 'sea':
                            dw3 += 1
                        elif resource.basicData['money']['classify'][k.track['name']] == 'sky':
                            dw4 += 1
                area.setItem(i, 3, QTableWidgetItem(str(total)))
                area.setItem(i, 4, QTableWidgetItem(str(dw1)))
                area.setItem(i, 5, QTableWidgetItem(str(dw2)))
                area.setItem(i, 6, QTableWidgetItem(str(dw3)))
                area.setItem(i, 7, QTableWidgetItem(str(dw4)))

            inner_btns = []
            layout_inner_btns = QBoxLayout(QBoxLayout.LeftToRight, self.childWindow)
            def chagneInForces(arg):
                for i in self.users:
                    if i['flag'] == arg:
                        children = self.childWindow.findChildren(QLabel)
                        children[0].setPixmap(resource.find({'usage': 'hero', 'name': i['hero'], 'action': 'post'})['pixmap'].scaled(100,400))
                        children[1].setText(resource.basicData['hero_1'][i['hero']]['skill_dsc'])
                        children[2].setText(resource.basicData['hero_2'][i['hero']]['skill_dsc'])
                        children[3].setText(resource.basicData['hero_3'][i['hero']]['skill_dsc'])
                        break

            for i in self.users:
                inner_tem = QPushButton(i['flag'], self.childWindow)
                inner_tem.clicked.connect(functools.partial(chagneInForces,i['flag']))
                layout_inner_btns.addWidget(inner_tem)
                inner_btns.append(inner_tem)

            layout.addWidget(area)
            layout_2 = QBoxLayout(QBoxLayout.LeftToRight, self.childWindow)
            label = QLabel(self.childWindow)
            label.setPixmap(resource.find({'usage': 'hero', 'name': self.user['hero'], 'action': 'post'})['pixmap'].scaled(100,400))
            label.setScaledContents(True)
            layout_2.addWidget(label)
            layout_3 = QBoxLayout(QBoxLayout.TopToBottom, self.childWindow)
            layout_3.addWidget(QLabel(resource.basicData['hero_1'][self.user['hero']]['skill_dsc'], self.childWindow))
            layout_3.addWidget(QLabel(resource.basicData['hero_2'][self.user['hero']]['skill_dsc'], self.childWindow))
            layout_3.addWidget(QLabel(resource.basicData['hero_3'][self.user['hero']]['skill_dsc'], self.childWindow))
            layout_2.addLayout(layout_3)
            layout.addLayout(layout_inner_btns)
            layout.addLayout(layout_2)
            self.childWindow.setLayout(layout)
            self.childWindow.show()
            self.childWindow.setMinimumSize(900, 600)
        elif data == 'save':
            def save():
                self.map['recordName'] = self.childWindow.findChild(QLineEdit).text()
                resource.saveRecord(self.map)
                self.childWindow.findChild(QLabel).setText('已保存')
            self.childWindow.setWindowTitle('保存地图')
            input = QLineEdit(self.childWindow)
            label = QLabel('', self.childWindow)
            label.setAlignment(QtCore.Qt.AlignCenter)
            btn1 = QPushButton('保存', self.childWindow)
            btn2 = QPushButton('取消', self.childWindow)
            btn1.clicked.connect(save)
            btn2.clicked.connect(self.childWindow.close)
            layout.addWidget(input)
            layout.addWidget(label)
            layout.addWidget(btn1)
            layout.addWidget(btn2)
            self.childWindow.setLayout(layout)
            self.childWindow.show()
        elif data == 'exit':
            self.close()
        elif data == 'end':
            self.boutUpdate()
            self.rightMenu.hide()

    def myUpdate(self):
        self.Head.raise_()
        if self.isVictory():
            pass
        for j in self.findChildren(DW):
            if j:
                j.flush()
                j.myUpdate()

    def boutUpdate(self):
        self.user['bout'] += 1
        self.isRun = False
        for i in self.findChildren(DW):
            if i.track['flag'] == self.user['flag']:
                i.doBody(self.user['action'])
        ###玩家更换
        for i1, i in enumerate(self.users):
            if i == self.user:
                if i1 == len(self.users) - 1:
                    self.user = self.users[0]
                else:
                    self.user = self.users[i1 + 1]
                break
        print(self.user['flag'])
        print('播放特效->等待电脑或玩家')
        ##资金
        for i in self.findChildren(Geo):
            if i.track['usage'] == 'build':
                if i.track['flag'] == self.user['flag']:
                    self.user['money'] += self.globalData['income']
                    self.user['outcome'] = 0
        ###补给
        directions = [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        cols = len(self.map['map'][0])
        rows = len(self.map['map'])
        for i in self.findChildren(DW):
            if i.track['flag'] != self.user['flag']:
                continue
            ###激活
            i.moved = False
            i.doBody(self.user['action'])
            ###特性油耗
            cost = float(resource.basicData['money']['daycost'][i.track['name']])
            if i.isStealth or i.isDiving:
                cost += 4
            i.oil -= cost
            #下面这个 if 为：城市的补给内容
            build = self.pointer_geo[i.mapId[0]][i.mapId[1]]
            key = resource.basicData['geo']['cansupply'][build.track['name']]
            if i.track['name'] in key or resource.basicData['money']['classify'][i.track['name']] in key:
                i.oil = int(resource.basicData['gf'][i.track['name']]['oil'])
                i.bullect = int(resource.basicData['gf'][i.track['name']]['bullect'])
                cost = round(10 - round(i.bloodValue))
                cost = 2 if cost >=2 else cost
                if cost:
                    money = int(float(resource.basicData['money']['money'][i.track['name']]) *cost/10)
                    if money < self.user['money']:
                        self.user['money'] -= money
                        if round(i.bloodValue + cost) == 10:
                            i.doBlood(10)
                        else:
                            i.doBlood(i.bloodValue+cost)
            ##计划补给
            if 'transport' in i.track['name']:
                shouldsupply = []
                points = []
                supplies = i.supplies
                for r1 in range(1, 3):
                    for y in range(0,r1+1):
                        for r2 in directions:
                            x1, y1 = i.mapId[0]+y*r2[0], i.mapId[1]+(r1-y)*r2[1]
                            if x1 <0 or x1 >= rows or y1 <0 or y1 >= cols or (x1, y1) in points:
                                continue
                            if self.pointer_dw[x1][y1]:
                                if len(i.supplies):
                                    if round(self.pointer_dw[x1][y1].bloodValue) != 10 and self.pointer_dw[x1][y1].track['flag'] == self.user['flag']:
                                        print(self.pointer_dw[x1][y1])
                                        shouldsupply.append(self.pointer_dw[x1][y1])
                                        points.append((x1, y1))
                                else:
                                    data_1 = self.pointer_dw[x1][y1]
                                    data_1.oil = int(resource.basicData['gf'][data_1.track['name']]['oil'])
                                    data_1.bullect = int(resource.basicData['gf'][data_1.track['name']]['bullect'])
                shouldsupply = sorted(shouldsupply, key=lambda arg:float(resource.basicData['money']['money'][arg.track['name']]))
                for j in shouldsupply:
                    if j.track['name'] in supplies:
                        price = int(resource.basicData['money']['money'][j.track['name']])
                        addedBlood = supplies[j.track['name']]/price*10
                        oil = int(resource.basicData['gf'][j.track['name']]['oil'])
                        print(price, addedBlood)
                        bullect = int(resource.basicData['gf'][j.track['name']]['bullect'])

                        if 10 - float(j.bloodValue) >= addedBlood:
                            j.doBlood(j.bloodValue+addedBlood)
                            del supplies[j.track['name']]
                        else:
                            supplies[j.track['name']] -= (10 - round(j.bloodValue))*price
                            if round(supplies[j.track['name']]) == 0:
                                del supplies[j.track['name']]
                            j.doBlood(10)
                        j.oil = oil
                        j.bullect = bullect
                # for i in

            ##死亡断定
            if int(i.oil) <= 0:
                self.pointer_dw[i.mapId[0]][i.mapId[1]] = None
                i.deleteLater()

        ## hide
        for i, i1 in enumerate(self.users):
            if i1['flag'] == self.tUser['flag']:
                break
        for i in self.findChildren(DW):
            i.show()
            if i.track['flag'] in i1['enemy'] and (i.isDiving or i.isStealth):
                for j in directions:
                    x, y = j[0]+i.mapId[0], j[1]+i.mapId[1]
                    if x <0 or x >=rows or y < 0 or y >= cols:
                        continue
                    if self.pointer_dw[x][y]:
                        if self.pointer_dw[x][y].track['flag'] not in i1['enemy']:

                            break
                else:
                    i.hide()

        self.isRun = True

    def proValueChange(self):
        print(self.Head_exp.value(), self.Head_exp.maximum(), self.Head_exp.isMaximized())
        if self.Head_exp.value() == int(resource.basicData['hero_f'][self.user['hero']]['max_energy']):
            self.Head_exp.setStyleSheet('background-color:black;color:black;border-radius:0;')
        elif self.Head_exp.value() >= int(resource.basicData['hero_f'][self.user['hero']]['energy']):
            self.Head_exp.setStyleSheet('background-color:red;color:red;border-radius:0;')
        else:
            self.Head_exp.setStyleSheet('background-color:white;color:white;border-radius:0;')




if __name__ == '__main__':
    # QListWidgetItem()
    window = TMap()
    window.initUI()
    # window.moveToDw()
    sys.exit(qapp.exec_())
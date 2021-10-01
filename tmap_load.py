#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :tmap_load.py
# @Time      :2021/7/22 16:06
# @Author    :russionbear
import random
import time

from PyQt5.Qt import *
from PyQt5 import QtGui
from PyQt5 import QtCore
import functools
import sys, json, zlib, os, random
from map_load import DW, GeoD as Geo, VMap
from resource import resource
from net.netTool import ROOMSERVER, myThread
from multiprocessing import Queue, Process
from threading import Thread

'''
---------guider--------------
    showHead, showDWInfo, showTalk, showTitle, showChat, showInput, 
    fightData, imperialEdict, 
    mapMove, mapScale, control
    
    control:fight, move, loadings, planSupply
'''

qapp = QApplication(sys.argv)


# qapp = QApp()

class TMap(VMap):
    def __init__(self, mapName='default', users=None, tUser=None, conn=None, parent=None):
        super(TMap, self).__init__(parent)
        # self.users = [{'flag': 'red', 'enemy': ['blue'], 'action': 'right', 'command_bg': '会战', 'command': '消灭敌方', \
        #                'outcome': 0, 'money': 99999, 'hero': 'google', 'header_loc': None, 'canBeGua': False, 'bout': 1,
        #                'exp': 2}, \
        #               {'flag': 'blue', 'enemy': ['red'], 'action': 'left', 'command_bg': '会战', 'command': '消灭敌方', \
        #                'outcome': 0, 'money': 0, 'hero': 'warhton', 'header_loc': None, 'canBeGua': False, 'bout': 1,
        #                'exp': 2}]
        ####加载地图内部参数
        userMode = {'flag': 'red', 'action': 'right', 'enemy': [], 'command_bg': '会战', 'command': '消灭敌方', \
                    'outcome': 0, 'money': 999, 'hero': 'google', 'header_loc': None, 'canBeGua': False,
                    'isOver': False, 'bout': 0,
                    'exp': 0}
        self.users = users
        for i1, i in enumerate(self.users):
            userMode.update(i)
            self.users[i1] = userMode.copy()
        self.user = self.users[0]
        self.user['bout'] += 1
        for i in self.users:
            if i['flag'] == tUser['flag']:
                i['action'] = 'right'
            else:
                i['action'] = 'left'
        self.globalData = {'income': 1000}
        self.bout = 1
        self.tUser = tUser
        for i in self.users:
            if i['flag'] == self.tUser['flag']:
                self.tUser = i
                break
        #### 开挂
        # print(self.users)
        self.users[0].update({'enemy': ['blue', 'yellow']})
        self.users[1].update({'enemy': ['red', 'yellow']})
        # print(self.users)

        self.initUI(mapName)

        for i in self.findChildren(DW):
            if i.track['flag'] == self.tUser['flag']:
                i.doBody('right')
            else:
                i.doBody('left')

        self.client = conn
        self.clientEnd = False
        self.clientThread = None
        self.isClientThreadEnd = True
        self.clientSendThread = None
        if self.client:
            self.clientThread = myThread(target=self.clientHandle)
            self.clientThread.start()
            self.isClientThreadEnd = False
            print('handle start不是单机')

        self.commands = []
        self.command = None
        self.command_ponit = 0

        self.costMap = None
        self.dwChoosed = None
        self.targetChoosed = None
        self.areaToChoose = []
        self.planToSupply = []
        self.roadsToChoose = {'point': 0, 'roads': [], 'layers': []}
        self.targetsToChoose = {'choosed': None, 'layers': []}
        self.planToUnload = {'layers': [], 'data': [], 'loc': None}  # [[k:记录, odk2：可选落地点, 0：是否落地]]
        self.actionTreeList = [None, 'areashowed', 'pathshowed', 'targetshowed', 'gtargetshowed', 'unloadingshow']
        self.choose_status = None  # None, areashowd, pathshowed, targetshowd, gtargetshowed, unloadshow
        self.dwChoosedStatus = 'move'
        self.shouldShow = []

        self.isRun = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerStop)

        self.dwUpdater = QTimer(self)
        self.dwUpdater.timeout.connect(self.myUpdate)
        self.dwUpdater.start(1400)

        self.screnMoveAnimate = QParallelAnimationGroup(self)
        self.isUserTrackOpen = True

        self.mapSizeStatus = 'big'

    def initUI(self, name='test1', parent=None, block=(100, 100), winSize=(800, 800), brother=None):
        super(TMap, self).initUI(name, parent, block, winSize, brother)
        self.circle.deleteLater()
        del self.circled, self.circleStatus
        # self.showFullScreen()
        self.canMove = (True if self.mapBlockSize[0] * self.mapSize[0] > self.width() else False,
                        True if self.mapBlockSize[1] * self.mapSize[1] > self.height() else False)
        x, y = (self.width() - self.mapBlockSize[0] * self.mapSize[0]) // 2, (
                self.height() - self.mapBlockSize[1] * self.mapSize[1]) // 2
        self.mapMove(x, y, True)
        self.isCtrlDown = False

        self.dwsListWidget = None

        self.choosePathMenu = QFrame(self)
        layout_choosePath = QBoxLayout(QBoxLayout.TopToBottom)
        self.choose_btn_waiting = QPushButton('待命')
        self.choose_btn_waiting.clicked.connect(functools.partial(self.dwCpu, 'waiting'))
        layout_choosePath.addWidget(self.choose_btn_waiting)
        self.choose_btn_attacking = QPushButton('攻击')
        self.choose_btn_attacking.clicked.connect(functools.partial(self.dwCpu, 'attack'))
        layout_choosePath.addWidget(self.choose_btn_attacking)
        self.choose_btn_stealth = QPushButton('隐身')
        self.choose_btn_stealth.clicked.connect(functools.partial(self.dwCpu, 'stealth'))
        layout_choosePath.addWidget(self.choose_btn_stealth)
        self.choose_btn_occupy = QPushButton('占领')
        self.choose_btn_occupy.clicked.connect(functools.partial(self.dwCpu, 'occupy'))
        layout_choosePath.addWidget(self.choose_btn_occupy)
        self.choose_btn_loading = QPushButton('搭载')
        self.choose_btn_loading.clicked.connect(functools.partial(self.dwCpu, 'loading'))
        layout_choosePath.addWidget(self.choose_btn_loading)
        self.choose_btn_unloading = QPushButton('卸载')
        self.choose_btn_unloading.clicked.connect(functools.partial(self.dwCpu, 'unload'))
        layout_choosePath.addWidget(self.choose_btn_unloading)
        self.choose_btn_laymine = QPushButton('布雷')
        self.choose_btn_laymine.clicked.connect(functools.partial(self.dwCpu, 'laymine'))
        layout_choosePath.addWidget(self.choose_btn_laymine)
        self.choose_btn_buy = QPushButton('计划补给')
        self.choose_btn_buy.clicked.connect(functools.partial(self.dwCpu, 'buy'))
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
            tem_btn.clicked.connect(functools.partial(self.dwCpu, 'unloading', tem_btn))
            # tem_btn.show()
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
        self.Head_head.setPixmap(
            QPixmap(resource.find({'usage': 'hero', 'name': self.user['hero']})['pixmap']).scaled(80, 80))
        self.Head_exp = QProgressBar(self.Head)
        self.Head_exp.setMaximum(int(resource.basicData['hero_f'][self.user['hero']]['max_energy']))
        self.Head_exp.setAlignment(Qt.AlignVCenter)
        self.Head_exp.valueChanged.connect(self.proValueChange)
        self.Head_exp.setValue(self.user['exp'])
        self.Head_name = QLabel(self.user['hero'])
        self.Head_money = QLabel('$' + str(int(self.user['money'])))
        head_font = QFont('宋体', 20)
        head_font.setBold(True)
        self.Head_money.setFont(head_font)
        self.Head_name.setFont(head_font)
        self.Head.setStyleSheet('border-radius:5px;background-color:' + self.user['flag'] + ';')
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

        self.infoView = InfoView(self)
        self.infoView.show()
        self.infoView.hide()

        actions = {}
        for i in self.users:
            actions[i['flag']] = i['action']
        # for i in self.pointer_dw:
        #     for j in i:
        #         if j:
        #             j.doBody(actions[j.track['flag']])

        self.childWindow = QWidget()
        self.childWindow.setWindowModality(Qt.ApplicationModal)

        self.talkView = QLabel(self)
        self.talkView.setMaximumWidth(400)
        # self.talkView.setStyleSheet('border-radius:12px;background-color:white;padding:6px;border-top-left-radius:0;')
        self.talkView.setFont(QFont('宋体', 22))
        self.talkView.setWordWrap(True)
        self.talkView.show()
        self.talkView.hide()
        self.talkView.mapId = (0, 0)
        self.talkView.shouldShow = False

        self.mapScale(True)

        # self.setMouseTracking(True)

    def mapScale(self, shouldBigger=True):
        min, max = 0, 5
        if (shouldBigger and self.mapScalePoint == max) or \
                (not shouldBigger and self.mapScalePoint == min):  # can scale
            return
        primA = self.width() // 2 - self.children()[0].x(), self.height() // 2 - self.children()[0].y()
        mapBlockSize = resource.mapScaleList[self.mapScalePoint]['body']
        self.mapScalePoint = max if shouldBigger else min
        self.mapBlockSize = resource.mapScaleList[self.mapScalePoint]['body']
        n = self.mapBlockSize[0] / mapBlockSize[0]
        primA = self.width() // 2 - round(primA[0] * n), self.height() // 2 - round(primA[1] * n)
        tem_data = resource.mapScaleList[self.mapScalePoint]
        tem_children = self.findChildren((Geo, DW))
        for j, i in enumerate(tem_children):
            i.scale(tem_data)
            i.move(primA[1] + i.mapId[1] * self.mapBlockSize[1], primA[0] + i.mapId[0] * self.mapBlockSize[0])

        move_x = self.mapSize[0] * self.mapBlockSize[0] - self.width()
        move_y = self.mapSize[1] * self.mapBlockSize[1] - self.height()
        self.canMove = True if move_x > 0 else False, True if move_y > 0 else False
        move_x = 0 if move_x > 0 else -move_x // 2
        move_y = 0 if move_y > 0 else -move_y // 2
        self.mapMove(move_x, move_y)
        self.mapAdjust()
        if shouldBigger:
            if self.talkView.shouldShow:
                self.talkView.show()
                tem_geo = self.pointer_geo[self.talkView.mapId[0]][self.talkView.mapId[1]]
                x1, y1 = tem_geo.x() > self.width() // 2, tem_geo.y() > self.height() // 2
                if not x1 and not y1:
                    self.talkView.setStyleSheet(
                        'background-color:white;padding:6px;border-radius:15px;border-top-left-radius:0;')
                    x2, y2 = tem_geo.x(), tem_geo.y() + tem_geo.height()
                elif x1 and not y1:
                    self.talkView.setStyleSheet(
                        'background-color:white;padding:6px;border-radius:15px;border-top-right-radius:0;')
                    x2, y2 = tem_geo.x() - (self.talkView.width() - tem_geo.width()), tem_geo.y() + tem_geo.height()
                elif not x1 and y1:
                    self.talkView.setStyleSheet(
                        'background-color:white;padding:6px;border-radius:15px;border-bottom-left-radius:0;')
                    x2, y2 = tem_geo.x(), tem_geo.y() - self.talkView.height()
                elif not x1 and not y1:
                    self.talkView.setStyleSheet(
                        'background-color:white;padding:6px;border-radius:15px;border-bottom-right-radius:0;')
                    x2, y2 = tem_geo.x() - (
                            self.talkView.width() - tem_geo.width()), tem_geo.y() - self.talkView.height()
                self.talkView.move(x2, y2)
            self.Head.show()
            self.Head.move(0, 0)
        else:
            self.talkView.hide()
            self.Head.hide()

    def judgement(self, dw: DW, endP, command={}):
        if not endP or not self.pointer_dw[endP[0]][endP[1]]:
            return
        resource.player['bao'].play()
        beginP = dw.mapId
        enemy = self.pointer_dw[endP[0]][endP[1]]
        ###此处忽略英雄加成
        at1 = float(resource.basicData['gf'][dw.track['name']][enemy.track['name']]) * \
              (float(resource.basicData['gfGeo_g'][dw.track['name']][
                         self.pointer_geo[beginP[0]][beginP[1]].track['name']]) / 100 + 1) * \
              ((100 - float(resource.basicData['gfGeo_f'][enemy.track['name']][
                                self.pointer_geo[endP[0]][endP[1]].track['name']])) / 100)
        at2 = float(resource.basicData['gf'][enemy.track['name']][dw.track['name']]) * \
              (float(resource.basicData['gfGeo_g'][enemy.track['name']][
                         self.pointer_geo[endP[0]][endP[1]].track['name']]) / 100 + 1) * \
              ((100 - float(resource.basicData['gfGeo_f'][dw.track['name']][
                                self.pointer_geo[beginP[0]][beginP[1]].track['name']])) / 100)
        if float(resource.basicData['gf'][enemy.track['name']]['gf_mindistance']) > 1:
            at2 = 0
        elif enemy.bullect == 0:
            at2 = 0
        blood2 = enemy.bloodValue - at1 * dw.bloodValue / 10
        blood2 = 0 if round(blood2) <= 0 else round(blood2, 1)
        blood1 = dw.bloodValue - at2 * blood2 / 10
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
            dw1['mapId'] = dw.mapId
            dw2['mapId'] = enemy.mapId
            print('all has beng!!!!!!!')
        elif blood1 == 0:
            dw.deleteLater()
            self.pointer_dw[beginP[0]][beginP[1]] = None
            print('dw has beng!!!!')
            enemy.doBlood(blood2)
            dw1['isAlive'] = False
            dw2 = enemy.makeTrack()
            dw1['mapId'] = dw.mapId
        elif blood2 == 0:
            enemy.deleteLater()
            self.pointer_dw[endP[0]][endP[1]] = None
            print('enemy has beng!!!!')
            dw.doBlood(blood1)
            dw.doBody(self.user['action'] + 'G')
            dw.moved = True
            dw1 = dw.makeTrack()
            dw2['isAlive'] = False
            dw2['mapId'] = enemy.mapId
        else:
            print('nothing has beng!!!')
            dw.doBlood(blood1)
            enemy.doBlood(blood2)
            dw.doBody(self.user['action'] + 'G')
            dw.moved = True
            dw1 = dw.makeTrack()
            dw2 = enemy.makeTrack()
        command['dw1'] = dw1
        command['dw2'] = dw2

    def timerStop(self):
        resource.player['move_' + resource.basicData['money']['sound_move'][self.dwChoosed.track['name']]].stop()
        command = {}
        road = []
        # def doSame():
        # #     global command, road
        #     self.dwChoosed.doBody(self.user['action']+'G')
        #     self.dwChoosed.moved = True
        #     road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
        #     command = {'type':self.dwChoosedStatus, 'flag': self.user['flag'], 'road':road}
        #     self.commands.append(command)
        #     return command, road

        if self.dwChoosedStatus == 'waiting':
            self.dwChoosed.doBody(self.user['action'] + 'G')
            self.dwChoosed.moved = True
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            command = {'type': self.dwChoosedStatus, 'flag': self.user['flag'], 'road': road}
            self.commands.append(command)
        ### 非tUser单位只能由命令修改
        elif self.dwChoosedStatus == 'encounter':
            self.dwChoosed.doBody(self.user['action'] + 'G')
            self.dwChoosed.moved = True
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            command = {'type': self.dwChoosedStatus, 'flag': self.user['flag'], 'road': road}
            self.commands.append(command)
        elif self.dwChoosedStatus == 'stealth':
            # if self.choose_btn_stealth.text() in ['下潜', '上浮']:
            if resource.basicData['money']['candiving'][self.dwChoosed.track['name']] == '1':
                self.dwChoosed.isDiving = not self.dwChoosed.isDiving
            else:
                self.dwChoosed.isStealth = not self.dwChoosed.isStealth
            self.dwChoosed.doBody(self.user['action'] + 'G')
            self.dwChoosed.moved = True
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            command = {'type': self.dwChoosedStatus, 'flag': self.user['flag'], 'road': road}
            self.commands.append(command)
        elif self.dwChoosedStatus == 'attacking':
            if self.dwChoosed.mapId[1] + 1 == self.targetsToChoose['choosed'][1]:
                self.dwChoosed.doBody('right')
            elif self.dwChoosed.mapId[1] - 1 == self.targetsToChoose['choosed'][1]:
                self.dwChoosed.doBody('left')
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            command = {'type': self.dwChoosedStatus, 'flag': self.user['flag'], 'road': road}
            self.judgement(self.dwChoosed, self.targetsToChoose['choosed'], command)
            self.commands.append(command)
        elif self.dwChoosedStatus == 'occupy':
            self.dwChoosed.occupied += round(self.dwChoosed.bloodValue)
            if self.dwChoosed.occupied >= 20:
                dw = self.pointer_geo[self.dwChoosed.mapId[0]][self.dwChoosed.mapId[1]]
                track = resource.find({'usage': 'build', 'name': dw.track['name'], 'flag': self.user['flag']})
                dw.change(track=track)
                self.dwChoosed.occupied = 0
            self.dwChoosed.doBody(self.user['action'] + 'G')
            self.dwChoosed.moved = True
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            command = {'type': self.dwChoosedStatus, 'flag': self.user['flag'], 'road': road}
            self.commands.append(command)
        elif self.dwChoosedStatus == 'loading':
            actions = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            self.pointer_dw[actions[-1][0]][actions[-1][1]].loadings.append(self.dwChoosed.makeTrack())
            self.pointer_dw[actions[0][0]][actions[0][1]] = None
            self.dwChoosed.deleteLater()
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            command = {'type': self.dwChoosedStatus, 'flag': self.user['flag'], 'road': road}
            self.commands.append(command)
        elif self.dwChoosedStatus == 'unloading':
            notDel = []
            dws = []
            for i in self.planToUnload['data']:
                if i[2]:
                    print('is counting')
                    dw = DW(self)
                    dw.initUI(
                        {'usage': 'dw', 'flag': self.user['flag'], 'action': self.user['action'], 'name': i[0]['name']},
                        i[2])
                    self.pointer_dw[i[2][0]][i[2][1]] = dw
                    dw.setGeometry(self.pointer_geo[i[2][0]][i[2][1]].geometry())
                    dw.moved = True
                    dw.oil = float(resource.basicData['gf'][i[0]['name']]['oil'])
                    dw.bullect = float(resource.basicData['gf'][i[0]['name']]['bullect'])
                    dw.show()
                    dw.raise_()
                    dw.doBody(self.user['action'] + 'G')
                    dws.append(dw.makeTrack())
                else:
                    notDel.append(int(i[0]['mapId']))
            newloadings = []
            for i1, i in enumerate(self.dwChoosed.loadings):
                if i['mapId'] in notDel:
                    newloadings.append(i)
            self.dwChoosed.loadings = newloadings
            self.dwChoosed.moved = True
            self.dwChoosed.doBody(self.user['action'] + 'G')
            road = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            command = {'type': self.dwChoosedStatus, 'flag': self.user['flag'], 'road': road,
                       'loadings': newloadings.copy(), 'dws': dws}
            self.commands.append(command)

        shouldShow = []
        for i in self.shouldShow:
            i.show()
            shouldShow.append(tuple(i.mapId))
        command['shouldShow'] = shouldShow
        if (self.dwChoosedStatus == 'attacking' and self.pointer_dw[road[-1][0]][
            road[-1][1]] != None) or self.dwChoosedStatus not in ['attacking', 'loading']:
            costOil = 0
            for i in road[1:]:
                costOil += int(resource.basicData['move'][self.dwChoosed.track['name']][
                                   self.pointer_geo[i[0]][i[1]].track['name']])
            self.dwChoosed.oil -= costOil
            command['costOil'] = costOil

        self.sentToServer(command)

        self.isRun = True
        self.clear(None)
        self.timer.stop()

    def commandTimeStop(self, command, choosed, type, scends):
        resource.player['move_' + resource.basicData['money']['sound_move'][choosed.track['name']]].play()
        time.sleep(scends)
        resource.player['move_' + resource.basicData['money']['sound_move'][choosed.track['name']]].stop()
        for ii in self.users:
            if ii['flag'] == command['flag']:
                break
        if type == 'waiting':
            choosed.doBody(ii['action'] + 'G')
            choosed.moved = True
        elif type == 'encounter':
            choosed.doBody(ii['action'] + 'G')
            choosed.moved = True
        elif type == 'stealth':
            choosed.doBody(ii['action'] + 'G')
            choosed.moved = True
            if resource.basicData['money']['candiving'][choosed.track['name']] != '1':
                choosed.isStealth = not choosed.isStealth
            else:
                choosed.isDiving = not choosed.isDiving

            if choosed.track['flag'] in self.tUser['enemy'] and (choosed.isDiving or choosed.isStealth):
                directions = [(-1, 1), (1, 1), (-1, -1), (1, -1)]
                cols = len(self.map['map'][0])
                rows = len(self.map['map'])
                for j in directions:
                    x, y = j[0] + choosed.mapId[0], j[1] + choosed.mapId[1]
                    if x < 0 or x >= rows or y < 0 or y >= cols:
                        continue
                    if self.pointer_dw[x][y]:
                        if self.pointer_dw[x][y].track['flag'] not in self.tUser['enemy']:
                            choosed.show()
                            break
                else:
                    choosed.hide()
            else:
                choosed.show()

        elif type == 'attacking':
            enemy = self.pointer_dw[command['dw2']['mapId'][0]][command['dw2']['mapId'][1]]
            tem_dw = self.pointer_dw[command['dw1']['mapId'][0]][command['dw1']['mapId'][1]]
            if tem_dw.mapId[1] + 1 == enemy.mapId[1]:
                tem_dw.doBody('right')
            elif tem_dw.mapId[1] - 1 == enemy.mapId[1]:
                tem_dw.doBody('left')
            if not command['dw1']['isAlive']:
                self.pointer_dw[command['dw1']['mapId'][0]][command['dw1']['mapId'][1]] = None
                tem_dw.deleteLater()
            else:
                tem_dw.updateByTrack(command['dw1'])
                tem_dw.doBlood(tem_dw.bloodValue)
                tem_dw.doBody(ii['action'] + 'G')
            if not command['dw2']['isAlive']:
                self.pointer_dw[command['dw2']['mapId'][0]][command['dw2']['mapId'][1]] = None
                enemy.deleteLater()
            else:
                enemy.updateByTrack(command['dw2'])
                enemy.doBlood(enemy.bloodValue)
        elif type == 'occupy':
            choosed.occupied = command['occupy']
            if choosed.occupied >= 20:
                dw = self.pointer_geo[choosed.mapId[0]][choosed.mapId[1]]
                track = resource.find({'usage': 'build', 'name': dw.track['name'], 'flag': ii['flag']})
                dw.change(track=track)
                choosed.occupied = 0
            choosed.doBody(ii['action'] + 'G')
            choosed.moved = True
        elif type == 'loading':
            tem_dw = self.pointer_dw[command['road'][0][0]][command['road'][0][1]]
            self.pointer_dw[command['road'][0][0]][command['road'][0][1]] = None
            enemy = self.pointer_dw[command['road'][-1][0]][command['road'][-1][1]]
            enemy.loadings.append(tem_dw.makeTrack())
            tem_dw.deleteLater()
        elif type == 'unloading':
            choosed.loadings = command['loadings']
            choosed.doBody(ii['action'] + 'G')
            choosed.moved = True
            response = {'type': 'unloadShow', 'dws': command['dws'], 'flag': command['flag'], 'action': ii['action']}
            postEvent = CommandEvent(response)
            QCoreApplication.postEvent(self, postEvent)

        if self.tUser['flag'] not in ii['enemy']:
            for i in command['shouldShow']:
                self.pointer_dw[i[0]][i[1]].show()
        if 'costOil' in command:
            self.pointer_dw[command['road'][-1][0]][command['road'][-1][1]].oil -= command['costOil']
        self.isRun = True
        self.clear(None)
        self.timer.stop()

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
            tem_data_1[str(i1)] = {'dws': [], 'geos': []}
            for j1, j in enumerate(e2):
                if j1 == i1:
                    continue
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
            tem_data_1[str(i1)]['geos'] = sorted(tem_data_1[str(i1)]['geos'], key=lambda arg: arg[1])
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

    def costAreaCount(self, dw: DW):
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

    def areaCount(self, dw: DW, costMap=None):
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
                x, y = beginP[0] + i[0], beginP[1] + i[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
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

    def roadCount(self, dw: DW, last, costMap=None):
        self.roadsToChoose['point'] = 0
        if not costMap:
            print('roadCount error')
            return
        cost = resource.basicData['move'][dw.track['name']]['move_distance']
        oil = float(cost) if float(cost) <= dw.oil else dw.oil
        tem_map = costMap

        cols = len(tem_map[0])
        rows = len(tem_map)
        directions = [(1, 0), (-1, 0), (0, -1), (0, 1)]
        end = []

        def road(beginP, endP, length, hasgo=[]):
            hasgo_ = hasgo[:]
            # length_ = length - tem_map[beginP[0]][beginP[1]]
            hasgo_.append((beginP[0], beginP[1]))
            if length < 0:
                return
            if beginP[0] == endP[0] and beginP[1] == endP[1]:
                end.append(hasgo_[:])
                return
            for i in directions:
                x, y = beginP[0] + i[0], beginP[1] + i[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
                    continue
                if (x, y) not in hasgo:
                    length_ = length - tem_map[x][y]
                    road((x, y), endP, length_, hasgo_)

        road(dw.mapId, last, oil)
        return sorted(end, key=lambda arg: len(arg))

    ####有点特殊
    def findTarget(self, dw: DW, endP, moved=False):
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
        for k in range(int(min), int(max) + 1):
            for j in range(k + 1):
                for i in directions:
                    x, y = x1 + j * i[0], y1 + (k - j) * i[1]
                    if x < 0 or x >= rows or y < 0 or y >= cols or ((x, y) in self.targetsToChoose['choosed']):
                        continue
                    if self.pointer_dw[x][y]:
                        # print(self.pointer_dw[x][y].track['flag'], self.user['enemy'])
                        if self.pointer_dw[x][y].track['flag'] in self.user['enemy'] and not self.pointer_dw[x][
                            y].isHidden():
                            if float(resource.basicData['gf'][dw.track['name']][
                                         self.pointer_dw[x][y].track['name']]) > 0:
                                self.targetsToChoose['choosed'].append((x, y))
                                # isEmpty = False
        return not self.targetsToChoose['choosed']

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
        elif type == 'showpath':
            for j in self.areaToChoose:
                j.hide()
            try:
                for j in self.roadsToChoose['roads'][self.roadsToChoose['point']]:
                    circle = QFrame(self)
                    circle.setStyleSheet('border-radius:5px;border:3px solid rgb(100, 100,200)')
                    circle.show()
                    circle.setGeometry(self.pointer_geo[j[0]][j[1]].geometry())
                    self.roadsToChoose['layers'].append(circle)
            except IndexError:
                # print(self.dwChoosed)
                self.clear(None)
                self.rightMenu.hide()
                return
        elif type == 'showgftargets':
            a0 = data
            for i in self.findChildren(DW):
                if i.geometry().contains(a0.pos()):
                    end = []
                    max = resource.basicData['gf'][i.track['name']]['gf_maxdistance']
                    min = resource.basicData['gf'][i.track['name']]['gf_mindistance']
                    rows = len(self.map['map'])
                    cols = len(self.map['map'][0])
                    directions = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

                    def gfAreaCount(x1, y1):
                        for k in range(int(min), int(max) + 1):
                            for j in range(k + 1):
                                for i5 in directions:
                                    x, y = x1 + j * i5[0], y1 + (k - j) * i5[1]
                                    if x < 0 or x >= rows or y < 0 or y >= cols or (x, y) in end:
                                        continue
                                    end.append((x, y))

                    if max == 0 or i.bullect == 0:
                        return False
                    if resource.basicData['gf'][i.track['name']]['attackAftermove'] == '0':
                        gfAreaCount(i.mapId[0], i.mapId[1])
                    else:
                        tem_map = self.areaCount(i)
                        tem_1 = []
                        for i61, i6 in enumerate(tem_map):
                            for i71, i7 in enumerate(i6):
                                if i7 != -1:
                                    tem_1.append((i61, i71))
                        for i in tem_1:
                            gfAreaCount(i[0], i[1])
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
            for i in resource.findAll({'usage': 'dw', 'flag': self.user['flag'], 'action': 'left'}):
                if i['name'] == 'delete':
                    continue
                if resource.basicData['money']['classify'][i['name']] in keys or i['name'] in keys:
                    money = resource.basicData['money']['money'][i['name']]
                    text = resource.basicData['money']['chineseName'][i['name']] + '\t\t' + money + '$'
                    tem_end.append((i['pixmap'], text, i['name'], float(money)))
            tem_end = sorted(tem_end, key=lambda arg: arg[3])
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
                    dw.initUI({'usage': 'dw', 'name': type.name, 'flag': self.user['flag'],
                               'action': self.user['action'] + 'G'}, self.dwChoosed)
                    dw.setGeometry(self.pointer_geo[self.dwChoosed[0]][self.dwChoosed[1]].geometry())
                    self.pointer_dw[self.dwChoosed[0]][self.dwChoosed[1]] = dw
                    dw.moved = True
                    dw.show()
                    dw.raise_()
                    self.dwsListWidget.close()
                    self.user['money'] -= float(resource.basicData['money']['money'][type.name])
                    self.user['outcome'] += float(resource.basicData['money']['money'][type.name])
                    # %%%%%%%
                    command = {'type': 'builddw', 'flag': self.user['flag'], 'dw': dw.makeTrack(),
                               'user': self.user.copy()}
                    self.commands.append(command)
                    self.sentToServer(command)
                    print(command)
                    if self.user['money'] > 999999:
                        self.Head_money.setText('$??????')
                    else:
                        self.Head_money.setText('$' + str(int(self.user['money'])))

            # elif self.dwChoosedStatus == 'buy':
            #
        elif type == 'buy':
            self.dwChoosedStatus = 'buy'
            self.dwsListWidget = QWidget()
            self.dwsListWidget.setWindowModality(QtCore.Qt.ApplicationModal)
            layout = QFormLayout()
            self.dwsListWidget.setWindowTitle('选择单位')
            self.dwsListWidget.setFixedSize(300, 300)
            keys = resource.basicData['geo']['canbuild'][
                'factory' if self.dwChoosed.track['name'] == 'transport' else 'shipyard']
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
            # self.dwsListWidget.
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
                        self.pointer_dw[i[0]][i[1]].doBody(self.user['action'] + 'G')
                        self.pointer_dw[i[0]][i[1]].moved = True
                        dws.append(self.pointer_dw[i[0]][i[1]].mapId)

                    command = {'type': 'buied', 'flag': self.user['flag'], 'supplies': self.dwChoosed.supplies.copy(),
                               'dws': dws, 'user': self.user.copy()}
                    self.commands.append(command)
                    self.sentToServer(command)
                    print(command)
                    if self.user['money'] > 999999:
                        self.Head_money.setText('$??????')
                    else:
                        self.Head_money.setText('$' + str(self.user['money']))

                    self.clear(None)
                    self.dwsListWidget.close()

            elif data == 'quit':
                self.clear(None)
                self.dwsListWidget.close()

        else:
            print(type, data)

    def dwCommandCpu(self, command):
        for i1, i in enumerate(self.users):
            if i['flag'] == command['flag']:
                break
        self.command = command

        def updateMoney():
            if self.user['money'] > 999999:
                self.Head_money.setText('$??????')
            else:
                self.Head_money.setText('$' + str(self.user['money']))

        def handTheSame():
            # , choosed, actions, type, command
            if self.isUserTrackOpen:
                dw = self.pointer_dw[command['road'][0][0]][command['road'][0][1]]
                self.moveToDw(dw, choosed=dw, actions=command['road'], type=command['type'], command=command)
            else:
                self.animeCommandMove(self.pointer_dw[command['road'][0][0]][command['road'][0][1]], command['road'],
                                      command['type'], command)

        if command['type'] == 'builddw':
            dw = DW(self)
            dw.initUI({'usage': 'dw', 'flag': command['flag'], 'name': command['dw']['name'],
                       'action': self.users[i1]['action']}, )
            dw.setGeometry(self.pointer_geo[command['dw']['mapId'][0]][command['dw']['mapId'][1]].geometry())
            self.pointer_dw[command['dw']['mapId'][0]][command['dw']['mapId'][1]] = dw
            dw.show()
            dw.raise_()
            dw.doBody(self.users[i1]['action'] + 'G')
            self.users[i1]['moeny'] = command['user']['money']
            self.users[i1]['outcome'] = command['user']['outcome']
            updateMoney()
        elif command['type'] == 'buied':
            tem_dw = self.pointer_dw[command['dws'][0][0]][command['dws'][0][1]]
            tem_dw.supplies = command['supplies']
            for i in command['dws']:
                self.pointer_dw[i[0]][i[1]].moved = True
                self.pointer_dw[i[0]][i[1]].doBody(self.users[i1]['action'] + 'G')
                # i.moved = True
                # i.doBody(self.users[i1]['action']+'G')
            self.users[i1]['moeny'] = command['user']['money']
            self.users[i1]['outcome'] = command['user']['outcome']
            updateMoney()
        elif command['type'] == 'waiting':
            handTheSame()
        elif command['type'] == 'encounter':
            handTheSame()
        elif command['type'] == 'stealth':
            handTheSame()
        elif command['type'] == 'loading':
            handTheSame()
        elif command['type'] == 'unloading':
            handTheSame()
        elif command['type'] == 'occupy':
            handTheSame()
        elif command['type'] == 'attacking':
            handTheSame()

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
                if tem_dw.track['flag'] in self.user['enemy'] and i1 != len(actions) - 1:
                    actions = actions[0:i1]
                    self.dwChoosedStatus = 'encounter'
                    break
            for j in directions:
                x, y = i[0] + j[0], i[1] + j[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
                    continue
                tem_dw = self.pointer_dw[x][y]
                if tem_dw:
                    if tem_dw.track['flag'] in self.user[
                        'enemy'] and tem_dw.isHidden() and tem_dw not in self.shouldShow:
                        self.shouldShow.append(tem_dw)

        group = QSequentialAnimationGroup(self)
        for i in range(len(actions[:-1])):
            self.dwChoosed.raise_()
            tem_anime = QPropertyAnimation(self.dwChoosed, b'pos', self)
            tem_anime.setStartValue(self.pointer_geo[actions[i][0]][actions[i][1]].pos())
            tem_anime.setEndValue(self.pointer_geo[actions[i + 1][0]][actions[i + 1][1]].pos())
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
        resource.player['move_' + resource.basicData['money']['sound_move'][self.dwChoosed.track['name']]].play()
        self.timerGo((len(actions) - 1) * inter_time)
        # qapp.timerGo(len(actions)*inter_time)

    def animeCommandMove(self, choosed, actions, type, command):
        # self.moveToDw(choosed)
        # myThread(target=self.moveToDw, kwargs={'dw':choosed}).start()
        # while self.screnMoveAnimate.state() != 0:
        #     pass
        inter_time = 200
        group = QSequentialAnimationGroup(self)
        for i in range(len(actions[:-1])):
            choosed.raise_()
            tem_anime = QPropertyAnimation(choosed, b'pos', self)
            tem_anime.setStartValue(self.pointer_geo[actions[i][0]][actions[i][1]].pos())
            tem_anime.setEndValue(self.pointer_geo[actions[i + 1][0]][actions[i + 1][1]].pos())
            tem_anime.setDuration(inter_time)
            if i == 0:
                tem_anime.setEasingCurve(QEasingCurve.InQuad)
            group.addAnimation(tem_anime)
        if len(actions) != 1:
            choosed.occupied = 0
            if type != 'loading':
                self.pointer_dw[actions[0][0]][actions[0][1]].mapId = tuple(actions[-1])
                self.pointer_dw[actions[0][0]][actions[0][1]] = None
                self.pointer_dw[actions[-1][0]][actions[-1][1]] = choosed

        if actions[-1][1] > actions[0][1]:
            choosed.doBody('right')
        elif actions[-1][1] < actions[0][1]:
            choosed.doBody('left')
        tem_thread = myThread(target=self.commandTimeStop, \
                              kwargs={'command': command, 'choosed': choosed, 'type': type,
                                      'scends': ((len(actions) - 1) * inter_time) / 1000})
        group.start()
        tem_thread.start()

    def clear(self, toChooseStatus):
        self.infoView.hide()
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
            for i in [self.areaToChoose, self.roadsToChoose['layers'], self.targetsToChoose['layers'],
                      self.planToUnload['layers']]:
                for j in i:
                    j.deleteLater()
            self.dwChoosed = None
            self.areaToChoose = []
            self.roadsToChoose = {'point': 0, 'roads': [], 'layers': []}
            self.targetsToChoose = {'choosed': None, 'layers': []}
            self.choosePathMenu.hide()
            self.planToUnload = {'layers': [], 'data': [], 'loc': None}
            self.unloadMenu.hide()
        elif toChooseStatus == 'areashowed':
            for i in [self.roadsToChoose['layers'], self.targetsToChoose['layers'], self.planToUnload['layers']]:
                for j in i:
                    j.deleteLater()
            for i in self.areaToChoose:
                i.show()
            self.roadsToChoose = {'point': 0, 'roads': [], 'layers': []}
            self.targetsToChoose = {'choosed': None, 'layers': []}
            self.choosePathMenu.hide()
            self.planToUnload = {'layers': [], 'data': [], 'loc': None}
            self.unloadMenu.hide()
        elif toChooseStatus == 'pathshowed':
            for i in [self.targetsToChoose['layers'], self.planToUnload['layers']]:
                for j in i:
                    j.deleteLater()
            for i in self.roadsToChoose['layers']:
                i.show()
            self.targetsToChoose = {'choosed': None, 'layers': []}
            self.choosePathMenu.show()
            self.choosePathMenu.raise_()
            self.planToUnload = {'layers': [], 'data': [], 'loc': None}
            self.unloadMenu.hide()
        self.choose_status = toChooseStatus

    '''选择， 移动， 缩放'''

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == 1:
            resource.player['btn'].play()
        if self.screnMoveAnimate.state() != 0:
            return
        if a0.y() < self.height() // 2:
            if a0.x() < self.width() // 2:
                self.Head.move(self.width() - self.Head.width(), 0)
            else:
                self.Head.move(0, 0)
        if not self.isRun:
            return
        self.canRightMenuShow = True
        self.rightMenu.hide()

        if a0.button() == 1 and not self.hasMove:
            if self.choose_status == None:  # 0:
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
                    if self.user['flag'] != self.tUser['flag']:
                        return
                    tem_dw = self.childAt(a0.pos())
                    if hasattr(tem_dw, 'track'):
                        if tem_dw.track['usage'] == 'build':
                            if tem_dw.track['flag'] == self.user['flag'] and tem_dw.track['name'] in ['factory',
                                                                                                      'shipyard',
                                                                                                      'airport']:
                                self.clear(None)
                                self.dwChoosed = tuple(tem_dw.mapId)
                                self.dwCpu('showbuild', tem_dw.track['name'])
                            else:
                                self.clear(None)
                        else:
                            self.clear(None)
                    else:
                        self.clear(None)

            elif self.choose_status == 'areashowed':  # 1: user want to choose a tartget to show paths
                if self.user['flag'] != self.tUser['flag']:
                    self.clear(None)
                for i in self.areaToChoose:
                    if i.geometry().contains(a0.pos()):
                        self.targetsToChoose['choosed'] = tuple(i.mapId)
                        for j in self.choosePathMenu.findChildren(QPushButton):
                            j.hide()
                        self.choose_btn_waiting.show()

                        # 过滤 敌方单位，已移动过的单位
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

                        tem_dw = self.pointer_dw[i.mapId[0]][i.mapId[1]]  #####应小心改变它的值 ,可能值为：运输单位，None，隐形敌方单位
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
                                    resource.basicData['money']['canloading'][tem_dw.track['name']] or \
                                    resource.basicData['money']['classify'][self.dwChoosed.track['name']] in \
                                    resource.basicData['money']['canloading'][tem_dw.track['name']]:
                                if len(tem_dw.loadings) < int(
                                        resource.basicData['money']['canloading'][tem_dw.track['name']][0:1]):
                                    for j in self.choosePathMenu.findChildren(QPushButton):
                                        j.hide()
                                    self.choose_btn_loading.show()
                                else:  # 过滤装满的单位
                                    continue
                            else:  ##过滤 友方己方单位
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
                                        x, y = i.mapId[0] + j[0], i.mapId[1] + j[1]
                                        if x >= 0 and x < rows and y >= 0 and y < cols:
                                            if int(resource.basicData['move'][k['name']][
                                                       self.pointer_geo[x][y].track['name']]) < 99 and not \
                                                    self.pointer_dw[x][y]:
                                                odk2.append((x, y))
                                    if odk2:
                                        self.planToUnload['data'].append([k, odk2, False])
                            if self.planToUnload['data']:
                                self.choose_btn_unloading.show()
                                for j in self.unloadMenuItems:
                                    j.hide()
                                for j1, j in enumerate(self.planToUnload['data']):
                                    self.unloadMenuItems[j1].setText(
                                        resource.basicData['money']['chineseName'][j[0]['name']])
                                    self.unloadMenuItems[j1].setIcon(QIcon(resource.find(
                                        {'usage': 'dw', 'flag': self.user['flag'], 'action': 'left',
                                         'name': j[0]['name']})['pixmap']))
                                    self.unloadMenuItems[j1].track = j[0]

                        #####显示路径
                        self.roadsToChoose['roads'] = self.roadCount(self.dwChoosed, i.mapId, self.costMap)
                        self.dwCpu('showpath')

                        ###显示菜单
                        x1, y1 = a0.x(), a0.y()
                        if x1 + self.choosePathMenu.width() > self.width():
                            x1 = self.width() - self.choosePathMenu.width()
                        if y1 + self.choosePathMenu.height() > self.height():
                            y1 = self.height() - self.choosePathMenu.height()
                        self.choosePathMenu.move(x1, y1)
                        self.choosePathMenu.show()
                        self.choosePathMenu.raise_()
                        self.choose_status = 'pathshowed'  # 2
                        break
                else:
                    self.clear(None)

            elif self.choose_status == 'targetshowed':  # 3:
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
                        if y1 + self.unloadMenu.height() > self.height():
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
        elif a0.button() == 4:
            self.clear(None)
            for i in self.findChildren(DW):
                if i.contains(a0.pos()):
                    self.infoView.updateInfo(i.makeTrack())
                    self.infoView.move(a0.pos())
                    self.infoView.show()
                    self.infoView.raise_()
                    self.choose_status = 'showDwInfo'
                    break

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self.isRun:
            return

        if a0.button() == 2:
            if self.hasMove:
                if self.canRightMenuShow:
                    # if not self.infoView.isHidden():
                    #     self.infoView.hide()
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
        # if a0.pos().x() < self.width() // 2:
        #     self.Head.move(0, 0)
        # else:
        #     self.Head.move(self.width() - self.Head.width(), 0)
        # print('tack')
        if not self.isRun:
            return
        self.canRightMenuShow = False
        if not self.hasMove:
            return
        x, y = a0.x() - self.hasMove.x(), a0.y() - self.hasMove.y()
        self.hasMove = a0.pos()
        if self.pointer_geo[0][0].x() + x >= 0 or \
                self.pointer_geo[-1][-1].x() + x <= self.width() - self.mapBlockSize[0]:
            x = 0
        if self.pointer_geo[0][0].y() + y >= 0 or \
                self.pointer_geo[-1][-1].y() + y <= self.height() - self.mapBlockSize[1]:
            y = 0
        for i, i1 in enumerate(self.pointer_geo):
            for j, j1 in enumerate(i1):
                j1.move(x + j1.x(), y + j1.y())
                if self.pointer_dw[i][j]:
                    self.pointer_dw[i][j].move(x + self.pointer_dw[i][j].x(), y + self.pointer_dw[i][j].y())
        self.talkView.move(self.talkView.x() + x, self.talkView.y() + y)

    def wheelEvent(self, a0: QtGui.QWheelEvent = None) -> None:
        if self.isCtrlDown:
            if self.isRun:
                self.clear(None)
                self.mapScale(True if a0.angleDelta().y() > 0 else False)
            return
        if self.choose_status != 'pathshowed':
            return
        isUp = a0 if isinstance(a0, int) else -a0.angleDelta().y()
        if (isUp < 0 and self.roadsToChoose['point'] == 0) or (
                isUp > 0 and self.roadsToChoose['point'] >= len(self.roadsToChoose['roads']) - 1):
            self.roadsToChoose['point'] == 0 if isUp < 0 else len(self.roadsToChoose['roads']) - 1
            return
        for i in self.roadsToChoose['layers']:
            i.deleteLater()
        self.roadsToChoose['layers'] = []
        self.roadsToChoose['point'] += -1 if isUp < 0 else 1
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

    def event(self, a0: QtCore.QEvent) -> bool:
        if a0.type() == CommandEvent.idType:
            if a0.command['type'] == 'bout':  # %%%%%%%%%
                self.boutUpdate(True)
            elif a0.command['type'] == 'unloadShow':
                for i in a0.command['dws']:
                    tem_dw = DW(self)
                    tem_dw.initUI(
                        {'usage': 'dw', 'flag': a0.command['flag'], 'action': a0.command['action'] + 'G',
                         'name': i['name']},
                        i['mapId'])
                    tem_dw.updateByTrack(i)
                    tem_dw.setGeometry(self.pointer_geo[i['mapId'][0]][i['mapId'][1]].geometry())
                    self.pointer_dw[i['mapId'][0]][i['mapId'][1]] = tem_dw
                    tem_dw.show()
                    tem_dw.raise_()

            elif a0.command['type'] == 'command':
                self.dwCommandCpu(a0.command['command'])
            a0.accept()
            return True
        elif a0.type() == ScreenMovingEnd.idType:
            # , choosed, actions, type, command
            self.animeCommandMove(a0.data['choosed'], a0.data['actions'], a0.data['type'], a0.data['command'])
        return super(TMap, self).event(a0)

    def canTransport(self, dw: DW, p):
        tem_e = self.pointer_dw[p[0]][p[1]]
        if tem_e:
            if 'transport' in tem_e.track['name'] and tem_e.track['transport']:
                if dw.track['name'] in ['footmen', 'gunnery'] and tem_e.track['name'] == 'transport':
                    return True
                elif dw.track['name'] in ['footmen', 'gunnery'] and tem_e.track['name'] == 'transportShip':
                    return True
        return False
        # else:
        #     return True

    def moveToDw(self, dw: DW = None, **kwargs):
        # dw = self.findChild(DW)
        x, y = self.width() / 2 - dw.x(), self.height() / 2 - dw.y()
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
                tem_anime.setEndValue(QPoint(int(x + j1.x()), int(y + j1.y())))
                tem_anime.setDuration(400)
                anime_group.addAnimation(tem_anime)
                if self.pointer_dw[i][j]:
                    # self.pointer_dw[i][j].move(x+self.pointer_dw[i][j].x(), y+self.pointer_dw[i][j].y())
                    tem_anime2 = QPropertyAnimation(self.pointer_dw[i][j], b'pos', self)
                    tem_anime2.setStartValue(self.pointer_dw[i][j].pos())
                    tem_anime2.setEndValue(
                        QPoint(int(x + self.pointer_dw[i][j].x()), int(y + self.pointer_dw[i][j].y())))
                    tem_anime2.setDuration(400)
                    anime_group.addAnimation(tem_anime2)
        self.screnMoveAnimate = anime_group

        def animateStopped():
            while self.screnMoveAnimate.state() != 0:
                pass
            postEvent = ScreenMovingEnd(kwargs)
            QCoreApplication.postEvent(self, postEvent)

        anime_group.start()
        if kwargs:
            myThread(target=animateStopped).start()

    def running(self):
        pass

    def isVictory(self):
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
                                j.change(track=resource.find(
                                    {'usgae': 'build', 'name': j.track['name'], 'flag': tem.track['flag']}))
                    i['isOver'] = True
                # else:
                #     newusers.append(i)
            else:
                for j in self.findChildren(DW):
                    if j.track['flag'] == i['flag']:
                        i['canBeGua'] = True
                        # newusers.append(i)
                        break
                else:
                    if i['canBeGua']:
                        i['isOver'] = True

        for i in self.users:
            if i['flag'] == self.tUser['flag'] and i['isOver']:
                print('你输了')

        count = 0
        for i in self.users:
            if not i['isOver']:
                count += 1
        if count <= 1:
            print('game is over')
            return True

        return False

    def chooseRightMenu(self, data):
        self.collectMap()
        self.childWindow.deleteLater()
        self.childWindow = QWidget()
        self.childWindow.setWindowModality(Qt.ApplicationModal)
        layout = QBoxLayout(QBoxLayout.TopToBottom, self.childWindow)
        if data == 'beforevictory':
            self.childWindow.setWindowTitle('胜利条件')
            tem_1 = QLabel('战斗背景：' + self.user['command_bg'])
            tem_1.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(tem_1)
            tem_1 = QLabel('战斗目标：' + self.user['command'])
            tem_1.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(tem_1)
            tem_1 = QPushButton('忍气吞声地接受。。。')
            tem_1.clicked.connect(self.childWindow.close)
            layout.addWidget(tem_1)
            self.childWindow.setLayout(layout)
            self.childWindow.show()
            self.childWindow.setMinimumSize(200, 200)
        elif data == 'forces':  ##此处忽略军队价值
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
                        children[0].setPixmap(
                            resource.find({'usage': 'hero', 'name': i['hero'], 'action': 'post'})['pixmap'].scaled(100,
                                                                                                                   400))
                        children[1].setText(resource.basicData['hero_1'][i['hero']]['skill_dsc'])
                        children[2].setText(resource.basicData['hero_2'][i['hero']]['skill_dsc'])
                        children[3].setText(resource.basicData['hero_3'][i['hero']]['skill_dsc'])
                        break

            for i in self.users:
                inner_tem = QPushButton(i['flag'], self.childWindow)
                inner_tem.clicked.connect(functools.partial(chagneInForces, i['flag']))
                layout_inner_btns.addWidget(inner_tem)
                inner_btns.append(inner_tem)

            layout.addWidget(area)
            layout_2 = QBoxLayout(QBoxLayout.LeftToRight, self.childWindow)
            label = QLabel(self.childWindow)
            label.setPixmap(
                resource.find({'usage': 'hero', 'name': self.user['hero'], 'action': 'post'})['pixmap'].scaled(100,
                                                                                                               400))
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
            print('game over')
            pass  # %%%%%
        for j in self.findChildren(DW):
            if j:
                j.flush()
                j.myUpdate()

    def boutUpdate(self, fromServer=False):
        if not fromServer:
            if self.user['flag'] != self.tUser['flag']:
                return

            def send():
                newCommand = {'type': 'bout', 'flag': self.user['flag']}
                self.client.send(zlib.compress(json.dumps(newCommand).encode('utf-8')))

            if self.client:
                myThread(target=send).start()

        self.user['bout'] += 1
        self.isRun = False
        ##变亮
        for i in self.findChildren(DW):
            if i.track['flag'] == self.user['flag']:
                i.doBody(self.user['action'])
                i.moved = False
        ###玩家更换
        for i1, i in enumerate(self.users):
            if i == self.user:
                self.user = self.users[(i1 + 1) % len(self.users)]
                if self.user['isOver']:
                    self.user = self.users[(i1 + 2) % len(self.users)]
                break
        else:
            print('error')
        if self.user['flag'] == self.tUser['flag']:
            self.isRun = True
        print(self.user['flag'])
        ###%%%%%%
        print('播放特效->等待电脑或玩家')
        ##资金
        for i in self.findChildren(Geo):
            if i.track['usage'] == 'build':
                if i.track['flag'] == self.user['flag']:
                    self.user['money'] += self.globalData['income']
        self.user['outcome'] = 0

        # 换头
        self.Head_head.setPixmap(
            resource.find({'usage': 'hero', 'name': self.user['hero'], 'action': 'head'})['pixmap'].scaled(80, 80))
        self.Head_exp.setValue(self.user['exp'])
        self.Head_exp.setMaximum(int(resource.basicData['hero_f'][self.user['hero']]['max_energy']))
        self.Head_name.setText(self.user['hero'])
        self.Head.setStyleSheet('border-radius:5px;background-color:' + self.user['flag'] + ';')
        if self.user['money'] > 999999:
            self.Head_money.setText('$??????')
        else:
            self.Head_money.setText('$' + str(int(self.user['money'])))
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
            # 下面这个 if 为：城市的补给内容
            build = self.pointer_geo[i.mapId[0]][i.mapId[1]]
            key = resource.basicData['geo']['cansupply'][build.track['name']]
            if i.track['name'] in key or resource.basicData['money']['classify'][i.track['name']] in key:
                i.oil = int(resource.basicData['gf'][i.track['name']]['oil'])
                i.bullect = int(resource.basicData['gf'][i.track['name']]['bullect'])
                cost = round(10 - round(i.bloodValue))
                cost = 2 if cost >= 2 else cost
                if cost:
                    money = int(float(resource.basicData['money']['money'][i.track['name']]) * cost / 10)
                    if money < self.user['money']:
                        self.user['money'] -= money
                        if round(i.bloodValue + cost) == 10:
                            i.doBlood(10)
                        else:
                            i.doBlood(i.bloodValue + cost)
            ##计划补给
            if 'transport' in i.track['name']:
                shouldsupply = []
                points = []
                supplies = i.supplies
                for r1 in range(1, 3):
                    for y in range(0, r1 + 1):
                        for r2 in directions:
                            x1, y1 = i.mapId[0] + y * r2[0], i.mapId[1] + (r1 - y) * r2[1]
                            if x1 < 0 or x1 >= rows or y1 < 0 or y1 >= cols or (x1, y1) in points:
                                continue
                            if self.pointer_dw[x1][y1]:
                                if self.pointer_dw[x1][y1].track['flag'] != self.user['flag']:
                                    continue
                                if len(i.supplies):
                                    if round(self.pointer_dw[x1][y1].bloodValue) != 10 and \
                                            self.pointer_dw[x1][y1].track['flag'] == self.user['flag']:
                                        # print(self.pointer_dw[x1][y1])
                                        shouldsupply.append(self.pointer_dw[x1][y1])
                                        points.append((x1, y1))
                                else:
                                    data_1 = self.pointer_dw[x1][y1]
                                    data_1.oil = int(resource.basicData['gf'][data_1.track['name']]['oil'])
                                    data_1.bullect = int(resource.basicData['gf'][data_1.track['name']]['bullect'])
                shouldsupply = sorted(shouldsupply,
                                      key=lambda arg: float(resource.basicData['money']['money'][arg.track['name']]))
                for j in shouldsupply:
                    if j.track['name'] in supplies:
                        price = int(resource.basicData['money']['money'][j.track['name']])
                        addedBlood = supplies[j.track['name']] / price * 10
                        oil = int(resource.basicData['gf'][j.track['name']]['oil'])
                        print(price, addedBlood)
                        bullect = int(resource.basicData['gf'][j.track['name']]['bullect'])

                        if 10 - float(j.bloodValue) >= addedBlood:
                            j.doBlood(j.bloodValue + addedBlood)
                            del supplies[j.track['name']]
                        else:
                            supplies[j.track['name']] -= (10 - round(j.bloodValue)) * price
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
                    x, y = j[0] + i.mapId[0], j[1] + i.mapId[1]
                    if x < 0 or x >= rows or y < 0 or y >= cols:
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

    def clientHandle(self):
        while 1:
            try:
                response = self.client.recv(3072)
                response = json.loads(zlib.decompress(response).decode('utf-8'))
            except OSError:
                if self.clientEnd:
                    print('break')
                    break
                else:
                    continue
            except (zlib.error):
                print('zlib error, game over')
                self.client.close()
                break
            if response['type'] == 'command':
                postEvent = CommandEvent(response)
                QCoreApplication.postEvent(self, postEvent)
            elif response['type'] == 'bout':
                postEvent = CommandEvent(response)
                QCoreApplication.postEvent(self, postEvent)
            elif response['type'] == 'gameover':
                pass
        self.isClientThreadEnd = True

    def sentToServer(self, command):
        def send():
            newCommand = {'type': 'command', 'command': command}
            self.client.send(zlib.compress(json.dumps(newCommand).encode('utf-8')))

        if self.client:
            myThread(target=send).start()

    def updateWholeMap(self, map):
        for i1, i in enumerate(map['map']):
            for j1, j in enumerate(i):
                self.pointer_geo[i1][j1].change(track=resource.findByHafuman(j))
                if self.pointer_dw[i1][j1]:
                    self.pointer_dw[i1][j1].deleteLater()
                    self.pointer_dw[i1][j1] = None
        for i in map['dw']:
            track = resource.findByHafuman(i['hafuman'])
            axis = i['axis']
            track.update(i)
            dw = DW(self)
            dw.initUI(track, axis)
            dw.move(axis[1] * self.mapBlockSize[1], axis[0] * self.mapBlockSize[0])
            self.pointer_dw[axis[0]][axis[1]] = dw

        for i, i1 in enumerate(self.users):
            if i1['flag'] == self.tUser['flag']:
                break

        directions = [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        cols = len(self.map['map'][0])
        rows = len(self.map['map'])
        for i in self.findChildren(DW):
            i.show()
            if i.track['flag'] in i1['enemy'] and (i.isDiving or i.isStealth):
                for j in directions:
                    x, y = j[0] + i.mapId[0], j[1] + i.mapId[1]
                    if x < 0 or x >= rows or y < 0 or y >= cols:
                        continue
                    if self.pointer_dw[x][y]:
                        if self.pointer_dw[x][y].track['flag'] not in i1['enemy']:
                            break
                else:
                    i.hide()

    def dwTalk(self, dw: DW, string):
        dw = self.findChild(DW)
        self.talkView.setText(string)
        self.talkView.mapId = dw.mapId
        tem_geo = self.pointer_geo[self.talkView.mapId[0]][self.talkView.mapId[1]]
        x1, y1 = tem_geo.x() > self.width() // 2, tem_geo.y() > self.height() // 2
        if not x1 and not y1:
            self.talkView.setStyleSheet(
                'background-color:white;padding:6px;border-radius:15px;border-top-left-radius:0;')
            x2, y2 = tem_geo.x(), tem_geo.y() + tem_geo.height()
        elif x1 and not y1:
            self.talkView.setStyleSheet(
                'background-color:white;padding:6px;border-radius:15px;border-top-right-radius:0;')
            x2, y2 = tem_geo.x() - (self.talkView.width() - tem_geo.width()), tem_geo.y() + tem_geo.height()
        elif not x1 and y1:
            self.talkView.setStyleSheet(
                'background-color:white;padding:6px;border-radius:15px;border-bottom-left-radius:0;')
            x2, y2 = tem_geo.x(), tem_geo.y() - self.talkView.height()
        elif not x1 and not y1:
            self.talkView.setStyleSheet(
                'background-color:white;padding:6px;border-radius:15px;border-bottom-right-radius:0;')
            x2, y2 = tem_geo.x() - (self.talkView.width() - tem_geo.width()), tem_geo.y() - self.talkView.height()
        self.talkView.move(x2, y2)
        self.talkView.show()
        self.talkView.shouldShow = True
        self.talkView.raise_()

    def talkManager(self):
        pass


class InfoView(QFrame):
    def __init__(self, parent):
        super(InfoView, self).__init__(parent)
        self.initUI()

    def updateInfo(self, track):
        self.head.setPixmap(
            resource.find({'usage': 'dw', 'name': track['name'], 'flag': track['flag'], 'action': 'left'})[
                'pixmap'].scaled(80, 80))
        self.dsc.setText(track['name'] + '\n' + resource.basicData['money']['dsc'][track['name']])
        stealth = '是' if track['isStealth'] else '否'
        diving = '是' if track['isDiving'] else '否'
        self.infoLabel.setText(
            '规模:' + str(int(track['blood'])) + '    ' + '弹药:' + str(int(track['bullect'])) + '    ' + '油量:' + str(
                int(track['oil'])) + '\n' \
            + '占领:' + str(track['occupied']) + '    ' + '隐形:' + stealth + '    ' + '下潜:' + diving)
        for i in self.loadings:
            i.hide()
        for i1, i in enumerate(track['loadings']):
            self.loadings[i1].setIcon(
                QIcon(resource.find({'usage': 'dw', 'name': i['name'], 'flag': i['flag'], 'action': 'left'})['pixmap']))
            self.loadings[i1].setText(i['name'] + '(' + str(int(i['blood'])) + ')')
            self.loadings[i1].show()
        self.supplies.clear()
        for i, j in track['supplies'].items():
            self.supplies.addItem(QListWidgetItem(
                QIcon(resource.find({'usage': 'dw', 'name': i, 'flag': track['flag'], 'action': 'left'})['pixmap']),
                i + '\t' + str(j)))
        if not track['supplies']:
            self.planTitle.hide()
            self.supplies.hide()
        else:
            self.supplies.show()
            self.planTitle.show()
        if not track['loadings']:
            for i in self.loading:
                i.hide()
        else:
            for i in self.loading:
                i.show()

    def initUI(self):
        self.setMinimumSize(200, 200)
        self.setStyleSheet('border-radius:20px;background-color:white;')
        self.head = QLabel(self)
        # self.dsc = QTextEdit(self)
        self.dsc = QLabel(self)
        # self.dsc.setLineWrapMode(1)
        # self.dsc.setWordWrapMode(1)
        self.infoLabel = QLabel(self)
        self.loadings = [QPushButton(self), QPushButton(self)]
        self.loading = []
        self.supplies = QListWidget(self)
        layout1 = QBoxLayout(QBoxLayout.LeftToRight)
        layout1.addWidget(self.head)
        layout1.addWidget(self.dsc)
        layout2 = QBoxLayout(QBoxLayout.LeftToRight)
        tem_titil = QLabel('装载:')
        layout2.addWidget(tem_titil)
        layout2.addWidget(self.loadings[0])
        layout2.addWidget(self.loadings[1])
        self.loading = [tem_titil, self.loadings[0], self.loadings[1]]
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addLayout(layout1)
        layout.addWidget(self.infoLabel)
        layout.addLayout(layout2)
        self.planTitle = QLabel('计划补给:', self)
        layout.addWidget(self.planTitle)
        layout.addWidget(self.supplies)
        self.setLayout(layout)

class CommandEvent(QEvent):
    idType = QEvent.registerEventType()

    def __init__(self, command):
        super(CommandEvent, self).__init__(CommandEvent.idType)
        self.command = command

class ScreenMovingEnd(QEvent):
    idType = QEvent.registerEventType()

    def __init__(self, kwargs):
        super(ScreenMovingEnd, self).__init__(ScreenMovingEnd.idType)
        self.data = kwargs


'''-----------------新的哦---------------------'''

class TMap_(QWidget):
    def __init__(self, fuse, mapName='default'):
        super(TMap_, self).__init__()
        # fuse = {'red':{'hero', 'isMe', 'user', 'userInfo}}
        ## userInfo, heroName, isMe/action, enemy, dataInfo, dispos,
        resource.initMap(mapName, True)
        self.forces = fuse
        self.nowForce = list(self.forces.keys())[0]
        self.myForce = 'red'
        for i, j in fuse.items():
            if j['isMe']:
                self.myForce = i
                break

        # ----
        keys1 = ['money', 'income', 'outcome', 'destory', 'loss', 'armyPrice', 'energy', \
                 'bout', 'oil', 'bullect', 'landmissile', 'seamissile', 'skymissile', 'nuclear', \
                 '_money', '_oil', '_bullect']
        keys2 = ['backup', 'lines', 'story']
        for i, j in fuse.items():
            tem_data = {}
            tem_dispos = {}
            for k1 in keys1:
                if k1 in resource.heroAtrs[i]:
                    tem_data[k1] = resource.heroAtrs[i][k1]
                else:
                    tem_data[k1] = 0
            for k1 in keys2:
                if k1 in resource.heroAtrs[i]:
                    tem_dispos[k1] = resource.heroAtrs[i][k1]
                else:
                    tem_dispos[k1] = ''

            self.forces[i]['dataInfo'] = tem_data
            self.forces[i]['enemy'] = resource.heroAtrs[i]['enemy'].copy()
            self.forces[i]['dispos'] = tem_dispos


        self.initUI(mapName)

        self.hasMove = False
        self.isCtrlDown = False

        self.dwUpdater = QTimer(self)
        self.dwUpdater.timeout.connect(self.myUpdate)
        self.dwUpdater.start(1400)


        '''太慢了'''
        '''99 kill all
        self.isGameOver = False
        self.mapMoveThread = None
        # self.mapMoveThreadStatus = False    # 方向
        self.canMapMoveThreadRun = True     # 停止
        self.mapMoveMessage = Queue(maxsize=32)
        self.mapMoveCpuThread = Thread(target=self.mapMoveCpuCall)
        self.mapMoveCpuThread.start()
        '''

    def initUI(self, mapName, winSize=QSize(800, 800)):
        self.mapBlockSize = resource.mapScaleList[resource.mapScaleDoublePoint]['body']

        self.setFixedSize(winSize)

        self.map = resource.findMap(mapName)
        if not self.map:
            print(self.map, 'error', mapName)
            sys.exit()

        self.mapSize = len(self.map['map'][0]), len(self.map['map'])

        self.bg = QLabel(self)
        self.bg.setScaledContents(True)
        self.bg.resize(self.mapSize[0] * self.mapBlockSize[0], self.mapSize[1] * self.mapBlockSize[1])
        self.bg.setPixmap(QPixmap('maps/' + mapName + '/bg.gif'))

        self.min_bg = MinBackground(self, mapName)
        self.min_bg.move((self.width() - self.min_bg.width()) // 2, (self.height() - self.min_bg.height()) // 2)
        self.min_bg.hide()

        self.pointer_geo = []
        self.pointer_dw = [[None for i in range(self.mapSize[0])] for j in range(self.mapSize[1])]



        tem_data = []
        for i in range(self.mapSize[0]):
            track = resource.find({'usage': 'border'})
            if not track:
                print('map error122343')
                return
            track['mapId'] = 0, i
            tem_geo = Geo(self, track)
            tem_geo.move(i * self.mapBlockSize[0], 0)
            tem_data.append(tem_geo)
        self.pointer_geo.append(tem_data)

        for i in range(1, len(self.map['map'])):
            tem_data = []
            for j in range(len(self.map['map'][i])):
                if j == 0 or j == self.mapSize[0] - 1:
                    track = resource.find({'usage': 'border'})
                else:
                    track = resource.findByHafuman(self.map['map'][i][j])
                    if not track:
                        print('map error123')
                        return
                track['mapId'] = i, j
                tem_geo = Geo(self, track)
                tem_geo.move(j * self.mapBlockSize[0], i * self.mapBlockSize[1])
                tem_data.append(tem_geo)
            self.pointer_geo.append(tem_data)

        # for i in range(1, self.mapSize[1]):
        #     tem_data = []
        #     for j in range(self.mapSize[0]):
        #         track = resource.findByHafuman(self.map['map'][i][j])
        #         if not track:
        #             print('error:map initUI, hafuman')
        #             sys.exit()
        #         track['mapId'] = i, j
        #         tem_geo = Geo(self, track)
        #         tem_geo.move(j*self.mapBlockSize[0], i*self.mapBlockSize[1])
        #         tem_data.append(tem_geo)
        #     self.pointer_geo.append(tem_data)

        tem_data = []
        for i in range(self.mapSize[0]):
            track = resource.find({'usage': 'border'})
            track['mapId'] = self.mapSize[1] - 1, i
            tem_geo = Geo(self, track)
            tem_geo.move(i * self.mapBlockSize[0], self.mapBlockSize[1] * (self.mapSize[1] - 1))
            tem_data.append(tem_geo)
        self.pointer_geo.append(tem_data)



        for i in self.map['dw']:
            track = resource.findByHafuman(i['base64'])
            track.update(i)
            axis = track['mapId']
            dw = DW(self, track)
            dw.move(axis[1] * self.mapBlockSize[1], axis[0] * self.mapBlockSize[0])
            if i['flag'] == self.myForce:
                action = 'right'
            else:
                action = 'left'
            if track['moved']:
                action += 'G'
            dw.doBody(action)
            self.pointer_dw[axis[0]][axis[1]] = dw





        self.setMouseTracking(True)
        for i in range(8):
            MapBorder(self, i)

        self.canMove = (True if self.mapBlockSize[0] * self.mapSize[0] > self.width() else False,
                        True if self.mapBlockSize[1] * self.mapSize[1] > self.height() else False)

        # self.mapScale(True)

        self.layers = []
        self.isRun = True


        self.rightMenu = mapRightMenu(self)
        self.rightMenu.hide()
        self.canRightMenuShow = True
        self.leftMenu = mapLeftMenu(self)
        self.leftMenu.hide()
        self.infoVew = infoView(self)
        self.infoVew.hide()
        self.animation = None
        self.shopkeeper = ShopKeeper(self)
        self.supplyMenu = None
        self.buildMenu = buildMenu(self, {'usage':'build', 'name':'shipyard', 'flag':'none'})
        self.buildMenu.setWindowModality(Qt.ApplicationModal)
        self.buildMenu.hide()

        self.victoryBG = storiesView(self)
        self.victoryBG.setWindowModality(Qt.ApplicationModal)
        self.victoryBG.hide()
        self.militaryView = militaryView(self)
        self.militaryView.setWindowModality(Qt.ApplicationModal)
        self.militaryView.hide()


        self.msgView = msgView(self)
        self.inputVew = inputView(self)
        self.inputVew.hide()
        self.headView = headView(self)
        self.headView.swapUser(self.myForce)

        self.postCoverView = postCoverView(self)

        self.show()

        # self.setTabletTracking(True)

        # self.canScale = False
        # self.hasCircle = self.hasMove = False
        # self.circled = []
        # self.circle = QFrame(self)
        # # self.setP
        # self.circle.setFrameShape(QFrame.Box)
        # self.circle.setFrameShadow(QFrame.Sunken)
        # self.circle.setStyleSheet('background-color:#00a7d0;')
        # op = QGraphicsOpacityEffect()
        # op.setOpacity(0.4)
        # self.circle.setGraphicsEffect(op)
        # self.circle.hide()
        # self.circle.setLineWidth(0)
        # self.circleStatus = None
        #
        #
        #
        #
        #
        # self.circle.deleteLater()
        # del self.circled, self.circleStatus
        # # self.showFullScreen()
        # self.canMove = (True if self.mapBlockSize[0] * self.mapSize[0] > self.width() else False,
        #                 True if self.mapBlockSize[1] * self.mapSize[1] > self.height() else False)
        # x, y = (self.width() - self.mapBlockSize[0] * self.mapSize[0]) // 2, (
        #             self.height() - self.mapBlockSize[1] * self.mapSize[1]) // 2
        # self.mapMove(x, y, True)
        # self.isCtrlDown = False
        #
        # self.dwsListWidget = None
        #
        # # self.choosePathMenu = QFrame(self)
        # # layout_choosePath = QBoxLayout(QBoxLayout.TopToBottom)
        # # self.choose_btn_waiting = QPushButton('待命')
        # # self.choose_btn_waiting.clicked.connect(functools.partial(self.dwCpu, 'waiting'))
        # # layout_choosePath.addWidget(self.choose_btn_waiting)
        # # self.choose_btn_attacking = QPushButton('攻击')
        # # self.choose_btn_attacking.clicked.connect(functools.partial(self.dwCpu, 'attack'))
        # # layout_choosePath.addWidget(self.choose_btn_attacking)
        # # self.choose_btn_stealth = QPushButton('隐身')
        # # self.choose_btn_stealth.clicked.connect(functools.partial(self.dwCpu, 'stealth'))
        # # layout_choosePath.addWidget(self.choose_btn_stealth)
        # # self.choose_btn_occupy = QPushButton('占领')
        # # self.choose_btn_occupy.clicked.connect(functools.partial(self.dwCpu, 'occupy'))
        # # layout_choosePath.addWidget(self.choose_btn_occupy)
        # # self.choose_btn_loading = QPushButton('搭载')
        # # self.choose_btn_loading.clicked.connect(functools.partial(self.dwCpu, 'loading'))
        # # layout_choosePath.addWidget(self.choose_btn_loading)
        # # self.choose_btn_unloading = QPushButton('卸载')
        # # self.choose_btn_unloading.clicked.connect(functools.partial(self.dwCpu, 'unload'))
        # # layout_choosePath.addWidget(self.choose_btn_unloading)
        # # self.choose_btn_laymine = QPushButton('布雷')
        # # self.choose_btn_laymine.clicked.connect(functools.partial(self.dwCpu, 'laymine'))
        # # layout_choosePath.addWidget(self.choose_btn_laymine)
        # # self.choose_btn_buy = QPushButton('计划补给')
        # # self.choose_btn_buy.clicked.connect(functools.partial(self.dwCpu, 'buy'))
        # # layout_choosePath.addWidget(self.choose_btn_buy)
        # # self.choosePathMenu.setLayout(layout_choosePath)
        # # self.choosePathMenu.show()
        # # self.choosePathMenu.hide()
        # #
        # # self.unloadMenu = QFrame(self)
        # # layout_choosePath = QBoxLayout(QBoxLayout.TopToBottom)
        # # self.unloadMenuItems = []
        # # for i in range(5):
        # #     tem_btn = QPushButton('完成')
        # #     tem_btn.track = None
        # #     layout_choosePath.addWidget(tem_btn)
        # #     tem_btn.clicked.connect(functools.partial(self.dwCpu, 'unloading', tem_btn))
        # #     # tem_btn.show()
        # #     self.unloadMenuItems.append(tem_btn)
        # # self.unloadMenu.setLayout(layout_choosePath)
        # # self.unloadMenu.show()
        # # self.unloadMenu.hide()
        # #
        # # self.rightMenu = QFrame(self)
        # # layout_choosePath = QBoxLayout(QBoxLayout.TopToBottom)
        # # tem_action = QPushButton('胜利条件')
        # # tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'beforevictory'))
        # # layout_choosePath.addWidget(tem_action)
        # # tem_action = QPushButton('兵力')
        # # tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'forces'))
        # # layout_choosePath.addWidget(tem_action)
        # # # tem_action = QPushButton('读取记录')
        # # # tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'read'))
        # # # layout_choosePath.addWidget(tem_action)
        # # tem_action = QPushButton('保存记录')
        # # tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'save'))
        # # layout_choosePath.addWidget(tem_action)
        # # tem_action = QPushButton('退出')
        # # tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'exit'))
        # # layout_choosePath.addWidget(tem_action)
        # # tem_action = QPushButton('回合结束')
        # # tem_action.clicked.connect(functools.partial(self.chooseRightMenu, 'end'))
        # # layout_choosePath.addWidget(tem_action)
        # # self.rightMenu.setLayout(layout_choosePath)
        # # self.rightMenu.show()
        # # self.rightMenu.hide()
        # # self.canRightMenuShow = True
        # #
        # # self.Head = QFrame(self)
        # # self.Head.setWindowFlag(Qt.WindowStaysOnTopHint)
        # # self.Head_head = QLabel(self.Head)
        # # self.Head_head.setPixmap(
        # #     QPixmap(resource.find({'usage': 'hero', 'name': self.user['hero']})['pixmap']).scaled(80, 80))
        # # self.Head_exp = QProgressBar(self.Head)
        # # self.Head_exp.setMaximum(int(resource.basicData['hero_f'][self.user['hero']]['max_energy']))
        # # self.Head_exp.setAlignment(Qt.AlignVCenter)
        # # self.Head_exp.valueChanged.connect(self.proValueChange)
        # # self.Head_exp.setValue(self.user['exp'])
        # # self.Head_name = QLabel(self.user['hero'])
        # # self.Head_money = QLabel('$' + str(int(self.user['money'])))
        # # head_font = QFont('宋体', 20)
        # # head_font.setBold(True)
        # # self.Head_money.setFont(head_font)
        # # self.Head_name.setFont(head_font)
        # # self.Head.setStyleSheet('border-radius:5px;background-color:' + self.user['flag'] + ';')
        # # head_layout = QBoxLayout(QBoxLayout.LeftToRight)
        # # head_layout_ = QBoxLayout(QBoxLayout.TopToBottom)
        # # head_layout_.addWidget(self.Head_name)
        # # head_layout_.addWidget(self.Head_money)
        # # head_layout_.addWidget(self.Head_exp)
        # # head_layout.addWidget(self.Head_head)
        # # head_layout.addLayout(head_layout_)
        # # self.Head.setLayout(head_layout)
        # # self.Head.move(0, 0)
        # # self.Head.show()
        # # self.Head.raise_()
        #
        # self.infoView = InfoView(self)
        # self.infoView.show()
        # self.infoView.hide()
        #
        #
        # self.childWindow = QWidget()
        # self.childWindow.setWindowModality(Qt.ApplicationModal)
        #
        # self.talkView = QLabel(self)
        # self.talkView.setMaximumWidth(400)
        # # self.talkView.setStyleSheet('border-radius:12px;background-color:white;padding:6px;border-top-left-radius:0;')
        # self.talkView.setFont(QFont('宋体', 22))
        # self.talkView.setWordWrap(True)
        # self.talkView.show()
        # self.talkView.hide()
        # self.talkView.mapId = (0, 0)
        # self.talkView.shouldShow = False

        # self.setMouseTracking(True)

    def showMiniMap(self, true=True):
        if true:
            self.min_bg.show()
            self.min_bg.raise_()
            self.isRun = False
        else:
            self.min_bg.hide()
            self.isRun = True

    def mapMove(self, x, y, isforce=False):
        def move(x, y):
            self.bg.move(x + self.bg.x(), y + self.bg.y())
            for i in self.findChildren((DW, Geo)):
                i.move(i.x() + x, i.y() + y)
            for i in self.findChildren(MapBorder):
                i.raise_()
            for i in self.layers:
                i.move(self.pointer_geo[i.mapId[0]][i.mapId[1]].geometry())

        def moveTo(x_, y_):
            # print(x_, y_, self.mapSize, self.pointer_geo[0][0].x())
            self.bg.move(x_, y_)
            if x_ == None and y_ == None:
                return
            elif x_ == None:
                for i in self.findChildren((DW, Geo)):
                    i.move(i.x(), y_ + i.mapId[0] * self.mapBlockSize[0])
            elif y_ == None:
                for i in self.findChildren((DW, Geo)):
                    i.move(x_ + i.mapId[1] * self.mapBlockSize[0], i.y())
            else:
                for i in self.findChildren((DW, Geo)):
                    i.move(x_ + i.mapId[1] * self.mapBlockSize[0], y_ + i.mapId[0] * self.mapBlockSize[1])

            for i in self.layers:
                # print(i.mapId, self.pointer_geo[i.mapId[0]][i.mapId[1]].pos())
                i.move(self.pointer_geo[i.mapId[0]][i.mapId[1]].pos())
                # i.setGeometry(self.pointer_geo[i.mapId[0]][i.mapId[1]].geometry())
                i.show()
                i.raise_()


        ##----------越界判断----------------#
        if isforce:
            move(x, y)

        else:
            moved_x, moved_y = None, None

            if self.canMove[0]:
                if self.bg.x() + x > 0:
                    moved_x = 0
                elif self.bg.x() + self.bg.width() + x < self.width():
                    moved_x = self.width() - self.bg.width()
                else:
                    moved_x = x + self.bg.x()

            if self.canMove[1]:
                if self.bg.y() + y > 0:
                    moved_y = 0
                elif self.bg.y() + self.bg.height() + y < self.height():
                    moved_y = self.height() - self.bg.height()
                else:
                    moved_y = y + self.bg.y()

            moveTo(moved_x, moved_y)

    '''太慢了'''
    '''太慢了
    
    def mapMoveCall(self, x, y, speed=1):
        x, y = x * speed, y * speed
        while self.canMapMoveThreadRun and not self.isGameOver:
            self.mapMove(x, y)
            print('22')
            if x < 0:
                if self.bg.x() < 0:
                    break
            else:
                if self.bg.x() + self.bg.width() >= self.width():
                    break
            if y < 0:
                if self.bg.y() < 0:
                    break
            else:
                if self.bg.y() + self.bg.height() >= self.height():
                    break

            # time.sleep(0.02)
        self.mapMoveThread = None
        print('break')
        # self.canMapMoveThreadRun = True

    def mapMoveCpuCall(self):
        while not self.isGameOver:
            direction = self.mapMoveMessage.get()
            print(direction, '111')
            if direction > 0:
                if direction == MapBorder.direction_bottom:
                    x, y = 0, 1
                elif direction == MapBorder.direction_top:
                    x, y = 0, -1
                elif direction == MapBorder.direction_left:
                    x, y = -1, 0
                elif direction == MapBorder.direction_right:
                    x, y = 1, 0
                elif direction == MapBorder.direction_rightTop:
                    x, y = 1, -1
                elif direction == MapBorder.direction_rightBottom:
                    x, y = 1, 1
                elif direction == MapBorder.direction_leftTop:
                    x, y = -1, -1
                elif direction == MapBorder.direction_leftBottom:
                    x, y = -1, 1
                self.canMapMoveThreadRun = False
                while self.mapMoveThread:
                    pass
                self.canMapMoveThreadRun = True
                self.mapMoveThread = Thread(target=self.mapMoveThread, kwargs={'x':x, 'y': y})
                self.mapMoveThread.start()

            elif direction < 0:
                self.canMapMoveThreadRun = False
    
    '''

    def moveToDw(self, p, **kwargs):
        '''

        :param p:(x, y)
        :param kwargs:
        :return:
        '''
        # dw = self.findChild(DW)
        x, y = self.width() / 2 - p[0], self.height() / 2 - p[1]
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
                tem_anime.setEndValue(QPoint(int(x + j1.x()), int(y + j1.y())))
                tem_anime.setDuration(400)
                anime_group.addAnimation(tem_anime)
                if self.pointer_dw[i][j]:
                    # self.pointer_dw[i][j].move(x+self.pointer_dw[i][j].x(), y+self.pointer_dw[i][j].y())
                    tem_anime2 = QPropertyAnimation(self.pointer_dw[i][j], b'pos', self)
                    tem_anime2.setStartValue(self.pointer_dw[i][j].pos())
                    tem_anime2.setEndValue(
                        QPoint(int(x + self.pointer_dw[i][j].x()), int(y + self.pointer_dw[i][j].y())))
                    tem_anime2.setDuration(400)
                    anime_group.addAnimation(tem_anime2)
        self.screnMoveAnimate = anime_group

        def animateStopped():
            while self.screnMoveAnimate.state() != 0:
                pass
            postEvent = ScreenMovingEnd(kwargs)
            QCoreApplication.postEvent(self, postEvent)

        anime_group.start()
        if kwargs:
            myThread(target=animateStopped).start()

    '''选择， 移动， 缩放'''

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self.isRun:
            return

        self.rightMenu.hide()
        self.canRightMenuShow = True
        if a0.button() == 1:
            resource.player['btn'].play()
        if a0.button() == 2:
            self.hasMove = a0.pos()
        else:
            self.shopkeeper.handleEvent(a0)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self.isRun:
            return
        self.shopkeeper.handleEvent(a0)
        if a0.button() == 2:
            self.hasMove = None
            '''不可删'''
            if not self.shopkeeper.waiter and self.canRightMenuShow:
                self.rightMenu.show(a0.pos())
            self.canRightMenuShow = True
            self.shopkeeper.handleEvent(a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self.isRun:
            return
        if not self.hasMove:
            return
        x, y = a0.x() - self.hasMove.x(), a0.y() - self.hasMove.y()
        self.hasMove = a0.pos()
        self.canRightMenuShow = False
        # self.mapMove(x, y, True)
        self.mapMove(x, y)

    def wheelEvent(self, a0: QtGui.QWheelEvent = None) -> None:
        if self.isRun:
            self.shopkeeper.handleEvent(a0)
        if self.isCtrlDown:
            self.showMiniMap(True if a0.angleDelta().y() > 0 else False)


    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Return:
            if self.inputVew.isHidden():
                self.inputVew.show()
            else:
                self.inputVew.hide()
        elif a0.key() == Qt.Key_Control:
            self.isCtrlDown = True

        if not self.isRun:
            return
        self.shopkeeper.handleEvent(a0)

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        #self.shopkeeper.handleEvent(a0)
        if a0.key() == Qt.Key_Control:
            self.isCtrlDown = False

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        self.canMapMoveThreadRun = False

    def event(self, a0: QtCore.QEvent) -> bool:
        if a0.type() == MapMoveEvent.idType:
            # if a0.isIn:
            #     self.mapMoveMessage.put(a0.direction)
            # else:
            #     self.mapMoveMessage.put(-a0.direction)
            pass

        elif a0.type() == UnloadDwEvent.idType:
            for i in a0.loadings:
                dw = DW(self, i)
                dw.setGeometry(self.pointer_geo[i['mapId'][0]][i['mapId'][1]].geometry())
                self.pointer_dw[i['mapId'][0]][i['mapId'][1]] = dw
                if i['flag'] == self.myForce:
                    action = 'right'
                else:
                    action = 'left'
                if resource.basicData['money']['canunloadbyfly'][i['name']] != '1':
                    action += 'G'
                    dw.moved = True
                else:
                    dw.moved = False

        elif a0.type() == BuildDwEvent.idType:
            if a0.track['flag'] == self.myForce:
                action = 'rightG'
            else:
                action = 'leftG'
            track = {'usage':'dw', 'moved':True, \
                     'flag':a0.track['flag'], 'name':a0.track['name'], \
                     'action':action, 'mapId':a0.track['mapId']}
            dw = DW(self, track)
            dw.setGeometry(self.pointer_geo[track['mapId'][0]][track['mapId'][1]].geometry())
            self.pointer_dw[track['mapId'][0]][track['mapId'][1]] = dw

        elif a0.type() == SupplyEvent.idType:
            if self.supplyMenu:
                try:
                    self.supplyMenu.deleteLater()
                except:
                    pass
            self.supplyMenu = supplyMenu(self, a0.supply)
            self.supplyMenu.setWindowModality(Qt.ApplicationModal)
            self.supplyMenu.show()

        return super(TMap_, self).event(a0)

    def showLayers(self, points, color='green', clear=True):
        if clear:
            self.clearLayers()
        for i in points:
            circle = QFrame(self)
            circle.mapId = i[0], i[1]
            circle.setStyleSheet('border-radius:5px;border:3px solid ' + color + ';')
            circle.show()
            circle.setGeometry(self.pointer_geo[i[0]][i[1]].geometry())
            # circle.resize()
            self.layers.append(circle)


    def clearLayers(self):
        for i in self.layers:
            i.deleteLater()
        self.layers = []

    def showrightmenu(self, actions):
        # self.rightMenu = mapRightMenu()
        pass

    def showleftMenu(self, actions, pos=None):
        # if self.leftMenu:
        #     try:
        #         self.leftMenu.deleteLater()
        #     except:
        #         pass
        if pos:
            self.leftMenu.move(pos)
        self.leftMenu.swap(actions, self.shopkeeper.waiter)
        # self.leftMenu.initUI(actions, self.shopkeeper.waiter)
        # self.leftMenu.show()

    def showbuildMenu(self, track):
        self.buildMenu.initUI(track)
        self.buildMenu.show()

    def showInfoView(self, pos):
        pass

    def animeMove(self, actions, obj):
        inter_time = 200
        dw = self.pointer_dw[actions[0][0]][actions[0][1]]
        group = QSequentialAnimationGroup(self)
        for i in range(len(actions[:-1])):
            dw.raise_()
            tem_anime = QPropertyAnimation(dw, b'pos', self)
            tem_anime.setStartValue(self.pointer_geo[actions[i][0]][actions[i][1]].pos())
            tem_anime.setEndValue(self.pointer_geo[actions[i + 1][0]][actions[i + 1][1]].pos())
            tem_anime.setDuration(inter_time)
            if i == 0:
                tem_anime.setEasingCurve(QEasingCurve.InQuad)
            group.addAnimation(tem_anime)
        # for i in self.roadsToChoose['layers']:
        #     i.hide()
        # self.choosePathMenu.hide()
        # if len(actions) != 1:
        #     self.dwChoosed.occupied = 0
        #     if self.dwChoosedStatus != 'loading':
        #         self.pointer_dw[actions[0][0]][actions[0][1]] = None
        #         self.pointer_dw[actions[-1][0]][actions[-1][1]] = self.dwChoosed

        if actions[-1][1] > actions[0][1]:
            dw.doBody('right')
        elif actions[-1][1] < actions[0][1]:
            dw.doBody('left')
        self.animation = group
        thread = Thread(target=self.afterAnimation, kwargs={'obj': obj, 'name':dw.track['name']})
        self.isRun = False

        for i in self.layers:
            i.deleteLater()
        self.layers = []
        self.leftMenu.hide()

        group.start()
        resource.player['move_' + resource.basicData['money']['sound_move'][dw.track['name']]].play()
        thread.start()

    def afterAnimation(self, obj, name):
        while self.animation.state():
            pass
        resource.player['move_' + resource.basicData['money']['sound_move'][name]].stop()
        obj.afterAnimation()
        # post = AfterMoveEvent()
        # QCoreApplication.postEvent(obj, post)
        self.isRun = True

    def checkUsers(self):
        pass

    def collectMap(self):
        map = {}
        map['map'] = []
        # geos = iter(self.findChildren(Geo))
        geos_ = []
        for i in self.pointer_geo:
            for j in i:
                geos_.append(j)
        geos = iter(geos_)
        for i in range(self.mapSize[1]):
            com = []
            for j in range(self.mapSize[0]):
                tem = geos.__next__()
                com.append(tem.track['base64'])
            map['map'].append(com)

        dws = []
        for i in self.findChildren(DW):
            dws.append(i.makeTrack())
        map['dw'] = dws
        self.map.update(map)
        # return self.map.copy()

    def myUpdate(self):
        for j in self.findChildren(DW):
            if j:
                j.flush()
                j.myUpdate()

    def boutEnd(self):
        self.postCoverView.showTime(self.forces[self.nowForce]['heroName'])
        users = list(self.forces.keys())
        for i1, i in enumerate(users):
            if i == self.nowForce:
                self.nowForce = users[(i1 + 1) % len(users)]
                break
        else:
            print('bout error')
        self.militaryView.updateInfo()
        self.forces[self.nowForce]['dataInfo']['money'] += \
            self.forces[self.nowForce]['dataInfo']['income']

    def initToggle(self):
        pass




class infoView(QFrame):
    def __init__(self, parent):
        super(infoView, self).__init__(parent)
        self.initUI()

    def updateInfo(self):
        self.head.setPixmap(
            resource.find({'usage': 'dw', 'name': track['name'], 'flag': track['flag'], 'action': 'left'})[
                'pixmap'].scaled(80, 80))
        self.dsc.setText(track['name'] + '\n' + resource.basicData['money']['dsc'][track['name']])
        stealth = '是' if track['isStealth'] else '否'
        diving = '是' if track['isDiving'] else '否'
        self.infoLabel.setText(
            '规模:' + str(int(track['blood'])) + '    ' + '弹药:' + str(int(track['bullect'])) + '    ' + '油量:' + str(
                int(track['oil'])) + '\n' \
            + '占领:' + str(track['occupied']) + '    ' + '隐形:' + stealth + '    ' + '下潜:' + diving)
        for i in self.loadings:
            i.hide()
        for i1, i in enumerate(track['loadings']):
            self.loadings[i1].setIcon(
                QIcon(resource.find({'usage': 'dw', 'name': i['name'], 'flag': i['flag'], 'action': 'left'})['pixmap']))
            self.loadings[i1].setText(i['name'] + '(' + str(int(i['blood'])) + ')')
            self.loadings[i1].show()
        self.supplies.clear()
        for i, j in track['supplies'].items():
            self.supplies.addItem(QListWidgetItem(
                QIcon(resource.find({'usage': 'dw', 'name': i, 'flag': track['flag'], 'action': 'left'})['pixmap']),
                i + '\t' + str(j)))
        if not track['supplies']:
            self.planTitle.hide()
            self.supplies.hide()
        else:
            self.supplies.show()
            self.planTitle.show()
        if not track['loadings']:
            for i in self.loading:
                i.hide()
        else:
            for i in self.loading:
                i.show()

    def initUI(self):
        self.setMinimumSize(200, 200)
        self.setStyleSheet('border-radius:20px;background-color:white;')
        self.head = QLabel(self)
        # self.dsc = QTextEdit(self)
        self.dsc = QLabel(self)
        # self.dsc.setLineWrapMode(1)
        # self.dsc.setWordWrapMode(1)
        self.infoLabel = QLabel(self)
        self.loadings = [QPushButton(self), QPushButton(self)]
        self.loading = []
        self.supplies = QListWidget(self)
        layout1 = QBoxLayout(QBoxLayout.LeftToRight)
        layout1.addWidget(self.head)
        layout1.addWidget(self.dsc)
        layout2 = QBoxLayout(QBoxLayout.LeftToRight)
        tem_titil = QLabel('装载:')
        layout2.addWidget(tem_titil)
        layout2.addWidget(self.loadings[0])
        layout2.addWidget(self.loadings[1])
        self.loading = [tem_titil, self.loadings[0], self.loadings[1]]
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addLayout(layout1)
        layout.addWidget(self.infoLabel)
        layout.addLayout(layout2)
        self.planTitle = QLabel('计划补给:', self)
        layout.addWidget(self.planTitle)
        layout.addWidget(self.supplies)
        self.setLayout(layout)

class msgView(QLabel):
    def __init__(self, parent):
        super(msgView, self).__init__(parent)
        '''msg:from, to, ..'''
        '''tip, war, title'''
        self.data = []
        self.setFixedSize(self.parent().width()//3, self.parent().height()//3*2)
        self.setStyleSheet('border:none;')
        self.setFont(QFont('宋体', 15))
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignBottom)
        self.send({'from':'polar', 'to':'red', \
                   'info':'09876543211234567890发斯蒂芬发送到<h1>h1</h1>'})
        self.flags = ['red', 'blue', 'green', 'yellow']
        self.alliance = []

        self.clearer = QTimer(self)
        self.clearer.timeout.connect(self.clear_)
        self.clearer.start(1000)


    def makeText(self, ms):
        text = ms['from'] + '@' + ms['to'] + ':' + ms['info']
        text = list(text)
        length = []
        endText = ''
        count = 0
        tem_text = ''
        block = self.fontMetrics().width(' ')
        hasBlock = 0
        for i in text:
            width = self.fontMetrics().width(i)
            length.append(width)

        for i1, i in enumerate(text):
            if count + length[i1] > self.width() - 10 - hasBlock:
                endText += tem_text + '\n'
                if hasBlock == 0:
                    hasBlock = block * 4
                if hasBlock != 0:
                    endText += ' ' * 4
                tem_text = i
                count = 0
            else:
                tem_text += i
            count += length[i1]
        endText += tem_text + '\n'

        return endText, self.fontMetrics().lineSpacing()*(endText.count('\n')+1)

    def send(self, ms):
        myForce = self.parent().myForce
        if myForce != ms['from']:
            if ms['to'] == '盟友们' and myForce in self.parent().forces[ms['from']]['enemy']:
                return
            elif ms['to'] == '敌人们' and myForce not in self.parent().forces[ms['from']]['enemy']:
                return
            elif ms['to'] == '所有人':
                pass
            elif ms['to'] != myForce:
                return
        ms['time'] = time.time()
        self.data.append(ms)
        msg = self.makeText(ms)
        ms['height'] = msg[1]
        self.setText(self.text()+msg[0])

        a = self.fontMetrics().lineSpacing()*(self.text().count('\n')+1)
        if a > self.height():
            height = 0
            for i1, i in enumerate(reversed(self.data)):
                if height + i['height'] > self.height():
                    break
            cursor = len(self.data) - i1
            self.data = self.data[cursor:]
            endT = ''
            for i in self.data:
                endT += self.makeText(i)[0]
            self.setText(endT)

        if ms['info'].lower() == 'tm':
            if ms['from'] not in self.flags or ms['to'] not in self.flags:
                return
            for i in self.alliance:
                if i['from'] == ms['to']:
                    if i['to'] == ms['from']:
                        for j, k in self.parent().forces.items():
                            if j == ms['from']:
                                enemy = []
                                for p in k['enemy']:
                                    if p != ms['to']:
                                        enemy.append(p)
                                self.parent().forces[j]['enemy'] = enemy
                            elif j == ms['to']:
                                enemy = []
                                for p in k['enemy']:
                                    if p != ms['from']:
                                        enemy.append(p)
                                self.parent().forces[j]['enemy'] = enemy
                    break
        elif ms['info'].lower() == 'hm':
            if ms['from'] not in self.flags or ms['to'] not in self.flags:
                return
            if ms['from'] not in self.parent().forces[ms['to']]['enemy']:
                self.parent().forces[ms['to']]['enemy'].append(ms['from'])
            elif ms['to'] not in self.parent().forces[ms['from']]['enemy']:
                self.parent().forces[ms['from']]['enemy'].append(ms['to'])



    def clear_(self):
        inner_time = 10

        for i1, i in enumerate(self.data):
            if i['time'] + inner_time > time.time():
                self.data = self.data[i1:]
                break
        else:
            self.data = []
        endT = ''
        for i in self.data:
            endT += self.makeText(i)[0]
        self.setText(endT)

class inputView(QFrame):
    def __init__(self, parent:TMap_):
        super(inputView, self).__init__(parent)
        self.initUI()
        self.setFixedWidth(self.parent().width()//3)
        self.move(self.parent().width()//3, self.parent().height()//3*2+self.height())

    def initUI(self):
        self.setFont(QFont('宋体', 15))
        layout = QHBoxLayout()
        tem = QComboBox(self)
        users = ['所有人', '盟友们', '敌人们']
        for i, j in self.parent().forces.items():
            if i == self.parent().myForce:
                continue
            users.append(i)
        tem.addItems(users)
        layout.addWidget(tem)
        tem = QLineEdit(self)
        tem.setMaxLength(64)
        tem.setStyleSheet('background:none')
        tem.editingFinished.connect(self.send)
        layout.addWidget(tem)
        self.setLayout(layout)

    def show(self):
        l = self.findChild(QLineEdit)
        l.setEnabled(True)
        l.setText('')
        l.setFocus()
        super(inputView, self).show()

    def send(self):
        l = self.findChild(QLineEdit)
        c = self.findChild(QComboBox)
        if l.text() == '':
            return
        ms = {'from':self.parent().myForce, 'to':c.currentText(), 'info':l.text()}
        l.setText('')
        QCoreApplication.postEvent(self.parent().shopkeeper, InputMsgEvent(ms))

    def hide(self):
        l = self.findChild(QLineEdit)
        l.setEnabled(False)
        super(inputView, self).hide()


class postCoverView(QLabel):
    def __init__(self, parent):
        super(postCoverView, self).__init__(parent)
        self.begin = QRect(self.parent().width()//16*7, self.parent().height()//16*7, \
                           self.parent().width()//8, self.parent().height()//8)
        self.end = QRect(0, 0, self.parent().width(), self.parent().height())
        self.setScaledContents(True)
        self.animate = None

    def showTime(self, heroName):
        self.resize(self.begin.size())
        self.show()
        self.raise_()
        self.setWindowOpacity(1)
        self.setPixmap(resource.find({'usage':'hero', 'name':heroName, 'action':'post'})['pixmap'])
        self.animate = QSequentialAnimationGroup(self)
        tem_animate = QPropertyAnimation(self, b'geometry', self)
        tem_animate.setStartValue(self.begin)
        tem_animate.setEndValue(self.end)
        tem_animate.setDuration(1400)
        self.animate.addAnimation(tem_animate)
        tem_animate = QPropertyAnimation(self, b'windowOpacity', self)
        tem_animate.setStartValue(1)
        tem_animate.setEndValue(0.1)
        tem_animate.setDuration(800)
        self.animate.addAnimation(tem_animate)
        # self.animate.
        self.animate.start()
        self.parent().isRun = False
        Thread(target=self.afterMove).start()

    def afterMove(self):
        while self.animate.state():
            pass
        time.sleep(1.8)
        self.parent().isRun = True
        self.hide()


class headView(QFrame):
    def __init__(self, parent):
        super(headView, self).__init__(parent)
        self.initUI()
        self.move(self.parent().width()-self.width(), 0)

    def initUI(self):
        self.setFont(QFont('宋体', 15))
        layout1 = QVBoxLayout()
        self.money = QLabel('?', self)
        layout1.addWidget(self.money)
        self.exp = QProgressBar(self)
        layout1.addWidget(self.exp)
        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addLayout(layout1)
        self.head = QLabel(self)
        self.head.setFrameShape(QFrame.WinPanel)
        self.head.setFrameShadow(QFrame.Raised)
        self.head.setLineWidth(5)
        body = resource.mapScaleList[resource.mapScaleDoublePoint]['body']
        self.head.setFixedSize(body[0], body[1])
        self.head.setScaledContents(True)
        layout.addWidget(self.head)
        self.setLayout(layout)
        self.setFixedSize(body[0]*3, body[1])

    def swapUser(self, flag):
        force = self.parent().forces[flag]
        self.head.setStyleSheet('background-color:'+flag+';')
        self.head.setPixmap(resource.find({'usage':'hero', 'name':force['heroName'], 'action':'head'})['pixmap'])
        self.money.setText(str(force['dataInfo']['money']))
        self.exp.setValue(int(force['dataInfo']['energy']/int(resource.basicData['hero_f'][force['heroName']]['max_energy'])*100))

    def setMoney(self, v):
        if v > 9999999:
            self.money.setText('?')
        else:
            self.money.setText(str(v))

    def setEnergy(self, v):
        self.exp.setValue(int(v/int(resource.basicData['hero_f']['max_energy'])*100))


class mapRightMenu(QWidget):
    def __init__(self, parent):
        super(mapRightMenu, self).__init__(parent)
        self.force = self.parent().myForce
        self.initUI()

    def initUI(self):
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        key_1 = ['背景', '兵力', '记录', '回合结束', '退出']
        for i in key_1:
            tem = QPushButton(i, self)
            tem.clicked.connect(functools.partial(self.handle, i))
            layout.addWidget(tem)

        self.setLayout(layout)

    def handle(self, key_):
        if key_ == '背景':
            self.parent().victoryBG.show()
        elif key_ == '兵力':
            self.parent().militaryView.show()
        elif key_ == '记录':
            pass
        elif key_ == '回合结束':
            if self.parent().nowForce == self.parent().myForce:
                self.parent().boutEnd()
        elif key_ == '退出':
            self.parent().dwUpdater.stop()
            sys.exit(print('bye'))
        self.parent().rightMenu.hide()
        
    def show(self, pos):
        self.move(pos)
        super(mapRightMenu, self).show()
        self.raise_()

class mapLeftMenu(QWidget):
    def __init__(self, parent):
        super(mapLeftMenu, self).__init__(parent)
        self.reciver = None
        #['wait', 'attack', 'load', 'unload', 'stealth', 'occupy', 'lay mine', 'supply']
        self.actions = []
        self.primActions = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        for i in range(8):
            tem = QPushButton(str(i), self)
            tem.clicked.connect(functools.partial(self.sendInfo, i))
            layout.addWidget(tem)
        self.setLayout(layout)
        self.show()


    def swap(self, actions, obj):
        print(actions, 'new', self.primActions)
        btns = self.findChildren(QPushButton)
        for i in btns:
            i.hide()

        for i1, i in enumerate(actions):
            btns[i1].setText(i)
            btns[i1].show()

        self.primActions = self.actions.copy()
        self.actions = actions
        self.reciver = obj
        self.show()
        self.raise_()

    def sendInfo(self, arg):
        post = LeftMenuEvent(self.actions[arg])
        QCoreApplication.postEvent(self.reciver, post)

class buildMenu(QListWidget):
    def __init__(self, tmap, track):
        super(buildMenu, self).__init__()
        self.tmap = tmap
        self.doubleClicked.connect(self.sendInfo)
        self.track = {}
        self.setFixedSize(400, 400)
        # self.initUI(track)

    def initUI(self, track):
        self.track['mapId'] = track['mapId']
        self.track['flag'] = track['flag']
        build = []
        dd = []
        cna = resource.basicData['geo']['canbuild'][track['name']]
        for i in resource.findAll({'usage':'dw'}):
            if i['flag'] != track['flag'] or i['name'] in build:
                continue
            if resource.basicData['money']['classify'][i['name']] in cna or i['name'] in cna:
                build.append(i['name'])
                dd.append(i)
        self.clear()
        for i in dd:
            name = resource.basicData['money']['chineseName'][i['name']]+\
                                   '\t\t\t'+resource.basicData['money']['money'][i['name']]
            item = QListWidgetItem(QIcon(i['pixmap']), name)
            item.name = i['name']
            self.addItem(item)

    def sendInfo(self, index:QModelIndex=None):
        self.track['name'] = self.currentItem().name
        post = BuildDwEvent(self.track)
        QCoreApplication.postEvent(self.tmap.shopkeeper.waiter, post)
        self.hide()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        QCoreApplication.postEvent(self.tmap.shopkeeper.waiter, BuildDwEvent())
        self.hide()

class supplyMenu(QWidget):
    def __init__(self, tmap:TMap_, track):
        super(supplyMenu, self).__init__()
        self.track = {}
        self.tmap = tmap
        self.maxMoney = 0
        self.initUI(track)

    def initUI(self, track):
        self.track = track
        build = []
        dd = []
        cna = resource.basicData['money']['cansupply'][track['name']]

        self.maxMoney = int(cna.split('%')[0])
        userMoney = self.tmap.forces[track['flag']]['dataInfo']['money']
        for i in resource.findAll({'usage': 'dw'}):
            if i['flag'] != track['flag'] or i['name'] in build:
                continue
            if resource.basicData['money']['classify'][i['name']] in cna or i['name'] in cna:
                build.append(i['name'])
                dd.append(i)

        layout1 = QHBoxLayout()

        for i in range(2):
            layout11 = QVBoxLayout()
            if i == 0:
                begin = 0
                length = len(dd)/2
                if length > int(length):
                    length = int(length) + 1
                else:
                    length = int(length)
            else:
                length = len(dd)
                begin = len(dd)/2
                if begin > int(begin):
                    begin = int(begin) + 1
                else:
                    begin = int(begin)

            for j in dd[begin:length]:
                tem_layout = QHBoxLayout()
                tem = QPushButton(QIcon(j['pixmap']), \
                                   resource.basicData['money']['chineseName'][j['name']] +\
                                  '\t\t￥' + resource.basicData['money']['money'][j['name']], self)
                tem.setStyleSheet('border:none;')
                tem_layout.addWidget(tem)
                tem = QSpinBox(self)
                tem.setMaximum(userMoney)
                tem.setMinimum(0)
                tem.setValue(0)
                tem.setSingleStep(1000)
                tem.data = j['name']
                tem_layout.addWidget(tem)
                layout11.addLayout(tem_layout)
            layout1.addLayout(layout11)


        layout2 = QHBoxLayout()
        tem = QPushButton('reset', self)
        tem.clicked.connect(self.reset)
        layout2.addWidget(tem)
        tem = QPushButton('ok', self)
        tem.clicked.connect(self.save)
        layout2.addWidget(tem)

        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addWidget(QLabel('最大补给限制：'+str(self.maxMoney)+'\t(超过部分会作废)', self))
        layout.addLayout(layout2)

        self.setLayout(layout)

    def reset(self):
        for i in self.findChildren(QSpinBox):
            i.setValue(0)

    def save(self):
        supply = {}
        userMoney = self.tmap.forces[self.track['flag']]['dataInfo']['money']
        topMoney = userMoney if userMoney < self.maxMoney else self.maxMoney
        nowMoney = 0
        for i in self.findChildren(QSpinBox):
            if nowMoney + i.value() >= topMoney:
                supply[i.data] = topMoney - nowMoney
                break
            else:
                nowMoney += i.value()
                supply[i.data] = i.value()
        if nowMoney == 0:
            supply = {}
        post = SupplyEvent(supply)
        QCoreApplication.postEvent(self.tmap.shopkeeper.waiter, post)
        self.deleteLater(False)

    def deleteLater(self, send=True) -> None:
        if send:
            post = SupplyEvent({})
            QCoreApplication.postEvent(self.tmap.shopkeeper.waiter, post)
        super(supplyMenu, self).deleteLater()

class storiesView(QWidget):
    def __init__(self, tmap):
        super(storiesView, self).__init__()
        self.tmap = tmap
        self.initUI()

    def initUI(self):
        layout1 = QHBoxLayout()
        for i, j in self.tmap.forces.items():
            tem = QPushButton(j['heroName'], self)
            tem.setStyleSheet('background-color:'+i+';')
            tem.clicked.connect(functools.partial(self.swap, i))
            layout1.addWidget(tem)
        layout = QVBoxLayout()
        layout.addLayout(layout1)
        tem = QTextEdit(self)
        tem.setReadOnly(True)
        tem.setPlaceholderText('任务背景')
        layout.addWidget(tem)
        tem = QTextEdit(self)
        tem.setReadOnly(True)
        tem.setPlaceholderText('任务目标')
        layout.addWidget(tem)
        self.setLayout(layout)

    def swap(self, flag):
        td = self.findChildren(QTextEdit)
        stories = self.tmap.forces[flag]['dispos']['stories']
        if stories == '':
            for i in td:
                i.setText('')
        else:
            td[0].setText(resource.storage_stories[stories]['command_bg'])
            td[1].setText(resource.storage_stories[stories]['command'])

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.hide()

class recordView(QWidget):
    def __init__(self, parent):
        super(recordView, self).__init__(parent)

class militaryView(QWidget):
    def __init__(self, tmap:TMap_):
        super(militaryView, self).__init__()
        self.tmap = tmap
        self.initUI()

    def initUI(self):
        layout1 = QHBoxLayout()
        key_1 = ['势力', '金钱', '收入', '本回合支出', '损失', '造成的损失', '军事实力', '能量值', '敌人']
        key_2 = ['money', 'income', 'outcome', 'loss', 'destory', 'armyPrice', 'energy']
        for i in key_1:
            tem = QLabel(i, self)
            layout1.addWidget(tem)
        layout = QVBoxLayout()
        layout.addLayout(layout1)
        for i, j in self.tmap.forces.items():
            layout1 = QHBoxLayout()
            tem = QPushButton('    ', self)
            tem.setStyleSheet('background-color:'+i+';')
            layout1.addWidget(tem)
            for k in key_2:
                tem = QLabel(str(j['dataInfo'][k]), self)
                tem.flag = i
                tem.data = k
                layout1.addWidget(tem)
            tem = QComboBox(self)
            tem.addItems(j['enemy'])
            layout1.addWidget(tem)
            layout.addLayout(layout1)
        self.setFixedSize(700, 400)
        self.setLayout(layout)

    def updateInfo(self):
        for i, j in self.tmap.forces.items():
            self.tmap.forces[i]['dataInfo']['armyPrice'] = 0
            self.tmap.forces[i]['dataInfo']['income'] = 0

        for i in self.tmap.findChildren(DW):
            self.tmap.forces[i.track['flag']]['dataInfo']['armyPrice'] += \
                int(i.bloodValue / 10) * int(resource.basicData['money']['money'][i.track['name']])

        for i in self.tmap.findChildren(Geo):
            if i.track['usage'] == 'build':
                if i.track['flag'] != 'none':
                    self.tmap.forces[i.track['flag']]['dataInfo']['income'] += 1000

        for i in self.findChildren(QLabel)[9:]:
            i.setText(str(self.tmap.forces[i.flag]['dataInfo'][i.data]))
            
    def show(self):
        self.updateInfo()
        super(militaryView, self).show()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.hide()



class LeftMenuEvent(QEvent):
    idType = QEvent.registerEventType()
    def __init__(self, action):
        super(LeftMenuEvent, self).__init__(LeftMenuEvent.idType)
        self.action = action

class AfterMoveEvent(QEvent):
    idType = QEvent.registerEventType()
    def __init__(self):
        super(AfterMoveEvent, self).__init__(AfterMoveEvent.idType)

class UnloadDwEvent(QEvent):
    idType = QEvent.registerEventType()
    def __init__(self, loadings):
        super(UnloadDwEvent, self).__init__(UnloadDwEvent.idType)
        self.loadings = loadings

class BuildDwEvent(QEvent):
    idType = QEvent.registerEventType()
    def __init__(self, track=None):
        super(BuildDwEvent, self).__init__(BuildDwEvent.idType)
        self.track = track

class InputMsgEvent(QEvent):
    idType = QEvent.registerEventType()
    def __init__(self, ms):
        super(InputMsgEvent, self).__init__(InputMsgEvent.idType)
        self.ms = ms

class SupplyEvent(QEvent):
    idType = QEvent.registerEventType()
    def __init__(self, supply):
        super(SupplyEvent, self).__init__(SupplyEvent.idType)
        self.supply = supply


class MinBackground(QFrame):
    def __init__(self, parent, mapName):
        super(MinBackground, self).__init__(parent)
        self.initUI(mapName)

    def initUI(self, mapName):
        self.label = QLabel(self)
        pm = QPixmap('maps/' + mapName + '/min_bg.gif')
        self.label.resize(pm.size())
        self.label.setPixmap(pm)
        self.label.setScaledContents(True)
        self.resize(pm.size())
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(5)
        self.show()


class MapBorder(QFrame):
    direction_right = 1
    direction_bottom = 2
    direction_left = 3
    direction_top = 4
    direction_rightTop = 5
    direction_rightBottom = 6
    direction_leftTop = 7
    direction_leftBottom = 8

    def __init__(self, parent, direction):
        super(MapBorder, self).__init__(parent)
        tem_size = resource.mapScaleList[resource.mapScaleDoublePoint]['body']
        doubleSize = QSize(tem_size[0], tem_size[1])
        # doubleSize = QSize(100, 100)
        self.direction = direction
        if direction == MapBorder.direction_right or \
                direction == MapBorder.direction_left:
            self.resize(doubleSize.width(), parent.height())
            if direction == MapBorder.direction_left:
                self.move(0, 0)
            else:
                self.move(self.parent().width() - doubleSize.width(), 0)
        elif direction == MapBorder.direction_top or \
                direction == MapBorder.direction_bottom:
            self.resize(parent.width(), doubleSize.height())
            if direction == MapBorder.direction_top:
                self.move(0, 0)
            else:
                self.move(0, self.parent().height() - doubleSize.height())
        else:
            self.resize(doubleSize)
            if direction == MapBorder.direction_leftBottom:
                self.move(0, self.parent().height() - doubleSize.height())
            elif direction == MapBorder.direction_leftTop:
                self.move(0, 0)
            elif direction == MapBorder.direction_rightTop:
                self.move(self.parent().width() - doubleSize.width(), 0)
            elif direction == MapBorder.direction_rightBottom:
                self.move(self.parent().width() - doubleSize.width(), \
                          self.parent().height() - doubleSize.height())

        self.setMouseTracking(True)
        self.show()
        self.raise_()

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        post = MapMoveEvent(self.direction, True)
        QCoreApplication.postEvent(self.parent(), post)

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        post = MapMoveEvent(self.direction, False)
        QCoreApplication.postEvent(self.parent(), post)
class MapMoveEvent(QEvent):
    idType = QEvent.registerEventType()

    def __init__(self, direction, isIn):
        super(MapMoveEvent, self).__init__(MapMoveEvent.idType)
        self.direction = direction
        self.isIn = isIn


'''
tmap: 
    show/hide layers, buyThing, showView, showInfo
    dw Move, dw Fight/loadings, 
    
    interupt connection
    ------------------------------------
    右键
    -------------------------------
    build, dw
'''

'''玩家与地图之间的信息传递者  信息通行'''


class ShopKeeper(QObject):
    onlyOne = None
    def __new__(cls, *args, **kwargs):
        if ShopKeeper.onlyOne == None:
            ShopKeeper.onlyOne = super(ShopKeeper, cls).__new__(cls, *args, **kwargs)
        return ShopKeeper.onlyOne

    def __init__(self, tmap: TMap_):
        super(ShopKeeper, self).__init__()
        self.legalEvent = []
        self.tmap = tmap
        self.waiter = None

    def handleEvent(self, a0):
        if not self.waiter:
            if a0.type() == QEvent.MouseButtonPress:
                if a0.button() == 1:
                    self.lockBaby(a0)
            # elif a0.type() == QEvent.MouseButtonRelease:
            #     if a0.button() == 2:
            #         if self.tmap.canRightMenuShow:
            #             self.tmap.rightMenu.show(a0.pos())
            #         self.tmap.canRightMenuShow = True
            return
        elif a0.type() == QEvent.MouseButtonRelease:
            if a0.button() == 2:
                self.waiter.actionBack()
                return


        if a0.type() not in self.legalEvent:
            return
        if a0.type() == QEvent.MouseButtonPress:
            self.waiter.mousePressEvent(a0)
        elif a0.type() == QEvent.Wheel:
            self.waiter.wheelEvent(a0)

    def lockBaby(self, a0, direct=False):
        def chooseBaby(track):
            if 'usage' in track:
                if resource.basicData['geo']['canbuild'][track['name']] != '0':
                    self.waiter = Building(self, self.tmap, track)
            elif track['name'] == 'footmen':
                self.waiter = DwFootmen(self, self.tmap, track)
            elif track['name'] == 'gunnery':
                self.waiter = DwFootmen(self, self.tmap, track)
            elif track['name'] == 'howitzer':
                self.waiter = DwHowitzer(self, self.tmap, track)
            elif track['name'] == 'B2':
                self.waiter = DwB2(self, self.tmap, track)
            elif track['name'] == 'conveyor':
                self.waiter = DwConveyor(self, self.tmap, track)
            elif track['name'] in ['transport', 'transportship']:
                self.waiter = DwTransport(self, self.tmap, track)

        if direct:
            chooseBaby(a0)
            return
        for i1, i in enumerate(self.tmap.pointer_geo):
            for j1, j in enumerate(i):
                if self.tmap.pointer_geo[i1][j1].contains(a0.pos()):
                    if self.tmap.pointer_dw[i1][j1]:
                        if not self.tmap.pointer_dw[i1][j1].moved:
                            chooseBaby(self.tmap.pointer_dw[i1][j1].makeTrack())
                    elif self.tmap.pointer_geo[i1][j1].track['usage'] == 'build':
                        track = self.tmap.pointer_geo[i1][j1].track.copy()
                        track['mapId'] = self.tmap.pointer_geo[i1][j1].mapId
                        chooseBaby(track)
                    return

    def unLockBaby(self):
        print('unlock')
        if self.waiter:
            self.waiter = None
            self.legalEvent = []

    def parent(self):
        return self.parent

    def sendToServer(self, command):
        print(command)

    def clientHandle(self):
        pass

    def event(self, a0: 'QEvent') -> bool:
        if a0.type() == ShopMsgEvent.idType:
            if a0.type_ == None:
                self.unLockBaby()
            elif a0.type_ == ShopMsgEvent.relock:
                track = self.waiter.dw.makeTrack()
                self.unLockBaby()
                self.lockBaby(track, True)

        elif a0.type() == InputMsgEvent.idType:
            self.tmap.msgView.send(a0.ms)

            command = a0.ms
            command['type'] = DwFootmen.input
            self.sendToServer(command)
            
        return super(ShopKeeper, self).event(a0)



class ShopMsgEvent(QEvent):
    idType = QEvent.registerEventType()
    relock = 1
    def __init__(self, type_=None):
        super(ShopMsgEvent, self).__init__(ShopMsgEvent.idType)
        self.type_ = None

class ShopWaiter(QObject):
    def __init__(self, shopkeeper, tmap:TMap_, track):
        super(ShopWaiter, self).__init__()
        self.shopkeeper = shopkeeper
        self.tmap = tmap
        self.track = track
        self.moveArea = None
        self.roadsToChoose = {'point': 0, 'roads': []}
        self.targetsToChoose = []
        self.movedShow = []
        self.unLoadArea = {}

    def mousePressEvent(self, a0: QtGui.QMouseEvent):
        pass

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        pass

    def wheelEvent(self, a0: QtGui.QWheelEvent):
        pass

    def setParent(self, parent):
        self.parent = parent

    def parent(self):
        return self.parent


    def countCostArea(self, dw: DW):
        '''-1:error, -2:不可停留， -3：运输车'''
        self.tmap.collectMap()
        cost = resource.basicData['move'][dw.track['name']]['move_distance']
        oil = float(cost) if float(cost) <= dw.oil else dw.oil
        if oil <= 0:
            return
        tem_map = []

        for i in self.tmap.map['map']:
            tem_map.append(i[:])
        for i, i1 in enumerate(tem_map):
            for j, j1 in enumerate(tem_map[i]):
                if self.tmap.pointer_dw[i][j]:
                    if self.tmap.pointer_dw[i][j].track['flag'] in \
                            self.tmap.forces[dw.track['flag']]['enemy']:
                        tem_map[i][j] = 99999
                        continue
                if self.tmap.pointer_geo[i][j].track['usage'] == 'border':
                    tem_map[i][j] = 99999
                else:
                    geo_name = resource.findByHafuman(int(j1))['name']
                    tem_map[i][j] = int(resource.basicData['move'][dw.track['name']][geo_name])

        # for i in tem_map:
        #     for j in i:
        #         print(j, ' ', end='')
        #     print()
        return tem_map

    def countCostArea_(self, track):
        '''-1:error, -2:不可停留， -3：运输车'''
        self.tmap.collectMap()
        cost = resource.basicData['move'][track['name']]['move_distance']
        oil = float(cost) if float(cost) <= track['oil'] else track['oil']
        if oil <= 0:
            return
        tem_map = []

        for i in self.tmap.map['map']:
            tem_map.append(i[:])
        for i, i1 in enumerate(tem_map):
            for j, j1 in enumerate(tem_map[i]):
                if self.tmap.pointer_dw[i][j]:
                    if self.tmap.pointer_dw[i][j].track['flag'] in \
                            self.tmap.forces[track['flag']]['enemy']:
                        tem_map[i][j] = 99999
                        continue
                if self.tmap.pointer_geo[i][j].track['usage'] == 'border':
                    tem_map[i][j] = 99999
                else:
                    geo_name = resource.findByHafuman(int(j1))['name']
                    tem_map[i][j] = int(resource.basicData['move'][track['name']][geo_name])

        return tem_map

    def showAttackArea(self):
        pass

    def showMoveArea(self, dw: DW, costMap=None):
        cost = resource.basicData['move'][dw.track['name']]['move_distance']
        oil = float(cost) if float(cost) <= dw.oil else dw.oil

        tem_map = costMap if costMap else self.countCostArea(dw)
        rows = len(tem_map)
        cols = len(tem_map[0])
        tem_area = [[-1 for i in range(cols)] for j in range(rows)]
        directions = [(1, 0), (-1, 0), (0, -1), (0, 1)]

        def area(beginP, oil):
            tem_area[beginP[0]][beginP[1]] = oil
            for i in directions:
                x, y = beginP[0] + i[0], beginP[1] + i[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
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
        # self.moveArea = tem_area
        return tem_area

    def showMoveArea_(self, track, costMap=None):
        cost = resource.basicData['move'][track['name']]['move_distance']
        oil = float(cost) if float(cost) <= track['oil'] else track['oil']

        tem_map = costMap if costMap else self.countCostArea_(track)
        rows = len(tem_map)
        cols = len(tem_map[0])
        tem_area = [[-1 for i in range(cols)] for j in range(rows)]
        directions = [(1, 0), (-1, 0), (0, -1), (0, 1)]

        def area(beginP, oil):
            tem_area[beginP[0]][beginP[1]] = oil
            for i in directions:
                x, y = beginP[0] + i[0], beginP[1] + i[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
                    continue
                if tem_area[x][y] == -1 and oil - tem_map[x][y] >= 0:
                    area((x, y), oil - tem_map[x][y])
                elif tem_area[x][y] != -1 and oil - tem_map[x][y] > tem_area[x][y]:
                    area((x, y), oil - tem_map[x][y])

        area(track['mapId'], oil)

        return tem_area


    def countRoad(self, dw: DW, last, costMap=None):
        costMap = costMap if costMap else self.countCostArea(dw)
        cost = resource.basicData['move'][dw.track['name']]['move_distance']
        oil = float(cost) if float(cost) <= dw.oil else dw.oil
        tem_map = costMap

        cols = len(tem_map[0])
        rows = len(tem_map)
        directions = [(1, 0), (-1, 0), (0, -1), (0, 1)]
        end = []

        def road(beginP, endP, length, hasgo=[]):
            hasgo_ = hasgo[:]
            # length_ = length - tem_map[beginP[0]][beginP[1]]
            hasgo_.append((beginP[0], beginP[1]))
            if length < 0:
                return
            if beginP[0] == endP[0] and beginP[1] == endP[1]:
                end.append(hasgo_[:])
                return
            for i in directions:
                x, y = beginP[0] + i[0], beginP[1] + i[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
                    continue
                if (x, y) not in hasgo:
                    length_ = length - tem_map[x][y]
                    road((x, y), endP, length_, hasgo_)

        road(dw.mapId, last, oil)
        return sorted(end, key=lambda arg: len(arg))
        # self.roadsToChoose['roads'] = sorted(end, key=lambda arg: len(arg))
        # print(self.roadsToChoose)
        # return

    def countRoad_(self, track, last, costMap=None):
        costMap = costMap if costMap else self.countCostArea_(track)
        cost = resource.basicData['move'][track['name']]['move_distance']
        oil = float(cost) if float(cost) <= track['oil'] else track['oil']
        tem_map = costMap

        cols = len(tem_map[0])
        rows = len(tem_map)
        directions = [(1, 0), (-1, 0), (0, -1), (0, 1)]
        end = []

        def road(beginP, endP, length, hasgo=[]):
            hasgo_ = hasgo[:]
            hasgo_.append((beginP[0], beginP[1]))
            if length < 0:
                return
            if beginP[0] == endP[0] and beginP[1] == endP[1]:
                end.append(hasgo_[:])
                return
            for i in directions:
                x, y = beginP[0] + i[0], beginP[1] + i[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
                    continue
                if (x, y) not in hasgo:
                    length_ = length - tem_map[x][y]
                    road((x, y), endP, length_, hasgo_)

        road(track['mapId'], last, oil)
        return sorted(end, key=lambda arg: len(arg))

    def countRoadNd(self, dw, road):
        directions = [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        cols = len(self.tmap.map['map'][0])
        rows = len(self.tmap.map['map'])
        self.movedShow = []
        for i1, i in enumerate(road):
            tem_dw = self.tmap.pointer_dw[i[0]][i[1]]
            if tem_dw:
                if tem_dw.track['flag'] in self.tmap.forces[dw.track['flag']]['enemy'] and \
                        i1 != len(road) - 1:
                    road = road[0:i1]
                    #self.dwChoosedStatus = 'encounter'
                    break
            for j in directions:
                x, y = i[0] + j[0], i[1] + j[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
                    continue
                tem_dw = self.tmap.pointer_dw[x][y]
                if tem_dw:
                    if tem_dw.track['flag'] in self.tmap.forces[dw.track['flag']]['enemy'] and \
                            tem_dw.isHidden() and tem_dw not in self.movedShow:
                        self.movedShow.append(tem_dw)
        # print(road)
        return road

    def countRoadNd_(self, track, road):
        directions = [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        cols = len(self.tmap.map['map'][0])
        rows = len(self.tmap.map['map'])
        movedShow = []
        for i1, i in enumerate(road):
            tem_dw = self.tmap.pointer_dw[i[0]][i[1]]
            if tem_dw:
                if tem_dw.track['flag'] in self.tmap.forces[track['flag']]['enemy'] and \
                        i1 != len(road) - 1:
                    road = road[0:i1]
                    break
            for j in directions:
                x, y = i[0] + j[0], i[1] + j[1]
                if x < 0 or x >= rows or y < 0 or y >= cols:
                    continue
                tem_dw = self.tmap.pointer_dw[x][y]
                if tem_dw:
                    if tem_dw.track['flag'] in self.tmap.forces[track['flag']]['enemy'] and \
                            tem_dw.isHidden() and tem_dw not in movedShow:
                        movedShow.append(tem_dw)
        return road, movedShow

    def countUnloadArea(self, dw:DW, endP):
        around = []
        direction = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for i in direction:
            x, y = endP[0] + i[0], endP[1] + i[1]
            if x < 0 or y < 0 or x >= self.tmap.mapSize[0] or y >= self.tmap.mapSize[1]:
                continue
            around.append((x, y))
        self.unLoadArea = {}
        for i1, i in enumerate(dw.loadings):
            self.unLoadArea[str(i1)] = []
            for j in around:
                name = self.tmap.pointer_geo[j[0]][j[1]].track['name']
                if name == 'border':
                    continue
                if int(resource.basicData['move'][i['name']][name]) >= 99:
                    continue
                self.unLoadArea[str(i1)].append(j)
            # if resource.basicData['money']['canunloadbyfly'][i['name']] == '1':
            #     tem_area = self.showMoveArea_(i)
            #     for i in tem_area:
            #         if i != self.dw.mapId:
            #             self.unLoadArea[str(i1)].append(i)
            # else:
            #     for j in around:
            #         if int(resource.basicData['move'][i['name']][self.tmap.pointer_geo[j[0]][j[1]].track['name']]) >= 99:
            #             continue
            #     self.unLoadArea[str(i1)].append(j)


    def countSupply(self, dw:DW):
        dwName = None
        geoName = None
        if dw.track['name'] == 'transport':
            dwName = 'transport'
            geoName = 'factory'
        elif dw.track['name'] == 'transportship':
            dwName = 'transportship'
            geoName = 'shipyard'

        e1 = []
        e2 = []
        for i in self.tmap.findChildren(Geo):
            if i.track['usage'] == 'build':
                if i.track['flag'] == self.tmap.myForce and \
                        i.track['name'] == geoName:
                    e1.append(i)
        for i in self.tmap.findChildren(DW):
            if i.track['flag'] == self.tmap.myForce and \
                    i.track['name'] == dwName and \
                    not i.moved:
                e2.append(i)
        if not e2 or not e1:
            print('here', e1, e2)
            return []
        tem_data_1 = {}
        for i1, i in enumerate(e2):
            costMap = self.countCostArea(i)
            tem_data_1[str(i1)] = {'dws': [], 'geos': []}
            for j1, j in enumerate(e2):
                if j1 == i1:
                    continue
                roads = self.countRoad(i, j.mapId, costMap)
                if roads:
                    cost = resource.basicData['move'][dw.track['name']]['move_distance']
                    oil = float(cost) if float(cost) <= dw.oil else dw.oil
                    for k in roads[0][1:]:
                        oil -= float(resource.basicData['move'][dw.track['name']][
                                         self.tmap.pointer_geo[k[0]][k[1]].track['name']])
                    if oil < 0:
                        continue
                else:
                    continue
                tem_data_1[str(i1)]['dws'].append((str(j1), len(roads[0])))
            for j1, j in enumerate(e1):
                roads = self.countRoad(i, j.mapId, costMap)
                if roads:
                    cost = resource.basicData['move'][dw.track['name']]['move_distance']
                    oil = float(cost) if float(cost) <= dw.oil else dw.oil
                    for k in roads[0][1:]:
                        oil -= float(resource.basicData['move'][dw.track['name']][
                                         self.tmap.pointer_geo[k[0]][k[1]].track['name']])
                    if oil < 0:
                        continue
                else:
                    continue
                tem_data_1[str(i1)]['geos'].append((str(j1), len(roads[0])))
            # tem_data_1[str(i1)]['dws'] = sorted(tem_data_1[str(i1)]['dws'], key=lambda arg:arg[1])
            tem_data_1[str(i1)]['geos'] = sorted(tem_data_1[str(i1)]['geos'], key=lambda arg: arg[1])
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
            if i == dw:
                supplyRoad(str(i1))
                break
        if not end:
            return []
        tend = []
        for i in end:
            for j in i[:-1]:
                tend.append(e2[int(j)].mapId)
            tend.append(e1[int(i[-1])].mapId)
        print('tend', tend)
        return tend


    def findTarget(self, dw: DW, endP, moved=False):
        ###移动攻击 判断
        targetsToChoose = []
        if resource.basicData['gf'][dw.track['name']]['attackAftermove'] == '0' and moved:
            return targetsToChoose
        max = resource.basicData['gf'][dw.track['name']]['gf_maxdistance']
        # if max == 0 or dw.bullect == 0 or (self.tmap.pointer_dw[endP[0]][endP[1]] and self.dw.mapId != endP ):
        if max == 0 or dw.bullect == 0:
            return targetsToChoose
        min = resource.basicData['gf'][dw.track['name']]['gf_mindistance']
        x1, y1 = endP
        rows = len(self.tmap.map['map'])
        cols = len(self.tmap.map['map'][0])
        directions = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        for k in range(int(min), int(max) + 1):
            for j in range(k + 1):
                for i in directions:
                    x, y = x1 + j * i[0], y1 + (k - j) * i[1]
                    if x < 0 or x >= rows or y < 0 or y >= cols or ((x, y) in targetsToChoose):
                        continue
                    if self.tmap.pointer_dw[x][y]:
                        if self.tmap.pointer_dw[x][y].track['flag'] in \
                                self.tmap.forces[dw.track['flag']]['enemy'] and not \
                                self.tmap.pointer_dw[x][y].isHidden():
                            if float(resource.basicData['gf'][dw.track['name']][
                                         self.tmap.pointer_dw[x][y].track['name']]) > 0:
                                targetsToChoose.append((x, y))

        return targetsToChoose

    def handleLeftMenu(self, arg):
        pass

    def judgement(self, dw: DW, endP):
        if not endP or not self.tmap.pointer_dw[endP[0]][endP[1]]:
            return
        resource.player['bao'].play()
        beginP = dw.mapId
        enemy = self.tmap.pointer_dw[endP[0]][endP[1]]
        ###此处忽略英雄加成
        at1 = float(resource.basicData['gf'][dw.track['name']][enemy.track['name']]) * \
              (float(resource.basicData['gfGeo_g'][dw.track['name']][
                         self.tmap.pointer_geo[beginP[0]][beginP[1]].track['name']]) / 100 + 1) * \
              ((100 - float(resource.basicData['gfGeo_f'][enemy.track['name']][
                                self.tmap.pointer_geo[endP[0]][endP[1]].track['name']])) / 100)
        at2 = float(resource.basicData['gf'][enemy.track['name']][dw.track['name']]) * \
              (float(resource.basicData['gfGeo_g'][enemy.track['name']][
                         self.tmap.pointer_geo[endP[0]][endP[1]].track['name']]) / 100 + 1) * \
              ((100 - float(resource.basicData['gfGeo_f'][dw.track['name']][
                                self.tmap.pointer_geo[beginP[0]][beginP[1]].track['name']])) / 100)
        if float(resource.basicData['gf'][enemy.track['name']]['gf_mindistance']) > 1:
            at2 = 0
        elif enemy.bullect == 0:
            at2 = 0
        blood2 = enemy.bloodValue - at1 * dw.bloodValue / 10
        blood2 = 0 if round(blood2) <= 0 else round(blood2, 1)
        blood1 = dw.bloodValue - at2 * blood2 / 10
        blood1 = 0 if round(blood1) <= 0 else round(blood1, 1)
        # dw1 = {}
        # dw2 = {}
        if blood1 == 0 and blood2 == 0:
            dw.deleteLater()
            enemy.deleteLater()
            self.tmap.pointer_dw[beginP[0]][beginP[1]] = None
            self.tmap.pointer_dw[endP[0]][endP[1]] = None
            # dw1['isAlive'] = False
            # dw2['isAlive'] = False
            # dw1['mapId'] = dw.mapId
            # dw2['mapId'] = enemy.mapId
            print('all has beng!!!!!!!')
        elif blood1 == 0:
            dw.deleteLater()
            self.tmap.pointer_dw[beginP[0]][beginP[1]] = None
            print('dw has beng!!!!')
            enemy.doBlood(blood2)
            # dw1['isAlive'] = False
            # dw2 = enemy.makeTrack()
            # dw1['mapId'] = dw.mapId
        elif blood2 == 0:
            enemy.deleteLater()
            self.tmap.pointer_dw[endP[0]][endP[1]] = None
            print('enemy has beng!!!!')
            dw.doBlood(blood1)
            dw.doBody('leftG' if dw.track['flag'] != self.tmap.myForce else 'rigthG')
            dw.moved = True
            # dw1 = dw.makeTrack()
            # dw2['isAlive'] = False
            # dw2['mapId'] = enemy.mapId
        else:
            print('nothing has beng!!!')
            dw.doBlood(blood1)
            enemy.doBlood(blood2)
            dw.doBody('leftG' if dw.track['flag'] != self.tmap.myForce else 'rigthG')
            dw.moved = True
            # dw1 = dw.makeTrack()
            # dw2 = enemy.makeTrack()
        # command['dw1'] = dw1
        # command['dw2'] = dw2


    def actionBack(self):
        pass





'''选择单位->展示区域选择目标点->(待命， 攻击，)'''
'''普通近程攻击单位'''




class DwFootmen(ShopWaiter):
    locked = 1
    destination = 2
    occupy = 5
    waiting = 6
    encounter = 7
    attackShow = 8
    attacked = 9
    load = 10
    input = 18
    def __init__(self, shopkeeper, tmap, track):
        super(DwFootmen, self).__init__(shopkeeper, tmap, track)
        self.dw = self.tmap.pointer_dw[self.track['mapId'][0]][self.track['mapId'][1]]
        self.moveArea = self.showMoveArea(self.dw)
        self.moveLayers = []
        for i1, i in enumerate(self.moveArea):
            for j1, j in enumerate(i):
                if j >= 0:
                    self.moveLayers.append((i1, j1))
        self.tmap.showLayers(self.moveLayers)
        self.actionStatus = DwFootmen.locked
        self.shopkeeper.legalEvent = [QEvent.MouseButtonPress]
        self.enemy = None

    '''待命, 攻击， 搭载， 占领, 占领打断'''
    def mousePressEvent(self, a0: QtGui.QMouseEvent, actions=None):
        if self.actionStatus == DwFootmen.locked:
            for i in self.tmap.layers:
                if i.geometry().contains(a0.pos()):
                    actions_ = []
                    canoccupy = False
                    if actions:
                        for k in actions:
                            actions_.append(k)
                    if tuple(i.mapId) == tuple(self.dw.mapId):
                        # actions_.append('待命')
                        canoccupy = True
                    else:
                        otherdw = self.tmap.pointer_dw[i.mapId[0]][i.mapId[1]]
                        if otherdw:
                            canloding = resource.basicData['money']['canloading'][otherdw.track['name']]
                            if (int(canloding[0]) > 0 and len(otherdw.loadings) < int(canloding[0])) \
                                    and \
                                    (
                                            resource.basicData['money']['classify'][self.track['name']] in canloding or \
                                            self.track['name'] in canloding
                                    ):
                                actions_.append('搭载')
                            else:
                                return
                        else:
                            canoccupy = True
                        self.dw.occupied = 0

                    if canoccupy:
                        actions_.append('待命')
                        build = self.tmap.pointer_geo[i.mapId[0]][i.mapId[1]]
                        if build.track['usage'] == 'build' and \
                                build.track['flag'] in self.tmap.forces[self.track['flag']]['enemy'] and \
                                resource.basicData['money']['canoccupy'][self.track['name']] != '0':
                            actions_.append('占领')


                    # dw = self.tmap.pointer_dw[self.dw.mapId[0]][self.dw.mapId[1]]
                    self.roadsToChoose['roads'] = self.countRoad(self.dw, i.mapId)
                    self.roadsToChoose['point'] = 0
                    self.tmap.showLayers(self.roadsToChoose['roads'][0])

                    self.targetsToChoose = self.findTarget(self.dw, i.mapId, i.mapId == self.track['mapId'])
                    if self.targetsToChoose:
                        actions_.append('攻击')


                    self.actionStatus = DwFootmen.destination

                    self.tmap.showleftMenu(actions_, a0.pos())

                    self.shopkeeper.legalEvent.append(QEvent.Wheel)
                    break
            else:
                post = ShopMsgEvent()
                QCoreApplication.postEvent(self.shopkeeper, post)
                self.tmap.clearLayers()

        elif self.actionStatus == DwFootmen.attackShow:
            for i in self.tmap.layers:
                if i.geometry().contains(a0.pos()):
                    self.tmap.clearLayers()
                    oldRoad = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                    newRoad = self.countRoadNd(self.dw, oldRoad)
                    if len(oldRoad) != len(newRoad):
                        self.actionStatus = DwFootmen.encounter
                    else:
                        self.actionStatus = DwFootmen.attacked
                    self.enemy = i.mapId
                    self.tmap.animeMove(newRoad, self)

                    command = {'type': self.actionStatus, 'road':newRoad, 'moveShow':self.movedShow, 'enemy':self.enemy}
                    self.shopkeeper.sendToServer(command)
                    break

    def wheelEvent(self, a0: QtGui.QWheelEvent):
        if a0.angleDelta().y() > 0:
            if self.roadsToChoose['point'] == len(self.roadsToChoose['roads']) - 1:
                return
            self.roadsToChoose['point'] += 1
            #self.tmap.showLayers(self.roadsToChoose['roads'][self.roadsToChoose['point']])
        else:
            if self.roadsToChoose['point'] == 0:
                return
            self.roadsToChoose['point'] -= 1

        self.tmap.showLayers(self.roadsToChoose['roads'][self.roadsToChoose['point']])

    def handleLeftMenu(self, arg):
        self.shopkeeper.legalEvent = [QEvent.KeyPress]
        if arg in ['待命', '搭载']:
            oldRoad = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            newRoad = self.countRoadNd(self.dw, oldRoad)
            if len(oldRoad) != len(newRoad):
                self.actionStatus = DwFootmen.encounter
            else:
                if arg == '待命':
                    self.actionStatus = DwFootmen.waiting
                elif arg == '搭载':
                    self.actionStatus = DwFootmen.load
            self.tmap.animeMove(newRoad, self)

            command = {'type': self.actionStatus, 'road':newRoad, 'moveShow':self.movedShow}
            self.shopkeeper.sendToServer(command)
        elif arg == '攻击':
            self.tmap.showLayers(self.targetsToChoose, 'red')
            self.actionStatus = DwFootmen.attackShow
            self.tmap.leftMenu.hide()
            self.shopkeeper.legalEvent = [QEvent.MouseButtonPress]
        elif arg == '占领':
            oldRoad = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            newRoad = self.countRoadNd(self.dw, oldRoad)
            if len(oldRoad) != len(newRoad):
                self.actionStatus = DwFootmen.encounter
            else:
                self.actionStatus = DwFootmen.occupy
            self.tmap.animeMove(newRoad, self)

            command = {'type': self.actionStatus, 'road':newRoad, 'moveShow':self.movedShow}
            self.shopkeeper.sendToServer(command)

    def afterAnimation(self):
        if self.actionStatus == DwFootmen.encounter or self.actionStatus == DwFootmen.waiting:
            if self.track['flag'] == self.tmap.myForce:
                self.dw.doBody('rightG')
            else:
                self.dw.doBody('leftG')
            action = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            self.tmap.pointer_dw[action[0][0]][action[0][1]] = None
            self.tmap.pointer_dw[action[-1][0]][action[-1][1]] = self.dw
            self.dw.mapId = action[-1]
            post = ShopMsgEvent()
            QCoreApplication.postEvent(self.shopkeeper, post)

        elif self.actionStatus == DwFootmen.attacked:
            action = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            self.tmap.pointer_dw[action[0][0]][action[0][1]] = None
            self.tmap.pointer_dw[action[-1][0]][action[-1][1]] = self.dw
            self.dw.mapId = action[-1]
            self.judgement(self.dw, self.enemy)
            # self.shopkeeper.unLockBaby()
            post = ShopMsgEvent()
            QCoreApplication.postEvent(self.shopkeeper, post)

        elif self.actionStatus == DwFootmen.load:
            if self.track['flag'] == self.tmap.myForce:
                self.dw.doBody('rightG')
            else:
                self.dw.doBody('leftG')
            action = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            self.tmap.pointer_dw[action[0][0]][action[0][1]] = None
            self.tmap.pointer_dw[action[-1][0]][action[-1][1]].loadings.append(self.dw.makeTrack())
            self.dw.deleteLater()
            self.roadsToChoose = {'point':0, 'roads':[]}

            post = ShopMsgEvent()
            QCoreApplication.postEvent(self.shopkeeper, post)

        elif self.actionStatus == DwFootmen.occupy:
            if self.track['flag'] == self.tmap.myForce:
                self.dw.doBody('rightG')
            else:
                self.dw.doBody('leftG')
            action = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            self.tmap.pointer_dw[action[0][0]][action[0][1]] = None
            self.tmap.pointer_dw[action[-1][0]][action[-1][1]] = self.dw
            self.dw.mapId = action[-1]
            self.dw.occupied += int(self.dw.bloodValue)
            if self.dw.occupied >= 20:
                self.dw.occupied = 0
                self.tmap.pointer_geo[action[-1][0]][action[-1][1]].change(self.track['flag'])
            post = ShopMsgEvent()
            QCoreApplication.postEvent(self.shopkeeper, post)

        else:
            print('error:herer23464895gd', self.actionStatus)

    def actionBack(self):
        if self.actionStatus == DwFootmen.locked:
            post = ShopMsgEvent()
            QCoreApplication.postEvent(self.shopkeeper, post)
            self.tmap.clearLayers()
        elif self.actionStatus == DwFootmen.destination:
            self.tmap.leftMenu.hide()
            self.tmap.showLayers(self.moveLayers)
            self.actionStatus = DwFootmen.locked
        elif self.actionStatus == DwFootmen.attackShow:
            self.tmap.showLayers(self.roadsToChoose['roads'][0])
            self.tmap.leftMenu.show()
            self.actionStatus = DwFootmen.destination

    def event(self, a0: 'QEvent') -> bool:
        if a0.type() == LeftMenuEvent.idType:
            self.handleLeftMenu(a0.action)
        return super(DwFootmen, self).event(a0)


class DwGunnery(DwFootmen):
    def __init__(self, shopkeeper, tmap, track):
        super(DwGunnery, self).__init__(shopkeeper, tmap, track)
        print(self.track)


class DwHowitzer(DwFootmen):
    def __init__(self, shopkeeper, tmap, track):
        super(DwHowitzer, self).__init__(shopkeeper, tmap, track)


class DwB2(DwFootmen):
    stealth = 11
    def mousePressEvent(self, a0: QtGui.QMouseEvent, actions=None):
        if self.actionStatus == DwB2.locked:
            actions_ = []
            if actions:
                for i in actions:
                    actions_.append(i)
            if self.dw.isStealth:
                actions_.append('现身')
            else:
                actions_.append('隐身')
        super(DwB2, self).mousePressEvent(a0, actions_)

    def handleLeftMenu(self, arg):
        if arg in ['隐身', '现身']:
            oldRoad = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            newRoad = self.countRoadNd(self.dw, oldRoad)
            if len(oldRoad) != len(newRoad):
                self.actionStatus = DwFootmen.encounter
            else:
                self.actionStatus = DwB2.stealth
            self.tmap.animeMove(newRoad, self)

            command = {'type': self.actionStatus, 'road':newRoad, 'moveShow':self.movedShow}
            self.shopkeeper.sendToServer(command)
        else:
            super(DwB2, self).handleLeftMenu(arg)

    def afterAnimation(self):
        if self.actionStatus == DwB2.stealth:
            self.dw.isStealth = not self.dw.isStealth
            self.actionStatus = DwB2.waiting
            # post = ShopMsgEvent()
            # QCoreApplication.postEvent(self.shopkeeper, post)
        super(DwB2, self).afterAnimation()

class DwSubmarine(DwFootmen):
    stealth = 11
    def mousePressEvent(self, a0: QtGui.QMouseEvent, actions=None):
        if self.actionStatus == DwSubmarine.locked:
            actions_ = []
            if actions:
                for i in actions:
                    actions_.append(i)
            if self.dw.isDiving:
                actions.append('上浮')
            else:
                actions.append('下潜')
        super(DwSubmarine, self).mousePressEvent(a0, actions_)

    def handleLeftMenu(self, arg):
        if arg in ['下潜', '上浮']:
            oldRoad = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            newRoad = self.countRoadNd(self.dw, oldRoad)
            if len(oldRoad) != len(newRoad):
                self.actionStatus = DwFootmen.encounter
            else:
                self.actionStatus = DwSubmarine.stealth
            self.tmap.animeMove(newRoad, self)

            command = {'type': self.actionStatus, 'road':newRoad, 'moveShow':self.movedShow}
            self.shopkeeper.sendToServer(command)
        else:
            super(DwSubmarine, self).handleLeftMenu(arg)

    def afterAnimation(self):
        if self.actionStatus == DwSubmarine.stealth:
            self.dw.isDiving = not self.dw.isDiving
            self.actionStatus = DwSubmarine.waiting
            # post = ShopMsgEvent()
            # QCoreApplication.postEvent(self.shopkeeper, post)
        # else:
        super(DwSubmarine, self).afterAnimation()


class DwConveyor(DwFootmen):
    unloadChoose = 11
    unloadmove = 12
    def __init__(self, shopkeeper, tmap, track):
        super(DwConveyor, self).__init__(shopkeeper, tmap, track)
        self.unloadNameDict = {}
        self.unloadAreaChoosed = []
        self.unloadChoosed = []

    def mousePressEvent(self, a0: QtGui.QMouseEvent, actions=None):
        actions_ = []
        if actions:
            for k in actions:
                actions_.append(k)
        if self.actionStatus == DwConveyor.locked:
            for i in self.tmap.layers:
                if i.geometry().contains(a0.pos()):
                    self.countUnloadArea(self.dw, i.mapId)
                    for i1, j in self.unLoadArea.items():
                        if j:
                            actions_.append('卸载')
                            break
                    break
        elif self.actionStatus == DwConveyor.unloadChoose:
            for i in self.tmap.layers:
                if i.geometry().contains(a0.pos()):
                    if i.mapId not in self.unloadAreaChoosed:
                        self.unloadAreaChoosed.append(i.mapId)
                        # self.tmap.clearLayers()
                        atm = []
                        for j1, j2 in self.unLoadArea.items():
                            tem_a = []
                            for k in j2:
                                if tuple(j2) != tuple(i.mapId):
                                    tem_a.append(k)
                            self.unLoadArea[j1] = tem_a
                            if tem_a and int(j1) not in self.unloadChoosed:
                                for t1, t in self.unloadNameDict.items():
                                    if t == j1:
                                        atm.append(t1)
                                        break
                        if atm:
                            self.tmap.showleftMenu(atm)
                        else:
                            oldRoad = self.roadsToChoose['roads'][self.roadsToChoose['point']]
                            newRoad = self.countRoadNd(self.dw, oldRoad)
                            if len(oldRoad) != len(newRoad):
                                self.actionStatus = DwFootmen.encounter
                            else:
                                self.actionStatus = DwConveyor.unloadmove
                            self.tmap.animeMove(newRoad, self)

                            command = {'type': self.actionStatus, 'road':newRoad, \
                                       'moveShow':self.movedShow, 'area':self.unloadAreaChoosed, 'cursor':self.unloadChoosed}
                            self.shopkeeper.sendToServer(command)
                    break
            else:
                self.actionBack()
                return
        super(DwConveyor, self).mousePressEvent(a0, actions_)

    def handleLeftMenu(self, arg):
        if arg == '卸载':
            actions = []
            self.unloadNameDict = {}
            for i, j in self.unLoadArea.items():
                if j:
                    oldName = self.dw.loadings[int(i)]['name']
                    name = resource.basicData['money']['chineseName'][oldName]
                    while 1:
                        if name in self.unloadNameDict:
                            name += 'I'
                        else:
                            self.unloadNameDict[name] = int(i)
                            break
                    actions.append(name)
            self.tmap.clearLayers()
            pos = self.tmap.leftMenu.pos()
            self.tmap.showleftMenu(actions, pos)
            self.actionStatus = DwConveyor.unloadChoose
            self.unloadChoosed = []
            self.unloadAreaChoosed = []

        elif self.actionStatus == DwConveyor.unloadChoose:
            self.unloadChoosed.append(self.unloadNameDict[arg])
            self.tmap.leftMenu.hide()
            self.tmap.showLayers(self.unLoadArea[str(self.unloadNameDict[arg])])
            self.tmap.showLayers(self.unloadAreaChoosed, 'black', False)

        else:
            print('oh no')
            super(DwConveyor, self).handleLeftMenu(arg)

    def afterAnimation(self):
        if self.actionStatus == DwConveyor.unloadmove:
            if self.track['flag'] == self.tmap.myForce:
                self.dw.doBody('rightG')
            else:
                self.dw.doBody('leftG')
            action = self.roadsToChoose['roads'][self.roadsToChoose['point']]
            self.tmap.pointer_dw[action[0][0]][action[0][1]] = None
            self.tmap.pointer_dw[action[-1][0]][action[-1][1]] = self.dw
            self.dw.mapId = action[-1]

            loadings = []
            tem_ = []
            choosed = []
            for i, j in enumerate(self.unloadChoosed):
                self.dw.loadings[int(j)]['mapId'] = self.unloadAreaChoosed[i]
                choosed.append(self.dw.loadings[int(j)])

                tem_.append(int(j))
            for i1, i in enumerate(self.dw.loadings):
                if i1 not in tem_:
                    loadings.append(i)
            self.dw.loadings = loadings

            post = UnloadDwEvent(choosed)
            QCoreApplication.postEvent(self.tmap, post)

            post = ShopMsgEvent()
            QCoreApplication.postEvent(self.shopkeeper, post)

        else:
            super(DwConveyor, self).afterAnimation()

    def actionBack(self):
        if self.actionStatus == DwConveyor.unloadChoose:
            '''----------不能删！！！---------'''
            # self.tmap.showLayers(self.roadsToChoose['roads'][self.roadsToChoose['point']])
            # self.tmap.showleftMenu(self.tmap.leftMenu.primActions)
            # self.unloadAreaChoosed = []
            # self.unloadChoosed = []
            # self.actionStatus == DwConveyor.destination

            # self.tmap.showLayers(self.moveLayers)
            # self.tmap.leftMenu.hide()
            # self.actionStatus = DwConveyor.locked

            self.tmap.leftMenu.hide()
            self.tmap.clearLayers()
            QCoreApplication.postEvent(self.shopkeeper, ShopMsgEvent(ShopMsgEvent.relock))
        else:
            super(DwConveyor, self).actionBack()

class DwTransport(DwConveyor):
    supply = 17
    def __init__(self, shopkeeper, tmap, track):
        super(DwTransport, self).__init__(shopkeeper, tmap, track)
        self.supplyElement = []

    def mousePressEvent(self, a0: QtGui.QMouseEvent, actions=None):
        actions_ = []
        if actions:
            for k in actions:
                actions_.append(k)
        if self.actionStatus == DwTransport.locked:
            for i in self.tmap.layers:
                if i.geometry().contains(a0.pos()):
                    if tuple(i.mapId) == tuple(self.dw.mapId):
                        self.supplyElement = self.countSupply(self.dw)
                        print(4444)
                        if self.supplyElement:
                            actions_.append('计划补给')
                    break
        super(DwTransport, self).mousePressEvent(a0, actions_)

    def handleLeftMenu(self, arg):
        if arg == '计划补给':
            self.tmap.clearLayers()
            self.tmap.leftMenu.hide()
            post = SupplyEvent(self.track)
            QCoreApplication.postEvent(self.tmap, post)
        else:
            super(DwTransport, self).handleLeftMenu(arg)

    def event(self, a0: 'QEvent') -> bool:
        if a0.type() == SupplyEvent.idType:
            if a0.supply:
                self.dw.supplies = a0.supply
                self.dw.doBody(self.track['action']+'G')
                for i in self.supplyElement:
                    dw = self.tmap.pointer_dw[i[0]][i[1]]
                    if dw:
                        dw.doBody(dw.track['action']+'G')
                    else:
                        print(i, 'supply error')

                command = {'type': DwTransport.supply, 'element':self.supplyElementp, 'supply':a0.supply}
                self.shopkeeper.sendToServer(command)

            post = ShopMsgEvent()
            QCoreApplication.postEvent(self.shopkeeper, post)
        return super(DwTransport, self).event(a0)


class Building(ShopWaiter):
    build = 16
    def __init__(self, shopkeeper, tmap, track):
        super(Building, self).__init__(shopkeeper, tmap, track)
        # QCoreApplication.postEvent(self.tmap, BuildDwEvent(track, True))
        self.tmap.showbuildMenu(track)

    def event(self, a0: 'QEvent') -> bool:
        if a0.type() == BuildDwEvent.idType:
            if a0.track:
                post = BuildDwEvent(a0.track)
                print('buld')
                command = {'type': Building.build, 'track': a0.track}
                self.shopkeeper.sendToServer(command)

                QCoreApplication.postEvent(self.tmap, post)
            post = ShopMsgEvent()
            QCoreApplication.postEvent(self.shopkeeper, post)
        return super(Building, self).event(a0)



'''================================================='''
'''=====================仲裁者======================='''


class Arbitrator(QObject):
    def __init__(self, mapName, tmap:TMap_):
        super(Arbitrator, self).__init__()
        self.mapName = mapName
        self.tmap = tmap
        self.helper = ArbitratorEvent(self)

        path = 'maps/'+mapName+'/markets.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.markets = json.load(f)
        else:
            self.markets = {}


        path = 'maps/'+mapName+'/toggles.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.toggles = json.load(f)
        else:
            self.toggles = {}

        path = 'maps/'+mapName+'/toggleEvents.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.toggleEvents = json.load(f)
        else:
            self.toggleEvents = {}

    def checkData(self):
        shouldDel = []
        for i1, i in self.markets.items():
            if not i['flags']:
                shouldDel.append(i1)
                continue

            end = []
            if i['type'] == '单位':
                dws = self.tmap.pointer_dw
                for j in i['data']:
                    if dws[j[0]][j[1]]:
                        if dws[j[0]][j[1]].track['flag'] in i['flags']:
                            end.append(j)
                if not end:
                    shouldDel.append(i1)
            elif i['type'] == '建筑':
                dws = self.tmap.pointer_geo
                for j in i['data']:
                    if dws[j[0]][j[1]]:
                        if dws[j[0]][j[1]].track['flag'] in i['flags']:
                            end.append(j)
                if not end:
                    shouldDel.append(i1)
        for i in shouldDel:
            del self.markets[i]

        shouldDel = []
        for i1, i in self.toggles.items():
            if 'market' in i:
                if i['market'] not in self.markets:
                    shouldDel.append(i1)
        for i in shouldDel:
            del self.toggles[i]

        shouldDel = []
        for i1, i in self.toggleEvents.items():
            if 'market' in i:
                if i['market'] not in self.markets:
                    shouldDel.append(i1)
        for i in shouldDel:
            del self.toggleEvents[i]

        shouldDel = []
        for i1, i in self.toggleEvents.items():
            if i['response'] not in self.toggles:
                shouldDel.append(i1)
            elif i['obj'] == '触发器':
                if i['data'] not in self.toggles:
                    shouldDel.append(i1)
        for i in shouldDel:
            del self.toggleEvents[i]


    def installToggles(self):
        pass

    def installToggleEvents(self):
        pass

    '''阵亡==》直接调用,要调用两个哦'''
    def dwCall(self, dw:DW, triggerFlag=None):
        news = []
        for i in dw.triggers:
            if i in self.toggles:
                news.append(i)
            else:
                continue
            toggle = self.toggles[i]
            if toggle['type'] == '所属':
                if dw.track['flag'] not in self.markets[toggle['market']]['flags']:
                    self.helper.handle(toggle['response'], \
                                       dw.track['flag'], triggerFlag)

            elif toggle['type'] == '隐身':
                if not (bool(toggle['data']) ^ bool(dw.isStealth)):
                    self.helper.handle(toggle['response'], dw.track['flag'])
            elif toggle['type'] == '下潜':
                if not (bool(toggle['data']) ^ bool(dw.isDiving)):
                    self.helper.handle(toggle['response'], dw.track['flag'])
            elif toggle['type'] == '占领':
                if dw.occupied > 0:
                    self.helper.handle(toggle['response'], dw.track['flag'])
                # elif toggle['type'] == '阵亡':
                #     if '阵亡' in types:
                #         self.helper.handle(toggle['response'], dw.track['flag'])
            elif toggle['type'] == '规模':
                isOk = False
                if toggle['data'] == '<':
                    if dw.bloodValue < toggle['value']:
                        isOk = True
                elif toggle['data'] == '=':
                    if dw.bloodValue == toggle['value']:
                        isOk = True
                elif toggle['data'] == '>':
                    if dw.bloodValue > toggle['value']:
                        isOk = True
                if isOk:
                    self.helper.handle(toggle['response'], dw.track['flag'], triggerFlag)

            elif toggle['type'] == '弹药':
                isOk = False
                if toggle['data'] == '<':
                    if dw.bullect < toggle['value']:
                        isOk = True
                elif toggle['data'] == '=':
                    if dw.bullect == toggle['value']:
                        isOk = True
                elif toggle['data'] == '>':
                    if dw.bullect > toggle['value']:
                        isOk = True
                if isOk:
                    self.helper.handle(toggle['response'], dw.track['flag'], triggerFlag)

            elif toggle['type'] == '油量':
                isOk = False
                if toggle['data'] == '<':
                    if dw.oil < toggle['value']:
                        isOk = True
                elif toggle['data'] == '=':
                    if dw.oil == toggle['value']:
                        isOk = True
                elif toggle['data'] == '>':
                    if dw.oil > toggle['value']:
                        isOk = True
                if isOk:
                    self.helper.handle(toggle['response'], dw.track['flag'])

        dw.triggers = news

    def buildCall(self, geo:Geo, triggerFlag=None):
        news = []
        for i in geo.triggers:
            if i in self.toggles:
                news.append(i)
            else:
                continue
            toggle = self.toggles[i]
            if toggle['type'] == '所属':
                if toggle['type'] not in self.markets[toggle['market']]['flags']:
                    self.helper.handle(self.toggles, geo.track['flag'], triggerFlag)


        geo.triggers = news

    '''移动之后才能调用'''
    def areaCall(self, triggerFlag=None):
        for j, i in self.toggles.items():
            if i['obj'] != '区域':
                continue
            hasF = False
            fFlag = None
            hasE = False
            eFalg = None
            if '己方' in i['type']:
                for j in self.markets[self.toggles['market']]:
                    dw = self.tmap.pointer_dw[j[0]][j[1]]
                    if dw:
                        if dw.track['flag'] in j['flags']:
                            hasF = True
                            fFlag = dw.track['flag']
                            break
            elif '敌方' in i['type']:
                for j in self.markets[self.toggles['market']]:
                    dw = self.tmap.pointer_dw[j[0]][j[1]]
                    if dw:
                        for k in j['flags']:
                            if dw.track['flag'] in self.tmap.forces[k]['enemy']:
                                hasE = True
                        if hasE:
                            break

            if i['type'] == '无己方单位':
                if not hasF:
                    self.helper.handle(i['response'], self.markets[self.toggles['market']]['flags'][0])

            elif i['type'] == '有己方单位':
                if hasF:
                    self.helper.handle(i['response'], fFlag, fFlag)
            elif i['type'] == '无敌方单位':
                if not hasE:
                    self.helper.handle(i['response'], self.markets[self.toggles['market']]['flags'][0])
            elif i['type'] == '有敌方单位':
                if hasE:
                    self.helper.handle(i['response'], eFalg, self.markets[self.toggles['market']]['flags'][0])


        # class Status:
        #     none = 0
        #     outer = 1
        #     inner = 2
        #     goin = 3
        #     goout = 4
        #     all = 5
        # for i in self.toggles:
        #     if i['obj'] != '区域':
        #         continue
        #     status = Status.none
        #     for j in road:
        #         for k in self.markets[i['market']]['data']:
        #             if tuple(k) == tuple(j):
        #                 if status == Status.none:
        #                     status = Status.inner
        #                 elif status == Status.outer:
        #                     status = Status.goin
        #                 elif status == Status.goout:
        #                     status = Status.all
        #                 break
        #         else:
        #             if status == Status.none:
        #                 status = Status.outer
        #             elif status == Status.inner:
        #                 status = Status.goout
        #             elif status == Status.goin:
        #                 status = Status.all
        #     if status == Status.goin:
        #         if '进入' in i['type']:
        #             self.helper.handle(i['response'], )
        #     elif status == Status.goout:
        #         if '移出' in i['type']:
        #             pass
        #     elif status == Status.all:
        #         pass

    def moneyCall(self, triggerFlag=None):
        key_1 = ['资金', '损失', '回合支出', '造成损失', '军力', '总油耗', '总弹药消耗', '能量']
        key_2 = ['money', 'loss', 'outcome', 'destory', 'armyPrice', 'oil', 'bullect', 'energy']
        for j, i in self.toggles.items():
            if i['obj'] != '资金':
                continue
            dd2 = self.tmap.forces[i['flag']]['dataInfo'][key_2[key_1.index(i['type'])]]
            canToggle = False
            if i['data'] == '<':
                if dd2 < i['value']:
                    canToggle = True
            elif i['data'] == '>':
                    canToggle = True
            elif i['data'] == '=':
                if dd2 == i['value']:
                    canToggle = True
            if canToggle:
                self.helper.handle(i['response'], i['flag'], triggerFlag)

    def boutCall(self, nowBout, triggerFlag):
        for j, i in self.toggles.items():
            if i['obj'] != '回合':
                continue
            if triggerFlag not in i['value']:
                continue
            if i['type'] == '指定回合':
                if nowBout == i['data']:
                    self.helper.handle(i['response'], trigger=self.tmap.nowForce)
            elif i['type'] == '间隔回合':
                if int(nowBout) % int(i['data']) == 0:
                    self.helper.handle(i['response'], trigger=self.tmap.nowForce)

    def commandCall(self, command, triggerFalg):
        for j, i in self.toggles.items():
            if i['obj'] != '命令':
                continue
            if command == i['data']:
                self.helper.handle(i['response'], trigger=triggerFalg)

class ArbitratorEvent(QObject):
    def __init__(self, arbitrator):
        super(ArbitratorEvent, self).__init__()
        self.arbitrator = arbitrator
        self.tmap = arbitrator.tmap

    def handle(self, eventId, triggered=None, trigger=None):
        event = self.arbitrator.toggleEvents[eventId]
        if event['obj'] == '单位':
            self.dwCall(eventId, triggered, trigger)
        elif event['obj'] == '建筑':
            self.buildCall(eventId, triggered, trigger)
        elif event['obj'] == '区域':
            self.areaCall(eventId, triggered, trigger)
        elif event['obj'] == '镜头':
            self.lenCall(eventId, triggered, trigger)
        elif event['obj'] == '资金':
            self.moneyCall(eventId, triggered, trigger)
        elif event['obj'] == '触发器':
            self.toggleCall(eventId, triggered, trigger)
        elif event['obj'] == '胜败':
            self.victoryCall(eventId, triggered, trigger)
        elif event['obj'] == '指挥权':
            self.ctrlCall(eventId, triggered, trigger)
        elif event['obj'] == '消息':
            self.msgCall(eventId, triggered, trigger)

    def dwCall(self, eventId, triggered, trigger):
        event = self.arbitrator.toggleEvents[eventId]
        if event['type'] == '规模':
            if event['data'] == '+':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.doBlood(i.bloodValue + event['value'])
            if event['data'] == '-':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.doBlood(i.bloodValue - event['value'])
            if event['data'] == '=':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.doBlood(event['value'])

        elif event['type'] == '油量':
            if event['data'] == '+':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.oil += event['value']
            if event['data'] == '-':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.oil -= event['value']
            if event['data'] == '=':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.oil = event['value']

        elif event['type'] == '弹药':
            if event['data'] == '+':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.bullect += event['value']
            if event['data'] == '-':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.bullect -= event['value']
            if event['data'] == '=':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.bullect = event['value']

        elif event['type'] == '占领':
            if event['data'] == '+':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        if resource.basicData['money']['canoccupy'][i.track['name']] == '1':
                            i.occupied += event['value']
            if event['data'] == '-':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        if resource.basicData['money']['canoccupy'][i.track['name']] == '1':
                            i.occupied -= event['value']
            if event['data'] == '=':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        if resource.basicData['money']['canoccupy'][i.track['name']] == '1':
                            i.occupied = event['value']

        elif event['type'] == '所属':
            if event['type'] == '被触发者':
                pass
            elif event['data'] == '触发者':
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.change(trigger)
            else:
                for i in self.tmap.findChildren(DW):
                    if eventId in i.triggerEvents:
                        i.change(event['data'])

        elif event['type'] == '阵亡':
            for i in self.tmap.findChildren(DW):
                if eventId in i.triggerEvents:
                    self.tmap.pointer_dw[i.mapId[0]][i.mapId[1]] = None
                    i.deleteLater()

        elif event['type'] == '隐身':
            for i in self.tmap.findChildren(DW):
                if eventId in i.triggerEvents:
                    if resource.basicData['money']['canstealth'][i.track['name']] == '1':
                        i.isStealth = event['data']

        elif event['type'] == '下潜':
            for i in self.tmap.findChildren(DW):
                if eventId in i.triggerEvents:
                    if resource.basicData['money']['candiving'][i.track['name']] == '1':
                        i.isDiving = event['data']

    def buildCall(self, eventId, triggered, trigger):
        event = self.arbitrator.toggleEvents[eventId]
        if event['type'] == '所属':
            if event['data'] == '被触发者':
                pass
            elif event['data'] == '触发者':
                for i in self.tmap.findChildren(Geo):
                    if i.track['usage'] == 'geo':
                        if eventId in i.triggerEvents:
                            track = i.track
                            track['flag'] = trigger
                            i.change(track)
            else:
                for i in self.tmap.findChildren(Geo):
                    if i.track['usage'] == 'geo':
                        if eventId in i.triggerEvents:
                            track = i.track
                            track['flag'] = event['data']
                            i.change(track)

    def areaCall(self, eventId, triggered, trigger):
        event = self.arbitrator.toggleEvents[eventId]
        flags = self.arbitrator.markets[event]['market']['flags']
        markets = self.arbitrator.markets[event]['market']['data']
        destory = 0
        if event['type'] == '阵亡':
            for i in markets:
                dw = self.tmap.pointer_dw[i[0]][i[1]]
                if dw:
                    if dw.track['flag'] in flags:
                        self.tmap.pointer_dw[i[0]][i[1]] = None
                        dw.deleteLater()
        elif event['type'] == '大损伤':
            destory = 5
        elif event['type'] == '中等损伤':
            destory = 2
        elif event['type'] == '小损伤':
            destory = 1
        elif event['type'] == '支援':
            empty = []
            for i in markets:
                if not self.tmap.pointer_dw[i[0]][i[1]]:
                    empty.append(tuple(i))
            if not empty:
                return
            loadings = []
            for i in empty:
                ran = random.randint(0, event['value']['__up__']-1)
                ran2 = random.randint(0, len(flags) - 1)
                for j1, j in event['value']:
                    if j['donw'] <= ran < j['up']:
                        break
                track = resource.find({'usage':'dw', 'name':'j1', 'flag':ran2})
                track['mapId'] = i
                loadings.append(track)
            QCoreApplication.postEvent(self.tmap, UnloadDwEvent(loadings))

        if destory:
            for i in markets:
                dw = self.tmap.pointer_dw[i[0]][i[1]]
                if dw:
                    if dw.track['flag'] in flags:
                        dw.doBlood(dw.bloodValue - destory)

    '''需要sorket'''
    def lenCall(self, eventId, triggered, trigger):
        market = self.arbitrator.markets[self.arbitrator.toggleEvents[eventId]['market']]
        self.tmap.moveToDw(market['data'][0])

    def moneyCall(self, eventId, triggered, trigger):
        keys_1 = ['money', 'energy', 'oil', 'bullect', \
                 'landmissile', 'seamissile', 'skymissile', 'nuclear']
        keys_2 = ['资金', '能量', '油', '弹药', '对陆导弹', '对空导弹', '对舰导弹', '核弹']
        event = self.arbitrator.toggleEvents[eventId]
        key3 = keys_1[keys_2.index(event['data'])]
        if event['data'] == '=':
            if '触发者' in event['flags']:
                self.tmap.forces[trigger]['dataInfo'][key3] = event['value']
            for i in event['flags']:
                self.tmap.forces[i]['dataInfo'][key3] = event['value']
        elif event['data'] == '+':
            if '触发者' in event['flags']:
                self.tmap.forces[trigger]['dataInfo'][key3] += event['value']
            for i in event['flags']:
                self.tmap.forces[i]['dataInfo'][key3] += event['value']
        elif event['data'] == '-':
            if '触发者' in event['flags']:
                self.tmap.forces[trigger]['dataInfo'][key3] -= event['value']
            for i in event['flags']:
                self.tmap.forces[i]['dataInfo'][key3] -= event['value']
        if key3 in ['money', 'energy']:
            self.tmap.infoView.updateInfo()

    def toggleCall(self, eventId, triggered, trigger):
        pass

    def victoryCall(self, eventId, triggered, trigger):
        pass

    def ctrlCall(self, eventId, triggered, trigger):
        pass

    def msgCall(self, eventId, triggered, trigger):
        pass






'''远程攻击单位：榴弹炮'''

###--------------------暂不考虑触发器----------------------------###
if __name__ == '__main__':
    # hereusers = [{'flag': 'red', 'enemy': ['blue', 'yellow'], 'action': 'right', 'command_bg': '会战', 'command': '消灭敌方', \
    #                'outcome': 0, 'money': 99999, 'hero': 'google', 'header_loc': None, 'canBeGua': False, 'bout': 1,
    #                'exp': 2}, \
    #               {'flag': 'blue', 'enemy': ['red', 'yellow'], 'action': 'left', 'command_bg': '会战', 'command': '消灭敌方', \
    #                'outcome': 0, 'money': 0, 'hero': 'warhton', 'header_loc': None, 'canBeGua': False, 'bout': 1,
    #                'exp': 2}]
    #
    # window = TMap(users=hereusers, tUser=hereusers[0])
    # window.show()
    fuse = {
        'red': {'heroName': 'google', 'isMe': True, 'user':'玩家', \
                'userInfo': {'userId': '123', 'userName': 'sdfd'}}, \
        'blue': {'heroName': 'google', 'isMe': False, 'user':'玩家', \
                 'userInfo': {'userId': '123', 'userName': 'sdfd'}}, \
        'green': {'heroName': 'google', 'isMe': False, 'user':'玩家', \
                  'userInfo': {'userId': '123', 'userName': 'sdfd'}}
    }
    window = TMap_(fuse)
    window.show()

    print(window.forces)
    sys.exit(qapp.exec_())

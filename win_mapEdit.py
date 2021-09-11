#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :main_window.py
# @Time      :2021/7/18 14:05
# @Author    :russionbear
import json, os, shutil

from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui
from map_load import Geo, DW, miniVMap
# from tmap_load import TMap
# from resource_load import resource
from resource import resource
from win_basicdataEdit import basicEditW
import sys, functools, time, hashlib

Qapp = QApplication(sys.argv)


class EditTool(QWidget):
    def initUi(self, winSize=(340, 800), blockSize=(100, 100), mainWin=None):
        self.status = [0, 0]
        self.mainWin = mainWin
        self.choosed = None
        self.choosedLoadings = {}
        self.choosedSupplies = {}
        # self.data = {}
        # self.choosedData = None
        self.setFixedSize(winSize[0], winSize[1])
        self.blockSize = blockSize
        self.row = winSize[0]//blockSize[0]
        btn1_s = ['地形', '建筑', '单位']
        self.btn1_s = btn1_s
        layout1 = QBoxLayout(QBoxLayout.LeftToRight)
        for i in btn1_s:
            btn1 = QPushButton(i)
            btn1.clicked.connect(functools.partial(self.swapBtn1,i))
            layout1.addWidget(btn1)

        color = [ 'none','red', 'blue', 'green', 'yellow']
        self.btn2_s = color
        layout2 = QGridLayout()
        for j, i in enumerate(color):
            btn2 = QPushButton(i)
            btn2.clicked.connect(functools.partial(self.swapBtn2,i))
            layout2.addWidget(btn2,j//4, j%4, 1, 1)

        self.data = {'geo':[], 'build':{'red':[], 'blue':[], 'yellow':[], 'green':[], 'none':[]}, 'dw':{'red':[], 'blue':[], 'yellow':[], 'green':[], 'none':[]}}
        for j, i in enumerate(resource.data):
            if 'action' in i:
                # if i['action'] != 'left':
                if i['name'] == 'sea' and i['action'] != '':
                    continue
                elif i['name'] == 'road' and i['action'] != 'across':
                    continue
                elif i['name'] == 'river' and i['action'] != 'across':
                    continue
                elif i['action'] not in ['left', 'across', '', 'center']:
                    continue
                elif i['usage'] == 'dw2':
                    continue

                if i['usage'] == 'geo':
                    self.data['geo'].append(i.copy())
                else:
                    self.data[i['usage']][i['flag']].append(i.copy())

        area = QListWidget(self)

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addSpacing(10)
        layout.addLayout(layout1)
        layout.addSpacing(20)
        layout.addLayout(layout2)
        layout.addWidget(area)

        keys = ['blood', 'oil', 'bullect', 'ocupied', 'isStealth', 'isDiving', 'moved', 'loadings', 'supplies']
        keys_ = ['规模', '油量(%)', '弹药(%)', '占领', '隐身', '下潜', '已移动', '装载', '补给']
        self.dwInfo = []
        layout_4 = QFormLayout()
        for i1, i in enumerate(keys[0:4]):
            tem = QSpinBox(self)
            tem.setMinimum(0)
            tem.setMaximum(100)
            layout_4.addRow(keys_[i1],tem)
            self.dwInfo.append(tem)
        tem.setMaximum(20)
        self.dwInfo[0].setMaximum(10)
        for i1, i in enumerate(keys[4:7]):
            tem = QCheckBox(self)
            tem.setChecked(False)
            layout_4.addRow(keys_[i1+4], tem)
            self.dwInfo.append(tem)
        tem = QPushButton('装载', self)
        tem.clicked.connect(functools.partial(self.selectDws, 'loadings'))
        self.dwInfo.append(tem)
        tem_ = QPushButton('补给', self)
        tem_.clicked.connect(functools.partial(self.selectDws, 'supplies'))
        self.dwInfo.append(tem_)
        layout_4_ = QBoxLayout(QBoxLayout.LeftToRight)
        layout_4_.addWidget(tem)
        layout_4_.addWidget(tem_)
        tem_ = QPushButton('重置', self)
        tem_.clicked.connect(functools.partial(self.selectDws, 'reset'))
        layout_4.addRow(tem_, layout_4_)
        layout.addSpacing(50)
        layout.addLayout(layout_4)

        self.setLayout(layout)


        self.swapBtn1(self.btn1_s[0])
        self.selectDws('reset')

    def swapBtn1(self, data):
        key = {}
        def enable(bool):
            tem_child = self.findChildren(QPushButton)
            for i in tem_child:
                if i.text() in self.btn2_s:
                    i.setEnabled(bool)
        keys = ['geo', 'build', 'dw']
        for i, j in enumerate(self.btn1_s):
            if j == data:
                self.status[0] = i
                # key['usage'] = keys[i]
                # key['flag'] = ''
                if keys[i] == 'geo':
                    enable(False)
                    # self.swap(resource.findAll(key))
                    self.swap(self.data['geo'])
                    break
                # key['flag'] = self.btn2_s[self.status[1]]
                enable(True)
                # self.swap(resource.findAll(key))
                self.swap(self.data[keys[i]][self.btn2_s[self.status[1]]])
                break
        # self.enableSlider(key['usage'])

    def swapBtn2(self, data):
        keys = ['geo', 'build', 'dw']
        for i, j in enumerate(self.btn2_s):
            if j == data:
                self.status[1] = i
                # self.swap(resource.findAll({'flag':data, 'usage':keys[self.status[0]]}))
                self.swap(self.data[keys[self.status[0]]][data])
                break

    def swap(self, list):
        tem = self.findChild(QListWidget)
        tem.clear()
        for i in list:
            if i['name'] == 'delete':
                tem_dd = QListWidgetItem(QIcon(i['pixmap']), i['name'])
            elif i['usage'] == 'dw':
                tem_dd = QListWidgetItem(QIcon(i['pixmap']), resource.basicData['money']['chineseName'][i['name']])
            else:
                tem_dd = QListWidgetItem(QIcon(i['pixmap']), resource.basicData['geo']['chineseName'][i['name']])
            tem_dd.track = i
            tem.addItem(tem_dd)

    def choose(self, mapId):
        for i in self.findChildren(QLabel):
            if hasattr(i, 'mapId'):
                if i.mapId == self.choosed:
                    i.choose(False)
                    break
        self.choosed = mapId
        if self.parent():
            if self.parent().parent():
                try:
                    self.parent().parent().statusBar().showMessage(resource.basicData['money']['dsc'][mapId['name']])
                except KeyError:
                    pass

    def valueChange(self, label, value):
        text = label.text()
        text = text.split('：')[0] + '：' + str(value) + '%'
        label.setText(text)

    def selectDws(self, data):
        if data == 'loadings':
            if self.mainWin:
                self.mainWin.showLSView(self.choosedLoadings, data)
        elif data == 'supplies':
            if self.mainWin:
                self.mainWin.showLSView(self.choosedSupplies, data)
        else:
            key1 = [10, 100, 100, 0]
            for i1, i in enumerate(self.dwInfo[0:4]):
                i.setValue(key1[i1])
            self.dwInfo[4].setChecked(False)
            self.dwInfo[5].setChecked(False)
            self.choosedLoadings = {}
            self.choosedSupplies = {}

    def getChoosedData(self):
        tem = self.findChild(QListWidget)
        try:
            self.choosed = tem.currentItem().track
            # del self.choosed['pixmap']
        except:
            return None
        if self.choosed['name'] == 'delete':
            # print(self.choosed)
            return {'track':self.choosed}
        if self.choosed['usage'] in ['geo', 'build']:
            return {'track':self.choosed}
        end = {}
        key1 = ['blood', 'oil', 'bullect', 'occupied', 'isStealth', 'isDiving', 'moved', 'loadings', 'supplies']
        # cursor = iter([i for i in range(len(key1))])
        # print(nex)
        for i1, i in enumerate(self.dwInfo[0:4]):
            end[key1[i1]] = i.value()
        for i in range(4, 7):
            end[key1[i]] = self.dwInfo[i].isChecked()

        loadings = []
        tem_key = resource.basicData['money']['canloading'][self.choosed['name']]
        max = int(tem_key[0])
        while True:
            max -= 1
            if max < 0:
                break
            for i, j in self.choosedLoadings.items():
                if j <=0:
                    continue
                elif j > int(resource.basicData['money']['money'][i]):
                    guimo = 10
                    self.choosedLoadings[i] -= int(resource.basicData['money']['money'][i])
                else:
                    guimo = j//int(resource.basicData['money']['money'][i])
                if guimo == 0 or (i not in tem_key and resource.basicData['money']['classify'][self.choosed['name']] not in tem_key):
                    continue
                track = {'blood':guimo, 'oil':int(resource.basicData['gf'][i]['oil']), 'bullect':int(resource.basicData['gf'][i]['bullect']), \
                         'occupied':0, 'isStealth':False, 'isDiving':False, 'name':i, 'flag':self.choosed['flag']}
                loadings.append(track)
            else:
                break
        end[key1[7]] = loadings
        end[key1[8]] = self.choosedSupplies
        end['oil'] = int(end['oil']/100*int(resource.basicData['gf'][self.choosed['name']]['oil']))
        end['bullect'] = int(end['bullect']/100*int(resource.basicData['gf'][self.choosed['name']]['bullect']))
        if resource.basicData['money']['canoccupy'][self.choosed['name']] == '0':
            end['occupied'] = 0
        if resource.basicData['money']['canstealth'][self.choosed['name']] == '0':
            end['isStealth'] = False
        if resource.basicData['money']['candiving'][self.choosed['name']] == '0':
            end['isDiving'] = False
        if resource.basicData['money']['cansupply'][self.choosed['name']] == '0':
            end['supplies'] = {}
        end['track'] = self.choosed.copy()
        if end['moved']:
            end['track']['action'] += 'G'
            end['track'] = resource.find(end['track'])
            # print(end['track'])
        # print(end)
        return end

    def saveLS(self, view, type):
        end = {}
        for i in view.findChildren(QSpinBox):
            end[i.name] = int(i.value())
        if type == 'loadings':
            self.choosedLoadings = end
        else:
            self.choosedSupplies = end
        view.deleteLater()

class EditMap(QWidget):
    def __init__(self, name='default', parent=None, block=(100, 100), winSize=(800, 800), brother=None):
        super(EditMap, self).__init__(parent)
        self.brother = brother
        self.isTargetChoosing = False
        self.isTargetShowing = False
        self.targetChooseType = None
        self.targetChoosedLayer = []
        self.initUI(name, block, winSize)

        self.dwUpdater = QTimer(self)
        self.dwUpdater.timeout.connect(self.myUpdate)
        self.dwUpdater.start(1400)

    def initUI(self, name, block, winSize):
        self.setFixedSize(winSize[0], winSize[1])
        self.map = resource.findMap(name)
        if not self.map:
            print(self.map, 'error', name)
            sys.exit()
        self.mapSize = len(self.map['map'][0]), len(self.map['map'])
        self.mapBlockSize = block

        self.pointer_geo = []
        for i in range(len(self.map['map'])):
            tem_data = []
            for j in range(len(self.map['map'][i])):
                track = resource.findByHafuman(self.map['map'][i][j])
                if not track:
                    print('map error123')
                    return
                track['mapId'] = i, j
                tem_geo = Geo(self, track)
                tem_geo.move(j*self.mapBlockSize[0], i*self.mapBlockSize[1])
                tem_data.append(tem_geo)
            self.pointer_geo.append(tem_data)

        self.canMove = (True if self.mapBlockSize[0]*self.mapSize[0] > self.width() else False,
                               True if self.mapBlockSize[1]*self.mapSize[1]>self.height() else False)

        self.canScale = False
        self.mapScalePoint = 9
        self.hasCircle = self.hasMove = False
        self.circled = []
        self.circle = QFrame(self)
        self.circle.setFrameShape(QFrame.Box)
        self.circle.setFrameShadow(QFrame.Sunken)
        self.circle.setStyleSheet('background-color:#00a7d0;')
        op = QGraphicsOpacityEffect()
        op.setOpacity(0.4)
        self.circle.setGraphicsEffect(op)
        self.circle.hide()
        self.circle.setLineWidth(0)
        self.circleStatus = None

        self.pointer_dw = [[None for i in range(self.mapSize[0])] for j in range(self.mapSize[1])]
        for i in self.map['dw']:
            axis = i['mapId']
            dw = DW(self, i)
            dw.move(axis[1]*block[1], axis[0]*block[0])
            self.pointer_dw[axis[0]][axis[1]] = dw

    def mapAdjust(self):
        move_x, move_y = (self.mapBlockSize[0]*self.mapSize[0]-self.width())//2, (self.mapBlockSize[1]*self.mapSize[1]-self.height())//2
        move_x, move_y = -move_x - self.pointer_geo[0][0].x(), -move_y - self.pointer_geo[0][0].y()
        self.mapMove(move_x, move_y, True)

    def mapMove(self, x, y, isforce=False):
        def move(x, y):
            for i in self.children():
                if not hasattr(i, 'move'):
                    continue
                i.move(i.x() + x, i.y() + y)
        if isforce:
            move(x,y)
        else:
            last_cursor = self.mapSize[0]*self.mapSize[1] - 1
            if self.children()[0].x()+x>0 and self.canMove[0]:
                # print('111')
                move_x = - self.children()[0].x()
                move_y = 0 if self.children()[0].y()<0 and self.canMove[1] else - self.children()[0].y()
                move(move_x,move_y)
            elif self.children()[0].y() + y > 0 and self.canMove[1]:
                # print('22')
                move_x = 0 if self.children()[0].x()<0 and self.canMove[0] else - self.children()[0].x()
                move_y = - self.children()[0].y()
                move(move_x, move_y)
            elif self.children()[last_cursor].x() +x <self.width()-self.mapBlockSize[0] and self.canMove[0]:
                # print('333')
                move_x = self.width()-self.mapBlockSize[0]-self.children()[last_cursor].x()
                move_y = self.height()-self.mapBlockSize[0]-self.children()[last_cursor].y()
                move_y = 0 if move_y <0 and self.canMove[1] else move_y
                move(move_x, move_y)
            elif self.children()[last_cursor].y() +y < self.height()-self.mapBlockSize[1] and self.canMove[1]:
                # print('444')
                move_x = self.width()-self.mapBlockSize[0]-self.children()[last_cursor].x()
                move_y = self.height()-self.mapBlockSize[0]-self.children()[last_cursor].y()
                move_x = 0 if move_x <0 and self.canMove[0] else move_x
                move(move_x, move_y)
            else:
                # print('555')
                move(0 if not self.canMove[0] else x,0 if not self.canMove[1] else y)

    def mapScale(self, shouldBigger=True):
        if ( shouldBigger and self.mapScalePoint == len(resource.mapScaleList) -1 ) or\
            (not shouldBigger and self.mapScalePoint ==0):   #can scale
            return
        primA = self.width()//2-self.children()[0].x(), self.height()//2-self.children()[0].y()
        mapBlockSize = resource.mapScaleList[self.mapScalePoint]['body']
        self.mapScalePoint += 1 if shouldBigger else -1
        self.mapBlockSize = resource.mapScaleList[self.mapScalePoint]['body']
        n = self.mapBlockSize[0]/mapBlockSize[0]
        primA = self.width()//2-round(primA[0]*n), self.height()//2-round(primA[1]*n)
        tem_data = resource.mapScaleList[self.mapScalePoint]
        # print(n, tem_data)
        tem_children = self.findChildren((Geo, DW))
        # for j, i in enumerate(self.children()[:self.mapSize[0]* self.mapSize[1]]):
        for j, i in enumerate(tem_children):
            i.scale(tem_data)
            i.move(primA[1]+i.mapId[1]*self.mapBlockSize[1], primA[0]+i.mapId[0]*self.mapBlockSize[0])
            # i.move(primA[0]+j%self.mapSize[0]*self.mapBlockSize[0], primA[1]+j//self.mapSize[1]*self.mapBlockSize[1])

        move_x = self.mapSize[0]*self.mapBlockSize[0] - self.width()
        move_y = self.mapSize[1]* self.mapBlockSize[1] - self.height()
        self.canMove = True if move_x>0 else False, True if move_y>0 else False
        move_x = 0 if move_x > 0 else -move_x//2
        move_y = 0 if move_y > 0 else -move_y//2
        self.mapMove(move_x, move_y)
        for i in self.targetChoosedLayer:
            i.setGeometry(self.pointer_geo[i.mapId[0]][i.mapId[1]].geometry())

    #地图修改
    def modify(self, areaGroup, tTrack):
        # if tTrack == None:
        #     return
        newTrack = tTrack['track'].copy()
        cols = len(self.pointer_geo[0])
        rows = len(self.pointer_geo)
        direction = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        direction_ = ['top', 'right', 'bottom', 'left']
        if newTrack['usage'] == 'dw':
            try:
                x1, y1 = areaGroup[0].mapId
            except IndexError:
                return
            x2, y2 = areaGroup[-1].mapId
            dws = self.findChildren(DW)
            for i in dws:
                if  i.mapId[0] >= x1 and i.mapId[0] <= x2 and i.mapId[1] >= y1 and i.mapId[1] <= y2:
                    i.deleteLater()
            if newTrack['name'] == 'delete':
                return
            # ttdTrack = newTrack
            del tTrack['track']
            newTrack.update(tTrack)
            # tem_c = newTrack['track'].copy()
            # del newTrack['track']
            # newTrack.update(tem_c)
            for i in areaGroup:
                if int(resource.basicData['move'][newTrack['name']][self.pointer_geo[i.mapId[0]][i.mapId[1]].track['name']]) >= 99:
                    continue
                newTrack['mapId'] = i.mapId
                dw = DW(self, newTrack)
                dw.scale(resource.mapScaleList[self.mapScalePoint])
                dw.move(i.x(), i.y())
                # dw.updateByTrack(tTrack)
                dw.show()
        # elif newTrack['usage'] == 'build':
        #     for i in areaGroup:
        #         tem_dw = self.pointer_dw[i.mapId[0]][i.mapId[1]]
        #         if tem_dw:
        #             tem_dw.deleteLater()
        #             self.pointer_dw[i.mapId[0]][i.mapId[1]] = None
        #         if newTrack['name'] == 'sand':
        #             should = []
        #             for k1, k in enumerate(direction):
        #                 x, y = k[0] + i.mapId[0], k[1] + i.mapId[1]
        #                 if x < 0 or x >= rows or y < 0 or y >= cols:
        #                     continue
        #                 if self.pointer_geo[x][y].track['name'] not in ['sea', 'rocks', 'sand']:
        #                     should.append(direction_[k1])
        #             length = len(should)
        #             if length == 4 or length == 3 or length == 0:
        #                 continue
        #             elif length == 2:
        #                 if 'top' in should and 'bottom' in should:
        #                     continue
        #                 elif 'left' in should and 'right' in should:
        #                     continue
        #         i.change(track=newTrack)
        elif newTrack['usage'] in ['geo', 'build']:
            for i in areaGroup:
                tem_dw = self.pointer_dw[i.mapId[0]][i.mapId[1]]
                if tem_dw:
                    tem_dw.deleteLater()
                    self.pointer_dw[i.mapId[0]][i.mapId[1]] = None
                if newTrack['name'] == 'sand':
                    should = []
                    for k1, k in enumerate(direction):
                        x, y = k[0] + i.mapId[0], k[1] + i.mapId[1]
                        if x < 0 or x >= rows or y < 0 or y >= cols:
                            continue
                        if self.pointer_geo[x][y].track['name'] not in ['sea', 'rocks', 'sand']:
                            should.append(direction_[k1])
                    length = len(should)
                    if length == 4 or length == 3 or length == 0:
                        continue
                    elif length == 2:
                        if 'top' in should and 'bottom' in should:
                            continue
                        elif 'left' in should and 'right' in should:
                            continue
                i.change(track=newTrack)
            # return
            if newTrack['usage'] == 'geo':
                for i1, i in enumerate(self.pointer_geo):
                    for j1, j in enumerate(i):
                        if j.track['name'] == 'road':
                            should = []
                            for k1, k in enumerate(direction):
                                x, y = k[0]+i1, k[1]+j1
                                if x<0 or x >= rows or y<0 or y >= cols:
                                    continue
                                if self.pointer_geo[x][y].track['name'] in ['road', 'bridge']:
                                    should.append(direction_[k1])
                            length = len(should)
                            if length == 4:
                                j.change({'usage':'geo', 'name':'road', 'flag':'', 'action':'center'})
                            elif length == 3:
                                for p1 in direction_:
                                    if p1 not in should:
                                        j.change({'usage':'geo', 'name':'road', 'flag':'', 'action':'no-'+p1})
                                        break
                            elif length == 2:
                                if 'top' in should and 'bottom' in should:
                                    j.change({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'vertical'})
                                elif 'left' in should and 'right' in should:
                                    j.change({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'across'})
                                else:
                                    tem_dd = resource.find({'usage': 'geo', 'name': 'road', 'flag': '', 'action': should[0]+'-'+should[1]})
                                    if not tem_dd:
                                        j.change({'usage': 'geo', 'name': 'road', 'flag': '', 'action': should[1]+'-'+should[0]})
                                    else:
                                        j.change(track=tem_dd)
                            elif length == 1:
                                if should[0] in ['left', 'right']:
                                    j.change({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'across'})
                                else:
                                    j.change({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'vertical'})
                        elif j.track['name'] == 'bridge':
                            should = []
                            for k1, k in enumerate(direction):
                                x, y = k[0] + i1, k[1] + j1
                                if x < 0 or x >= rows or y < 0 or y >= cols:
                                    continue
                                if self.pointer_geo[x][y].track['name'] in ['road', 'bridge']:
                                    should.append(direction_[k1])
                            length = len(should)
                            if length in [0, 4]:
                                j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'})
                            elif length == 1:
                                if should[0] in ['left', 'right']:
                                    j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'})
                                else:
                                    j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'vertical'})
                            elif length == 2:
                                if 'left' in should and 'right' in should:
                                    j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'})
                                elif 'top' in should and 'bottom' in should:
                                    j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'vertical'})
                                else:
                                    j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'})
                            elif length == 3:
                                if 'left' in should and 'right' in should:
                                    j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'})
                                elif 'top' in should and 'bottom' in should:
                                    j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'vertical'})
                        elif j.track['name'] == 'sea':
                            should = []
                            for k1, k in enumerate(direction):
                                x, y = k[0] + i1, k[1] + j1
                                if x < 0 or x >= rows or y < 0 or y >= cols:
                                    continue
                                if self.pointer_geo[x][y].track['name'] not in ['sea', 'rocks', 'sand', 'river']:
                                    should.append(direction_[k1])
                            length = len(should)
                            if length == 4:
                                j.change({'usage':'geo', 'name':'sea', 'flag':'', 'action':'center'})
                            elif length == 3:
                                for p1 in direction_:
                                    if p1 not in should:
                                        j.change({'usage':'geo', 'name':'sea', 'flag':'', 'action':'no-'+p1})
                                        break
                            elif length == 2:
                                if 'top' in should and 'bottom' in should:
                                    j.change({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': 'across'})
                                elif 'left' in should and 'right' in should:
                                    j.change({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': 'vertical'})
                                else:
                                    tem_dd = resource.find({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': should[0]+'-'+should[1]})
                                    if not tem_dd:
                                        j.change({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': should[1]+'-'+should[0]})
                                    else:
                                        j.change(track=tem_dd)
                            elif length == 1:
                                j.change({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': should[0]})
                            elif length == 0:
                                j.change({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': ''})
                        elif j.track['name'] == 'river':
                            should = []
                            for k1, k in enumerate(direction):
                                x, y = k[0] + i1, k[1] + j1
                                if x < 0 or x >= rows or y < 0 or y >= cols:
                                    continue
                                if self.pointer_geo[x][y].track['name'] not in ['sea', 'rocks', 'river']:
                                    should.append(direction_[k1])
                            length = len(should)
                            if length == 4:
                                j.change({'action': 'center'})
                            elif length == 3:
                                for p1 in direction_:
                                    if p1 not in should:
                                        if p1 in ['left', 'right']:
                                            j.change({'action': 'across'})
                                        else:
                                            j.change({'action': 'vertical'})
                                        break
                            elif length == 2:
                                if 'top' in should and 'bottom' in should:
                                    j.change(
                                        {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'across'})
                                elif 'left' in should and 'right' in should:
                                    j.change(
                                        {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'vertical'})
                                else:
                                    tem_dd = resource.find(
                                        {'usage': 'geo', 'name': 'river', 'flag': '', 'action': should[0] + '-' + should[1]})
                                    if not tem_dd:
                                        j.change({'usage': 'geo', 'name': 'river', 'flag': '',
                                                                      'action': should[1] + '-' + should[0]})
                                    else:
                                        j.change(track=tem_dd)
                            elif length == 1:
                                if should[0] in ['left', 'right']:
                                    j.change(
                                        {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'vertical'})
                                else:
                                    j.change(
                                        {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'across'})
                            elif length == 0:
                                    j.change(
                                        {'usage': 'geo', 'name': 'plain', 'flag': ''})
                        elif j.track['name'] == 'sand':
                            should = []
                            for k1, k in enumerate(direction):
                                x, y = k[0] + i1, k[1] + j1
                                if x < 0 or x >= rows or y < 0 or y >= cols:
                                    continue
                                if self.pointer_geo[x][y].track['name'] not in ['sea', 'rocks', 'sand']:
                                    should.append(direction_[k1])
                            length = len(should)
                            if length == 4 or length == 3:
                                j.change(
                                    {'usage': 'geo', 'name': 'plain', 'flag': ''})
                            elif length == 2:
                                if 'top' in should and 'bottom' in should:
                                    j.change(
                                        {'usage': 'geo', 'name': 'plain', 'flag': ''})
                                elif 'left' in should and 'right' in should:
                                    j.change(
                                        {'usage': 'geo', 'name': 'plain', 'flag': ''})
                                else:
                                    tem_dd = resource.find(
                                        {'usage': 'geo', 'name': 'sand', 'flag': '', 'action': should[0] + '-' + should[1]})
                                    if not tem_dd:
                                        j.change({'usage': 'geo', 'name': 'sand', 'flag': '',
                                                                      'action': should[1] + '-' + should[0]})
                                    else:
                                        j.change(track=tem_dd)
                            elif length == 1:
                                j.change(
                                    {'usage': 'geo', 'name': 'sand', 'flag': '', 'action': should[0]})
                            elif length == 0:
                                j.change(
                                    {'usage': 'geo', 'name': 'plain', 'flag': ''})

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == 1 and not self.hasMove:
            if self.isTargetShowing:
                return
            self.hasCircle = a0.pos()
            # try:
            #     self.circle.setParent(self)
            # except AttributeError:
            #     pass
            self.circle.setParent(self)
            self.circle.setGeometry(a0.x(), a0.y(), 1, 1)
            self.circle.show()
        elif a0.button() == 2 and not self.hasCircle:
            self.hasMove = a0.pos()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == 1:
            if self.isTargetShowing:
                return
            self.circle.hide()
            self.circle.setParent(None)
            x2, y2 = a0.x(), a0.y()
            x1, y1 = self.hasCircle.x(), self.hasCircle.y()

            x1, x2 = (x1, x2) if x1<=x2 else (x2, x1)
            y1, y2 = (y1, y2) if y1<=y2 else (y2, y1)
            end = []
            for i in self.children():
                if hasattr(i, 'inRect'):
                    if i.inRect(x1, x2, y1, y2):
                        end.append(i)

            ##dw...
            if self.isTargetChoosing:
                for i in end:
                    if i not in self.circled:
                        self.circled.append(i)
            else:
                self.circled = end
            if self.isTargetChoosing:
                for i in self.targetChoosedLayer:
                    i.deleteLater()
                self.targetChoosedLayer = []
                for i in self.circled:
                    j = i.mapId
                    circle = QFrame(self)
                    circle.setStyleSheet('border-radius:5px;border:3px solid rgb(100, 100,200)')
                    circle.show()
                    circle.mapId = j
                    circle.setGeometry(self.pointer_geo[j[0]][j[1]].geometry())
                    self.targetChoosedLayer.append(circle)
            elif self.brother:
                # if self.brother.choosed:
                tem = self.brother.getChoosedData()
                if tem:
                    self.modify(end, tem)

            # print(len(end))
            self.hasCircle = False
        elif a0.button() == 2:
            self.hasMove = False

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.hasMove:
            x, y = self.hasMove.x()-a0.x(), self.hasMove.y()-a0.y()
            self.mapMove(-x, -y)
            self.hasMove = a0.pos()
        elif self.hasCircle:
            x1, x2 = (self.hasCircle.x() , a0.x()) if self.hasCircle.x() < a0.x() else (a0.x(), self.hasCircle.x())
            y1, y2 = (self.hasCircle.y() , a0.y()) if self.hasCircle.y() < a0.y() else (a0.y(), self.hasCircle.y())
            self.circle.setGeometry(x1, y1, x2-x1, y2-y1)

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if self.hasCircle or self.hasMove:
            return
        self.mapScale(True if a0.angleDelta().y()>0 else False)

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Return:
            end = []

            if self.targetChooseType == 'dw':
                for j in self.circled:
                    i = j.mapId
                    if self.pointer_dw[i[0]][i[1]]:
                        end.append(i)
            elif self.targetChooseType == 'build':
                for j in self.circled:
                    i = j.mapId
                    if self.pointer_geo[i[0]][i[1]].track['usage'] == 'build':
                        end.append(i)
            elif self.targetChooseType in ['area', 'dws', 'builds']:
                for j in self.circled:
                    end.append(j.mapId)

            type_ = 'toShowed' if self.isTargetShowing else 'toChoosed'

            post = toggleChooseEvent(type_, end)
            QCoreApplication.postEvent(self.parent().parent(), post)

            for i in self.targetChoosedLayer:
                i.deleteLater()
            self.circled = []
            self.targetChoosedLayer = []
            self.isTargetChoosing = False
            self.isTargetShowing = False
        elif a0.key() == Qt.Key_Escape:
            type_ = 'toShowed' if self.isTargetShowing else 'toChoosed'
            post = toggleChooseEvent(type_)
            QCoreApplication.postEvent(self.parent().parent(), post)
            # print(end)
            # self.parent().parent().targetChoosed()
            for i in self.targetChoosedLayer:
                i.deleteLater()
            self.targetChoosedLayer = []
            self.circled = []
            self.isTargetChoosing = False
        else:
            pass
        # a0.accept()
            # return super(EditMap, self).keyReleaseEvent(a0)

    def enterChooseMode(self, type, data=None):
        if type == 'toChoose':
            self.isTargetChoosing = True
            self.targetChooseType = data
        elif type == 'toShow':
            self.isTargetShowing = True
            for i in data:
                circle = QFrame(self)
                circle.setStyleSheet('border-radius:5px;border:3px solid rgb(100, 100,200)')
                circle.show()
                circle.mapId = i
                circle.setGeometry(self.pointer_geo[i[0]][i[1]].geometry())
                self.targetChoosedLayer.append(circle)

    def myUpdate(self):
        for j in self.findChildren(DW):
            if j:
                j.flush()
                j.myUpdate()

    def collectMap(self):
        map = {}
        map['map'] = []
        geos = iter(self.findChildren(Geo))
        for i in range(self.mapSize[1]):
            com = []
            for j in range(self.mapSize[0]):
                tem = geos.__next__()
                com.append(tem.track['base64'])
            map['map'].append(com)

        dws = []
        for i in self.findChildren(DW):
            # com = {}
            # com['hafuman'] = resource.findHafuman(i.track['base64'])
            # com['hafuman'] = i.track['base64']
            # com['axis'] = i.mapId
            # com['oil'] = i.oil
            # com['bullect'] = i.bullect
            # com['blood'] = i.bloodValue
            # com['occupied'] = i.occupied
            # dws.append(com)
            dws.append(i.makeTrack())
        map['dw'] = dws
        self.map.update(map)
        return self.map.copy()

class EditWin(QMainWindow):
    def __init__(self):
        super(EditWin, self).__init__()
        self.roles = {}
        self.JC = {}
        self.CF_ = []
        self.CF = []
        self.lines = {}
        self.basicData = {}
        self.basicData_ = {}
        self.targetChooseStatus = None
        self.tmpBasicKey = None
        self.vmapMode = None
        self.initUI()

    def initUI(self, mapName='default'):
        mapMenu = self.menuBar().addMenu('地图')
        mapMenu.addAction('打开').triggered.connect(self.skimMap)
        mapMenu.addSeparator()
        mapMenu.addAction('新建').triggered.connect(self.newMap)
        mapMenu.addAction('修改').triggered.connect(self.modifyMap)
        mapMenu.addAction('保存').triggered.connect(self.saveMap)

        mapMenu = self.menuBar().addMenu('素材')
        mapMenu.addAction('图片').triggered.connect(functools.partial(self.sourceCpu, 'images'))
        mapMenu.addAction('切换图片').triggered.connect(functools.partial(self.sourceCpu, 'swap'))
        mapMenu.addSeparator()
        mapMenu.addAction('音效').triggered.connect(functools.partial(self.sourceCpu, 'sounds'))

        mapMenu = self.menuBar().addMenu('规则')
        mapMenu.addAction('故事背景').triggered.connect(self.storyCpu)
        mapMenu.addAction('指挥官限制').triggered.connect(functools.partial(self.heroCpu, 'open'))
        mapMenu.addSeparator()
        mapMenu.addAction('制作游戏参数').triggered.connect(self.basicDataCpu)
        mapMenu.addAction('制作游戏加成').triggered.connect(self.backupCpu)
        mapMenu.addAction('制作台词').triggered.connect(self.linesCpu)
        mapMenu.addAction('制作触发器').triggered.connect(self.toggleCpu)
        mapMenu.addAction('制作事件').triggered.connect(self.toggleEventCpu)
        mapMenu.addSeparator()
        mapMenu.addAction('合并数据').triggered.connect(self.mergeCpu)
        mapMenu.addAction('最终整合').triggered.connect(self.ruleCpu)

        self.center = QWidget(self)
        self.tool = EditTool()
        self.tool.initUi(mainWin=self)
        self.vmap = EditMap(mapName, self.center, brother=self.tool)
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addWidget(self.tool)
        layout.addWidget(self.vmap)
        self.center.setLayout(layout)
        self.setCentralWidget(self.center)

        self.modeLSView = self.modeSkim = self.modeModify = None
        self.tmpView = None

    def skimMap(self):
        self.modeSkim = SkimWin()
        self.modeSkim.initUI(brother=self)
        self.modeSkim.setWindowModality(Qt.ApplicationModal)
        self.modeSkim.show()
        
    def newMap(self):
        self.modeModify = newWin()
        self.modeModify.initUI(brother=self)
        self.modeModify.setWindowModality(Qt.ApplicationModal)
        self.modeModify.show()

    def showLSView(self, data={}, type='loadings'):
        self.modeLSView = QWidget()
        if type == 'loadings':
            self.setWindowTitle('装载')
        else:
            self.setWindowTitle('计划补给')
        self.modeLSView.setWindowModality(QtCore.Qt.ApplicationModal)
        self.modeLSView.setFixedSize(250, 600)
        keys = resource.basicData['geo']['canbuild']['factory']
        keys_ = resource.basicData['geo']['canbuild']['shipyard']
        tem_end = []
        tem_end_ = []
        for i in resource.findAll({'usage': 'dw', 'flag': 'red', 'action': 'left'}):
            if i['name'] == 'delete':
                continue
            if resource.basicData['money']['classify'][i['name']] in keys or i['name'] in keys:
                money = resource.basicData['money']['money'][i['name']]
                text = resource.basicData['money']['chineseName'][i['name']] + '\t\t' + money + '$'
                tem_end.append((i['pixmap'], text, i['name'], float(money)))
            elif resource.basicData['money']['classify'][i['name']] in keys_ or i['name'] in keys_:
                money = resource.basicData['money']['money'][i['name']]
                text = resource.basicData['money']['chineseName'][i['name']] + '\t\t' + money + '$'
                tem_end_.append((i['pixmap'], text, i['name'], float(money)))
        tem_end = sorted(tem_end, key=lambda arg: arg[3])
        tem_end_ = sorted(tem_end_, key=lambda arg: arg[3])
        tem_end += tem_end_
        layout = QFormLayout()
        for i in tem_end:
            tem_btn = QPushButton(QIcon(i[0]), i[1])
            tem_btn.setStyleSheet("border:none;")
            tem_btn.setFocusPolicy(Qt.NoFocus)
            tem_spin = QSpinBox()
            tem_spin.setMaximum(120000)
            tem_spin.setSingleStep(int(i[3]))
            tem_spin.name = i[2]
            tem_spin.money = i[3]
            if i[2] in data:
                tem_spin.setValue(data[i[2]])
            layout.addRow(tem_btn, tem_spin)
        tem_btn_1 = QPushButton('保存')
        if self.tool:
            tem_btn_1.clicked.connect(functools.partial(self.tool.saveLS, self.modeLSView, type))
        layout.addWidget(tem_btn_1)
        self.modeLSView.setLayout(layout)
        self.modeLSView.show()

    def modifyMap(self, mapName=None):
        if not mapName:
            self.modeModify = newWin()
            self.modeModify.initUI(brother=self, mapName=self.vmap.map['name'])
            self.modeModify.setWindowModality(Qt.ApplicationModal)
            self.modeModify.show()
        else:
            self.modeModify = newWin()
            self.modeModify.initUI(brother=self, mapName=mapName)
            self.modeModify.setWindowModality(Qt.ApplicationModal)
            self.modeModify.show()

    def saveMap(self):
        tem_v = self.findChild(EditMap)
        tem_map = tem_v.collectMap()
        resource.saveMap(tem_map['name'], map=tem_map)

    def swapMap(self, name):
        # tem_v = self.findChild(VMap)
        # x, y = tem_v.x(), tem_v.y()
        # tem_v.deleteLater()
        # self.vmap = VMap()
        # self.vmap.initUI(name, self.center, brother=self.tool)
        # layout = QBoxLayout(QBoxLayout.LeftToRight)
        # layout.addWidget(self.tool)
        # layout.addWidget(self.vmap)
        # self.center.setLayout(layout)
        # self.setCentralWidget(self.center)
        # self.vmap.show()
        # self.vmap.move(x, y)

        self.center.deleteLater()
        self.center = QWidget(self)
        self.tool = EditTool()
        self.tool.initUi()
        self.vmap = EditMap(name, self.center, brother=self.tool)
        # self.vmap.initUI(name, self.center, brother=self.tool)
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addWidget(self.tool)
        layout.addWidget(self.vmap)
        self.center.setLayout(layout)
        self.vmap.move(self.tool.width(), 0)
        self.setCentralWidget(self.center)

    def linesCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        path = 'maps/'+self.vmap.map['name']+'/lines.json'
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)
        self.tmpView = linesEditWin(path)
        self.tmpView.setWindowTitle('台词设计')
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()
        # print(key, data)
        # '''
        #     开战前
        #     主城附近，
        #     收入支出，
        #     故事背景
        #     局势，
        #     单位：侦查，补给，下潜，隐身，计划补给，体力，油量，弹药，攻击范围，所在地形，安全系数+可攻击目标，
        #     随机
        # '''
        # key1 = ['随机', '开战前', '主城附近', '收入不足', '收入充足', '收入过多', '支出过多', '支出过少', \
        #         '故事背景', '局势', '侦查到', '侦查没到', '下潜没被发现', '下潜被发现', '隐身被发现', '隐身没被发现', '计划补给', \
        #         '规模低', '规模充足', '油量低', '油量充足', '弹药低', '弹药充足', '近战', '远程', '移动攻击',  \
        #         '单位被困且危险', '单位被困但安全', '单位安全', '可攻击目标少', '可攻击目标多']
        # key2 = ['random', 'beforebattle', 'nearhead', 'smallsalary', 'enoughsalary', 'muchsalary', \
        #         'storybackground', 'situation', 'watched', 'watching', 'diving', 'dived', 'stealthing', 'stealthed', \
        #         'plansupply', 'lessguimo', 'enoughguimo', 'lessoil', 'enoughoil', 'lessbullect', 'enoughbullect', \
        #         'shortrange', 'longrange', 'attackaftermove', 'trapped_danger', 'trapped_safe', 'untrapped', 'moretargets', 'lesstargets']
        #
        # for i in resource.findAll({'usage':'geo'}):
        #     if i['name'] not in key2:
        #         key2.append(i['name'])
        #         key1.append(resource.basicData['geo']['chineseName'][i['name']])
        # for i in resource.findAll({'usage':'build', 'flag':'red'}):
        #     key2.append(i['name'])
        #     key1.append(resource.basicData['geo']['chineseName'][i['name']])
        # for i in resource.findAll({'usage': 'dw', 'action': 'left', 'flag': 'red'}):
        #     key2.append(i['name'])
        #     key1.append(resource.basicData['money']['chineseName'][i['name']])
        #
        # if key == 'skim_double':
        #     if self.tmpView:
        #         try:
        #             self.tmpView.deleteLater()
        #         except RuntimeError:
        #             pass
        #     self.tmpView = QWidget()
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     self.tmpView.name = list(self.lines.keys())[data.row()]
        #     self.tmpView.data = self.lines[self.tmpView.name]
        #     self.tmpView.setWindowTitle('台词《'+self.tmpView.name+'》')
        #     # print(self.lines.keys())
        #     layout1 = QHBoxLayout()
        #     tem = QComboBox(self.tmpView)
        #     tem.before = key1[0]
        #     tem.isconnected = True
        #     tem.currentIndexChanged.connect(functools.partial(self.linesCpu, 'add_modify'))
        #     tem.addItems(key1)
        #     layout1_1 = QHBoxLayout()
        #     layout1_1.addWidget(tem)
        #     tem = QPushButton('上一个', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', 1))
        #     layout1_1.addWidget(tem)
        #     tem = QPushButton('下一个', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', -1))
        #     layout1_1.addWidget(tem)
        #     layout1.addLayout(layout1_1)
        #     tem = QPushButton('ok', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_ok'))
        #     layout1.addWidget(tem)
        #     layout = QHBoxLayout()
        #     layout.addLayout(layout1)
        #     tem = QTextEdit(self.tmpView)
        #     # tem.setReadOnly(True)
        #     layout.addWidget(tem)
        #     self.tmpView.setLayout(layout)
        #     self.tmpView.show()
        #     self.tmpView.findChild(QComboBox).setCurrentIndex(0)
        #
        # elif key == 'skim':
        #     if self.tmpView:
        #         try:
        #             self.tmpView.deleteLater()
        #         except RuntimeError:
        #             pass
        #     self.tmpView = QWidget()
        #     self.tmpView.setWindowTitle('浏览')
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     layout = QVBoxLayout()
        #     tem = QListWidget()
        #     tem.addItems(self.lines.keys())
        #     self.tmpView = QListWidget()
        #     self.tmpView.setWindowTitle('浏览')
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     self.tmpView.addItems(self.lines.keys())
        #     print(self.lines.keys())
        #     self.tmpView.show()
        #     self.tmpView.doubleClicked.connect(functools.partial(self.linesCpu, 'skim_double'))
        # elif key == 'delete':
        #     pass
        #
        # elif key == 'add':
        #     if self.tmpView:
        #         try:
        #             self.tmpView.deleteLater()
        #         except RuntimeError:
        #             pass
        #     self.tmpView = QWidget()
        #     self.tmpView.setWindowTitle('添加台词')
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     end = {}
        #     for i in key2:
        #         end[i] = []
        #     self.tmpView.data = end
        #     layout1 = QHBoxLayout()
        #     tem = QLineEdit(self.tmpView)
        #     tem.setPlaceholderText('名称')
        #     layout1.addWidget(tem)
        #     tem = QComboBox(self.tmpView)
        #     tem.before = key1[0]
        #     tem.isconnected = True
        #     tem.currentIndexChanged.connect(functools.partial(self.linesCpu, 'add_modify'))
        #     tem.addItems(key1)
        #     layout1_1 = QHBoxLayout()
        #     layout1_1.addWidget(tem)
        #     tem = QPushButton('上一个', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', 1))
        #     layout1_1.addWidget(tem)
        #     tem = QPushButton('下一个', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', -1))
        #     layout1_1.addWidget(tem)
        #     layout1.addLayout(layout1_1)
        #     tem = QPushButton('ok', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_ok'))
        #     layout1.addWidget(tem)
        #     layout = QHBoxLayout()
        #     layout.addLayout(layout1)
        #     tem = QTextEdit(self.tmpView)
        #     # tem.setReadOnly(True)
        #     layout.addWidget(tem)
        #     self.tmpView.setLayout(layout)
        #     self.tmpView.show()
        #
        # elif key == 'add_updown':
        #     com = self.tmpView.findChild(QComboBox)
        #     com.isconnected = False
        #     view = self.tmpView.findChild(QTextEdit)
        #     id = com.currentText()
        #     for i1, i in enumerate(key1):
        #         if i == id:
        #             break
        #     com.before = id
        #     id = key2[i1]
        #     self.tmpView.data[id] = view.toPlainText().split('\n')
        #     if data == 1:
        #         if com.currentIndex() == 0:
        #             return
        #         com.setCurrentIndex(com.currentIndex()-1)
        #         text = ''
        #         for i in self.tmpView.data[key2[com.currentIndex()]]:
        #             text += '\n' + i
        #         view.setText(text)
        #     else:
        #         if com.currentIndex() == len(key2) -1:
        #             return
        #         com.setCurrentIndex(com.currentIndex()+1)
        #         text = ''
        #         for i in self.tmpView.data[key2[com.currentIndex()]]:
        #             text += '\n' + i
        #         view.setText(text)
        #     # com.currentIndexChanged.disconnect(functools.partial(self.linesCpu, 'add_modify'))
        #
        # elif key == 'add_modify':
        #     com = self.tmpView.findChild(QComboBox)
        #     view = self.tmpView.findChild(QTextEdit)
        #     if not com.isconnected:
        #         com.isconnected = True
        #         return
        #     id_ = com.before
        #     for i1, i in enumerate(key1):
        #         if i == id_:
        #             break
        #     try:
        #         self.tmpView.data[key2[i1]] = view.toPlainText().split('\n')
        #     except AttributeError:
        #         return
        #     id = com.currentText()
        #     for i1, i in enumerate(key1):
        #         if i == id:
        #             break
        #     com.before = id
        #     id = key2[i1]
        #     text = ''
        #     for i in self.tmpView.data[id]:
        #         text +=  i +'\n'
        #     view.setText(text)
        #
        # elif key == 'add_ok':
        #     id = self.tmpView.findChild(QComboBox).currentText()
        #     for i1, i in enumerate(key1):
        #         if i == id:
        #             break
        #     id = key2[i1]
        #     self.tmpView.data[id] = self.tmpView.findChild(QTextEdit).toPlainText().split('\n')
        #     #%%%%%%
        #     for i1, i in self.tmpView.data.items():
        #         newData = []
        #         for j in i:
        #             if j != '':
        #                 newData.append(j)
        #         self.tmpView.data[i1] = newData
        #     print(self.tmpView.data)
        #     if self.tmpView.findChild(QLineEdit):
        #         self.lines[self.tmpView.findChild(QLineEdit).text()] = self.tmpView.data
        #     else:
        #         self.lines[self.tmpView.name] = self.tmpView.data
        #     self.tmpView.deleteLater()
        #     resource.saveMap(self.vmap.map['name'], lines=self.lines)
        # # elif key == 'zz':
        # #     if not self.roles:
        # #         return
        # #     if self.tmpView:
        # #         try:
        # #             self.tmpView.deleteLater()
        # #         except RuntimeError:
        # #             pass
        # #     self.tmpView = QWidget()
        # #     self.tmpView.setWindowTitle('组装台词')
        # #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        # #     layout1 = QVBoxLayout()
        # #     items = self.roles.keys()
        # #     for i in items:
        # #         tem = QPushButton('    ', self.tmpView)
        # #         tem.setStyleSheet('background-color:'+str(i)+';')
        # #         layout1.addWidget(tem)
        # #     tem = QPushButton('ok', self.tmpView)
        # #     tem.clicked.connect(functools.partial(self.linesCpu, 'zz_ok'))
        # #     layout1.addWidget(tem)
        # #     layout2 = QVBoxLayout()
        # #     for i in items:
        # #         tem = QComboBox(self.tmpView)
        # #         tem.addItem('')
        # #         tem.addItems(self.lines.keys())
        # #         tem.flag = i
        # #         layout2.addWidget(tem)
        # #     layout = QHBoxLayout()
        # #     layout.addLayout(layout1)
        # #     layout.addLayout(layout2)
        # #     self.tmpView.setLayout(layout)
        # #     self.tmpView.show()
        # # elif key == 'zz_ok':
        # #     items = self.tmpView.findChildren(QComboBox)
        # #     for i in items:
        # #         self.roles[i.flag] = i.currentText()
        # #     self.tmpView.deleteLater()

    def basicDataCpu(self, data=None):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        # path = 'maps/' + self.vmap.map['name'] + '/lines.json'
        # if not os.path.exists(path):
        #     with open(path, 'w') as f:
        #         json.dump({}, f)
        self.tmpView = bscEditWin(self.vmap.map['name'])
        self.tmpView.setWindowTitle('参数设置')
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()
        # if key == 'skim':
        #     if self.tmpView:
        #         try:
        #             self.tmpView.deleteLater()
        #         except RuntimeError:
        #             pass
        #     self.tmpView = QWidget()
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     self.tmpView.setWindowTitle('备用参数')
        #     layout = QVBoxLayout()
        #     tem = QListWidget(self.tmpView)
        #     if os.path.exists('maps/'+self.vmap.map['name']+'/basicInfo_.json'):
        #         with open('maps/'+self.vmap.map['name']+'/basicInfo_.json', 'r') as f:
        #             self.basicData_ = json.load(f)
        #         tem.addItems(list(self.basicData_.keys()))
        #     else:
        #         with open('maps/' + self.vmap.map['name'] + '/basicInfo_.json', 'w') as f:
        #             json.dump({}, f)
        #     tem.doubleClicked.connect(functools.partial(self.basicDataCpu, 'double'))
        #     layout.addWidget(tem)
        #     layout_ = QHBoxLayout()
        #     tem = QPushButton('删除', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.basicDataCpu, 'delete'))
        #     layout_.addWidget(tem)
        #     layout_.addSpacing(30)
        #     layout.addWidget(QLineEdit(self.tmpView))
        #     tem = QPushButton('添加', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.basicDataCpu, 'add'))
        #     layout_.addWidget(tem)
        #     layout.addLayout(layout_)
        #     self.tmpView.setLayout(layout)
        #     self.tmpView.show()
        #
        # elif key == 'basic':
        #     # self.isTmpBasicDataBak = False
        #     if self.tmpView:
        #         try:
        #             self.tmpView.deleteLater()
        #         except RuntimeError:
        #             pass
        #     if not os.path.exists('maps/'+self.vmap.map['name']+'/basicInfo.json'):
        #         shutil.copy('resource/basicInfo.json', 'maps/'+self.vmap.map['name']+'/basicInfo.json')
        #     self.tmpView = basicEditW('maps/'+self.vmap.map['name']+'/basicInfo.json')
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     self.tmpView.setWindowTitle('基本参数')
        #     self.tmpView.show()
        #
        # elif key == 'delete':
        #     tem = self.tmpView.findChild(QListWidget)
        #     data = tem.currentIndex().row()
        #     # QModelIndex.row()
        #     print(data)
        #     if data < 0:
        #         return
        #     del self.basicData_[tem.item(data).text()]
        #     tem.takeItem(data)
        #     self.basicDataCpu('save')
        # elif key == 'add':
        #     if self.tmpBasicKey != None:
        #         with open('resource/tmp/basicInfo.json', 'r') as f:
        #             self.basicData_[self.tmpBasicKey] = json.load(f)
        #     title = self.tmpView.findChild(QLineEdit).text()
        #     if title in self.basicData_ or title == '':
        #         return
        #     self.tmpBasicKey = title
        #     self.basicData_[title] = {}
        #     with open('resource/tmp/basicInfo.json', 'w') as f:
        #         json.dump(self.basicData_[title], f)
        #     self.tmpView.deleteLater()
        #     self.tmpView = basicEditW('resource/tmp/basicInfo.json')
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     self.tmpView.setWindowTitle('添加备用配置')
        #     self.tmpView.show()
        #
        # elif key == 'double':
        #     if self.tmpBasicKey != None:
        #         with open('resource/tmp/basicInfo.json', 'r') as f:
        #             self.basicData_[self.tmpBasicKey] = json.load(f)
        #     if data == -1:
        #         return
        #     text = self.tmpView.findChild(QListWidget).item(data).text()
        #     self.tmpBasicKey = text
        #     with open('resource/tmp/basicInfo.json', 'w') as f:
        #         json.dump(self.basicData_[text], f)
        #     self.tmpView.deleteLater()
        #     # with open('resource/tmp/basicInfo.json', 'w') as f:
        #     #     json.dump(self.basicData_[text], f)
        #     self.tmpView = basicEditW('resource/tmp/basicInfo.json')
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     self.tmpView.setWindowTitle('备用参数')
        #
        # elif key == 'save':
        #     if self.tmpBasicKey != None:
        #         with open('resource/tmp/basicInfo.json', 'r') as f:
        #             self.basicData_[self.tmpBasicKey] = json.load(f)
        #     # for i in list(self.basicData_.keys()):
        #     #     for j in list(self.basicData_[i].keys()):
        #     #         for k in list(self.basicData_[i][j].keys()):
        #     #             if self.basicData_[i][j][k] == '':
        #     #                 del self.basicData_[i][j][k]
        #     #                 print(333)
        #     #         if self.basicData_[i][j] == {}:
        #     #             del self.basicData_[i][j]
        #     #             print(2222)
        #         # if self.basicData_[i] == {}:
        #         #     del self.basicData_[i]
        #         #     print('fsd111')
        #
        #     with open('maps/'+self.vmap.map['name']+'/basicInfo_.json', 'w') as f:
        #         json.dump(self.basicData_, f)

    def backupCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        path = 'maps/' + self.vmap.map['name'] + '/backup.json'
        self.tmpView = backupEditWin(path)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()

    def toggleCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        path = 'maps/' + self.vmap.map['name'] + '/toggles.json'
        self.tmpView = toggleEditWin(path, self)
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()

    def toggleEventCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        path = 'maps/' + self.vmap.map['name'] + '/toggleEvents.json'
        self.tmpView = toggleEventEditWin(path, self)
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()

    def sourceCpu(self, key):
        if key == 'swap':
            if self.tmpView:
                try:
                    self.tmpView.deleteLater()
                except RuntimeError:
                    pass
            resource.initMap(self.vmap.map['name'])
            self.swapMap(self.vmap.map['name'])
        elif key == 'sounds':
            file = QFileDialog.getExistingDirectory(self, '选择音效所在文件夹')
            resource.saveMap(self.vmap.map['name'], soundPath=file)
        elif key == 'images':
            file = QFileDialog.getExistingDirectory(self, '选择图片所在文件夹')
            resource.saveMap(self.vmap.map['name'], imagePath=file)

    def storyCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        path = 'maps/' + self.vmap.map['name'] + '/stories.json'
        self.tmpView = storyEditWin(path)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()

    #--> 没选则此势力没有指挥官 <--#
    def heroCpu(self, key):
        path = 'maps/' + self.vmap.map['name'] + '/heros.json'
        if key == 'open':
            if self.tmpView:
                try:
                    self.tmpView.deleteLater()
                except RuntimeError:
                    pass
            self.tmpView = QWidget()
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            if not os.path.exists(path):
                tem_data = {}
                with open(path, 'w') as f:
                    json.dump({}, f)
            else:
                with open(path, 'r') as f:
                    tem_data = json.load(f)
            layout = QVBoxLayout()
            heros = []
            for i in resource.findAll({'usage':'hero', 'action':'head'}):
                heros.append(i['name'])
            for i in ['red', 'blue', 'green', 'yellow']:
                layout1 = QHBoxLayout()
                layout1.addWidget(QLabel(i, self.tmpView))
                for j in heros:
                    tem = QCheckBox(j, self.tmpView)
                    tem.data = i
                    if i in tem_data:
                        if j in tem_data[i]:
                            tem.setChecked(True)
                    layout1.addWidget(tem)
                layout.addLayout(layout1)
            tem = QPushButton('save', self.tmpView)
            tem.clicked.connect(functools.partial(self.heroCpu, 'save'))
            layout.addWidget(tem)
            self.tmpView.setLayout(layout)
            self.tmpView.show()

        elif key == 'save':
            end = {'red':[], 'blue':[], 'green':[], 'yellow':[]}
            for i in self.tmpView.findChildren(QCheckBox):
                if i.isChecked():
                    end[i.data].append(i.text())
            for i, j in end.items():
                if not j:
                    del end[i]
            with open(path, 'w') as f:
                json.dump(end, f)
            self.tmpView.deleteLater()

    def ruleCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        self.tmpView = ruleEditWin(self.vmap.map['name'])
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()

    ##---------------------懒啊-------------------------#
    def mergeCpu(self):
        ## lines, basicData
        with open('maps/'+self.vmap.map['name']+'/lines.json', 'r') as f:
            tem = json.load(f)
        with open('resource/lines.json', 'r') as f:
            tem_ = json.load(f)

        if 'default' not in tem:
            tem['default'] = tem_['default']
        else:
            for i, j in tem_['default'].items():
                if i not in tem['default']:
                    tem[i] = j

        with open('maps/'+self.vmap.map['name']+'/lines.json', 'w') as f:
            json.dump(tem, f)

        with open('maps/'+self.vmap.map['name']+'/basicInfo.json', 'r') as f:
            tem = json.load(f)
        with open('resource/basicInfo.json', 'r') as f:
            tem_ = json.load(f)
        if 'default' not in tem:
            tem['default'] = tem_['default']
        else:
            for i1, i in tem_['default'].items():
                if i1 not in tem['default']:
                    tem[i] = i
                else:
                    for j1, j in tem_['default'][i1].items():
                        if j1 not in tem['default'][i1]:
                            tem['default'][j1] = j
                        else:
                            for k1, k in tem_['default'][i1][j1].items():
                                if k1 not in tem_['default'][i1][j1]:
                                    tem_['default'][i1][j1][k1] = k

        with open('maps/'+self.vmap.map['name']+'/basicInfo.json', 'w') as f:
            json.dump(tem, f)


    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() in [Qt.Key_Escape, Qt.Key_Return] and self.vmapMode != None:
            self.vmap.keyReleaseEvent(a0)
        else:
            return super(EditWin, self).keyReleaseEvent(a0)

    def event(self, event: QtCore.QEvent) -> bool:
        if event.type() == toggleChooseEvent.idType:
            if event.type_ == 'toChoose':
                self.vmap.enterChooseMode(event.type_, event.data)
                self.tmpView.hide()
                self.vmapMode = event.type_
                self.findChild(QMenuBar).setEnabled(False)
            elif event.type_ == 'toShow':
                self.vmap.enterChooseMode(event.type_, event.data)
                self.tmpView.hide()
                self.vmapMode = event.type_
                self.findChild(QMenuBar).setEnabled(False)
            elif event.type_ == 'toChoosed':
                print(event.data, 'server')
                if event.data:
                    self.tmpView.choosed(event.data)
                self.tmpView.show()
                self.vmapMode = None
                self.findChild(QMenuBar).setEnabled(True)
            elif event.type_ == 'toShowed':
                self.tmpView.show()
                self.vmapMode = None
                self.findChild(QMenuBar).setEnabled(True)
        return super(EditWin, self).event(event)


##nav
class newWin(QWidget):
    def initUI(self, brother=None, mapName=None, winSize=(600, 400)):
        '''
        :param brother:
        :param mapName: 无名则为newMap
        :param winSize:
        :return:
        '''
        self.mapName = mapName
        self.map = {}
        self.isNewMap = True if mapName == None else False
        if self.mapName == None:
            self.mapName = hashlib.md5(str(time.time_ns()).encode()).hexdigest()[:8]
        else:
            self.mapName = mapName
        self.map = resource.makeMap(self.mapName, '地图描述')
        self.mapPriName = self.mapName if self.isNewMap else mapName
        # print(self.mapPriName)
        self.setWindowTitle('新建地图' if self.isNewMap else '修改地图')
        self.setFixedSize(winSize[0], winSize[1])
        self.brother = brother

        frame1 = QFrame()
        frame1.setFixedWidth(winSize[0]//5*2)
        self.name_ = QLineEdit(self.mapName, frame1)
        self.width_ = QSpinBox(frame1)
        self.width_.setRange(4, 100)
        self.width_.setValue(10)
        self.height_ = QSpinBox(frame1)
        self.height_.setRange(4, 100)
        self.height_.setValue(10)
        self.select_ = QComboBox()
        tem_list = resource.findAll({'usage':'geo'})
        tem_list_2 = ['random']
        for i in tem_list:
            if i['name'] not in tem_list_2:
                tem_list_2.append(i['name'])
        self.select_.addItems(tem_list_2)
        btn_preview = QPushButton('预览')
        btn_preview.clicked.connect(self.preView)
        btn_ok = QPushButton('OK')
        btn_ok.clicked.connect(self.comfirm)
        btn_delete = QPushButton('删除地图')
        btn_delete.setEnabled(not self.isNewMap)
        btn_delete.clicked.connect(self.deleteMap)
        self.text_dsc = QTextEdit()
        layout1 = QFormLayout()
        layout1.addRow('名称(唯一标识)', self.name_)
        layout1.addRow('宽度', self.width_)
        layout1.addRow('高度', self.height_)
        layout1.addRow('填充类型', self.select_)
        layout1.addRow('地图描述', self.text_dsc)
        layout1.addRow('删除地图', btn_delete)
        layout1.addRow(btn_preview, btn_ok)
        frame1.setLayout(layout1)

        area2 = QScrollArea(self)
        self.area = area2
        frame2 = miniVMap()
        frame2.initUI(mapName, area2, self.map)
        # frame2.setFixedSize(frame2.width(),frame2.height())
        area2.setWidget(frame2)

        layout = QGridLayout()
        layout.addWidget(frame1,0, 1, 1, 1)
        layout.addWidget(area2, 0, 0, 1, 1)
        self.time = time.time()


        # self.message = QMessageBox.information(self,'提示', '地图名称重复')

        self.setLayout(layout)

    def preView(self):
        title = self.name_.text()
        self.mapName = title
        tem_child = self.findChild(miniVMap)
        if tem_child:
            tem_child.deleteLater()
        frame2 = miniVMap()
        self.map = resource.makeMap(title, self.text_dsc.toPlainText(), self.select_.currentText(), (int(self.width_.text()), int(self.height_.text())))

        frame2.initUI(title, self.area, self.map)
        self.area.setWidget(frame2)

    def deleteMap(self):
        resource.deleteMap(self.mapName)

    def comfirm(self):
        # if self.isNewMap:
        nowName = self.findChild(QLineEdit).text()
        if nowName == 'default' or nowName == '':
            return
        self.mapName = nowName
        # print(self.mapPriName, self.mapName)
        resource.saveMap(self.mapPriName, newName=self.mapName, map=self.map)
        if self.brother:
            self.brother.swapMap(self.mapName)
            self.close()
        # else:
        #     self.map['name'] = self.name_.text()
        #     resource.saveMap(self.map, self.mapPriName)
        #     if self.brother:
        #         self.brother.swapMap(self.map['name'])
        #         self.close()

##nav
class SkimWin(QWidget):
    def initUI(self, winSize=(600, 400), brother=None, isModify=False):
        self.isModify = isModify
        self.mapName = 'default'
        self.setWindowTitle('浏览地图(双击选择)')
        self.setFixedSize(winSize[0], winSize[1])
        self.brother = brother
        area1 = QScrollArea(self)
        frame1 = QFrame()
        frame1.setFixedWidth(winSize[0]//2)
        layout1 = QBoxLayout(QBoxLayout.TopToBottom)
        for i in resource.getAllMaps():
            tem_label = QPushButton(i['name'])
            tem_label.setStyleSheet('border:none')
            tem_label.setFont(QFont('宋体', 20))
            tem_label.pressed.connect(functools.partial(self.choose, tem_label))
            layout1.addWidget(tem_label,alignment=QtCore.Qt.AlignLeft)
        frame1.setLayout(layout1)
        area1.setWidget(frame1)

        area2 = QScrollArea(self)
        self.area = area2
        frame2 = miniVMap()
        frame2.initUI('default', area2)
        # frame2.setFixedSize(frame2.width(),frame2.height())
        area2.setWidget(frame2)
        # area2.setFixedSize(winSize[0]//4, winSize[1]//4)

        frame3 = QLabel(resource.findMap('default')['dsc'])
        frame3.setFixedHeight(winSize[1]//2)
        self.dec_label = frame3

        layout = QGridLayout()
        layout.addWidget(area1,0, 1, 2, 1)
        layout.addWidget(area2, 0, 0, 1, 1)
        layout.addWidget(frame3, 1, 0, 1, 1)
        self.time = time.time()

        self.setLayout(layout)

    def choose(self, data):
        if time.time() - self.time < 0.2 and data.text() == self.mapName:
            if self.brother:
                if self.isModify:
                    self.brother.modifyMap(data.text())
                    self.close()
                else:
                    self.brother.swapMap(data.text())
                    self.close()
        else:
            self.time = time.time()
            if self.mapName == data.text():
                return
            self.mapName = data.text()
            tem_child = self.findChild(miniVMap)
            if tem_child:
                tem_child.deleteLater()
            frame2 = miniVMap()
            frame2.initUI(data.text(), self.area)
            self.area.setWidget(frame2)
            map = resource.findMap(data.text())
            if map:
                self.dec_label.setText(map['dsc'])

##%%台词模板%% or 无模板
class linesEditWin(QWidget):
    def __init__(self, file):
        super(linesEditWin, self).__init__()
        self.key1 = ['随机', '开战前', '主城附近', '收入不足', '收入充足', '收入过多', '支出过多', '支出过少', \
                '故事背景', '局势', '侦查到', '侦查没到', '下潜没被发现', '下潜被发现', '隐身被发现', '隐身没被发现', '计划补给', \
                '规模低', '规模充足', '油量低', '油量充足', '弹药低', '弹药充足', '近战', '远程', '移动攻击', \
                '单位被困且危险', '单位被困但安全', '单位安全', '可攻击目标少', '可攻击目标多']
        self.key2 = ['random', 'beforebattle', 'nearhead', 'smallsalary', 'enoughsalary', 'muchsalary', \
                'storybackground', 'situation', 'watched', 'watching', 'diving', 'dived', 'stealthing', 'stealthed', \
                'plansupply', 'lessguimo', 'enoughguimo', 'lessoil', 'enoughoil', 'lessbullect', 'enoughbullect', \
                'shortrange', 'longrange', 'attackaftermove', 'trapped_danger', 'trapped_safe', 'untrapped',
                'moretargets', 'lesstargets']

        for i in resource.findAll({'usage': 'geo'}):
            if i['name'] not in self.key2:
                self.key2.append(i['name'])
                self.key1.append(resource.basicData['geo']['chineseName'][i['name']])
        for i in resource.findAll({'usage': 'build', 'flag': 'red'}):
            self.key2.append(i['name'])
            self.key1.append(resource.basicData['geo']['chineseName'][i['name']])
        for i in resource.findAll({'usage': 'dw', 'action': 'left', 'flag': 'red'}):
            self.key2.append(i['name'])
            self.key1.append(resource.basicData['money']['chineseName'][i['name']])
        self.data = {}
        self.nowName = None
        for i in self.key2:
            self.data[i] = []
        self.path = file
        with open(file, 'r') as f:
            self.lines = json.load(f)
        self.initUI()
        self.openEle(False)

    def initUI(self):
        tem = QListWidget(self)
        tem.addItems(self.lines.keys())
        tem.doubleClicked.connect(self.linesDouble)
        tem.itemClicked.connect(self.linesDouble)
        layout1 = QVBoxLayout()
        layout1.addWidget(tem)
        layout11 = QHBoxLayout()
        tem = QPushButton('delete', self)
        tem.clicked.connect(self.linesDelete)
        layout11.addWidget(tem)
        tem = QLineEdit(self)
        tem.setPlaceholderText('名称')
        layout11.addWidget(tem)
        tem = QPushButton('add', self)
        tem.clicked.connect(self.linesAdd)
        layout11.addWidget(tem)
        tem = QPushButton('rename', self)
        tem.clicked.connect(self.linesRename)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout2 = QVBoxLayout()
        tem = QComboBox(self)
        tem.before = self.key1[0]
        tem.isconnected = True
        tem.currentIndexChanged.connect(self.modify)
        tem.addItems(self.key1)
        layout2.addWidget(tem)
        tem = QPushButton('上一个(alt+&q)', self)
        tem.clicked.connect(functools.partial(self.upOrDown, 1))
        layout2.addWidget(tem)
        tem = QPushButton('下一个(alt+&w)', self)
        tem.clicked.connect(functools.partial(self.upOrDown, -1))
        layout2.addWidget(tem)
        tem = QPushButton('save(ctrl+s)', self)
        tem.setShortcut('ctrl+s')
        tem.clicked.connect(self.save)
        layout2.addWidget(tem)
        layout = QHBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        tem = QTextEdit(self)
        # tem.setReadOnly(True)
        layout.addWidget(tem)
        self.setLayout(layout)
        self.show()

    def upOrDown(self, data):
        com = self.findChild(QComboBox)
        com.isconnected = False
        view = self.findChild(QTextEdit)
        id = com.currentText()
        for i1, i in enumerate(self.key1):
            if i == id:
                break
        com.before = id
        id = self.key2[i1]
        self.data[id] = view.toPlainText().split('\n')
        if data == 1:
            if com.currentIndex() == 0:
                return
            com.setCurrentIndex(com.currentIndex()-1)
            text = ''
            for i in self.data[self.key2[com.currentIndex()]]:
                text += '\n' + i
            view.setText(text)
        else:
            if com.currentIndex() == len(self.key2) -1:
                return
            com.setCurrentIndex(com.currentIndex()+1)
            text = ''
            for i in self.data[self.key2[com.currentIndex()]]:
                text += '\n' + i
            view.setText(text)

    def modify(self):
        com = self.findChild(QComboBox)
        view = self.findChild(QTextEdit)
        if not com.isconnected:
            com.isconnected = True
            return
        id_ = com.before
        for i1, i in enumerate(self.key1):
            if i == id_:
                break
        try:
            self.data[self.key2[i1]] = view.toPlainText().split('\n')
        except AttributeError:
            return
        id = com.currentText()
        for i1, i in enumerate(self.key1):
            if i == id:
                break
        com.before = id
        id = self.key2[i1]
        text = ''
        for i in self.data[id]:
            text +=  i +'\n'
        view.setText(text)

    def openEle(self, should=True):
        # if should:
        self.findChild(QComboBox).setEnabled(should)
        tem = self.findChildren(QPushButton)
        for i in tem[-3:]:
            i.setEnabled(should)
        # QComboBox.setEnabled()

    def linesDouble(self, data:None):
        self.openEle(True)
        tem = self.findChild(QListWidget)
        tem.current = tem.currentItem()
        tem.index = tem.currentIndex().row()
        tem_ = tem.currentItem()
        if tem_.text() == self.nowName:
            return
        self.nowName = tem_.text()
        self.data = self.lines[tem_.text()]
        self.findChild(QComboBox).setCurrentIndex(0)
        text = ''
        tem_d = self.findChild(QComboBox).currentText()
        for i1, i in enumerate(self.key1):
            if i == tem_d:
                break
        for i in self.data[self.key2[i1]]:
            text += i +'\n'
        self.findChild(QTextEdit).setText(text)

    def linesDelete(self):
        tem = self.findChild(QListWidget)
        item = tem.current
        text = item.text()
        if text not in self.lines:
            return
        del self.lines[text]
        tem.takeItem(tem.index)

    def linesAdd(self):
        tem = self.findChild(QLineEdit)
        if tem.text() == '' or tem.text() in self.lines:
            return
        end = {}
        for i in self.key2:
            end[i] = []
        self.lines[tem.text()] = end
        self.findChild(QListWidget).addItem(QListWidgetItem(tem.text()))
        self.nowName = tem.text()
        self.findChild(QTextEdit).setText('')
        self.openEle(True)

    def linesRename(self):
        tem = self.findChild(QLineEdit)
        tem_ = self.findChild(QListWidget)
        if tem.text() == '' or self.nowName == None:
            return
        self.lines[tem.text()] = self.lines[self.nowName].copy()
        del self.lines[self.nowName]
        tem_.addItem(QListWidgetItem(tem.text()))
        tem_.takeItem(tem_.index)
        self.nowName = tem.text()

    def save(self):
        id = self.findChild(QComboBox).currentText()
        for i1, i in enumerate(self.key1):
            if i == id:
                break
        id = self.key2[i1]
        self.data[id] = self.findChild(QTextEdit).toPlainText().split('\n')
        #%%%%%%
        for i1, i in self.data.items():
            newData = []
            for j in i:
                if j != '':
                    newData.append(j)
            self.data[i1] = newData
        if self.nowName == None:
            return
        self.lines[self.nowName] = self.data
        with open(self.path, 'w') as f:
            json.dump(self.lines, f)

##QListWidget模板哦
class bscEditWin(QWidget):
    def __init__(self, mapName):
        super(bscEditWin, self).__init__()
        self.path = 'maps/'+mapName+'/basicInfo.json'
        self.tmpPath = 'resource/tmp/basicInfo.json'

        with open(self.tmpPath, 'w') as f:
            json.dump({}, f)

        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({}, f)
                self.data = {}
        else:
            with open(self.path, 'r') as f:
                self.data = json.load(f)

        self.tmpView = None
        self.nowName = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        tem = QListWidget(self)
        tem.doubleClicked.connect(self.doubleClicked)
        layout.addWidget(tem)

        layout11 = QHBoxLayout()
        tem = QPushButton('delete', self)
        tem.clicked.connect(self.delete)
        layout11.addWidget(tem)
        tem = QLineEdit(self)
        tem.setPlaceholderText('name')
        layout11.addWidget(tem)
        tem = QPushButton('add', self)
        tem.clicked.connect(self.add)
        layout11.addWidget(tem)
        tem = QPushButton('rename', self)
        tem.clicked.connect(self.rename)
        layout11.addWidget(tem)
        tem = QPushButton('save', self)
        tem.clicked.connect(self.save)
        layout11.addWidget(tem)
        layout.addLayout(layout11)

        self.setLayout(layout)
        self.show()

    def doubleClicked(self, data: None):
        self.save()
        try:
            self.tmpView.deleteLater()
        except:
            pass
        self.tmpView = basicEditW(self.tmpPath)
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()
        self.nowName = self.findChild(QListWidget).item(data.row())

    ##模板
    def delete(self):
        self.save()
        #----------------------------------
        tem_ = self.findChild(QListWidget)
        tem = tem_.currentItem()
        if tem == None:
            return
        del self.data[tem.text()]
        tem_.takeItem(tem_.currentIndex().row())
        #----------------------------------
    ##模板
    def add(self):
        #----------------------------------
        tem = self.findChild(QListWidget)
        text = self.findChild(QLineEdit).text()
        if text in self.data or text == '':
            return
        tem.addItem(QListWidgetItem(text))
        #----------------------------------

        self.data[text] = {}        ##模板
        with open(self.tmpPath, 'w') as f:
            json.dump({}, f)
    ##模板
    def rename(self):
        self.save()
        #----------------------------------
        tem_ = self.findChild(QListWidget)
        tem = tem_.currentItem()
        if tem == None:
            return
        text = self.findChild(QLineEdit).text()

        if text in self.data or text == '':
            return
        self.data[text] = self.data[tem.text()].copy()
        del self.data[tem.text()]
        tem.setText(text)
        #----------------------------------
        self.save()                 ##模板

    def save(self):
        tem_ = self.findChild(QListWidget).currentItem()
        if tem_ == None:
            return
        if self.nowName != None:
            with open(self.tmpPath, 'r') as f:
                end = json.load(f)
            self.data[tem_.text()] = end
            self.nowMap = None
        with open(self.path, 'w') as f:
            json.dump(self.data, f)

class backupEditWin(QWidget):
    def __init__(self, path, MAX=12):
        super(backupEditWin, self).__init__()
        self.path = path
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)
                self.data = {}
        else:
            with open(path, 'r') as f:
                self.data = json.load(f)
        self.MAX = MAX
        self.initUI()
        self.read()

    def initUI(self):
        self.setWindowTitle('制作加成')
        tem_table = QTableWidget(self)
        dws = resource.findAll({'usage': 'dw', 'flag': 'red', 'action': 'left'})
        tem_table.setColumnCount(len(dws) + 1)
        tem_table.setRowCount(self.MAX)
        tem_table.setHorizontalHeaderItem(0, QTableWidgetItem('id'))
        for i, j in enumerate(dws):
            tem_table.setHorizontalHeaderItem(i + 1, QTableWidgetItem(QIcon(j['pixmap']), j['name']))
        for i in range(self.MAX):
            for j in range(len(dws) + 1):
                tem_table.setItem(i, j, QTableWidgetItem(''))
        layout = QVBoxLayout()
        layout.addWidget(QLabel('加成的影响范围'))
        layout.addWidget(tem_table)
        tem_table = QTableWidget(self)
        dws = ['move_distance', 'view_distance', 'gf_g', 'gf_maxdistance', 'gf_mindistance', 'dsc']
        tem_table.setColumnCount(len(dws) + 1)
        tem_table.setRowCount(self.MAX)
        tem_table.setHorizontalHeaderItem(0, QTableWidgetItem('id'))
        for i, j in enumerate(dws):
            tem_table.setHorizontalHeaderItem(i + 1, QTableWidgetItem(j))
        for i in range(self.MAX):
            for j in range(len(dws) + 1):
                tem_table.setItem(i, j, QTableWidgetItem(''))
        layout.addWidget(QLabel('加成的实体'))
        layout.addWidget(tem_table)
        tem_table = QPushButton('ok', self)
        tem_table.clicked.connect(self.save)
        layout.addWidget(tem_table)
        self.setLayout(layout)
        self.resize(800, 400)
        self.show()

    def read(self):
        tables = self.findChildren(QTableWidget)
        for i, j in enumerate(self.data.keys()):
            tables[0].item(i, 0).setText(j)
            tables[1].item(i, 0).setText(j)
        for i1, i in enumerate(self.data.keys()):
            for j in range(1, tables[1].columnCount()):
                if tables[1].horizontalHeaderItem(j).text() in self.data[i]:
                    tables[1].item(i1, j).setText(str(self.data[i][tables[1].horizontalHeaderItem(j).text()]))
            for j in range(1, tables[0].columnCount()):
                if tables[0].horizontalHeaderItem(j).text() in self.data[i]['range']:
                    tables[0].item(i1, j).setText('1')

    def save(self):
        self.data = {}
        self.setWindowTitle('制作加成')
        tables = self.findChildren(QTableWidget)
        for i in range(tables[1].rowCount()):
            tem_data = tables[1].item(i, 0).text()
            if tem_data == '':
                continue
            self.data[tem_data] = {}
            for j in range(1, tables[1].columnCount()):
                try:
                    tem_data_1 = int(tables[1].item(i, j).text())
                except ValueError:
                    if tables[1].item(i, j).text() != '':
                        self.setWindowTitle('制作加成;error:格式不符')
                        return
                    continue
                if tem_data_1 == 0:
                    continue
                self.data[tem_data][tables[1].horizontalHeaderItem(j).text()] = tem_data_1
            for j in range(tables[0].rowCount()):
                tem_dd = tables[0].item(i, 0).text()
                if tem_dd == tem_data:
                    end = []
                    for k in range(1, tables[0].columnCount()):
                        if tables[0].item(j, k).text() in ['', '0']:
                            continue
                        end.append(tables[0].horizontalHeaderItem(k).text())
                    if end:
                        self.data[tem_data]['range'] = end
                    break
        with open(self.path, 'w') as f:
            json.dump(self.data, f)

class storyEditWin(QWidget):
    def __init__(self, path):
        super(storyEditWin, self).__init__()
        self.path = path
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)
                self.data = {}
        else:
            with open(path, 'r') as f:
                self.data = json.load(f)
        self.nowName = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('制作故事情节')
        layout1 = QVBoxLayout()
        tem = QListWidget()
        tem.addItems(self.data.keys())
        tem.clicked.connect(self.clicked)
        layout1.addWidget(tem)
        layout11 = QHBoxLayout()
        tem = QPushButton('delete', self)
        tem.clicked.connect(self.delete)
        layout11.addWidget(tem)
        layout11.addWidget(QLineEdit(self))
        tem = QPushButton('add', self)
        tem.clicked.connect(self.add)
        layout11.addWidget(tem)
        tem = QPushButton('rename', self)
        tem.clicked.connect(self.rename)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout2 = QVBoxLayout()
        tem = QTextEdit(self)
        tem.setPlaceholderText('任务背景')
        layout2.addWidget(tem)
        tem = QTextEdit(self)
        tem.setPlaceholderText('任务目标')
        layout2.addWidget(tem)
        tem = QPushButton('save')
        tem.clicked.connect(self.save)
        layout2.addWidget(tem)
        layout = QHBoxLayout(self)
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)
        self.show()

    def clicked(self, data:None):
        self.save()
        tem_ = self.findChild(QListWidget)
        tem = tem_.currentItem().text()
        tem_.index = tem_.currentIndex().row()
        com = self.findChildren(QTextEdit)
        com[0].setText(self.data[tem]['command_bg'])
        com[1].setText(self.data[tem]['command'])
        self.nowName = tem

    def delete(self):
        if self.nowName == None:
            return
        tem = self.findChild(QListWidget)
        try:
            tem.takeItem(tem.currentIndex().row())
            # tem.takeItem(tem.index)
        except:
            print('nono')
        del self.data[self.nowName]
        com = self.findChildren(QTextEdit)
        com[0].setText('')
        com[1].setText('')
        self.nowName = None

    def add(self):
        tem = self.findChild(QListWidget)
        text = self.findChild(QLineEdit).text()
        if text in self.data or text == '':
            return
        tem.addItem(QListWidgetItem(text))
        self.data[text] = {'command_bg':'', 'command':''}

    def rename(self):
        if self.nowName == None:
            return
        text = self.findChild(QLineEdit).text()
        if text == '' or text in self.data:
            return
        tem = self.findChild(QListWidget)
        text_ = tem.currentItem().text()
        tem.takeItem(tem.currentIndex().row())
        tem.addItem(QListWidgetItem(text))
        self.data[text] = self.data[text_].copy()
        del self.data[text_]
        self.save()

    def save(self):
        if self.nowName == None:
            return
        com = self.findChildren(QTextEdit)
        self.data[self.nowName]['command_bg'] = com[0].toPlainText()
        self.data[self.nowName]['command'] = com[1].toPlainText()
        with open(self.path, 'w') as f:
            json.dump(self.data, f)


class toggleEditWin(QWidget):
    def __init__(self, path, brother=None):
        super(toggleEditWin, self).__init__()
        self.path = path
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)
                self.data = {}
        else:
            with open(path, 'r') as f:
                self.data = json.load(f)
        self.nowName = None
        self.brother = brother
        self.cfType = {'dw': ['alive', 'blood', 'oil', 'bullect', 'occupy', 'stealth'], \
                  'build': ['occupy'], \
                  'area': ['alive', 'blood', 'oil', 'bullect', 'enemyIn'], 'money': ['loss', 'cause', 'army'], \
                  'bout': ['at', 'every'], 'energy': [], 'command': []}
        self.initUI()

    def initUI(self):
        roles = ['red', 'blue', 'yellow', 'green']

        layout1 = QVBoxLayout()
        tem = QLineEdit(self)
        tem.setPlaceholderText('触发器名称')
        layout1.addWidget(tem)
        tem = QLineEdit(self)
        tem.setPlaceholderText('触发器描述')
        layout1.addWidget(tem)
        layout11 = QHBoxLayout()
        tem = QComboBox(self)
        tem.addItems(self.cfType.keys())
        tem.currentTextChanged.connect(self.cfTypeChanged1)
        layout11.addWidget(tem)
        tem = QComboBox(self)
        tem.currentTextChanged.connect(self.cfTypeChanged2)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout11 = QHBoxLayout()
        tem = QPushButton('选择', self)
        tem.clicked.connect(self.toChoose)
        tem.data = []
        layout11.addWidget(tem)
        tem = QPushButton('显示', self)
        tem.clicked.connect(self.toShow)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout11 = QHBoxLayout()
        for i in roles:
            tem = QCheckBox(i, self)
            layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout11 = QHBoxLayout()
        layout11.addWidget(QCheckBox('123', self))
        tem = QComboBox(self)
        tem.addItems(['>', '<'])
        layout11.addWidget(tem)
        layout11.addWidget(QLineEdit(self))
        layout1.addLayout(layout11)
        layout11 = QHBoxLayout()
        tem = QPushButton('add', self)
        tem.clicked.connect(self.add)
        layout11.addWidget(tem)
        tem = QPushButton('rename', self)
        tem.clicked.connect(self.rename)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout2 = QVBoxLayout()
        tem = QListWidget(self)
        tem.addItems(self.data.keys())
        tem.clicked.connect(self.clicked)
        layout2.addWidget(tem)
        layout22 = QHBoxLayout()
        tem = QPushButton('delete', self)
        tem.clicked.connect(self.delete)
        layout22.addWidget(tem)
        tem = QPushButton('save', self)
        tem.clicked.connect(self.save)
        layout22.addWidget(tem)
        layout2.addLayout(layout22)
        layout = QHBoxLayout()
        layout.addLayout(layout2)
        layout.addLayout(layout1)
        self.setLayout(layout)
        self.cfTypeChanged1(list(self.cfType.keys())[0])

    def cfTypeChanged1(self, data=None):
        print(data, '111')
        tem = self.findChildren(QComboBox)[1]
        tem.clear()
        tem.addItems(self.cfType[data])
        if data == 'bout':
            tem = self.findChildren(QPushButton)
            tem[0].hide()
            tem[1].hide()
        elif self.cfType[data]:
            self.cfTypeChanged2(self.cfType[data][0])
        else:
            for i in self.findChildren(QCheckBox):
                i.show()
            i.hide()
            # self.findChild(QPushButton).hide()
            for i in self.findChildren(QPushButton)[:2]:
                i.hide()
            tem = self.findChildren(QComboBox)[2]
            com = self.findChildren(QLineEdit)[2]
            com.show()
            if data == 'energy':
                tem.clear()
                tem.addItems(['>', '<'])
                tem.show()
                com.setText('')
                com.setPlaceholderText('输入值（0~100）')
            elif data == 'command':
                tem.hide()
                com.setPlaceholderText('输入命令')

    def cfTypeChanged2(self, data=None):
        print(data, '222')
        btns = self.findChildren(QPushButton)
        if data in ['alive', 'stealth']:
            for i in self.findChildren(QCheckBox):
                i.show()
            i.setText(data)
            # self.findChild(QPushButton).show
            btns[0].show()
            btns[1].show()
            self.findChildren(QComboBox)[2].hide()
            self.findChildren(QLineEdit)[2].hide()
        elif data in ['blood', 'oil', 'bullect', 'occupy', 'loss', 'cause', 'army']:
            for i in self.findChildren(QCheckBox):
                i.show()
            i.hide()
            if data in ['loss', 'cause', 'army']:
                # self.findChild(QPushButton).hide()
                btns[0].hide()
                btns[1].hide()
            else:
                # self.findChild(QPushButton).show()
                btns[0].show()
                btns[1].show()
            tem = self.findChildren(QComboBox)[2]
            tem.clear()
            tem.addItems(['>', '<'])
            tem.show()
            com = self.findChildren(QLineEdit)[2]
            com.show()
            com.setPlaceholderText('输入值')
        elif data == 'at':
            for i in self.findChildren(QCheckBox):
                i.show()
            i.hide()
            # self.findChild(QPushButton).hide()
            btns[0].show()
            btns[1].show()
            self.findChildren(QComboBox)[2].hide()
            tem = self.findChildren(QLineEdit)[2]
            tem.setPlaceholderText('输入回合')
            tem.show()
        elif data == 'every':
            for i in self.findChildren(QCheckBox):
                i.show()
            i.hide()
            # self.findChild(QPushButton).hide()
            btns[0].show()
            btns[1].show()
            self.findChildren(QComboBox)[2].hide()
            self.findChildren(QLineEdit)[2].hide()
        elif data == 'enemyIn':
            for i in self.findChildren(QCheckBox):
                i.show()
            i.hide()
            btns[0].show()
            btns[1].show()
            self.findChildren(QComboBox)[2].hide()
            self.findChildren(QLineEdit)[2].hide()

    def add(self):
        name = self.findChild(QLineEdit).text()
        if name == '' or name in self.data:
            return
        cf = {}
        com = self.findChildren(QComboBox)
        cf['type'] = com[0].currentText()+"_"+com[1].currentText()
        cf['flags'] = []
        tem = self.findChildren(QCheckBox)
        dtm = self.findChildren(QLineEdit)
        cf['name'] = dtm[0].text()
        cf['dsc'] = dtm[1].text()
        for i in tem[:4]:
            if i.isChecked():
                cf['flags'].append(i.text())
        if not tem[-1].isHidden():
            cf['data'] = tem[-1].isChecked()
        elif not com[2].isHidden():
            cf['data'] = com[2].currentText()
            if not dtm[2].isHidden():
                cf['value'] = dtm[2].text()
        elif not dtm[2].isHidden():
            cf['data'] = dtm[2].text()
        btn = self.findChild(QPushButton)
        if not btn.isHidden():
            if btn.data:
                cf['area'] = btn.data.copy()

        print(cf)
        self.data[cf['name']] = cf
        self.findChild(QListWidget).addItem(QListWidgetItem(cf['name']))

    def rename(self):
        tem = self.findChild(QListWidget).currentItem()
        if tem == None:
            return
        com = self.findChild(QLineEdit)
        if com.text() == '' or com.text() in self.data:
            return
        self.data[com.text()] = self.data[tem.text()].copy()
        self.data[com.text()]['name'] = com.text()
        del self.data[tem.text()]
        tem.setText(com.text())

    def delete(self):
        tem = self.findChild(QListWidget)
        index = tem.currentIndex().row()
        if index == -1:
            return
        del self.data[tem.currentItem().text()]
        tem.takeItem(index)

    def clicked(self):
        tem = self.findChild(QListWidget)
        guard = self.data[tem.currentItem().text()]
        guard_ = guard['type'].split('_')
        coms = self.findChildren(QComboBox)
        lines = self.findChildren(QLineEdit)
        btn = self.findChild(QPushButton)
        lines[0].setText(guard['name'])
        lines[1].setText(guard['dsc'])
        self.cfTypeChanged1(guard_[0])
        if guard_[1] == '':
            coms[1].clear()
        else:
            self.cfTypeChanged2(guard_[1])
        checks = self.findChildren(QCheckBox)
        for i in checks[:4]:
            if i.text() in guard['flags']:
                i.setChecked(True)
            else:
                i.setChecked(False)
        if not checks[-1].isHidden():
            checks[-1].setChecked(guard['data'])
        elif not coms[2].isHidden():
            coms[2].setCurrentText(guard['data'])
            if not lines[2].isHidden():
                lines[2].setText(guard['value'])
        if not lines[2].isHidden():
            lines[2].setText(guard['data'])
        if 'area' in guard:
            if guard['area']:
                btn.data = guard['area']
            else:
                btn.data = []
        else:
            btn.data = []

    def save(self):
        print(self.data)
        with open(self.path, 'w') as f:
            json.dump(self.data, f)

    def toChoose(self):
        if not self.brother:
            return
        text = self.findChild(QComboBox).currentText()
        post = toggleChooseEvent('toChoose', text)
        QCoreApplication.postEvent(self.brother, post)
        # self.hide()

    def toShow(self):
        if not self.findChild(QPushButton).data or not self.brother:
            return
        post = toggleChooseEvent('toShow', self.findChild(QPushButton).data)
        QCoreApplication.postEvent(self.brother, post)
        # self.hide()

    def choosed(self, data):
        # text = self.findChild(QComboBox).com.currentText()
        self.findChild(QPushButton).data = data
        print(data)
        # if text == 'area':
        #     btn.data = data
        # elif text == 'dw':
        #     if len(data)
''''
    指定单位：存活，规模，油量，弹药，占领，下潜/隐身
    指定建筑：占领
    指定区域：敌军进入
    资金：损失，造成，军队资金，
    指定回合，每个回合
    指挥官能量
    输入指令


    *** 回合延迟
    指定单位：规模，油量，弹药，加成，存活，所属，
    指定建筑：所属，改变
    资金：减少，增加，变为，
    触发：启动，删除，停止
    指挥官能量
    故事背景，台词，基本配置
    胜利，移交控制权限
    屏幕提示
'''
class toggleEventEditWin(QWidget):
    def __init__(self, path, brother=None):
        super(toggleEventEditWin, self).__init__()
        self.path = path
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)
                self.data = {}
        else:
            with open(path, 'r') as f:
                self.data = json.load(f)
        self.nowName = None
        self.brother = brother
        self.cfType = {'dw': ['alive', 'blood', 'oil', 'bullect', 'flag'], \
                       'dws': ['alive', 'blood', 'oil', 'bullect', 'flag'], \
                       'build': ['flag', 'change'], 'builds': ['flag', 'change'],\
                       'money': [], 'backup':[], \
                       'toggle':['start', 'stop', 'kill'], 'energy':['become'], \
                       'story': [], 'lines':[], 'basicData':[], 'tip': ['normal', 'screen'], \
                       'target': ['victory', 'failure', 'control']}
        self.tmpView = None
        self.initUI()
        self.cfTypeChanged1(list(self.cfType.keys())[0])

    def initUI(self):
        roles = ['red', 'blue', 'yellow', 'green', 'toggle']
        self.component1 = []
        self.component2 = []
        self.component_flag = []
        self.component_time = []
        layout1 = QVBoxLayout()
        tem = QLineEdit(self)
        tem.setPlaceholderText('事件名称')
        layout1.addWidget(tem)
        tem = QLineEdit(self)
        tem.setPlaceholderText('事件描述')
        layout1.addWidget(tem)
        layout11 = QHBoxLayout()
        tem = QComboBox(self)
        tem.addItems(self.cfType.keys())
        tem.currentTextChanged.connect(self.cfTypeChanged1)
        layout11.addWidget(tem)
        tem = QComboBox(self)
        tem.currentTextChanged.connect(self.cfTypeChanged2)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout11 = QHBoxLayout()
        tem = QPushButton('选择区域', self)
        tem.clicked.connect(self.toChoose)
        tem.data = []
        self.component1.append(tem)
        layout11.addWidget(tem)
        tem = QPushButton('显示', self)
        tem.clicked.connect(self.toShow)
        self.component1.append(tem)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout11 = QHBoxLayout()
        for i in roles:
            tem = QCheckBox(i, self)
            self.component_flag.append(tem)
            layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout11 = QHBoxLayout()
        tem = QCheckBox('True', self)
        self.component2.append(tem)
        layout11.addWidget(tem)
        tem = QPushButton('选择', self)
        tem.clicked.connect(self.dwChoose)
        self.component2.append(tem)
        layout11.addWidget(tem)
        tem = QComboBox(self)
        tem.addItems(['+', '-', '='])
        self.component2.append(tem)
        layout11.addWidget(tem)
        tem = QLineEdit(self)
        self.component2.append(tem)
        layout11.addWidget(tem)
        tem = QComboBox(self)
        tem.addItems(roles)
        self.component2.append(tem)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)

        layout12 = QHBoxLayout()
        layout12.addWidget(QLabel('延迟效果'))
        tem = QComboBox(self)
        tem.addItems(['every', 'delay', 'interval'])
        self.component_time.append(tem)
        layout12.addWidget(tem)
        tem = QLineEdit(self)
        self.component_time.append(tem)
        layout12.addWidget(tem)
        layout1.addLayout(layout12)

        layout11 = QHBoxLayout()
        tem = QPushButton('add', self)
        tem.clicked.connect(self.add)
        layout11.addWidget(tem)
        tem = QPushButton('rename', self)
        tem.clicked.connect(self.rename)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout2 = QVBoxLayout()
        tem = QListWidget(self)
        tem.addItems(self.data.keys())
        tem.clicked.connect(self.clicked)
        layout2.addWidget(tem)

        layout22 = QHBoxLayout()
        tem = QPushButton('delete', self)
        tem.clicked.connect(self.delete)
        layout22.addWidget(tem)
        tem = QPushButton('save', self)
        tem.clicked.connect(self.save)
        layout22.addWidget(tem)
        layout2.addLayout(layout22)
        layout = QHBoxLayout()
        layout.addLayout(layout2)
        layout.addLayout(layout1)
        self.setLayout(layout)
        self.cfTypeChanged1(list(self.cfType.keys())[0])

    def cfTypeChanged1(self, data=None):
        if self.cfType[data]:
            tem = self.findChildren(QComboBox)[1]
            tem.clear()
            tem.addItems(self.cfType[data])
            self.cfTypeChanged2(self.cfType[data][0])
        elif data == 'money':
            for i in self.component2:
                i.hide()
            for i in self.component_flag:
                i.show()
            self.component2[2].show()
            self.component2[3].show()
        elif data in ['story', 'lines', 'basicData', 'backup']:
            for i in self.component2:
                i.hide()
            for i in self.component_flag:
                i.show()
            self.component2[1].show()

    def cfTypeChanged2(self, data=None):
        if data == 'alive':
            for i in self.component_flag:
                i.show()
            for i in self.component2[:2]:
                i.show()
            if self.findChild(QComboBox).currentText() == 'dw':
                self.component2[1].hide()
            for i in self.component2[2:]:
                i.hide()
        elif data in ['oil', 'blood', 'bullect']:
            for i in self.component2:
                i.hide()
            for i in self.component_flag:
                i.show()
            self.component2[2].show()
            self.component2[3].show()
        elif data == 'flag':
            for i in self.component2:
                i.hide()
            for i in self.component_flag:
                i.show()
            self.component2[-1].show()
        elif data == 'change':
            for i in self.component2:
                i.hide()
            for i in self.component_flag:
                i.show()
            self.component2[1].show()
        elif data in ['start', 'stop', 'kill']:
            for i in self.component2:
                i.hide()
            for i in self.component_flag:
                i.hide()
            self.component2[1].show()
        elif data == 'become':
            for i in self.component2:
                i.hide()
            for i in self.component_flag:
                i.show()
            self.component2[2].show()
        elif data in ['normal', 'screen']:
            for i in self.component2:
                i.hide()
            for i in self.component_flag:
                i.show()
            self.component2[2].show()
        elif data in ['victory', 'failure']:
            for i in self.component2:
                i.hide()
            for i in self.component_flag:
                i.show()
        elif data == 'control':
            for i in self.component2:
                i.hide()
            for i in self.component_flag:
                i.show()
            self.component2[-1].show()

    def dwChoose(self):
        tem_text = self.findChild(QComboBox).currentText()
        try:
            self.tmpView.deleteLater()
        except:
            pass
        self.tmpView = QWidget()
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        tem_item = self.findChild(QListWidget).currentItem()
        if tem_item == None:
            return
        name = tem_item.text()
        if tem_text == 'dws':
            if not self.component2[0].isChecked():
                return
            layout1 = QFormLayout()
            for i in resource.findAll({'usage':'dw', 'flag':'red', 'action':'left'}):
                tem = QPushButton(QIcon(i['pixmap']), resource.basicData['money']['chineseName'][i['name']], self.tmpView)
                tem.setEnabled(False)
                tem_ = QSpinBox(self.tmpView)
                if 'data' in self.data[name]:
                    if i['name'] in self.data[name]['data']:
                        tem_.setValue(self.data[name]['value'][i['name']])
                tem_.data = i['name']
                layout1.addRow(tem, tem_)
            layout = QVBoxLayout()
            layout.addLayout(layout1)
            tem = QPushButton('save', self.tmpView)
            tem.clicked.connect(self.dwChoosed)
            layout.addLayout(layout1)
            layout.addWidget(tem)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
        elif tem_text == 'dw':
            return
        elif tem_text == 'story':
            layout = QVBoxLayout()
            path = 'maps/' + self.brother.vmap.map['name'] + '/stories.json'
            if os.path.exists(path):
                with open(path, 'r') as f:
                    end = json.load(f)
            else:
                end = {}
            for i, j in end.items():
                tem = QRadioButton(self.tmpView)
                tem.setText(i)
                if 'data' in self.data[name]:
                    if self.data[name]['data'] == i:
                        tem.setChecked(True)
                layout.addWidget(tem)
            tem = QPushButton('save', self.tmpView)
            tem.clicked.connect(self.dwChoosed)
            layout.addWidget(tem)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
        elif tem_text == 'lines':
            layout = QVBoxLayout()
            path = 'maps/' + self.brother.vmap.map['name'] + '/lines.json'
            if os.path.exists(path):
                with open(path, 'r') as f:
                    end = json.load(f)
            else:
                end = {}
            for i, j in end.items():
                tem = QRadioButton(self.tmpView)
                tem.setText(i)
                if 'data' in self.data[name]:
                    if self.data[name]['data'] == i:
                        tem.setChecked(True)
                layout.addWidget(tem)
            tem = QPushButton('save', self.tmpView)
            tem.clicked.connect(self.dwChoosed)
            layout.addWidget(tem)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
        elif tem_text == 'basicData':
            layout = QVBoxLayout()
            path = 'maps/' + self.brother.vmap.map['name'] + '/basicInfo.json'
            if os.path.exists(path):
                with open(path, 'r') as f:
                    end = json.load(f)
            else:
                end = {}
            for i, j in end.items():
                tem = QRadioButton(self.tmpView)
                tem.setText(i)
                if 'data' in self.data[name]:
                    if self.data[name]['data'] == i:
                        tem.setChecked(True)
                layout.addWidget(tem)
            tem = QPushButton('save', self.tmpView)
            tem.clicked.connect(self.dwChoosed)
            layout.addWidget(tem)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
        elif tem_text == 'toggle':
            layout = QVBoxLayout()
            path = 'maps/' + self.brother.vmap.map['name'] + '/toggles.json'
            if os.path.exists(path):
                with open(path, 'r') as f:
                    end = json.load(f)
            else:
                end = {}
            for i, j in end.items():
                tem = QCheckBox(i, self.tmpView)
                layout.addWidget(tem)
            tem = QPushButton('save', self.tmpView)
            tem.clicked.connect(self.dwChoosed)
            layout.addWidget(tem)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
        elif tem_text in ['build', 'builds']:
            layout = QVBoxLayout()
            end = []
            names = []
            for i in resource.data:
                if i['usage'] not in ['geo', 'build']:
                    continue
                if i['name'] in names:
                    continue
                end.append(i.copy())
                names.append(i['name'])
            del names

            for i in end:
                tem = QRadioButton(self.tmpView)
                tem.setText(resource.basicData['geo']['chineseName'][i['name']])
                tem.setIcon(QIcon(i['pixmap']))
                tem.data = i['name']
                layout.addWidget(tem)
            tem = QPushButton('save', self.tmpView)
            tem.clicked.connect(self.dwChoosed)
            layout.addWidget(tem)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
        elif tem_text == 'backup':
            layout = QVBoxLayout()
            path = 'maps/' + self.brother.vmap.map['name'] + '/backup.json'
            if os.path.exists(path):
                with open(path, 'r') as f:
                    end = json.load(f)
            else:
                end = {}
            for i, j in end.items():
                tem = QRadioButton(self.tmpView)
                tem.setText(i)
                if 'data' in self.data[name]:
                    if self.data[name]['data'] == i:
                        tem.setChecked(True)
                layout.addWidget(tem)
            tem = QPushButton('save', self.tmpView)
            tem.clicked.connect(self.dwChoosed)
            layout.addWidget(tem)
            self.tmpView.setLayout(layout)
            self.tmpView.show()

    def dwChoosed(self):
        tem_text = self.findChild(QComboBox).currentText()
        name = self.findChild(QListWidget).currentItem().text()
        if tem_text == 'dws':
            end = {}
            for i in self.tmpView.findChild(QSpinBox):
                end[i.data] = i.value()
            self.data[name]['value'] = end
            self.tmpView.deleteLater()
        elif tem_text in ['story', 'lines', 'basicData', 'build', 'builds', 'backup']:
            for i in self.tmpView.findChildren(QRadioButton):
                if i.isChecked():
                    self.data[name]['data'] = i.text()
                    break
            self.tmpView.deleteLater()
        elif tem_text == 'toggle':
            self.data[name]['data'] = []
            for i in self.tmpView.findChildren(QRadioButton):
                if i.isChecked():
                    self.data[name]['data'].append(i.text())
            self.tmpView.deleteLater()

        print(self.data[name])

    def collectData(self):
        cf = {}
        com = self.findChildren(QComboBox)
        cf['type'] = com[0].currentText() + "_" + com[1].currentText()
        cf['flags'] = []
        for i in self.component_flag:
            if i.isChecked():
                cf['flags'].append(i.text())
        dtm = self.findChildren(QLineEdit)
        cf['name'] = dtm[0].text()
        cf['dsc'] = dtm[1].text()
        if com[1].currentText() == 'alive':
                cf['data'] = self.component2[0].isChecked()
        elif com[1].currentText() in ['blood', 'oil', 'bullect']:
            cf['data'] = self.component2[2].currentText()
            cf['value'] = self.component2[3].text()
        elif com[1].currentText() == 'flag':
            cf['data'] = self.component2[4].currentText()
        elif com[1].currentText() == 'become':
            cf['data'] = self.component2[3].text()
        elif com[0].currentText() == 'tip':
            cf['data'] = self.component2[3].text()
        elif com[1].currentText() == 'control':
            cf['data'] = self.component2[4].currentText()

        cf['tType'] = self.component_time[0].currentText()
        cf['tData'] = self.component_time[1].text()
        if not self.component1[0].isHidden():
            cf['area'] = self.component1[0].data
        return cf

    def add(self):
        name = self.findChild(QLineEdit).text()
        if name == '' or name in self.data:
            return

        self.data[name] = self.collectData()
        self.findChild(QListWidget).addItem(QListWidgetItem(name))
        # print(self.data)

    def rename(self):
        tem = self.findChild(QListWidget).currentItem()
        if tem == None:
            return
        com = self.findChild(QLineEdit)
        if com.text() == '' or com.text() in self.data:
            return
        self.data[com.text()] = self.data[tem.text()].copy()
        self.data[com.text()]['name'] = com.text()
        del self.data[tem.text()]
        tem.setText(com.text())

    def delete(self):
        tem = self.findChild(QListWidget)
        index = tem.currentIndex().row()
        if index == -1:
            return
        del self.data[tem.currentItem().text()]
        tem.takeItem(index)

    def clicked(self):
        tem = self.findChild(QListWidget)
        name = tem.currentItem().text()
        guard_ = self.data[name]['type'].split('_')
        lines = self.findChildren(QLineEdit)
        btn = self.findChild(QPushButton)
        coms = self.findChildren(QComboBox)

        if 'area' in self.data[name]:
            btn.area = self.data[name]['area']
        else:
            btn.area = []
        lines[0].setText(self.data[name]['name'])
        lines[1].setText(self.data[name]['dsc'])
        coms[0].setCurrentText(guard_[0])

        if guard_[1] != '':
            coms[1].setCurrentText(guard_[1])


        for i in self.component_flag:
            if i.text() in self.data[name]['flags']:
                i.setChecked(True)
            else:
                i.setChecked(False)

        if guard_[1] == 'alive':
            self.component2[0].setChecked(self.data[name]['data'])
        elif guard_[1] in ['oil', 'blood', 'bullect']:
            self.component2[2].setCurrentText(self.data[name]['data'])
            self.component2[3].setText(self.data[name]['value'])
        elif guard_[1] == 'flag':
            self.component2[4].setCurrentText(self.data[name]['data'])
        elif guard_[0] in ['money', 'energy', 'tip']:
            self.component2[3].setText(self.data[name]['data'])
        elif guard_[1] == 'control':
            self.component2[4].setCurrentText(self.data[name]['data'])

        self.component_time[0].setCurrentText(self.data[name]['tType'])
        self.component_time[1].setText(self.data[name]['tData'])

        if not self.component1[0].isHidden():
            self.component1[0].data = self.data[name]['area']

    def save(self):
        name = self.findChild(QLineEdit).text()

        if name not in self.data:
            return

        cf = self.collectData()
        guard_ = self.data[name]['type'].split('_')

        if guard_[0] in ['story', 'lines', 'basicData','toggle'] or guard_[1] == 'change':
            cf['data'] = self.data[name]['data'].copy()
        elif guard_[0] == 'dws' and guard_[1] == 'alive' and cf['data']:
            cf['value'] = self.data[name]['value'].copy()

        self.data[name] = cf

        with open(self.path, 'w') as f:
            json.dump(self.data, f)

        print(self.data)

    def toChoose(self):
        if not self.brother:
            return
        text = self.findChild(QComboBox).currentText()
        post = toggleChooseEvent('toChoose', text)
        QCoreApplication.postEvent(self.brother, post)
        # self.hide()

    def toShow(self):
        if not self.component1[0].data or not self.brother:
            return
        post = toggleChooseEvent('toShow', self.findChild(QPushButton).data)
        QCoreApplication.postEvent(self.brother, post)

    def choosed(self, data):
        self.component1[0].data = data

class toggleChooseEvent(QEvent):
    idType = QEvent.registerEventType()
    def __init__(self, type_, data=None):
        super(toggleChooseEvent, self).__init__(toggleChooseEvent.idType)
        self.type_ = type_
        self.data = data


class ruleEditWin(QWidget):
    def __init__(self, mapName):
        super(ruleEditWin, self).__init__()
        self.basic_path = ['stories', 'lines', 'basicInfo', 'backup', 'toggles', 'toggleEvents', 'rule']
        self.data = {}
        for i in self.basic_path:
            path = 'maps/'+mapName+'/'+i+'.json'
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump({}, f)
                    self.data[i] = {}
            else:
                with open(path, 'r') as f:
                    self.data[i] = json.load(f)
        self.ruleData = self.data['rule'].copy()
        del self.data['rule']
        self.path = 'maps/'+mapName+'/rule.json'
        self.initUI()

    def initUI(self):
        max_cols = 12
        layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout1.addWidget(QLabel('role', self))
        for i in self.basic_path[:-3]:
            layout1.addWidget(QLabel(i, self))
        layout.addLayout(layout1)
        for i in ['red', 'blue', 'green', 'yellow']:
            layout1 = QHBoxLayout()
            layout1.addWidget(QLabel(i, self))
            for j in self.basic_path[:-3]:
                tem = QComboBox(self)
                tem.addItems(self.data[j].keys())
                tem.data = j
                tem.key = i
                if i in self.ruleData:
                    if j in self.ruleData[i]:
                        tem.setCurrentText(self.ruleData[i][j])
                layout1.addWidget(tem)
            tem = QLineEdit(self)
            tem.setPlaceholderText('初始资金')
            tem.key = i
            tem.data = 'beginMoney'
            if i in self.ruleData:
                if 'beginMoney' in self.ruleData[i]:
                    tem.setText(self.ruleData[i]['beginMoney'])
            layout1.addWidget(tem)
            tem = QLineEdit(self)
            tem.setPlaceholderText('初始能量(%)')
            tem.key = i
            tem.data = 'beginEnergy'
            if i in self.ruleData:
                if 'beginEnergy' in self.ruleData[i]:
                    tem.setText(self.ruleData[i]['beginEnergy'])
            layout1.addWidget(tem)
            layout1.addWidget(QLabel('敌人', self))
            for j in ['red', 'blue', 'green', 'yellow']:
                tem = QCheckBox(j, self)
                tem.data = i
                if i in self.ruleData:
                    if 'enemy' in self.ruleData[i]:
                        if j in self.ruleData[i]['enemy']:
                            tem.setChecked(True)
                layout1.addWidget(tem)

            layout.addLayout(layout1)
        layout.addWidget(QLabel('启动触发器', self))
        if 'itIsOn' in self.ruleData:
            toggles_ = self.ruleData['itIsOn']
        else:
            self.ruleData['itIsOn'] = []
            toggles_ = []
        toggles = list(self.data['toggles'].keys())
        tLen = len(toggles)
        i = 0
        while 1:
            layout1 = QHBoxLayout()
            for j in toggles[i:i+max_cols if i+max_cols < tLen else tLen]:
                tem = QCheckBox(j, self)
                if j in toggles_:
                    tem.setChecked(True)
                layout1.addWidget(tem)
            layout.addLayout(layout1)
            i += max_cols
            if i >= tLen:
                break
        tem = QPushButton('save', self)
        tem.clicked.connect(self.save)
        layout.addWidget(tem)
        self.setLayout(layout)
        self.show()

    def save(self):
        end = {'red':{}, 'blue':{}, 'green':{} , 'yellow':{}, 'itIson':[]}
        for i in self.findChildren(QComboBox):
            end[i.key][i.data] = i.currentText()
        for i in self.findChildren(QLineEdit):
            end[i.key][i.data] = i.text()
        tems = self.findChildren(QCheckBox)
        for i in tems[:16]:
            if i.isChecked():
                if 'enemy' not in end[i.data]:
                    end[i.data]['enemy'] = []
                end[i.data]['enemy'].append(i.text())
        for i in tems[16:]:
            if i.isChecked():
                end['itIson'].append(i.text())
        self.ruleData = end
        with open(self.path, 'w') as f:
            json.dump(self.ruleData, f)


if __name__ == '__main__':
    window = EditWin()
    # window = linesEditWin('E:\workspace\game\\resource\lines.json')
    # window = backupEditWin('E:\workspace\game\\resource\\tmp\\backup.json')
    # window = storyEditWin('E:\workspace\game\\resource\\tmp\\stories.json.json')
    # window = toggleEditWin('E:\workspace\game\\resource\\tmp\\toggles.json')

    window.show()
    sys.exit(Qapp.exec_())
# else:
#     window = QWidget()
#     for i in range(200):
#         for j in range(100):
#             tem_label = QLabel(window)
#             tem_label.move(i*20, j*20)
#             tem_label.setPixmap(resource.find({'usage':'geo', 'name':'tree'})['pixmap'].scaled(20,20))
#
#
#     window.show()
#     sys.exit(Qapp.exec_())
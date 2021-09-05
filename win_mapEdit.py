#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :main_window.py
# @Time      :2021/7/18 14:05
# @Author    :russionbear
import json, os, shutil

from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui
from map_load import VMap, Geo, DW, miniVMap
from tmap_load import TMap
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

        area = QScrollArea(self)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        frame = QWidget(self)
        frameHeight = ((len(resource.data) - 1) // self.row + 1) * self.blockSize[1]
        frame.setFixedSize(winSize[0]//blockSize[0]*blockSize[0], frameHeight)
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

            tem_geo = Geo(frame, newKey=i, mapId=i, brother=self)
            tem_geo.move(j%self.row*self.blockSize[0], j//self.row*self.blockSize[1])
        area.setWidget(frame)

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addSpacing(10)
        layout.addLayout(layout1)
        layout.addSpacing(20)
        layout.addLayout(layout2)
        layout.addWidget(area)

        keys = ['blood', 'oil', 'bullect', 'ocupied', 'isStealth', 'isDiving', 'loadings', 'supplies']
        keys_ = ['规模', '油量(%)', '弹药(%)', '占领', '隐身', '下潜', '装载', '补给']
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
        for i1, i in enumerate(keys[4:6]):
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
                key['usage'] = keys[i]
                key['flag'] = ''
                if keys[i] == 'geo':
                    enable(False)
                    self.swap(resource.findAll(key))
                    break
                key['flag'] = self.btn2_s[self.status[1]]
                enable(True)
                self.swap(resource.findAll(key))
                break
        # self.enableSlider(key['usage'])

    def swapBtn2(self, data):
        keys = ['geo', 'build', 'dw']
        for i, j in enumerate(self.btn2_s):
            if j == data:
                self.status[1] = i
                self.swap(resource.findAll({'flag':data, 'usage':keys[self.status[0]]}))
                break

    def swap(self, list):
        # print(list)
        fixedHeight = 400
        tem_child = self.findChild(QScrollArea)
        newHeight = ((len(list)-1)//self.row+1)*self.blockSize[1]
        tem_child.children()[0].children()[0].setFixedHeight(fixedHeight if newHeight <= fixedHeight else newHeight)
        shouldShow =[]
        for i in tem_child.children()[0].children()[0].children():
            if i.mapId in list:
                shouldShow.append(i)
                i.show()
            else:
                i.hide()
        for j, i in enumerate(shouldShow):
            i.move(j%self.row*self.blockSize[0], j//self.row*self.blockSize[1])

    def choose(self, mapId):
        for i in self.findChildren(QLabel):
            if hasattr(i, 'mapId'):
                if i.mapId == self.choosed:
                    i.choose(False)
                    break
        self.choosed = mapId
        if self.parent():
            if self.parent().parent():
                self.parent().parent().statusBar().showMessage(mapId['dsc'])

    def valueChange(self, label, value):
        text = label.text()
        text = text.split('：')[0] + '：' + str(value) + '%'
        label.setText(text)

    # def enableSlider(self, type):
    #     return
    #     sliders = [self.bloodSlider, self.oilSlider, self.bullectSlider]
    #     # values = [self.bloodValue, self. oilValue, self.bullectValue]
    #     if type == 'dw':
    #         for i in sliders:
    #             i.setEnabled(True)
    #     elif type == 'geo':
    #         for i in sliders:
    #             i.setEnabled(False)
    #     elif type == 'build':
    #         for i in sliders[1:]:
    #             i.setEnabled(False)
    #         sliders[0].setEnabled(True)

    # def getChoosedValue(self):
    #     if not self.choosed:
    #         return None
    #     track = self.choosed.copy()
    #     track['blood'] = int(self.bloodValue.text().split('%')[0].split('：')[1])/10
    #     track['oil'] = int(self.oilValue.text().split('%')[0].split('：')[1])/10
    #     track['bullect'] = int(self.bullectValue.text().split('%')[0].split('：')[1])/10
    #     return track

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
        if not self.choosed:
            return None
        if self.choosed['name'] == 'delete':
            # print(self.choosed)
            return {'track':self.choosed}
        if self.choosed['usage'] in ['geo', 'build']:
            return {'track':self.choosed}
        end = {'moved':False, 'moved':False, 'mapId':False}
        key1 = ['blood', 'oil', 'bullect', 'occupied', 'isStealth', 'isDiving', 'loadings', 'supplies']
        for i1, i in enumerate(self.dwInfo[0:4]):
            end[key1[i1]] = i.value()
        end[key1[4]] = self.dwInfo[4].isChecked()
        end[key1[5]] = self.dwInfo[5].isChecked()
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
        end[key1[6]] = loadings
        end[key1[7]] = self.choosedSupplies
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
        end['track'] = self.choosed
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


class EditMap(VMap):
    def __init__(self, name='default', parent=None, block=(100, 100), winSize=(800, 800), brother=None):
        super(EditMap, self).__init__(parent)
        self.brother = brother
        self.isTargetChoosing = False
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
                track = resource.findByHafuman(str(self.map['map'][i][j]))
                # print(track, str(self.map['map'][i][j]))
                if not track:
                    print('map error')
                    return
                tem_geo = Geo(self, track, (i, j))
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
            track = resource.findByHafuman(i['hafuman'])
            # for k in ['blood', 'oil', 'bullect', 'move']:
            #     if k in i:
            #         track[k] = i[k]

            # track['blood'] = i['blood']
            # track['oil'] = i['oil']
            # track['bullect'] = i['bullect']
            # track['moved'] = i['moved']
            axis = i['axis']
            # del i['axis']
            track.update(i)
            dw = DW(self)
            # print(track, axis)
            dw.initUI(track, axis)
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

    #地图修改
    def modify(self, areaGroup, tTrack):
        if tTrack == None:
            return
        newTrack = tTrack['track']
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
                if  i.mapId[0] >= x1 and i.mapId[0] <= x2 and i.mapId[1] >= y1 and i.mapId[1] <= y2 :
                    i.deleteLater()
            if newTrack['name'] == 'delete' :
                return
            for i in areaGroup:
                if int(resource.basicData['move'][newTrack['name']][self.pointer_geo[i.mapId[0]][i.mapId[1]].track['name']]) >= 99:
                    continue
                dw = DW(self)
                dw.initUI(newTrack, i.mapId)
                dw.scale(resource.mapScaleList[self.mapScalePoint])
                dw.move(i.x(), i.y())
                dw.updateByTrack(tTrack)
                dw.show()
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
                            j.change(track=resource.find({'usage':'geo', 'name':'road', 'flag':'', 'action':'center'}))
                        elif length == 3:
                            for p1 in direction_:
                                if p1 not in should:
                                    j.change(track=resource.find({'usage':'geo', 'name':'road', 'flag':'', 'action':'no-'+p1}))
                                    break
                        elif length == 2:
                            if 'top' in should and 'bottom' in should:
                                j.change(track=resource.find({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'vertical'}))
                            elif 'left' in should and 'right' in should:
                                j.change(track=resource.find({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'across'}))
                            else:
                                tem_dd = resource.find({'usage': 'geo', 'name': 'road', 'flag': '', 'action': should[0]+'-'+should[1]})
                                if not tem_dd:
                                    j.change(track=resource.find({'usage': 'geo', 'name': 'road', 'flag': '', 'action': should[1]+'-'+should[0]}))
                                else:
                                    j.change(track=tem_dd)
                        elif length == 1:
                            if should[0] in ['left', 'right']:
                                j.change(track=resource.find({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'across'}))
                            else:
                                j.change(track=resource.find({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'vertical'}))
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
                            j.change(track=resource.find({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'}))
                        elif length == 1:
                            if should[0] in ['left', 'right']:
                                j.change(track=resource.find({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'}))
                            else:
                                j.change(track=resource.find({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'vertical'}))
                        elif length == 2:
                            if 'left' in should and 'right' in should:
                                j.change(track=resource.find({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'}))
                            elif 'top' in should and 'bottom' in should:
                                j.change(track=resource.find({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'vertical'}))
                            else:
                                j.change(track=resource.find({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'}))
                        elif length == 3:
                            if 'left' in should and 'right' in should:
                                j.change(track=resource.find({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'}))
                            elif 'top' in should and 'bottom' in should:
                                j.change(track=resource.find({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'vertical'}))
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
                            j.change(track=resource.find({'usage':'geo', 'name':'sea', 'flag':'', 'action':'center'}))
                        elif length == 3:
                            for p1 in direction_:
                                if p1 not in should:
                                    j.change(track=resource.find({'usage':'geo', 'name':'sea', 'flag':'', 'action':'no-'+p1}))
                                    break
                        elif length == 2:
                            if 'top' in should and 'bottom' in should:
                                j.change(track=resource.find({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': 'across'}))
                            elif 'left' in should and 'right' in should:
                                j.change(track=resource.find({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': 'vertical'}))
                            else:
                                tem_dd = resource.find({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': should[0]+'-'+should[1]})
                                if not tem_dd:
                                    j.change(track=resource.find({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': should[1]+'-'+should[0]}))
                                else:
                                    j.change(track=tem_dd)
                        elif length == 1:
                            j.change(track=resource.find({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': should[0]}))
                        elif length == 0:
                            j.change(track=resource.find({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': ''}))
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
                            j.change(
                                track=resource.find({'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'center'}))
                        elif length == 3:
                            for p1 in direction_:
                                if p1 not in should:
                                    if p1 in ['left', 'right']:
                                        j.change(track=resource.find(
                                            {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'across'}))
                                    else:
                                        j.change(track=resource.find(
                                            {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'vertical'}))
                                    break
                        elif length == 2:
                            if 'top' in should and 'bottom' in should:
                                j.change(track=resource.find(
                                    {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'across'}))
                            elif 'left' in should and 'right' in should:
                                j.change(track=resource.find(
                                    {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'vertical'}))
                            else:
                                tem_dd = resource.find(
                                    {'usage': 'geo', 'name': 'river', 'flag': '', 'action': should[0] + '-' + should[1]})
                                if not tem_dd:
                                    j.change(track=resource.find({'usage': 'geo', 'name': 'river', 'flag': '',
                                                                  'action': should[1] + '-' + should[0]}))
                                else:
                                    j.change(track=tem_dd)
                        elif length == 1:
                            if should[0] in ['left', 'right']:
                                j.change(track=resource.find(
                                    {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'vertical'}))
                            else:
                                j.change(track=resource.find(
                                    {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'across'}))
                        elif length == 0:
                                j.change(track=resource.find(
                                    {'usage': 'geo', 'name': 'plain', 'flag': ''}))
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
                                track=resource.find({'usage': 'geo', 'name': 'plain', 'flag': ''}))
                        elif length == 2:
                            if 'top' in should and 'bottom' in should:
                                j.change(
                                    track=resource.find({'usage': 'geo', 'name': 'plain', 'flag': ''}))
                            elif 'left' in should and 'right' in should:
                                j.change(
                                    track=resource.find({'usage': 'geo', 'name': 'plain', 'flag': ''}))
                            else:
                                tem_dd = resource.find(
                                    {'usage': 'geo', 'name': 'sand', 'flag': '', 'action': should[0] + '-' + should[1]})
                                if not tem_dd:
                                    j.change(track=resource.find({'usage': 'geo', 'name': 'sand', 'flag': '',
                                                                  'action': should[1] + '-' + should[0]}))
                                else:
                                    j.change(track=tem_dd)
                        elif length == 1:
                            j.change(track=resource.find(
                                {'usage': 'geo', 'name': 'sand', 'flag': '', 'action': should[0]}))
                        elif length == 0:
                            j.change(
                                track=resource.find({'usage': 'geo', 'name': 'plain', 'flag': ''}))

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == 1 and not self.hasMove:
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
                    circle.setGeometry(self.pointer_geo[j[0]][j[1]].geometry())
                    self.targetChoosedLayer.append(circle)
            elif self.brother:
                if self.brother.choosed:
                    self.modify(end, self.brother.getChoosedData())

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
        if self.hasCircle or self.hasMove or self.isTargetChoosing:
            return
        self.mapScale(True if a0.angleDelta().y()>0 else False)

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Return:
            end = []
            for i in self.circled:
                end.append(tuple(i.mapId))
            self.parent().parent().targetChoosed(end)                
            for i in self.targetChoosedLayer:
                i.deleteLater()
            self.circled = []
            self.targetChoosedLayer = []
            self.isTargetChoosing = False
        elif a0.key() == Qt.Key_Escape:
            self.parent().parent().targetChoosed()             
            for i in self.targetChoosedLayer:
                i.deleteLater()
            self.targetChoosedLayer = []
            self.circled = []
            self.isTargetChoosing = False
        else:
            pass
        # a0.accept()
            # return super(EditMap, self).keyReleaseEvent(a0)

    def enterTargetChoose(self):
        self.isTargetChoosing = True

    def myUpdate(self):
        for j in self.findChildren(DW):
            if j:
                j.flush()
                j.myUpdate()

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
        self.initUI()

    def initUI(self, mapName='default'):
        mapMenu = self.menuBar().addMenu('地图')
        mapMenu.addAction('打开').triggered.connect(self.skimMap)
        mapMenu.addSeparator()
        mapMenu.addAction('新建').triggered.connect(self.newMap)
        mapMenu.addAction('修改').triggered.connect(self.modifyMap)
        mapMenu.addAction('保存').triggered.connect(self.saveMap)

        #加成， 英雄限制，目的限制， 资金， 最大支出， 台词，
        mapMenu = self.menuBar().addMenu('台词')
        mapMenu.addAction('浏览').triggered.connect(functools.partial(self.linesCpu, 'skim'))
        mapMenu.addAction('添加').triggered.connect(functools.partial(self.linesCpu, 'add'))
        mapMenu.addSeparator()
        mapMenu.addAction('组装').triggered.connect(functools.partial(self.linesCpu, 'zz'))

        mapMenu = self.menuBar().addMenu('游戏参数')
        mapMenu.addAction('基本参数').triggered.connect(functools.partial(self.basicDataCpu, 'basic'))
        mapMenu.addAction('备用参数').triggered.connect(functools.partial(self.basicDataCpu, 'skim'))
        mapMenu.addAction('保存').triggered.connect(functools.partial(self.basicDataCpu, 'save'))

        mapMenu = self.menuBar().addMenu('规则')
        mapMenu.addAction('故事背景').triggered.connect(functools.partial(self.ruleCpu, 'story'))
        mapMenu.addSeparator()
        mapMenu.addAction('胜利条件').triggered.connect(functools.partial(self.ruleCpu, 'role'))
        mapMenu.addAction('制作加成').triggered.connect(functools.partial(self.ruleCpu, 'powers'))
        mapMenu.addAction('制作触发器').triggered.connect(functools.partial(self.ruleCpu, 'plan'))

        mapMenu = self.menuBar().addMenu('素材')
        mapMenu.addAction('素材说明（不可用）').triggered.connect(functools.partial(self.sourceCpu, 'instruction'))
        mapMenu.addSeparator()
        mapMenu.addAction('图片').triggered.connect(functools.partial(self.sourceCpu, 'images'))
        mapMenu.addAction('音效').triggered.connect(functools.partial(self.sourceCpu, 'sounds'))

        self.pages = {}
        self.statusBar().showMessage('lalal')

        self.center = QWidget(self)
        self.tool = EditTool()
        self.tool.initUi(mainWin=self)
        self.vmap = EditMap(mapName, self.center, brother=self.tool)
        # self.vmap.initUI()
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addWidget(self.tool)
        layout.addWidget(self.vmap)
        self.center.setLayout(layout)
        # self.vmap.move(self.tool.width(), 0)
        self.setCentralWidget(self.center)

        self.modeLSView = self.modeSkim = self.modeModify = None
        # self.showLSView()
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
            self.modeSkim = SkimWin()
            self.modeSkim.initUI(brother=self, isModify=True)
            self.modeSkim.setWindowModality(Qt.ApplicationModal)
            self.modeSkim.show()
        else:
            self.modeModify = newWin()
            self.modeModify.initUI(brother=self, mapName=mapName, isNewMap=False)
            self.modeModify.setWindowModality(Qt.ApplicationModal)
            self.modeModify.show()

    def saveMap(self):
        tem_v = self.findChild(VMap)
        resource.saveMap(tem_v.collectMap())

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
        self.vmap = VMap()
        self.vmap.initUI(name, self.center, brother=self.tool)
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addWidget(self.tool)
        layout.addWidget(self.vmap)
        self.center.setLayout(layout)
        self.vmap.move(self.tool.width(), 0)
        self.setCentralWidget(self.center)

    def linesCpu(self, key, data=None):
        print(key, data)
        '''
            开战前
            主城附近，
            收入支出，
            故事背景
            局势，
            单位：侦查，补给，下潜，隐身，计划补给，体力，油量，弹药，攻击范围，所在地形，安全系数+可攻击目标，
            随机
        '''
        key1 = ['随机', '开战前', '主城附近', '收入不足', '收入充足', '收入过多', '支出过多', '支出过少', \
                '故事背景', '局势', '侦查到', '侦查没到', '下潜没被发现', '下潜被发现', '隐身被发现', '隐身没被发现', '计划补给', \
                '规模低', '规模充足', '油量低', '油量充足', '弹药低', '弹药充足', '近战', '远程', '移动攻击',  \
                '单位被困且危险', '单位被困但安全', '单位安全', '可攻击目标少', '可攻击目标多']
        key2 = ['random', 'beforebattle', 'nearhead', 'smallsalary', 'enoughsalary', 'muchsalary', \
                'storybackground', 'situation', 'watched', 'watching', 'diving', 'dived', 'stealthing', 'stealthed', \
                'plansupply', 'lessguimo', 'enoughguimo', 'lessoil', 'enoughoil', 'lessbullect', 'enoughbullect', \
                'shortrange', 'longrange', 'attackaftermove', 'trapped_danger', 'trapped_safe', 'untrapped', 'moretargets', 'lesstargets']

        for i in resource.findAll({'usage':'geo'}):
            if i['name'] not in key2:
                key2.append(i['name'])
                key1.append(resource.basicData['geo']['chineseName'][i['name']])
        for i in resource.findAll({'usage':'build', 'flag':'red'}):
            key2.append(i['name'])
            key1.append(resource.basicData['geo']['chineseName'][i['name']])
        for i in resource.findAll({'usage': 'dw', 'action': 'left', 'flag': 'red'}):
            key2.append(i['name'])
            key1.append(resource.basicData['money']['chineseName'][i['name']])

        if key == 'skim_double':
            if self.tmpView:
                try:
                    self.tmpView.deleteLater()
                except RuntimeError:
                    pass
            self.tmpView = QWidget()
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            self.tmpView.name = list(self.lines.keys())[data.row()]
            self.tmpView.data = self.lines[self.tmpView.name]
            self.tmpView.setWindowTitle('台词《'+self.tmpView.name+'》')
            # print(self.lines.keys())
            layout1 = QHBoxLayout()
            tem = QComboBox(self.tmpView)
            tem.before = key1[0]
            tem.isconnected = True
            tem.currentIndexChanged.connect(functools.partial(self.linesCpu, 'add_modify'))
            tem.addItems(key1)
            layout1_1 = QHBoxLayout()
            layout1_1.addWidget(tem)
            tem = QPushButton('上一个', self.tmpView)
            tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', 1))
            layout1_1.addWidget(tem)
            tem = QPushButton('下一个', self.tmpView)
            tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', -1))
            layout1_1.addWidget(tem)
            layout1.addLayout(layout1_1)
            tem = QPushButton('ok', self.tmpView)
            tem.clicked.connect(functools.partial(self.linesCpu, 'add_ok'))
            layout1.addWidget(tem)
            layout = QHBoxLayout()
            layout.addLayout(layout1)
            tem = QTextEdit(self.tmpView)
            # tem.setReadOnly(True)
            layout.addWidget(tem)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
            self.tmpView.findChild(QComboBox).setCurrentIndex(0)

        elif key == 'skim':
            if self.tmpView:
                try:
                    self.tmpView.deleteLater()
                except RuntimeError:
                    pass
            self.tmpView = QListWidget()
            self.tmpView.setWindowTitle('浏览')
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            self.tmpView.addItems(self.lines.keys())
            print(self.lines.keys())
            self.tmpView.show()
            self.tmpView.doubleClicked.connect(functools.partial(self.linesCpu, 'skim_double'))

        elif key == 'add':
            if self.tmpView:
                try:
                    self.tmpView.deleteLater()
                except RuntimeError:
                    pass
            self.tmpView = QWidget()
            self.tmpView.setWindowTitle('添加台词')
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            end = {}
            for i in key2:
                end[i] = []
            self.tmpView.data = end
            layout1 = QHBoxLayout()
            tem = QLineEdit(self.tmpView)
            tem.setPlaceholderText('名称')
            layout1.addWidget(tem)
            tem = QComboBox(self.tmpView)
            tem.before = key1[0]
            tem.isconnected = True
            tem.currentIndexChanged.connect(functools.partial(self.linesCpu, 'add_modify'))
            tem.addItems(key1)
            layout1_1 = QHBoxLayout()
            layout1_1.addWidget(tem)
            tem = QPushButton('上一个', self.tmpView)
            tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', 1))
            layout1_1.addWidget(tem)
            tem = QPushButton('下一个', self.tmpView)
            tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', -1))
            layout1_1.addWidget(tem)
            layout1.addLayout(layout1_1)
            tem = QPushButton('ok', self.tmpView)
            tem.clicked.connect(functools.partial(self.linesCpu, 'add_ok'))
            layout1.addWidget(tem)
            layout = QHBoxLayout()
            layout.addLayout(layout1)
            tem = QTextEdit(self.tmpView)
            # tem.setReadOnly(True)
            layout.addWidget(tem)
            self.tmpView.setLayout(layout)
            self.tmpView.show()

        elif key == 'add_updown':
            com = self.tmpView.findChild(QComboBox)
            com.isconnected = False
            view = self.tmpView.findChild(QTextEdit)
            id = com.currentText()
            for i1, i in enumerate(key1):
                if i == id:
                    break
            com.before = id
            id = key2[i1]
            self.tmpView.data[id] = view.toPlainText().split('\n')
            if data == 1:
                if com.currentIndex() == 0:
                    return
                com.setCurrentIndex(com.currentIndex()-1)
                text = ''
                for i in self.tmpView.data[key2[com.currentIndex()]]:
                    text += '\n' + i
                view.setText(text)
            else:
                if com.currentIndex() == len(key2) -1:
                    return
                com.setCurrentIndex(com.currentIndex()+1)
                text = ''
                for i in self.tmpView.data[key2[com.currentIndex()]]:
                    text += '\n' + i
                view.setText(text)
            # com.currentIndexChanged.disconnect(functools.partial(self.linesCpu, 'add_modify'))

        elif key == 'add_modify':
            com = self.tmpView.findChild(QComboBox)
            view = self.tmpView.findChild(QTextEdit)
            if not com.isconnected:
                com.isconnected = True
                return
            id_ = com.before
            for i1, i in enumerate(key1):
                if i == id_:
                    break
            try:
                self.tmpView.data[key2[i1]] = view.toPlainText().split('\n')
            except AttributeError:
                return
            id = com.currentText()
            for i1, i in enumerate(key1):
                if i == id:
                    break
            com.before = id
            id = key2[i1]
            text = ''
            for i in self.tmpView.data[id]:
                text +=  i +'\n'
            view.setText(text)

        elif key == 'add_ok':
            id = self.tmpView.findChild(QComboBox).currentText()
            for i1, i in enumerate(key1):
                if i == id:
                    break
            id = key2[i1]
            self.tmpView.data[id] = self.tmpView.findChild(QTextEdit).toPlainText().split('\n')
            #%%%%%%
            for i1, i in self.tmpView.data.items():
                newData = []
                for j in i:
                    if j != '':
                        newData.append(j)
                self.tmpView.data[i1] = newData
            print(self.tmpView.data)
            if self.tmpView.findChild(QLineEdit):
                self.lines[self.tmpView.findChild(QLineEdit).text()] = self.tmpView.data
            else:
                self.lines[self.tmpView.name] = self.tmpView.data
            self.tmpView.deleteLater()
            resource.saveMap(self.vmap.map['name'], lines=self.lines)
        elif key == 'zz':
            if not self.roles:
                return
            if self.tmpView:
                try:
                    self.tmpView.deleteLater()
                except RuntimeError:
                    pass
            self.tmpView = QWidget()
            self.tmpView.setWindowTitle('组装台词')
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            layout1 = QVBoxLayout()
            items = self.roles.keys()
            for i in items:
                tem = QPushButton('    ', self.tmpView)
                tem.setStyleSheet('background-color:'+str(i)+';')
                layout1.addWidget(tem)
            tem = QPushButton('ok', self.tmpView)
            tem.clicked.connect(functools.partial(self.linesCpu, 'zz_ok'))
            layout1.addWidget(tem)
            layout2 = QVBoxLayout()
            for i in items:
                tem = QComboBox(self.tmpView)
                tem.addItem('')
                tem.addItems(self.lines.keys())
                tem.flag = i
                layout2.addWidget(tem)
            layout = QHBoxLayout()
            layout.addLayout(layout1)
            layout.addLayout(layout2)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
        elif key == 'zz_ok':
            items = self.tmpView.findChildren(QComboBox)
            for i in items:
                self.roles[i.flag] = i.currentText()
            self.tmpView.deleteLater()

    def basicDataCpu(self, key, data=None):
        if key == 'skim':
            if self.tmpView:
                try:
                    self.tmpView.deleteLater()
                except RuntimeError:
                    pass
            self.tmpView = QWidget()
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            self.tmpView.setWindowTitle('备用参数')
            layout = QVBoxLayout()
            tem = QListWidget(self.tmpView)
            if os.path.exists('maps/'+self.vmap.map['name']+'/basicInfo_.json'):
                with open('maps/'+self.vmap.map['name']+'/basicInfo_.json', 'r') as f:
                    self.basicData_ = json.load(f)
                tem.addItems(list(self.basicData_.keys()))
            else:
                with open('maps/' + self.vmap.map['name'] + '/basicInfo_.json', 'w') as f:
                    json.dump({}, f)
            tem.doubleClicked.connect(functools.partial(self.basicDataCpu, 'double'))
            layout.addWidget(tem)
            layout_ = QHBoxLayout()
            tem = QPushButton('删除', self.tmpView)
            tem.clicked.connect(functools.partial(self.basicDataCpu, 'delete'))
            layout_.addWidget(tem)
            layout_.addSpacing(30)
            layout.addWidget(QLineEdit(self.tmpView))
            tem = QPushButton('添加', self.tmpView)
            tem.clicked.connect(functools.partial(self.basicDataCpu, 'add'))
            layout_.addWidget(tem)
            layout.addLayout(layout_)
            self.tmpView.setLayout(layout)
            self.tmpView.show()

        elif key == 'basic':
            # self.isTmpBasicDataBak = False
            if self.tmpView:
                try:
                    self.tmpView.deleteLater()
                except RuntimeError:
                    pass
            if not os.path.exists('maps/'+self.vmap.map['name']+'/basicInfo.json'):
                shutil.copy('resource/basicInfo.json', 'maps/'+self.vmap.map['name']+'/basicInfo.json')
            self.tmpView = basicEditW('maps/'+self.vmap.map['name']+'/basicInfo.json')
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            self.tmpView.setWindowTitle('基本参数')
            self.tmpView.show()

        elif key == 'delete':
            tem = self.tmpView.findChild(QListWidget)
            data = tem.currentIndex().row()
            # QModelIndex.row()
            print(data)
            if data < 0:
                return
            del self.basicData_[tem.item(data).text()]
            tem.takeItem(data)
            self.basicDataCpu('save')
        elif key == 'add':
            if self.tmpBasicKey != None:
                with open('resource/tmp/basicInfo.json', 'r') as f:
                    self.basicData_[self.tmpBasicKey] = json.load(f)
            title = self.tmpView.findChild(QLineEdit).text()
            if title in self.basicData_ or title == '':
                return
            self.tmpBasicKey = title
            self.basicData_[title] = {}
            with open('resource/tmp/basicInfo.json', 'w') as f:
                json.dump(self.basicData_[title], f)
            self.tmpView.deleteLater()
            self.tmpView = basicEditW('resource/tmp/basicInfo.json')
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            self.tmpView.setWindowTitle('添加备用配置')
            self.tmpView.show()

        elif key == 'double':
            if self.tmpBasicKey != None:
                with open('resource/tmp/basicInfo.json', 'r') as f:
                    self.basicData_[self.tmpBasicKey] = json.load(f)
            if data == -1:
                return
            text = self.tmpView.findChild(QListWidget).item(data).text()
            self.tmpBasicKey = text
            with open('resource/tmp/basicInfo.json', 'w') as f:
                json.dump(self.basicData_[text], f)
            self.tmpView.deleteLater()
            # with open('resource/tmp/basicInfo.json', 'w') as f:
            #     json.dump(self.basicData_[text], f)
            self.tmpView = basicEditW('resource/tmp/basicInfo.json')
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            self.tmpView.setWindowTitle('备用参数')

        elif key == 'save':
            if self.tmpBasicKey != None:
                with open('resource/tmp/basicInfo.json', 'r') as f:
                    self.basicData_[self.tmpBasicKey] = json.load(f)
            # for i in list(self.basicData_.keys()):
            #     for j in list(self.basicData_[i].keys()):
            #         for k in list(self.basicData_[i][j].keys()):
            #             if self.basicData_[i][j][k] == '':
            #                 del self.basicData_[i][j][k]
            #                 print(333)
            #         if self.basicData_[i][j] == {}:
            #             del self.basicData_[i][j]
            #             print(2222)
                # if self.basicData_[i] == {}:
                #     del self.basicData_[i]
                #     print('fsd111')

            with open('maps/'+self.vmap.map['name']+'/basicInfo_.json', 'w') as f:
                json.dump(self.basicData_, f)

    def ruleCpu(self, key, data=None):
        print(key, data)
        key1 = ['单位阵亡', '建筑被占领', '军队进入区域', '资金损失', '制造的损失', '到达指定回合']
        key2 = ['beattack', 'beoccupy', 'beinarea', 'maxloss', 'mindamage', 'atbout']
        key3 = ['区域内单位阵亡', '区域内添加单位', '指定单位阵亡', '修改建筑所属', '修改区域内单位所属', '修改指定单位所属', '资金增减', '资金修改', '修改加成']
        key4 = ['areadeath', 'areasupport', 'death', 'modifybuildflag', 'areadwflag', 'money_', 'money', 'jc']
        if key == 'story':
            if self.tmpView:
                self.tmpView.deleteLater()
            self.tmpView = QWidget()
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            self.tmpView.data = {'red': {'command':'', 'heros':[]}, 'blue':{'command':'', 'heros':[]}, 'green':{'command':'', 'heros':[]}, 'yellow':{'command':'', 'heros':[]}}
            self.tmpView.now = 'red'
            layout = QHBoxLayout()
            layout_ = QVBoxLayout()
            tem_ = QComboBox(self.tmpView)
            tem_.addItems(['1', '2', '3', '4'])
            tem_.setCurrentIndex(3)
            tem_.currentIndexChanged.connect(functools.partial(self.ruleCpu, 'story_roles'))
            layout_.addWidget(tem_)
            for i in ['red', 'blue', 'green', 'yellow']:
                tem_ = QPushButton('    ', self.tmpView)
                tem_.clicked.connect(functools.partial(self.ruleCpu, 'story_role', i))
                tem_.setStyleSheet('background-color:'+i+';')
                layout_.addWidget(tem_)
            tem_ = QTextEdit(self.tmpView)
            tem_.setPlaceholderText('故事背景')
            layout.addWidget(tem_)
            layout.addLayout(layout_)
            layout_1 = QVBoxLayout()
            tem_ = QTextEdit(self.tmpView)
            tem_.setPlaceholderText('为角色设定任务')
            layout_1.addWidget(tem_)
            layout_3 = QVBoxLayout()
            tem_ = QComboBox(self.tmpView)
            tem_.addItem('全部英雄')
            for i in resource.findAll({'usage':'hero', 'action':'head'}):
                tem_.addItem(QIcon(i['pixmap']), i['name'])
            tem_.currentIndexChanged.connect(functools.partial(self.ruleCpu, 'story_hero'))
            layout_3.addWidget(tem_)
            tem_ = QPushButton('重置', self.tmpView)
            tem_.clicked.connect(functools.partial(self.ruleCpu, 'story_clear'))
            layout_3.addWidget(tem_)
            # tem_ = QComboBox(self.tmpView)
            # for i in ['阻拦', '抵达', '保护', '击杀', '占领', '防守', '']
            layout_2 = QHBoxLayout()
            layout_2.addLayout(layout_3)
            tem_ = QListWidget(self.tmpView)
            for i in resource.findAll({'usage':'hero', 'action':'head'}):
                tem_.addItem(QListWidgetItem(QIcon(i['pixmap']), i['name']))
            layout_2.addWidget(tem_)
            layout_1.addLayout(layout_2)
            tem_ = QPushButton('OK', self.tmpView)
            tem_.clicked.connect(functools.partial(self.ruleCpu, 'story_save'))
            layout_1.addWidget(tem_)
            layout.addLayout(layout_1)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
        elif key == 'story_roles':
            self.tmpView.data[self.tmpView.now]['command'] = self.tmpView.findChildren(QTextEdit)[1].toPlainText()
            heros = []
            view = self.tmpView.findChild(QListWidget)
            for i in range(view.count()):
                heros.append(view.item(i).text())
            self.tmpView.data[self.tmpView.now]['heros'] = heros
            children = self.tmpView.findChildren(QPushButton)[0:4]
            for i in children[0:data+1]:
                i.show()
            for i in children[data+1:]:
                i.hide()
            self.tmpView.findChildren(QTextEdit)[1].setText(self.tmpView.data['red']['command'])
            self.tmpView.now = 'red'
            view.clear()
            for i in self.tmpView.data['red']['heros']:
                view.addItem(QListWidgetItem(QIcon(resource.find({'usage':'hero', 'name':i, 'action':'head'})['pixmap']), i))
        elif key == 'story_role':
            self.tmpView.data[self.tmpView.now]['command'] = self.tmpView.findChildren(QTextEdit)[1].toPlainText()
            heros = []
            view = self.tmpView.findChild(QListWidget)
            for i in range(view.count()):
                heros.append(view.item(i).text())
            self.tmpView.data[self.tmpView.now]['heros'] = heros
            self.tmpView.now = data
            self.tmpView.findChildren(QTextEdit)[1].setText(self.tmpView.data[data]['command'])
            view.clear()
            for i in self.tmpView.data[data]['heros']:
                view.addItem(QListWidgetItem(QIcon(resource.find({'usage':'hero', 'name':i, 'action':'head'})['pixmap']), i))
        elif key == 'story_hero':
            name = self.tmpView.findChildren(QComboBox)[1].currentText()
            view = self.tmpView.findChild(QListWidget)
            if name == '全部英雄':
                view.clear()
                for i in resource.findAll({'usage':'hero', 'action':'head'}):
                    view.addItem(QListWidgetItem(QIcon(i['pixmap']), i['name']))
                return
            for i in range(view.count()):
                if view.item(i).text() == name:
                    return
            view.addItem(QListWidgetItem(QIcon(resource.find({'usage':'hero', 'name':name, 'action':'head'})['pixmap']), name))
        elif key == 'story_clear':
            view = self.tmpView.findChild(QListWidget)
            view.clear()
            self.tmpView.data[self.tmpView.now]['heros'] = []
        elif key == 'story_save':
            self.tmpView.data[self.tmpView.now]['command'] = self.tmpView.findChildren(QTextEdit)[1].toPlainText()
            heros = []
            view = self.tmpView.findChild(QListWidget)
            for i in range(view.count()):
                heros.append(view.item(i).text())
            self.tmpView.data[self.tmpView.now]['heros'] = heros
            dd = int(self.tmpView.findChild(QComboBox).currentText())
            self.roles = {}
            bg = self.tmpView.findChildren(QTextEdit)[0].toPlainText()
            for i, j in self.tmpView.data.items():
                if dd <= 0:
                    break
                self.tmpView.data[i]['command_bg'] = bg
                dd -= 1
            self.roles = self.tmpView.data
            self.tmpView.close()

        elif key == 'role':
            if self.tmpView:
                self.tmpView.deleteLater()
            if not self.roles:
                return
            self.tmpView = QWidget()
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            self.tmpView.setWindowTitle('设定目标')
            layout = QVBoxLayout()
            layout_ = QHBoxLayout()
            for i in ['目标类型','阻拦', '抵达', '保护', '击杀', '占领', '防守', '最大资金损失', '最小敌军损失']:
                layout_.addWidget(QLabel(i))
            layout.addLayout(layout_)
            for i in self.roles.keys():
                layout_ = QHBoxLayout()
                tem_btn = QPushButton(' 重置 ', self.tmpView)
                tem_btn.setStyleSheet('background-color:'+i+';')
                tem_btn.clicked.connect(functools.partial(self.ruleCpu, 'role_reset', i))
                layout_.addWidget(tem_btn)
                tem_btn = QPushButton('选择区域', self.tmpView)
                tem_btn.flag = i
                tem_btn.clicked.connect(functools.partial(self.ruleCpu, 'role_choose', tem_btn))
                layout_.addWidget(tem_btn)
                tem_btn = QPushButton('选择区域', self.tmpView)
                tem_btn.flag = i
                tem_btn.clicked.connect(functools.partial(self.ruleCpu, 'role_choose', tem_btn))
                layout_.addWidget(tem_btn)
                tem_btn = QPushButton('选择单位', self.tmpView)
                tem_btn.flag = i
                tem_btn.clicked.connect(functools.partial(self.ruleCpu, 'role_choose', tem_btn))
                layout_.addWidget(tem_btn)
                tem_btn = QPushButton('选择单位', self.tmpView)
                tem_btn.flag = i
                tem_btn.clicked.connect(functools.partial(self.ruleCpu, 'role_choose', tem_btn))
                layout_.addWidget(tem_btn)
                tem_btn = QPushButton('选择建筑', self.tmpView)
                tem_btn.flag = i
                tem_btn.clicked.connect(functools.partial(self.ruleCpu, 'role_choose', tem_btn))
                layout_.addWidget(tem_btn)
                tem_btn = QPushButton('选择建筑', self.tmpView)
                tem_btn.flag = i
                tem_btn.clicked.connect(functools.partial(self.ruleCpu, 'role_choose', tem_btn))
                layout_.addWidget(tem_btn)
                # layout_.addWidget(QPushButton('选择区域', self.tmpView))
                # layout_.addWidget(QPushButton('选择单位', self.tmpView))
                # layout_.addWidget(QPushButton('选择单位', self.tmpView))
                # layout_.addWidget(QPushButton('选择建筑', self.tmpView))
                # layout_.addWidget(QPushButton('选择建筑', self.tmpView))
                tem_btn = QSpinBox(self.tmpView)
                tem_btn.flag = i
                tem_btn.setSingleStep(1000)
                tem_btn.setMinimum(-1)
                tem_btn.setMaximum(999999999)
                tem_btn.setValue(-1)
                layout_.addWidget(tem_btn)
                tem_btn = QSpinBox(self.tmpView)
                tem_btn.flag = i
                tem_btn.setSingleStep(1000)
                tem_btn.setMinimum(-1)
                tem_btn.setValue(-1)
                tem_btn.setMaximum(999999999)
                layout_.addWidget(tem_btn)
                layout.addLayout(layout_)
            tem_btn = QPushButton('ok', self.tmpView)
            tem_btn.clicked.connect(functools.partial(self.ruleCpu, 'role_ok'))
            layout.addWidget(tem_btn)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
        elif key == 'role_choose':
            self.tmpView.choose = data
            self.vmap.enterTargetChoose()
            self.tmpView.hide()
        elif key == 'role_reset':
            end = []
            for i1, i in enumerate(self.roles.keys()):
                if i == data:
                    for j in self.tmpView.children():
                        if hasattr(j, 'flag'):
                            end.append(j)
                    break
            for i in end[0:6]:
                i.data = None
            end[0].setText('选择区域')
            end[1].setText('选择区域')
            end[2].setText('选择单位')
            end[3].setText('选择单位')
            end[4].setText('选择建筑')
            end[5].setText('选择建筑')
            end[6].setValue(-1)
            end[7].setValue(-1)
        elif key == 'role_ok':
            end = {}
            for i in self.roles.keys():
                end[i] = []
            for i in self.tmpView.findChildren((QPushButton, QSpinBox)):
                if hasattr(i, 'flag'):
                    end[i.flag].append(i)
            typeForCF = ['inarea', 'beinarea', 'beattack', 'attack', 'occupy', 'beoccupy', 'maxloss', 'mindamage']
            for i, j in end.items():
                for j1, j2 in enumerate(j[:-3]):
                    if j2.text() == '已选择':
                        cf = {'type':typeForCF[j1], 'owner':i, 'data':j2.data}
                        self.CF.append(cf)
                for j1, j2 in enumerate(j[-2:]):
                    if j2.value() != -1:
                        cf = {'type':typeForCF[j1+6], 'owner':i, 'data':j2.value()}
                        self.CF.append(cf)
            ## toggle:{type, data, ower}
            # print(self.CF)
            self.tmpView.deleteLater()

        elif key == 'powers':
            if self.tmpView:
                self.tmpView.deleteLater()
            MAX = 8
            self.tmpView = QWidget()
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            self.tmpView.setWindowTitle('制作加成')
            tem_table = QTableWidget(self.tmpView)
            dws = resource.findAll({'usage':'dw', 'flag':'red', 'action':'left'})
            tem_table.setColumnCount(len(dws)+1)
            tem_table.setRowCount(MAX)
            tem_table.setHorizontalHeaderItem(0, QTableWidgetItem('id'))
            for i, j in enumerate(dws):
                tem_table.setHorizontalHeaderItem(i+1, QTableWidgetItem(QIcon(j['pixmap']), j['name']))
            for i in range(MAX):
                for j in range(len(dws)+1):
                    tem_table.setItem(i, j, QTableWidgetItem(''))
            layout = QVBoxLayout()
            layout.addWidget(QLabel('加成的影响范围'))
            layout.addWidget(tem_table)
            tem_table = QTableWidget(self.tmpView)
            dws = ['move_distance', 'view_distance', 'gf_g', 'gf_maxdistance', 'gf_mindistance', 'dsc']
            tem_table.setColumnCount(len(dws)+1)
            tem_table.setRowCount(MAX)
            tem_table.setHorizontalHeaderItem(0, QTableWidgetItem('id'))
            for i, j in enumerate(dws):
                tem_table.setHorizontalHeaderItem(i + 1, QTableWidgetItem(j))
            for i in range(MAX):
                for j in range(len(dws) + 1):
                    tem_table.setItem(i, j, QTableWidgetItem(''))
            layout.addWidget(QLabel('加成的实体'))
            layout.addWidget(tem_table)
            tem_table = QPushButton('ok', self.tmpView)
            tem_table.clicked.connect(functools.partial(self.ruleCpu, 'powers_ok'))
            layout.addWidget(tem_table)
            self.tmpView.setLayout(layout)
            self.tmpView.resize(800 ,400)
            self.tmpView.show()
            tables = self.tmpView.findChildren(QTableWidget)
            for i, j in enumerate(self.JC.keys()):
                tables[0].item(i, 0).setText(j)
                tables[1].item(i, 0).setText(j)
            for i1, i in enumerate(self.JC.keys()):
                for j in range(1, tables[1].columnCount()):
                    if tables[1].horizontalHeaderItem(j).text() in self.JC[i]:
                        tables[1].item(i1, j).setText(str(self.JC[i][tables[1].horizontalHeaderItem(j).text()]))
                for j in range(1, tables[0].columnCount()):
                    if tables[0].horizontalHeaderItem(j).text() in self.JC[i]['range']:
                        tables[0].item(i1, j).setText('1')
        elif key == 'powers_ok':
            self.JC = {}
            self.tmpView.setWindowTitle('制作加成')
            tables = self.tmpView.findChildren(QTableWidget)
            for i in range(tables[1].rowCount()):
                tem_data = tables[1].item(i, 0).text()
                if tem_data == '':
                    continue
                self.JC[tem_data] = {}
                for j in range(1, tables[1].columnCount()):
                    try:
                        tem_data_1 = int(tables[1].item(i, j).text())
                    except ValueError:
                        if tables[1].item(i, j).text() != '':
                            self.tmpView.setWindowTitle('制作加成;error:格式不符')
                            return
                        continue
                    if tem_data_1 == 0:
                        continue
                    self.JC[tem_data][tables[1].horizontalHeaderItem(j).text()] = tem_data_1

            for i in range(tables[0].rowCount()):
                tem_data = tables[0].item(i, 0).text()
                if tem_data == '':
                    continue
                try:
                    self.JC[tem_data]['range'] = []
                except KeyError:
                    self.tmpView.setWindowTitle('制作加成;error:上下id不对应')
                    return
                for j in range(1, tables[0].columnCount()):
                    tem_data_1 = tables[0].item(i, j).text()
                    if tem_data_1 == '1':
                        self.JC[tem_data]['range'].append(tables[0].horizontalHeaderItem(j).text())
            self.tmpView.deleteLater()

        elif key == 'plan':
            if self.tmpView:
                self.tmpView.deleteLater()
            if not self.roles:
                return
            self.tmpView = QWidget()
            self.tmpView.setWindowTitle('制作触发器')
            self.tmpView.setWindowModality(Qt.ApplicationModal)
            tem = QComboBox(self.tmpView)
            tem.addItems(['单位阵亡', '建筑被占领', '敌军进入区域', '资金损失', '制造的损失', '到达指定回合'])
            tem.currentIndexChanged.connect(functools.partial(self.ruleCpu, 'plan_type'))
            layout_1 = QHBoxLayout()
            layout_1.addWidget(QLabel('触发类型：'))
            layout_1.addWidget(tem)
            tem = QComboBox(self.tmpView)
            tem.addItems(self.roles.keys())
            layout_1.addWidget(QLabel('触发对象所属：'))
            layout_1.addWidget(tem)
            tem = QPushButton('选择', self.tmpView)
            tem.type = 'toggle'
            tem.clicked.connect(functools.partial(self.ruleCpu, 'plan_choose', tem))
            layout_1.addWidget(tem)
            tem = QSpinBox(self.tmpView)
            tem.setMaximum(999999999)
            layout_1.addWidget(tem)
            layout1 = QVBoxLayout()
            tem = QLineEdit(self.tmpView)
            layout_1_ = QHBoxLayout()
            layout_1_.addWidget(QLabel('触发器id'))
            layout_1_.addWidget(tem)
            tem = QLineEdit(self.tmpView)
            # layout_1_1 = QHBoxLayout()
            layout_1_.addWidget(QLabel('触发器描述'))
            layout_1_.addWidget(tem)
            layout1.addLayout(layout_1_)
            # layout1.addLayout(layout_1_1)
            layout1.addLayout(layout_1)

            tem = QComboBox(self.tmpView)
            tem.addItems(['区域内单位阵亡', '区域内添加单位', '指定单位阵亡', '修改建筑所属', '修改区域内单位所属', '修改指定单位所属', '资金增减', '资金修改', '修改加成'])
            tem.currentIndexChanged.connect(functools.partial(self.ruleCpu, 'plan_event'))
            layout_1 = QHBoxLayout()
            layout_1.addWidget(QLabel('事件类型：'))
            layout_1.addWidget(tem)
            tem = QComboBox(self.tmpView)
            tem.addItems(self.roles.keys())
            layout_1.addWidget(QLabel('事件对象所属：'))
            layout_1.addWidget(tem)
            tem = QPushButton('选择', self.tmpView)
            tem.type = 'event'
            tem.clicked.connect(functools.partial(self.ruleCpu, 'plan_choose', tem))
            layout_1.addWidget(tem)
            tem = QSpinBox(self.tmpView)
            tem.setMaximum(999999999)
            tem.setMinimum(-999999999)
            tem.setSingleStep(1000)
            layout_1.addWidget(tem)
            tem = QComboBox(self.tmpView)
            tem.addItem('')
            for i, j in enumerate(self.JC):
                tem.addItem(i+'  '+j['dsc'])
            layout_1.addWidget(tem)
            layout1.addLayout(layout_1)
            layout_1 = QHBoxLayout()
            tem = QPushButton('重置', self.tmpView)
            tem.clicked.connect(functools.partial(self.ruleCpu, 'plan_reset'))
            layout_1.addWidget(tem)
            tem = QPushButton('添加触发', self.tmpView)
            tem.clicked.connect(functools.partial(self.ruleCpu, 'plan_add'))
            layout_1.addWidget(tem)
            layout1.addLayout(layout_1)

            layout2 = QVBoxLayout()
            tem = QListWidget(self.tmpView)
            tem.doubleClicked.connect(functools.partial(self.ruleCpu, 'plan_double'))
            layout2.addWidget(tem)
            tem = QPushButton('删除触发', self.tmpView)
            tem.clicked.connect(functools.partial(self.ruleCpu, 'plan_delete'))
            layout2.addWidget(tem)

            layout = QHBoxLayout()
            layout.addLayout(layout1)
            layout.addLayout(layout2)
            self.tmpView.setLayout(layout)
            self.tmpView.show()
            self.ruleCpu('plan_type', 0)
            self.ruleCpu('plan_event', 0)
        elif key == 'plan_choose':
            self.tmpView.choose = data
            self.vmap.enterTargetChoose()
            self.tmpView.hide()
        elif key == 'plan_type':
            btn = self.tmpView.findChild(QPushButton)
            spin = self.tmpView.findChild(QSpinBox)
            if data < 3:
                btn.show()
                spin.hide()
            else:
                btn.hide()
                spin.show()
        elif key == 'plan_event':
            btn = self.tmpView.findChildren(QPushButton)[1]
            spin = self.tmpView.findChildren(QSpinBox)[1]
            com = self.tmpView.findChildren(QComboBox)[-1]
            btn.hide()
            spin.hide()
            com.hide()
            if data < 6:
                btn.show()
            elif data < 8:
                spin.show()
            else:
                com.show()
        elif key == 'plan_reset':
            for i in self.tmpView.findChildren(QLineEdit):
                i.setText('')
            for i in self.tmpView.findChildren(QPushButton):
                if i.text() == '已选择':
                    i.data = None
                    i.setText('选择')
            for i in self.tmpView.findChildren(QSpinBox):
                i.setValue(0)
        elif key == 'plan_add':
            coms = self.tmpView.findChildren(QComboBox)
            btns = self.tmpView.findChildren(QPushButton)
            if self.tmpView.findChild(QLineEdit).text() == '':
                return
            if not btns[0].isHidden() and not hasattr(btns[0], 'data'):
                return
            if not btns[1].isHidden() and not hasattr(btns[1], 'data'):
                return
            tem_data = coms[0].currentText()
            for i, j in enumerate(key1):
                if j == tem_data:
                    break
            cf = {'type':key2[i]}
            if i < 3:
                cf['data'] = self.tmpView.choose.data
            else:
                cf['data'] = self.tmpView.findChild(QSpinBox).value()
                cf['owner'] = coms[1].currentText()

            tem_data = coms[2].currentText()
            for i, j in enumerate(key3):
                if j == tem_data:
                    break
            cf['eventtype'] = key4[i]
            cf['eventowner'] = coms[3].currentText()
            if i < 6:
                cf['eventdata'] = self.tmpView.choose.data
            elif i < 8:
                cf['eventdata'] = self.tmpView.findChildren(QSpinBox)[1].value()
            else:
                tem_dd = coms[4].currentIndex()
                if tem_dd == 0:
                    cf['eventdata'] = ''
                else:
                    cf['eventdata'] = self.JC.keys()[tem_dd]
            lines = self.tmpView.findChildren(QLineEdit)
            cf['id'] = lines[1].text()
            for i1, i in enumerate(self.CF_):
                if i['id'] == cf['id']:
                    self.CF_.pop(i1)
                    tem = self.tmpView.findChild(QListWidget)
                    for j in range(tem.count()):
                        if tem.item(j).id == cf['id']:
                            tem.takeItem(j)
                            break
            if lines[0].text() == '0':
                cf['dsc'] = ''
            else:
                cf['dsc'] = lines[0].text()
            tem_data = QListWidgetItem(cf['id']+'  '+cf['dsc'])
            tem_data.id = cf['id']
            print(cf, lines[0].text(), lines[1].text())
            self.tmpView.findChild(QListWidget).addItem(tem_data)
            self.CF_.append(cf)
        elif key == 'plan_delete':
            tem = self.tmpView.findChild(QListWidget)
            data = tem.currentIndex()
            if data == -1:
                return
            item = tem.item(data).id
            for i1, i in enumerate(self.CF_):
                if i['id'] == item:
                    self.CF_.pop(i1)
                    break
            tem.takeItem(data)
        ##%%%%%%%%%
        elif key == 'plan_double':
            return
            if data.row() == -1:
                return
            data = data.row()
            print(data)
            # abc = QtCore.QModelIndex
            # abc.
            tem = self.tmpView.findChild(QListWidget)
            coms = self.tmpView.findChildren(QComboBox)
            btns = self.tmpView.findChildren(QPushButton)
            lines = self.tmpView.findChildren(QLineEdit)
            spins = self.tmpView.findChildren(QSpinBox)
            for cf in self.CF_:
                if cf['id'] == tem.item(data).id:
                    break
            lines[0].setText(cf['id'])
            lines[1].setText(cf['dsc'])
            print(lines[0].text())
            lines[0].setText('fsdfsdf')
            print(lines[0].text())

            for i1, i in enumerate(key2):
                if i == cf['type']:
                    break
            coms[0].setCurrentIndex(i1)
            coms[1].setCurrentText(cf['owner'])
            if i1 < 3:
                btns[0].data = cf['data']
                btns[0].setText('已选择')
            else:
                spins[0].setValue(cf['data'])
            for i1, i in enumerate(key4):
                if i == cf['eventtype']:
                    break
            coms[2].setCurrentIndex(i1)
            coms[3].setCurrentText(cf['eventowner'])
            if i1 < 6:
                btns[2].data = cf['eventdata']
                btns[2].setText('已选择')
            elif i1 < 8:
                spins[1].setValue(cf['eventdata'])
            else:
                if cf['eventdata'] == '':
                    coms[4].setCurrentText('')
                else:
                    coms[4].setCurrentText(cf['eventdata']+'  '+self.JC[cf['eventdata']]['dsc'])

    def sourceCpu(self, key):
        if key == 'instruction':
            if self.tmpView:
                try:
                    self.tmpView.deleteLater()
                except RuntimeError:
                    pass
            # self.tmpView = QScro
            pass
        elif key == 'sounds':
            file = QFileDialog.getExistingDirectory(self, '选择音效所在文件夹')
            resource.saveMap(self.vmap.map['name'], soundPath=file)
        elif key == 'images':
            file = QFileDialog.getExistingDirectory(self, '选择图片所在文件夹')
            resource.saveMap(self.vmap.map['name'], imagePath=file)

    def targetChoosed(self, data=None):
        try:
            if self.tmpView.isHidden():
                self.tmpView.show()
                if not data:
                    return
                if hasattr(self.tmpView.choose.type, 'flag'):
                    if self.tmpView.choose.type == 'event':
                        tem_data = self.tmpView.findChildren(QComboBox)[1].currentIndex()
                        if '区域' in tem_data:
                            pass
                        elif '单位' in tem_data:
                            newData = []
                            for i in data:
                                if self.vmap.pointer_dw[i[0]][i[1]]:
                                    newData.append(i)
                            data = newData
                        elif '建筑' in tem_data:
                            newData = []
                            for i in data:
                                if self.vmap.pointer_geo[i[0]][i[1]].track['usage'] == 'build':
                                    newData.append(i)
                            data = newData
                        if data:
                            self.tmpView.choose.data = data
                            self.tmpView.choose.setText('已选择')
                    elif self.tmpView.choose.type == 'toggle':
                        tem_data = self.tmpView.findChildren(QComboBox)[1].currentIndex()
                        if '单位' in tem_data:
                            newData = []
                            for i in data:
                                if self.vmap.pointer_dw[i[0]][i[1]]:
                                    newData.append(i)
                            data = newData
                        elif '建筑' in tem_data:
                            newData = []
                            for i in data:
                                if self.vmap.pointer_geo[i[0]][i[1]].track['usage'] == 'build':
                                    newData.append(i)
                            data = newData
                        if data:
                            self.tmpView.choose.data = data
                            self.tmpView.choose.setText('已选择')
                else:
                    if '单位' in self.tmpView.choose.text():
                        newData = []
                        for i in data:
                            if self.vmap.pointer_dw[i[0]][i[1]]:
                                newData.append(i)
                        data = newData
                    elif '建筑' in self.tmpView.choose.text():
                        newData = []
                        for i in data:
                            if self.vmap.pointer_geo[i[0]][i[1]].track['usage'] == 'build':
                                newData.append(i)
                        data = newData
                    if data:
                        self.tmpView.choose.data = data
                        self.tmpView.choose.setText('已选择')
        except:
            pass
        print(self.tmpView.choose.data)

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() in [Qt.Key_Escape, Qt.Key_Return]:
            self.vmap.keyReleaseEvent(a0)
        else:
            return super(EditWin, self).keyReleaseEvent(a0)



##nav
class newWin(QWidget):
    def initUI(self, brother=None, mapName=None, isNewMap=True, winSize=(600, 400)):
        '''
        :param brother:
        :param mapName: 必须连带isNewMap
        :param isNewMap:
        :param winSize:
        :return:
        '''
        self.mapName = mapName
        self.map = {}
        self.isNewMap = isNewMap
        if not self.mapName:
            self.mapName = hashlib.md5(str(time.time_ns()).encode()).hexdigest()[:8]
        self.map = resource.makeMap(self.mapName, '地图描述')
        self.mapPriName = mapName if self.isNewMap else self.mapName
        self.setWindowTitle('新建地图' if isNewMap else '修改地图')
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
        if self.isNewMap:
            resource.saveMap(self.map)
            if self.brother:
                self.brother.swapMap(self.mapName)
                self.close()
        else:
            self.map['name'] = self.name_.text()
            resource.saveMap(self.map, self.mapPriName)
            if self.brother:
                self.brother.swapMap(self.map['name'])
                self.close()

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
            tem_label =  QPushButton(i['name'])
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



if __name__ == '__main__':
    window = EditWin()

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
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :main_window.py
# @Time      :2021/7/18 14:05
# @Author    :russionbear

from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui
from map_load import VMap, Geo, DW, miniVMap
from resource_load import resource
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
    def __init__(self, name='test', parent=None, block=(100, 100), winSize=(800, 800), brother=None):
        super(EditMap, self).__init__(parent)
        self.brother = brother
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
            self.circled = end
            if self.brother:
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
        if self.hasCircle or self.hasMove :
            return
        self.mapScale(True if a0.angleDelta().y()>0 else False)

    def myUpdate(self):
        for j in self.findChildren(DW):
            if j:
                j.flush()
                j.myUpdate()

class EditWin(QMainWindow):
    def initUI(self, mapName='test1'):
        mapMenu = self.menuBar().addMenu('地图')
        mapMenu.addAction('打开').triggered.connect(self.skimMap)
        mapMenu.addSeparator()
        mapMenu.addAction('新建').triggered.connect(self.newMap)
        mapMenu.addAction('修改').triggered.connect(self.modifyMap)
        mapMenu.addAction('保存').triggered.connect(self.saveMap)

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
        self.mapName = resource.maps[0]['name']
        self.setWindowTitle('浏览地图(双击选择)')
        self.setFixedSize(winSize[0], winSize[1])
        self.brother = brother
        area1 = QScrollArea(self)
        frame1 = QFrame()
        frame1.setFixedWidth(winSize[0]//2)
        layout1 = QBoxLayout(QBoxLayout.TopToBottom)
        for i in resource.maps:
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
        frame2.initUI(resource.maps[0]['name'], area2)
        # frame2.setFixedSize(frame2.width(),frame2.height())
        area2.setWidget(frame2)
        # area2.setFixedSize(winSize[0]//4, winSize[1]//4)

        frame3 = QLabel(resource.maps[0]['dsc'])
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

    window.initUI()
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
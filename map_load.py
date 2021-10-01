import json
import random
import sys, os
from PyQt5 import QtGui
from PyQt5.Qt import *
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore
# from resource_load import resource
from resource import resource
# from tmap_load import TMap_

Qapp = QApplication(sys.argv)

'''
坐标，地图：左边y轴 
size，宽高：左边宽度
'''

class DW(QWidget):
    def __init__(self, parent, newkey={}):
        super(DW, self).__init__(parent)
        key = {'usage': 'dw', 'name': 'footmen', 'flag': 'red', 'action': 'right', \
               'oil': int(resource.basicData['gf'][newkey['name']]['oil']), \
               'bullect': int(resource.basicData['gf'][newkey['name']]['oil']), \
               'blood': 10, 'moved': False, 'occupied': 0, 'loadings': [], 'isDiving': False, 'isStealth': False,
               'supplies': {}}
        key.update(newkey)
        scaly = resource.mapScaleList[resource.mapScaleDoublePoint]
        self.track = resource.find(key)
        self.mapId = key['mapId']
        self.bodySize = scaly['body']
        self.resize(self.bodySize[0], self.bodySize[1])
        self.occupied = key['occupied']
        self.loadings = key['loadings']
        self.bloodSize = scaly['font']
        self.isStealth = key['isStealth']
        self.isDiving = key['isDiving']
        self.bloodValue = key['blood']
        self.oil = key['oil']
        self.bullect = key['bullect']
        self.moved = key['moved']
        self.supplies = key['supplies']
        del key['blood'], key['oil'], key['bullect']
        self.bloodFont = QFont('宋体', self.bloodSize)
        self.statusSize = scaly['tag']
        self.statusList = [None for i in range(7)]
        self.statusPoint = 0
        self.initUI()
        self.triggers = []
        self.triggerEvents = []

    def initUI(self):
        self.body = QLabel(self)
        pm = self.track['pixmap'].scaled(self.bodySize[0], self.bodySize[1])
        self.body.setPixmap(pm)

        tem_box = QFrame(self, QtCore.Qt.FramelessWindowHint)
        tem_layout = QBoxLayout(QBoxLayout.BottomToTop, tem_box)
        self.status = QLabel(tem_box)
        self.blood = QLabel('', tem_box)
        self.blood.setStyleSheet('color:white;')
        self.doBlood(self.bloodValue)
        self.blood.setAlignment(QtCore.Qt.AlignBottom)
        self.blood.setFont(self.bloodFont)

        tem_layout_2 = QBoxLayout(QBoxLayout.LeftToRight, tem_box)
        tem_layout_2.addWidget(self.blood)
        tem_layout_2.addStretch(1)
        tem_layout_2.addWidget(self.status)
        tem_layout.addLayout(tem_layout_2)
        tem_layout.addStretch(1)
        tem_box.setLayout(tem_layout)

        layout = QStackedLayout(self)
        layout.setStackingMode(QStackedLayout.StackAll)
        layout.addWidget(tem_box)
        layout.addWidget(self.body)
        self.setLayout(layout)
        self.status.clear()
        self.show()

        # self.setFrameShape(QFrame.Box)
        # self.setFrameShadow(QFrame.Raised)
        # self.setLineWidth(0)

        # self.doBlood(5)

    def doBlood(self, nu:float):
        if nu > 10:
            nu = 10
        elif nu <= 0:
            self.parent().point_dw[self.mapId[0]][self.mapId[1]] = None
            self.deleteLater()
            return
        self.bloodValue = nu
        if round(nu) == 10:
            self.blood.setText('')
            # self.bloodFont.set
        else:
            self.blood.setText(str(round(nu)))

    def doStatus(self, str):
        '''ok, oil, bullet, occupy, loading, supplies, diving, stealth'''
        if str == None:
            self.status.clear()
        else:
            self.status.setPixmap(QPixmap(resource.find({'usage': 'dw2', 'name': str})['pixmap']).scaled(round(self.statusSize[0]), round(self.statusSize[1])))

    def change(self, flag):
        track = resource.find({'usgae': 'dw', 'name': self.track['name'], 'flag': flag, 'action': self.track['action']})
        self.track.update(track)
        self.doBody(self.track['action'])

    def doBody(self, str):
        track = self.track.copy()
        track['action'] = str
        del track['base64']
        del track['pixmap']
        tem = resource.find(track)
        if tem:
            pm = tem['pixmap'].scaled(round(self.bodySize[0]), round(self.bodySize[1]))
            self.body.setPixmap(pm)
            self.track = tem
            if str[-1] == 'G':
                self.moved = True
            else:
                self.moved = False

    def scale(self, data):
        self.bodySize = data['body']
        self.bloodSize = data['font']
        self.statusSize = data['tag']
        # print(self.bodySize, self.bloodSize, self.statusSize)
        self.doBody(self.track['action'])
        self.resize(self.bodySize[0], self.bodySize[1])
        self.bloodFont.setPointSize(round(self.bloodSize))
        self.bloodFont.setBold(True)
        self.blood.setFont(self.bloodFont)
        self.blood.setText(self.blood.text())

    def inRect(self, x1, x2, y1, y2):
        if self.x() < x2 and \
                self.y() < y2 and \
                self.x() + self.width() > x1 and \
                self.y() + self.height() > y1:
            return True
        else:
            return False


    def myUpdate(self):
        '''ok, oil, bullet, occupy, loading, supplies, diving, stealth'''
        count = len(self.statusList)
        while count:
            self.statusPoint = (self.statusPoint+1)%len(self.statusList)
            if not self.statusList[self.statusPoint]:
                count -= 1
            else:
                self.doStatus(self.statusList[self.statusPoint])
                break
        else:
            self.doStatus(None)

    def flush(self):
        if self.oil < 0:
            self.parent().point_dw[self.mapId[0]][self.mapId[1]] = None
            self.deleteLater()
        if self.occupied < 0:
            self.occupied = 0
        elif self.occupied >= 20:
            geo = self.parent().point_geo[self.mapId[0]][self.mapId[1]]
            track = geo.track
            track['flag'] = self.track['flag']
            geo.change(track)

        self.statusList[0] = 'oil' if self.oil <= float(resource.basicData['gf'][self.track['name']]['oil'])*0.4 else None
        self.statusList[1] = 'bullect' if self.bullect <= float(resource.basicData['gf'][self.track['name']]['bullect'])*0.4 \
                                          and int(resource.basicData['gf'][self.track['name']]['bullect']) != 0 else None
        self.statusList[2] = 'occupy' if self.occupied else None
        self.statusList[3] = 'loading' if self.loadings else None
        self.statusList[4] = 'supplies' if self.supplies else None
        self.statusList[5] = 'diving' if self.isDiving else None
        self.statusList[6] = 'stealth' if self.isStealth else None

    def makeTrack(self, keys=[]):
        keys1 = ['blood', 'oil', 'bullect', 'occupied', 'isStealth', 'isDiving', 'loadings', 'supplies', 'moved', 'mapId', 'name']
        keys2 = [self.bloodValue, self.oil, self.bullect, self.occupied, self.isStealth, \
                 self.isDiving, self.loadings, self.supplies, self.moved, self.mapId, self.track['name']]
        track = {'isAlive':True, 'action':self.track['action'], 'flag':self.track['flag'], 'base64':self.track['base64']}
        for i, j in enumerate(keys1):
            if j in keys or not keys:
                track[j] = keys2[i]
        return track

    def updateByTrack(self, track):
        '''不处理isAlive, name'''
        self.bloodValue = self.bloodValue if 'blood' not in track else track['blood']
        self.oil = self.oil if 'oil' not in track else track['oil']
        self.bullect = self.bullect if 'bullect' not in track else track['bullect']
        self.occupied = self.occupied if 'occupied' not in track else track['occupied']
        self.isStealth = self.isStealth if not track['isStealth'] else track['isStealth']
        self.isDiving = self.isDiving if not track['isDiving'] else track['isDiving']
        self.loadings = self.loadings if not track['loadings'] else track['loadings']
        self.supplies = self.supplies if not track['supplies'] else track['supplies']
        self.moved = self.moved if 'moved' not in track else track['moved']
        # self.mapId = self.mapId if not track['mapId'] else track['mapId']


class Geo(QLabel):
    def __init__(self, parent, newKey={}):
        super(Geo, self).__init__(parent)
        key = {'usage':'geo', 'name':'plain'}
        key.update(newKey)
        self.track = resource.find(key)
        self.mapId = key['mapId']
        self.initUI()

    def initUI(self):
        self.resize(100, 100)
        self.size_ = self.width(), self.height()
        pm = resource.find(self.track)['pixmap']
        self.setPixmap(pm.scaled(self.width(), self.height()))
        self.setScaledContents(True)

    def change(self, track):
        self.track.update(track)
        self.track = resource.find(self.track)
        try:
            self.setPixmap(self.track['pixmap'].scaled(self.width(), self.height()))
        except TypeError:
            print(self.track, track, self.mapId, 'map_load ;geo ;change error')
            sys.exit()

    def scale(self, data):
        self.size_ = data['body']
        self.resize(round(self.size_[0]), round(self.size_[1]))

    def inRect(self, x1, x2, y1, y2):
        if self.x()< x2 and \
                self.y() < y2 and \
                self.x()+self.width() > x1 and \
                self.y()+ self.height() > y1:
            return True
        else:
            return False

class GeoD(QRect, QObject):
    def __init__(self, parent, newKey={}):
        super(GeoD, self).__init__(parent)
        QRect.__init__(self)
        # QObject.__init__(self, parent)
        # self.setParent(parent)
        key = {'usage':'geo', 'name':'plain'}
        key.update(newKey)
        self.track = resource.find(key)
        self.primTrack = self.track.copy()
        self.mapId = key['mapId']
        self.label = None
        # self.parent_ = parent
        size = resource.mapScaleList[resource.mapScaleDoublePoint]['body']
        self.setSize(QSize(size[0], size[1]))
        self.triggers = []
        self.triggerEvents = []

    def change(self, track):
        self.track.update(track)
        self.track = resource.find(self.track)
        if self.track['name'] != self.primTrack['name']:
            if self.label:
                try:
                    self.label.deleteLater()
                    self.label = None
                except RuntimeError:
                    pass
                self.label = None
            self.label = QLabel(self.parent_)
            self.label.resize(self.size)
            self.label.setPixmap(self.track['pximap'].scaled(self.width(), self.height()))
            self.label.setScaledContents(True)
        else:
            if self.label:
                try:
                    self.label.deleteLater()
                except RuntimeError:
                    pass
                self.label = None

    def geometry(self):
        return QRect(self.x(), self.y(), self.width(), self.height())

    def contains(self, pos):
        return super(GeoD, self).contains(pos)

    def pos(self):
        return QPoint(self.x(), self.y())

    def move(self, x, y):
        QRect.moveTo(self, x, y)
        if self.label:
            self.label.move(x, y)


    def scale(self, data):
        self.setSize(QSize(data['body'][0], data['body'][1]))
        if self.label:
            self.label.resize(self.size())

    def show(self):
        super(GeoD, self).show()
        if self.label:
            self.label.show()


'''不可删'''
# class GeoD(QObject, QRect):
#     def __init__(self, parent, newKey={}):
#         super(GeoD, self).__init__(parent)
#         QRect.__init__(self)
#         # super(GeoD, self).__init__()
#         key = {'usage':'geo', 'name':'plain'}
#         key.update(newKey)
#         # self.rect = QRect()
#         self.x = 0
#         self.y = 0
#         self.track = resource.find(key)
#         self.primTrack = self.track.copy()
#         self.mapId = key['mapId']
#         self.label = None
#         self.parent_ = parent
#         size = resource.mapScaleList[resource.mapScaleDoublePoint]['body']
#         # self.setSize(QSize(size[0], size[1]))
#         # self.rect.setSize(QSize(size[0], size[1]))
#         self.size = size
# 
#     def x(self):
#         return self.x
# 
#     def y(self):
#         return self.x
# 
#     def width(self):
#         return self.size[0]
# 
#     def height(self):
#         return self.size[1]
# 
#     def size(self):
#         return QSize(self.width(), self.height())
# 
#     def change(self, track):
#         self.track.update(track)
#         self.track = resource.find(self.track)
#         if self.track['name'] != self.primTrack['name']:
#             if self.label:
#                 try:
#                     self.label.deleteLater()
#                     self.label = None
#                 except RuntimeError:
#                     pass
#                 self.label = None
#             self.label = QLabel(self.parent_)
#             self.label.resize(self.size)
#             self.label.setPixmap(self.track['pximap'].scaled(self.width(), self.height()))
#             self.label.setScaledContents(True)
#         else:
#             if self.label:
#                 try:
#                     self.label.deleteLater()
#                 except RuntimeError:
#                     pass
#                 self.label = None
# 
#     def geometry(self):
#         return QRect(self.x, self.y, self.width(), self.height())
# 
#     def contains(self, pos):
#         if self.geometry().contains(pos):
#             return True
#         return False
# 
#     def move(self, x, y):
#         # self.moveTo(x, y)
#         # self.rect.setX(x)
#         # self.rect.setY(y)
#         self.x, self.y = x, y
#         # print(x, y)
#         if self.label:
#             self.label.move(x, y)
# 
# 
#     def pos(self):
#         # return super(GeoD, self).pos()
#         return QPoint(self.x, self.y)
# 
#     def scale(self, data):
#         # self.setSize(QSize(data['body'][0], data['body'][1]))
#         # self.rect.setWidth(data['body'][0])
#         # self.rect.setHeight(data['body'][1])
#         self.size = tuple(data['body'])
#         if self.label:
#             self.label.resize(self.size())
# 
#     def parent(self):
#         return self.parent_
# 
#     def show(self):
#         if self.label:
#             self.label.show()



class VMap(QWidget):
    def initUI(self, name='test', parent=None, block=(100, 100), winSize=(800, 800), brother=None):
        self.setFixedSize(winSize[0], winSize[1])
        self.map = resource.findMap(name)
        # print(name)
        if not self.map:
            print(self.map, 'error', name)
            sys.exit()
        self.setParent(parent)
        # print(self.map)
        self.mapSize = len(self.map['map'][0]), len(self.map['map'])
        self.mapBlockSize = block

        self.pointer_geo = []
        for i in range(len(self.map['map'])):
            tem_data = []
            for j in range(len(self.map['map'][i])):
                track = resource.findByHafuman(self.map['map'][i][j])
                print(track, str(self.map['map'][i][j]))
                if not track:
                    print('map error', 'mini')
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
        # self.setP
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
            track = resource.findByHafuman(i['base64'])
            axis = i['axis']
            track.update(i)
            dw = DW(self)
            # print(track, axis)
            dw.initUI(track, axis)
            dw.move(axis[1]*block[1], axis[0]*block[0])
            self.pointer_dw[axis[0]][axis[1]] = dw

        self.brother = brother
        # print('reosourc1111e', resource.maps[0]['dw'])

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
    def modify(self, areaGroup, newTrack):
        cols = len(self.pointer_geo[0])
        rows = len(self.pointer_geo)
        direction = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        direction_ = ['top', 'right', 'bottom', 'left']
        if newTrack['usage'] == 'dw':
            x1, y1 = areaGroup[0].mapId
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



    '''选择， 移动， 缩放'''
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
                if i.inRect(x1, x2, y1, y2):
                    end.append(i)

            ##dw...
            self.circled = end
            if self.brother:
                # if self.brother.choosed:
                tem = self.brother.getChoosedValue()
                if tem:
                    self.modify(end, self.brother.getChoosedValue())

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

    # def leaveEvent(self, a0: QtCore.QEvent) -> None:
    #     self.hasCircle = self.hasMove = False

    def collectMap(self):
        map = {}
        map['map'] = []
        geos = iter(self.findChildren(Geo))
        for i in range(self.mapSize[1]):
            com = []
            for j in range(self.mapSize[0]):
                tem = geos.__next__()
                # com.append(int(resource.findHafuman(tem.track['base64'])))
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
        # print(self.map)
        return self.map

    ##初始化地图， 填充，地形窗口， 单位窗口， 科技窗口， 指挥官窗口，save， load

class miniVMap(QWidget):
    def initUI(self, name='default', parent=None, map=None):
        self.map = map
        if not self.map:
            self.map = resource.findMap(name)
        if parent:
            self.setParent(parent)
        # print(map, self.map)
        self.mapSize = len(self.map['map'][0]), len(self.map['map'])
        self.mapScalePoint = 1
        self.mapBlockSize = resource.mapScaleList[self.mapScalePoint]['body']
        self.setFixedSize(self.mapSize[0]*self.mapBlockSize[0], self.mapSize[1]*self.mapBlockSize[1])
        for i in range(len(self.map['map'])):
            for j in range(len(self.map['map'][i])):
                track = resource.findByHafuman(self.map['map'][i][j])
                # print(track, self.map['map'][i][j])
                if not track:
                    print('map error356')
                    return
                track['mapId'] = i, j
                tem_geo = Geo(self, track)
                tem_geo.move(j * self.mapBlockSize[0], i * self.mapBlockSize[1])
                tem_geo.scale(resource.mapScaleList[self.mapScalePoint])

        for i in self.map['dw']:
            track = resource.findByHafuman(i['hafuman'])
            # print('hh', track, i)
            # axis = i['axis']
            # del i['axis'] #######hhhhhaaaaaaa
            track.update(i)
            axis = track['mapId']
            dw = DW(self, track)
            # dw.initUI(track)
            dw.move(axis[1] * self.mapBlockSize[1], axis[0] * self.mapBlockSize[0])
            dw.scale(resource.mapScaleList[self.mapScalePoint])








# arbitrator = Arbitrator()

if __name__ == '__main__':
    # window = VMap()
    # window.initUI()
    # # window.modify([],None)
    # # window.collectMap()
    # window.show()
    # sys.exit(Qapp.exec_())
    geo = GeoD()
    # geo

    sys.exit(Qapp.exec_())
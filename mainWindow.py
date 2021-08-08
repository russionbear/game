#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :mainWindow.py
# @Time      :2021/8/7 14:11
# @Author    :russionbear

from PyQt5.Qt import *
from PyQt5 import QtCore
import sys, time, functools
from resource_load import resource
from map_load import DW, Geo
from net.netTool import findRooms, enterRoom

Qapp = QApplication(sys.argv)
class TopDirector(QWidget):
    def __init__(self):
        super(TopDirector, self).__init__()
        self.initUI()

    def initUI(self):
        bgUrl = ''
        self.bgFrame = QFrame(self)
        self.fgFrame = QFrame(self)
        bgImage = QLabel(self.bgFrame)
        bgImage_ = QLabel(self.bgFrame)
        pixmap = resource.find({'usage':'hero', ' name':'hero', 'action':'post'})['pixmap']
        bgImage.setPixmap(pixmap)
        bgImage_.setPixmap(pixmap)
        bgImage_.resize(pixmap.size())
        bgImage_.resize(pixmap.size())
        self.fgFrame.resize(pixmap.size())
        bgImage_.move(0, pixmap.height())
        # self.setFixedSize(pixmap.size())
        self.resize(pixmap.size())
        self.startTimer(20)

        # self.toBegin()
        # self.toOptions()
        self.toIntranet()

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        speed = 1
        for i in self.bgFrame.findChildren(QLabel):
            i.move(0, i.y()+speed)
            i.show()
        if i.y() >= self.height():
            for i1, i in enumerate(self.bgFrame.findChildren(QLabel)):
                i.move(0, (i1-1)*self.height())
        a0.accept()

    def toBegin(self):
        tipText = '这fsdfsdfsdfsdfsdfsdfsd是一个提示'
        self.fgFrame.deleteLater()
        self.fgFrame = QFrame(self)
        self.fgFrame.resize(self.size())
        tip = QLabel(tipText, self.fgFrame)
        tip.setAlignment(QtCore.Qt.AlignCenter)
        tip.setFont(QFont('宋体', 25))
        tip.setWordWrap(True)
        tip.setFixedWidth(self.width()//2)
        tip.setStyleSheet('color:white;')
        beginBtn = QPushButton('开始', self.fgFrame)
        beginBtn.clicked.connect(self.toOptions)
        layoutBegin = QBoxLayout(QBoxLayout.TopToBottom)
        layoutBegin.setAlignment(QtCore.Qt.AlignCenter)
        layoutBegin.addWidget(tip)
        layoutBegin.addSpacing(30)
        layoutBegin.addWidget(beginBtn)
        self.fgFrame.setLayout(layoutBegin)
        self.fgFrame.show()

    def toOptions(self):
        self.fgFrame.deleteLater()
        self.fgFrame = QFrame(self)
        self.fgFrame.resize(self.size())
        btns_text = ['战役', '局域网', '自定义', '编辑', '设置', '返回']
        btns_backMethod = [self.toBegin, self.toIntranet, self.toCustom, self.toEdit, self.toSetting, self.toBegin]
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.setAlignment(QtCore.Qt.AlignHCenter)
        for i1, i in enumerate(btns_text):
            tem_btn = QPushButton(i, self.fgFrame)
            tem_btn.clicked.connect(btns_backMethod[i1])
            tem_btn.show()
            layout.addWidget(tem_btn)
            layout.addSpacing(tem_btn.height()*2)
        self.fgFrame.setLayout(layout)
        self.fgFrame.show()

    def toBattle(self):
        pass

    def toIntranet(self):
        self.setWindowTitle('选择房间')
        self.fgFrame.deleteLater()
        self.fgFrame = SkimRoom(self, self.size())
        self.fgFrame.show()

    def enterRoom(self, room:QtCore.QModelIndex):
        print(room.row())
        tem = self.findChild(SkimRoom)
        self.room = tem.ipsAndRooms[tem.roomPoint]

    def toCustom(self):
        pass
    def toEdit(self):
        pass
    def toSetting(self):
        pass

class miniVMap(QWidget):
    def __init__(self, parent, map=None):
        super(miniVMap, self).__init__(parent)
        if map:
            self.initUI(map)

    def initUI(self, map):
        self.map = map
        self.mapSize = len(self.map['map'][0]), len(self.map['map'])
        self.mapScalePoint = 1
        self.mapBlockSize = resource.mapScaleList[self.mapScalePoint]['body']
        self.setFixedSize(self.mapSize[0]*self.mapBlockSize[0], self.mapSize[1]*self.mapBlockSize[1])
        self.point_geo = []
        self.point_dw = [[None for i in range(self.mapSize[1])] for j in range(self.mapSize[0])]
        for i in range(len(self.map['map'])):
            tem = []
            for j in range(len(self.map['map'][i])):
                track = resource.findByHafuman(str(self.map['map'][i][j]))
                if not track:
                    print('map error')
                    return
                tem_geo = Geo(self, track, (i, j))
                tem_geo.move(j * self.mapBlockSize[0], i * self.mapBlockSize[1])
                tem_geo.scale(resource.mapScaleList[self.mapScalePoint])
                tem.append(tem_geo)
            self.point_geo.append(tem)

        for i in self.map['dw']:
            track = resource.findByHafuman(i['hafuman'])
            axis = i['axis']
            track.update(i)
            dw = DW(self)
            dw.initUI(track, axis)
            self.point_dw[axis[0]][axis[1]] = dw
            dw.move(axis[1] * self.mapBlockSize[1], axis[0] * self.mapBlockSize[0])
            dw.scale(resource.mapScaleList[self.mapScalePoint])

class SkimRoom(QWidget):
    def __init__(self, parent, winSize=QSize(800, 600)):
        super(SkimRoom, self).__init__(parent=parent)
        self.ipsAndRooms = [(('192.168.100.9', 1111), {'type': 'map', 'author': 'hula', 'authorid': '123',
                       'map': {'name': 'netmap', 'map': [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], 'dw': [], 'dsc': 'just for test'}})]
        self.roomPoint = -1

        self.initUI(winSize)

        self.updateRooms()
        self.updateRooms()
    def initUI(self, winSize):
        self.setFixedSize(winSize)

        self.roomList = QListWidget(self)
        self.roomList.doubleClicked.connect(self.parent().enterRoom)
        self.roomList.clicked.connect(self.choose)

        self.area = QScrollArea(self)
        self.miniMap = miniVMap(self.area)
        self.area.setWidget(self.miniMap)

        self.text_dsc = QTextEdit('空空如也', self)
        self.text_dsc.setReadOnly(True)

        layout3 = QBoxLayout(QBoxLayout.LeftToRight)
        tem_btn = QPushButton('创建房间', self)
        tem_btn.clicked.connect(functools.partial(self.parent().enterRoom, self.ipsAndRooms[self.roomPoint]))
        layout3.addWidget(tem_btn)
        tem_btn = QPushButton('返回', self)
        tem_btn.clicked.connect(self.parent().toOptions)
        layout3.addWidget(tem_btn)
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout1 = QBoxLayout(QBoxLayout.TopToBottom)
        layout2 = QBoxLayout(QBoxLayout.TopToBottom)
        layout1.addWidget(self.area)
        layout1.addWidget(self.text_dsc)
        layout2.addWidget(self.roomList)
        layout2.addLayout(layout3)
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)

    def choose(self):
        self.roomPoint = self.roomList.currentRow()
        self.text_dsc.setText(self.ipsAndRooms[self.roomPoint][1]['map']['dsc'])
        self.miniMap.deleteLater()
        self.miniMap = miniVMap(self.area, self.ipsAndRooms[self.roomPoint][1]['map'])
        self.area.setWidget(self.miniMap)

    def updateRooms(self):
        # newData = findRooms()
        newData = [(('192.168.100.9', 1111), {'type': 'map', 'author': 'hula', 'authorid': '123',
                       'map': {'name': 'netmap', 'map': [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], 'dw': [], 'dsc': 'just for test'}})]
        if self.roomPoint == -1:
            selected = None
        else:
            selected = self.ipsAndRooms[self.roomPoint]
        if selected:
            for i1, i in newData:
                if i[0][0] == selected[0][0]:
                    self.roomPoint = i1
                    break
        self.ipsAndRooms = newData
        self.roomList.clear()
        for i in self.ipsAndRooms:
            item = QListWidgetItem(i[1]['map']['name']+'\t<'+i[1]['author']+'>')
            item.roomIp = i[0][0]
            self.roomList.addItem(item)
        if self.roomPoint != -1:
            self.roomList.selectedIndexes(self.roomPoint)
            self.text_dsc.setText(self.ipsAndRooms[self.roomPoint][1]['map']['dsc'])
            self.miniMap.deleteLater()
            self.miniMap = miniVMap(self.ipsAndRooms[self.roomPoint][1]['map']['map'])
            self.area.setWidget(self.miniMap)

class RoomInner(QWidget):
    def __init__(self, parent, winSize=QSize(800, 600), room=None):
        super(RoomInner, self).__init__(parent=parent)
        self.room = (('192.168.100.9', 1111), {'type': 'map', 'author': 'hula', 'authorid': '123',
                                               'map': {'name': 'netmap',
                                                       'map': [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]],
                                                       'dw': [], 'dsc': 'just for test'}, 'flags':['red', 'bule']})
        self.isOwner = False

        self.initUI(winSize)

    def initUI(self, winSize):
        self.setFixedSize(winSize)

        self.area = QScrollArea(self)
        self.miniMap = miniVMap(self.area, self.room[1]['map'])
        self.area.setWidget(self.miniMap)

        self.text_dsc = QTextEdit('空空如也', self)
        self.text_dsc.setReadOnly(True)

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        for i in self.room[1]['map']['flags']:
            tem_layout = QBoxLayout(QBoxLayout.LeftToRight)
            tem_flag = QLabel(self)
            tem_flag.setStyleSheet('background-color:'+i)
            tem_btn = QPushButton('', self)
            com1 =

    def choose(self):
        self.roomPoint = self.roomList.currentRow()
        self.text_dsc.setText(self.ipsAndRooms[self.roomPoint][1]['map']['dsc'])
        self.miniMap.deleteLater()
        self.miniMap = miniVMap(self.area, self.ipsAndRooms[self.roomPoint][1]['map'])
        self.area.setWidget(self.miniMap)

    def updateRooms(self):
        # newData = findRooms()
        newData = [(('192.168.100.9', 1111), {'type': 'map', 'author': 'hula', 'authorid': '123',
                       'map': {'name': 'netmap', 'map': [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], 'dw': [], 'dsc': 'just for test'}})]
        if self.roomPoint == -1:
            selected = None
        else:
            selected = self.ipsAndRooms[self.roomPoint]
        if selected:
            for i1, i in newData:
                if i[0][0] == selected[0][0]:
                    self.roomPoint = i1
                    break
        self.ipsAndRooms = newData
        self.roomList.clear()
        for i in self.ipsAndRooms:
            item = QListWidgetItem(i[1]['map']['name']+'\t<'+i[1]['author']+'>')
            item.roomIp = i[0][0]
            self.roomList.addItem(item)
        if self.roomPoint != -1:
            self.roomList.selectedIndexes(self.roomPoint)
            self.text_dsc.setText(self.ipsAndRooms[self.roomPoint][1]['map']['dsc'])
            self.miniMap.deleteLater()
            self.miniMap = miniVMap(self.ipsAndRooms[self.roomPoint][1]['map']['map'])
            self.area.setWidget(self.miniMap)


if __name__ == "__main__":
    window = TopDirector()
    window.show()
    sys.exit(Qapp.exec_())

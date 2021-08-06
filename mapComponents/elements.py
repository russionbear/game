#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :elements.py
# @Time      :2021/8/6 16:38
# @Author    :russionbear

import sys
from PyQt5.Qt import *
from PyQt5 import QtCore
from resource_load import resource

class Dw(QFrame):
    def initUI(self, newkey={}, mapId=None):
        key = {'usage': 'dw', 'name': 'footmen', 'flag': 'red', 'action':'right', \
               'oil':int(resource.basicData['gf'][newkey['name']]['oil']), \
               'bullect':int(resource.basicData['gf'][newkey['name']]['oil']), \
               'blood':10, 'moved':False, 'occupied':0, 'loadings':[], 'isDiving':False, 'isStealth':False, 'supplies': {}}
        key.update(newkey)
        # print(key)
        if isinstance(mapId, list):
            self.mapId = tuple(mapId)
        else:
            self.mapId = mapId
        self.bodySize = (100, 100)
        self.resize(self.bodySize[0], self.bodySize[1])
        self.occupied = key['occupied']
        self.loadings = key['loadings']
        self.bloodSize = 30
        self.isStealth = key['isStealth']
        self.isDiving = key['isDiving']
        self.bloodValue = key['blood']
        self.oil = key['oil']
        self.bullect = key['bullect']
        self.moved = key['moved']
        self.supplies = key['supplies']
        del key['blood'], key['oil'], key['bullect']
        self.bloodFont = QFont('宋体', self.bloodSize)
        self.statusSize = 40, 40
        self.statusList = [None for i in range(7)]
        self.statusPoint = 0

        self.body = QLabel(self)
        self.track = resource.find(key)
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

    def doBlood(self, nu:float):
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

    def contains(self, p:QPoint):
        if self.x() < p.x() and self.y() < p.y() and \
                self.x()+self.width() > p.x() and self.y() + self.height()> p.y():
            return True
        else:
            return False

    def change(self, track, data={}):
        self.body.setPixmap(track['pixmap'].scaled(self.bodySize[0], self.bodySize[1]))
        if 'blood' in data:
            self.blood.setText(str(data['blood']))
            self.bloodValue = str(data['blood'])
        if 'oil' in data:
            self.oil = data['oil']
        if 'bullect' in data:
            self.bullect = data['bullect']

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
        self.statusList[0] = 'oil' if self.oil <= float(resource.basicData['gf'][self.track['name']]['oil'])*0.4 else None
        self.statusList[1] = 'bullect' if self.bullect <= float(resource.basicData['gf'][self.track['name']]['bullect'])*0.4 else None
        self.statusList[2] = 'occupy' if self.occupied else None
        self.statusList[3] = 'loading' if self.loadings else None
        self.statusList[4] = 'supplies' if self.supplies else None
        self.statusList[5] = 'diving' if self.isDiving else None
        self.statusList[6] = 'stealth' if self.isStealth else None



Qapp = QApplication(sys.argv)

if __name__ == "__main__":
    dw = Dw()
    QImage
    sys.exit(Qapp.exec_())

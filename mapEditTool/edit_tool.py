#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :edit_tool.py
# @Time      :2021/7/18 14:53
# @Author    :russionbear

from PyQt5.Qt import *
from PyQt5 import QtCore
import functools
import sys
from resource_load import resource
from map_load import Geo

Qapp = QApplication(sys.argv)

class EditTool(QWidget):
    def initUi(self, winSize=(340, 800), blockSize=(100, 100)):
        self.status = [0, 0]
        self.choosed = None
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

        self.initLoadingSupplyView()

        self.swapBtn1(self.btn1_s[0])

    def initLoadingSupplyView(self):
        self.loadingSuplyView = QWidget(self)
        tem = QScrollArea(self.loadingSuplyView)
        tem_ = QWidget(self.loadingSuplyView)
        tem_.setFixedSize(400, 400)

        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout__ = QBoxLayout(QBoxLayout.LeftToRight)
        tem_1 = QLabel('单位', tem_)
        tem_2 = QLabel('规模', tem_)
        tem_2.shouldHide = True
        tem_3 = QLabel('数量', tem_)
        layout__.addWidget(tem_1)
        layout__.addWidget(tem_2)
        layout__.addWidget(tem_3)
        layout.addLayout(layout__)
        for i in resource.findAll({'usage': 'dw', 'flag': 'red', 'action': 'left'}):
            layout__ = QBoxLayout(QBoxLayout.LeftToRight)
            tem_1 = QPushButton(QIcon(i['pixmap']), resource.basicData['money']['chineseName'][i['name']], tem_)
            tem_1.setStyleSheet('border:none;background:none;')
            tem_2 = QSpinBox(tem_)
            tem_2.setMaximum(10)
            tem_2.setMinimum(1)
            tem_2.shouldHide = True
            tem_3 = QSpinBox(tem_)
            layout__.addWidget(tem_1)
            layout__.addWidget(tem_2)
            layout__.addWidget(tem_3)
            layout.addLayout(layout__)
        tem_.setLayout(layout)
        tem.setWidget(tem_)
        layout_6 = QBoxLayout(QBoxLayout.TopToBottom)
        layout_6.addWidget(tem)
        layout_6.addWidget(QPushButton('fsdf', self.loadingSuplyView))
        # layout_5 = QBoxLayout(QBoxLayout.LeftToRight)
        # tem = QPushButton('reset', self.loadingSuplyView)
        # tem.clicked.connect(functools.partial(self.saveOrReset, 'reset'))
        # layout_5.addWidget(tem)
        # tem = QPushButton('save', self.loadingSuplyView)
        # tem.clicked.connect(functools.partial(self.saveOrReset, 'save'))
        # layout_5.addWidget(tem)
        # layout_6.addLayout(layout_5)
        self.loadingSuplyView.setLayout(layout_6)

        self.loadingSuplyView.show()
        x, y = self.width() - self.loadingSuplyView.width(), self.height() - self.loadingSuplyView.height()
        # self.loadingSuplyView.move(-x//2, -y//2)
        self.loadingSuplyView.move(100, 300)
        self.loadingSuplyView.raise_()

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
        self.enableSlider(key['usage'])

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

    def enableSlider(self, type):
        return
        sliders = [self.bloodSlider, self.oilSlider, self.bullectSlider]
        # values = [self.bloodValue, self. oilValue, self.bullectValue]
        if type == 'dw':
            for i in sliders:
                i.setEnabled(True)
        elif type == 'geo':
            for i in sliders:
                i.setEnabled(False)
        elif type == 'build':
            for i in sliders[1:]:
                i.setEnabled(False)
            sliders[0].setEnabled(True)

    def getChoosedValue(self):
        if not self.choosed:
            return None
        track = self.choosed.copy()
        track['blood'] = int(self.bloodValue.text().split('%')[0].split('：')[1])/10
        track['oil'] = int(self.oilValue.text().split('%')[0].split('：')[1])/10
        track['bullect'] = int(self.bullectValue.text().split('%')[0].split('：')[1])/10
        return track

    def selectDws(self, data):
        if data == 'loadings':
            for i in self.loadingSuplyView.findChildren((QLabel, QSpinBox)):
                if hasattr(i, 'shouldHide'):
                    i.hide()
            self.loadingSuplyView.show()
        elif data == 'supplies':
            for i in self.loadingSuplyView.findChildren((QLabel, QSpinBox)):
                if hasattr(i, 'shouldHide'):
                    i.show()
            self.loadingSuplyView.show()
        else:
            key1 = [10, 100, 100, 0]
            for i1, i in enumerate(self.dwInfo[0:4]):
                i.setValue(key1[i1])
            self.dwInfo[4].setChecked(False)
            self.dwInfo[5].setChecked(False)
            for i in self.loadingSuplyView.findChildren(QSpinBox):
                if hasattr(i, 'shouldHide'):
                    i.setValue(10)
                else:
                    i.setValue(0)


    def saveOrReset(self, data):
        print(data)


if __name__ == '__main__':
    window = EditTool()
    window.initUi()
    window.show()
    sys.exit(Qapp.exec_())
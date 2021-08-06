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
                if i['action'] != 'left':
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

        self.bloodSlider = QSlider(Qt.Horizontal, self)
        self.oilSlider = QSlider(Qt.Horizontal)
        self.bullectSlider = QSlider(Qt.Horizontal)
        self.bloodValue = QLabel('规模：100%')
        self.oilValue = QLabel('燃油：100%')
        self.bullectValue = QLabel('弹药：100%')
        # print(self.bloodValue.text(),'jjjj')
        layout_1 = QBoxLayout(QBoxLayout.LeftToRight)
        layout_1.addWidget(self.bloodValue)
        layout_1.addWidget(self.bloodSlider)
        layout_2 = QBoxLayout(QBoxLayout.LeftToRight)
        layout_2.addWidget(self.oilValue)
        layout_2.addWidget(self.oilSlider)
        layout_3 = QBoxLayout(QBoxLayout.LeftToRight)
        layout_3.addWidget(self.bullectValue)
        layout_3.addWidget(self.bullectSlider)
        sliders = [self.bloodSlider, self.oilSlider, self.bullectSlider]
        values = [self.bloodValue, self. oilValue, self.bullectValue]
        for j, i in enumerate(sliders):
            i.setMaximum(100)
            i.setSingleStep(10)
            i.setMinimum(1)
            i.setValue(100)
            i.valueChanged.connect(functools.partial(self.valueChange, values[j]))

        layout.addSpacing(50)
        layout.addLayout(layout_1)
        layout.addLayout(layout_2)
        layout.addLayout(layout_3)

        self.setLayout(layout)

        self.swapBtn1(self.btn1_s[0])

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


if __name__ == '__main__':
    window = EditTool()
    window.initUi()
    window.show()
    sys.exit(Qapp.exec_())
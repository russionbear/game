#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :skim_map_win.py
# @Time      :2021/7/20 21:31
# @Author    :russionbear


from PyQt5.Qt import *
from PyQt5 import QtCore
import sys, functools, time
from resource_load import resource
from map_load import miniVMap

Qapp = QApplication(sys.argv)

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
    window = SkimWin()
    window.initUI()
    window.show()
    sys.exit(Qapp.exec_())
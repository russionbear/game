#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :main_window.py
# @Time      :2021/7/18 14:05
# @Author    :russionbear

from PyQt5.Qt import *
from map_load import VMap
from mapEditTool.edit_tool import EditTool
from mapEditTool.new_map_win import newWin
from mapEditTool.skim_map_win import SkimWin
from resource_load import resource
import sys

Qapp = QApplication(sys.argv)

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
        self.tool.initUi()
        self.vmap = VMap()
        self.vmap.initUI(mapName, self.center, brother=self.tool)
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addWidget(self.tool)
        layout.addWidget(self.vmap)
        self.center.setLayout(layout)
        # self.vmap.move(self.tool.width(), 0)
        self.setCentralWidget(self.center)

        self.modeSkim = self.modeModify = None

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



if __name__ == '__main__':
#     window = EditWin()
#
#     window.initUI()
#     window.show()
#     sys.exit(Qapp.exec_())
# else:
    window = QWidget()
    for i in range(200):
        for j in range(100):
            tem_label = QLabel(window)
            tem_label.move(i*20, j*20)
            tem_label.setPixmap(resource.find({'usage':'geo', 'name':'tree'})['pixmap'].scaled(20,20))


    window.show()
    sys.exit(Qapp.exec_())
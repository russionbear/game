#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :new_map_win.py
# @Time      :2021/7/21 9:53
# @Author    :russionbear


from PyQt5.Qt import *
from PyQt5 import QtCore
import sys, functools, time
from resource_load import resource
from map_load import miniVMap
import hashlib, time

Qapp = QApplication(sys.argv)

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

if __name__ == '__main__':
    window = newWin()
    window.initUI()
    window.show()
    sys.exit(Qapp.exec_())
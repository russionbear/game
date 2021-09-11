#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :main_window.py
# @Time      :2021/7/18 14:05
# @Author    :russionbear
import json, os, shutil

from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui
from map_load import Geo, DW, miniVMap
from resource import resource
from win_basicdataEdit import basicEditW
import sys, functools, time, hashlib

Qapp = QApplication(sys.argv)


class EditTool(QWidget):
    def __init__(self, parent, tmap):
        super(EditTool, self).__init__(parent)
        self.tmap = tmap
        self.btns = ['地形', '建筑', '单位', '标记']
        self.nowView = None
        self.views = []
        self.initUI()
        self.swap(self.btns[0])

    def initUI(self):
        self.geoView = editToolGeo(self)
        self.buildView = editToolBuild(self)
        self.dwView = editToolDw(self)
        self.marketView = editToolMarket(self)
        self.views = [self.geoView, self.buildView, \
                self.dwView, self.marketView]
        layout1 = QHBoxLayout()
        for i in self.btns:
            tem = QPushButton(i, self)
            tem.clicked.connect(functools.partial(self.swap, i))
            layout1.addWidget(tem)
        layout = QVBoxLayout()
        layout.addLayout(layout1)
        for i in self.views:
            layout.addWidget(i)
        self.setLayout(layout)

    def swap(self, arg):
        for i, j in zip(enumerate(self.views), self.btns):
            if j == arg:
                i[1].show()
                self.nowView = i[0]
            else:
                i[1].hide()

    def getChoosedValue(self):
        '''self.btns（list）的前三个值， 才有getChooseValue'''
        if self.nowView > 2:
            return None
        else:
            return self.views[self.nowView].getChoosedValue()

    def save(self):
        self.marketView.save()


class editToolGeo(QWidget):
    def __init__(self, parent):
        super(editToolGeo, self).__init__(parent)
        self.data = []
        self.track = None
        for j, i in enumerate(resource.data):
            if i['name'] == 'sea' and i['action'] != '':
                continue
            elif i['name'] == 'road' and i['action'] != 'across':
                continue
            elif i['name'] == 'river' and i['action'] != 'across':
                continue
            elif i['action'] not in ['left', 'across', '', 'center']:
                continue

            if i['usage'] == 'geo':
                self.data.append(i.copy())

        self.initUI()

    def initUI(self):
        self.listView = QListWidget(self)
        self.listView.clicked.connect(self.choosed)
        for i in self.data:
            tem = QListWidgetItem(QIcon(i['pixmap']), resource.basicData['geo']['chineseName'][i['name']])
            tem.track = i
            self.listView.addItem(tem)

    def choosed(self, index=None):
        self.track = self.listView.currentItem().track
        # self.parent().choosed()

    def getChoosedValue(self):
        return self.track

class editToolBuild(QWidget):
    def __init__(self, parent):
        super(editToolBuild, self).__init__(parent)
        self.flags = ['none', 'red', 'blue', 'green', 'yellow']
        self.data = {}
        self.track = None
        for i in self.flags:
            self.data[i] = []
        for i in resource.data:
            if i['usage'] == 'build':
                self.data[i['flag']].append(i)
        self.initUI()

    def initUI(self):
        layout1 = QHBoxLayout()
        for i in self.flags:
            tem = QPushButton(i, self)
            tem.clicked.connect(functools.partial(self.swap, i))
            layout1.addWidget(tem)

        self.listView = QListWidget(self)
        self.listView.clicked.connect(self.choosed)
        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addWidget(self.listView)
        self.setLayout(layout)

    def swap(self, flag):
        self.listView.clear()
        for i in self.data[flag]:
            tem = QListWidgetItem(QIcon(i['pixmap']), resource.basicData['geo']['chineseName'][i['name']])
            tem.track = i
            self.listView.addItem(tem)

    def choosed(self, index=None):
        self.track = self.listView.currentItem().track
        # self.parent().choosed()

    def getChoosedValue(self):
        return self.track

class editToolDw(QWidget):
    def __init__(self, parent):
        super(editToolDw, self).__init__(parent)
        self.flags = ['none', 'red', 'blue', 'green', 'yellow']
        self.data = {}
        for i in self.flags:
            self.data[i] = []
        for i in resource.data:
            if i['usage'] == 'dw':
                if i['action'] == 'left' or i['name'] == 'delete':
                    self.data[i['flag']].append(i)

        self.dwAtrs1 = ['规模', '油量', '弹药']
        self.dwAtrs2 = ['隐形', '下潜', '已移动']
        self.LSview = editToolDwLSView()
        self.LSview.setWindowModality(Qt.ApplicationModal)
        self.LSview.hide()
        self.track = None
        self.initUI()

    def initUI(self):
        layout1 = QHBoxLayout()
        for i in self.flags:
            tem = QPushButton(i, self)
            tem.clicked.connect(functools.partial(self.swap, i))
            layout1.addWidget(tem)

        self.listView = QListWidget(self)
        self.listView.clicked.connect(self.choosed)
        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addWidget(self.listView)

        self.loadingBtn = QPushButton('搭载', self)
        self.loadingBtn.data = {}
        self.loadingBtn.clicked.connect(self.showLoading)
        self.supplyBtn = QPushButton('补给', self)
        self.supplyBtn.data = {}
        self.supplyBtn.clicked.connect(self.showSupply)

        layout2 = QFormLayout()
        self.guimoSpin = QSpinBox(self)
        self.guimoSpin.setMaximum(10)
        self.guimoSpin.setValue(10)
        self.guimoSpin.data = self.dwAtrs1[0]
        layout2.addRow(self.dwAtrs1[0], self.guimoSpin)
        self.oilSpin = QSpinBox(self)
        self.oilSpin.setMaximum(100)
        self.oilSpin.setValue(100)
        self.oilSpin.data = self.dwAtrs1[1]
        layout2.addRow(self.dwAtrs1[1], self.oilSpin)
        self.bullectSpin = QSpinBox(self)
        self.bullectSpin.setMaximum(100)
        self.bullectSpin.setValue(100)
        self.bullectSpin.data = self.dwAtrs1[2]
        layout2.addRow(self.dwAtrs1[2], self.bullectSpin)

        self.stealthBtn = QCheckBox(self.dwAtrs2[0], self)
        self.divingBtn = QCheckBox(self.dwAtrs2[1], self)
        self.movedBtn = QCheckBox(self.dwAtrs2[2], self)
        layout2.addRow(self.stealthBtn, self.divingBtn)
        layout2.addWidget(self.movedBtn)
        layout2.addRow(self.loadingBtn, self.supplyBtn)

        layout.addLayout(layout2)

        self.setLayout(layout)

    def swap(self, flag):
        self.listView.clear()
        for i in self.data[flag]:
            if i['name'] == 'delete':
                tem = QListWidgetItem(QIcon(i['pixmap']), '删除')
            else:
                tem = QListWidgetItem(QIcon(i['pixmap']), resource.basicData['money']['chineseName'][i['name']])
            tem.track = i
            self.listView.addItem(tem)

    def choosed(self, index=None):
        self.track = self.listView.currentItem().track

    def showLoading(self):
        self.LSview.setDataSaver(self.loadingBtn)
        self.LSview.show(self.loadingBtn.data)

    def showSupply(self):
        self.LSview.setDataSaver(self.supplyBtn)
        self.LSview.show(self.supplyBtn.data)

    def getChoosedValue(self):
        if not self.track:
            return None
        end = self.track.copy()
        end['blood'] = self.guimoSpin.value()
        end['oil'] = self.oilSpin.value() / 100 * int(resource.basicData['gf'][end['name']]['oil'])
        end['bullect'] = self.bullectSpin.value() / 100 * int(resource.basicData['gf'][end['name']]['bullect'])
        end['moved'] = self.movedBtn.isChecked()
        if resource.basicData['money']['canstealth'][end['name']] == '1':
            end['isStealth'] = self.stealthBtn.isChecked()
        if resource.basicData['money']['candiving'][end['name']] == '1':
            end['isDiving'] = self.stealthBtn.isChecked()

        if resource.basicData['money']['canloading'][end['name']] == '1':
            end['loadings'] = self.loadingBtn.data
        if resource.basicData['money']['cansupply'][end['name']] == '1':
            end['supplies'] = self.loadingBtn.data

        return end

class editToolDwLSView(QWidget):
    def __init__(self, obj=None):
        super(editToolDwLSView, self).__init__()
        self.data = []
        for i in resource.data:
            if i['usage'] == 'dw':
                if i['action'] == 'left' and i['flag'] == 'red':
                    self.data.append(i)

        self.dataSaver = obj
        self.initUI()

    def initUI(self):
        '''len(self.data) >= 2 否则出错'''
        cursor = [(0, len(self.data)//2), (len(self.data)//2, len(self.data))]
        layout_ = QHBoxLayout()
        for i in cursor:
            layout1 = QFormLayout()
            for j in self.data[i[0]:i[1]]:
                tem1 = QPushButton(QIcon(j['pixmap']), resource.basicData['money']['chineseName'][j['name']], self)
                tem2 = QSpinBox(self)
                tem2.data = j['name']
                tem2.setSingleStep(1000)
                tem2.setMaximum(120000)
                layout1.addRow(tem1, tem2)
            layout_.addLayout(layout1)

        layout2 = QHBoxLayout()
        tem = QPushButton('重置', self)
        tem.clicked.connect(self.reset)
        layout2.addWidget(tem)
        tem = QPushButton('保存', self)
        tem.clicked.connect(self.save)
        layout2.addWidget(tem)
        layout = QHBoxLayout()
        layout.addLayout(layout_)
        layout.addLayout(layout2)
        self.setLayout(layout)

    def setDataSaver(self, obj):
        self.dataSaver = obj

    def reset(self):
        for i in self.findChildren(QSpinBox):
            i.setValue(0)

    def show(self, data={}):
        for i in self.findChildren(QSpinBox):
            if i.data in data:
                i.setValue(data[i.data])
            else:
                i.setValue(0)
        super(editToolDwLSView, self).show()

    def save(self):
        if not self.dataSaver:
            print('no saver')
            return
        data = {}
        for i in self.findChildren(QSpinBox):
            data[i.data] = i.value()
        self.dataSaver.data = data
        self.hide()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.hide()


'''name, type, flags, data'''
class editToolMarket(QWidget):
    def __init__(self, parent):
        super(editToolMarket, self).__init__(parent)
        self.mapName = self.parent().tmap.map['name']
        self.flags = ['none', 'red', 'blue', 'green', 'yellow']
        self.types = ['单位', '建筑', '区域', '镜头']
        self.path = 'maps/'+self.mapName+'/markets.json'
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                self.data = json.load(f)
        else:
            with open(self.path, 'w') as f:
                json.dump({}, f)
            self.data = {}
        self.initUI()

    def initUI(self):
        self.listView = QListWidget(self)
        self.listView.clicked.connect(self.choosed)
        for i in self.data:
            self.listView.addItem(QListWidgetItem(i['name'], self))
        layout = QVBoxLayout()
        layout.addWidget(self.listView)
        layout1 = QHBoxLayout()
        self.typeComBox = QComboBox(self)
        self.typeComBox.addItems(self.types)
        layout1.addWidget(self.typeComBox)
        for i in self.flags:
            tem = QCheckBox(i, self)
            layout1.addWidget(tem)
        self.chooseBtn = QPushButton('选择', self)
        self.chooseBtn.clicked.connect(self.chooseArea)
        self.chooseBtn.data = []
        self.showBtn = QPushButton('显示', self)
        self.showBtn.clicked.connect(self.showArea)
        layout1.addWidget(self.chooseBtn)
        layout1.addWidget(self.showBtn)
        self.deleteBtn = QPushButton('删除', self)
        self.deleteBtn.clicked.connect(self.listDelete)
        self.renameBtn = QPushButton('重命名', self)
        self.renameBtn.clicked.connect(self.listRename)
        self.addBtn = QPushButton('添加', self)
        self.addBtn.clicked.connect(self.listAdd)
        self.nameInput = QLineEdit(self)
        self.saveBtn = QPushButton('保存', self)
        self.saveBtn.clicked.connect(self.save)
        layout2 = QHBoxLayout()
        layout2.addWidget(self.deleteBtn)
        layout2.addWidget(self.nameInput)
        layout2.addWidget(self.addBtn)
        layout2.addWidget(self.renameBtn)
        layout2.addWidget(self.saveBtn)
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)

    def choosed(self, index=None):
        name = self.listView.currentItem().text()
        self.typeComBox.setCurrentText(self.listView.currentItem().text())
        if self.data[name]['type'] != self.types[2]:
            for i in self.findChildren(QCheckBox):
                if i.text() in self.data[name]['flags']:
                    i.setChecked(True)
                else:
                    i.setChecked(False)
        self.chooseBtn.data = self.data[name]['data']

    def swap(self, index=None):
        if index in [self.types[0], self.types[1]]:
            for i in self.findChildren(QCheckBox):
                i.show()
        elif index == self.types[3]:
            for i in self.findChildren(QCheckBox):
                if i.text() == self.flags[0]:
                    i.hide()
                else:
                    i.show()
        elif index == self.types[2]:
            for i in self.findChildren(QCheckBox):
                i.hide()

    def chooseArea(self):
        if self.listView.currentItem() == None:
            return
        if self.chooseBtn.text() == '正在选择':
            return

        self.chooseBtn.setText('正在选择')
        self.deleteBtn.setEnabled(False)
        QCoreApplication.postEvent(self.parent().tmap, \
                                   marketEditEvent(marketEditEvent.choose, obj=self))

    def areaChhosed(self, data):
        end = []
        if self.typeComBox.currentText() == self.types[0]:
            dws = self.parent().tmap.pointer_dw
            flags = []
            for i in self.findChildren(QCheckBox):
                if i.isChecked():
                    flags.append(i.text())
            for i in data:
                if dws[i[0]][i[1]]:
                    if dws[i[0]][i[1]].track['flag'] in flags:
                        end.append(i)
        elif self.typeComBox.currentText() == self.types[1]:
            geos = self.parent().tmap.pointer_geo
            flags = []
            for i in self.findChildren(QCheckBox):
                if i.isChecked():
                    flags.append(i.text())
            for i in data:
                if geos[i[0]][i[1]].track['usage'] == 'build':
                    if geos[i[0]][i[1]].track['flag'] in flags:
                        end.append(i)
        elif self.typeComBox.currentText() == self.types[2]:
            end = data
        elif self.typeComBox.currentText() == self.types[3]:
            end = data[:1]
        self.chooseBtn.data = end
        self.data[self.listView.currentItem().text()]['data'] = end

    def event(self, a0: QtCore.QEvent) -> bool:
        if a0.type() == marketEditEvent.idType:
            if a0.type_ == marketEditEvent.show:
                self.showBtn.setText('显示')
            elif a0.type_ == marketEditEvent.choose:
                self.chooseBtn.setText('选择')
                if a0.data:
                    self.areaChhosed(a0.data)
                self.deleteBtn.setEnabled(True)
        return super(editToolMarket, self).event(a0)

    def showArea(self):
        if self.listView.currentItem() == None:
            return
        if self.showBtn.text() == '正在预览':
            return
        name = self.listView.currentItem().text()
        print('name data', self.data[name])
        if not self.data[name]['data']:
            return
        self.showBtn.setText('正在预览')
        QCoreApplication.postEvent(self.parent().tmap, \
                                   marketEditEvent(marketEditEvent.show, data=self.chooseBtn.data, obj=self))

    def listAdd(self):
        text = self.nameInput.text()
        if text == '' or text in self.data:
            return
        self.listView.addItem(QListWidgetItem(text, self.listView))
        flags = []
        for i in self.findChildren(QCheckBox):
            if i.isChecked():
                flags.append(i.text())
        self.data[text] = {'name':text, 'type':self.typeComBox.currentText(), 'data':[], 'flags':flags}

    def listDelete(self):
        if self.listView.currentItem() == None:
            return
        index = self.listView.currentIndex().row()
        del self.data[self.listView.currentItem().text()]
        self.listView.takeItem(index)

    def listRename(self):
        if self.listView.currentItem() == None:
            return
        if self.nameInput.text() == '' or self.nameInput.text() in self.data:
            return
        self.data[self.nameInput.text()] = self.data[self.listView.currentItem().text()].copy()
        del self.data[self.listView.currentItem().text()]
        self.data[self.nameInput.text()]['name'] = self.nameInput.text()
        self.listView.currentItem().setText(self.nameInput.text())

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f)




class EditMap(QWidget):
    def __init__(self, name='default', parent=None, edittool=None):
        super(EditMap, self).__init__(parent)
        self.edittool = edittool
        # self.modifyTarget = None
        # self.isTargetChoosing = False
        # self.isTargetShowing = False
        # self.targetChooseType = None
        # self.targetChoosedLayer = []

        self.layers = []
        self.areaEditStatus = marketEditEvent.none
        self.areaEditData = {'flag':'none', 'type':'dw'}
        self.areaEditSaver = None
        self.initUI(name)
        self.mapScale(False)

        self.dwUpdater = QTimer(self)
        self.dwUpdater.timeout.connect(self.myUpdate)
        self.dwUpdater.start(1400)

    def initUI(self, name, winSize=QSize(800, 800)):
        self.setFixedSize(winSize)
        self.map = resource.findMap(name)
        if not self.map:
            print(self.map, 'error', name)
            sys.exit()
        self.mapSize = len(self.map['map'][0]), len(self.map['map'])
        self.mapBlockSize = resource.mapScaleList[resource.mapScaleDoublePoint]['body']

        self.pointer_geo = []

        tem_data = []
        for i in range(self.mapSize[0]):
            track = resource.find({'usage': 'border'})
            if not track:
                print('map error122343')
                return
            track['mapId'] = 0, i
            tem_geo = Geo(self, track)
            tem_geo.move(i * self.mapBlockSize[0], 0)
            tem_data.append(tem_geo)
        self.pointer_geo.append(tem_data)

        for i in range(1, len(self.map['map'])):
            tem_data = []
            for j in range(len(self.map['map'][i])):
                if j == 0 or j == self.mapSize[0] - 1:
                    track = resource.find({'usage': 'border'})
                else:
                    track = resource.findByHafuman(self.map['map'][i][j])
                    if not track:
                        print('map error123')
                        return
                track['mapId'] = i, j
                tem_geo = Geo(self, track)
                tem_geo.move(j*self.mapBlockSize[0], i*self.mapBlockSize[1])
                tem_data.append(tem_geo)
            self.pointer_geo.append(tem_data)

        tem_data = []
        for i in range(self.mapSize[0]):
            track = resource.find({'usage': 'border'})
            track['mapId'] = self.mapSize[1]-1, i
            tem_geo = Geo(self, track)
            tem_geo.move(i * self.mapBlockSize[0], self.mapBlockSize[1]*(self.mapSize[1]-1))
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
            axis = i['mapId']
            dw = DW(self, i)
            dw.move(axis[1]*self.mapBlockSize[1], axis[0]*self.mapBlockSize[0])
            self.pointer_dw[axis[0]][axis[1]] = dw

    def mapAdjust(self):
        move_x, move_y = (self.mapBlockSize[0]*self.mapSize[0]-self.width())//2, (self.mapBlockSize[1]*self.mapSize[1]-self.height())//2
        move_x, move_y = -move_x - self.pointer_geo[0][0].x(), -move_y - self.pointer_geo[0][0].y()
        self.mapMove(move_x, move_y, True)

    def mapMove(self, x, y, isforce=False):
        # def move(x, y):
        #     for i in self.children():
        #         if not hasattr(i, 'move'):
        #             continue
        #         i.move(i.x() + x, i.y() + y)
        # if isforce:
        #     move(x,y)
        # else:
        #     last_cursor = self.mapSize[0] * self.mapSize[1] - 1
        #     if self.children()[0].x() + x > 0 and self.canMove[0]:
        #         # print('111')
        #         move_x = - self.children()[0].x()
        #         move_y = 0 if self.children()[0].y() < 0 and self.canMove[1] else - self.children()[0].y()
        #         move(move_x, move_y)
        #     elif self.children()[0].y() + y > 0 and self.canMove[1]:
        #         # print('22')
        #         move_x = 0 if self.children()[0].x() < 0 and self.canMove[0] else - self.children()[0].x()
        #         move_y = - self.children()[0].y()
        #         move(move_x, move_y)
        #     elif self.children()[last_cursor].x() + x < self.width() - self.mapBlockSize[0] and self.canMove[0]:
        #         # print('333')
        #         move_x = self.width() - self.mapBlockSize[0] - self.children()[last_cursor].x()
        #         move_y = self.height() - self.mapBlockSize[0] - self.children()[last_cursor].y()
        #         move_y = 0 if move_y < 0 and self.canMove[1] else move_y
        #         move(move_x, move_y)
        #     elif self.children()[last_cursor].y() + y < self.height() - self.mapBlockSize[1] and self.canMove[1]:
        #         # print('444')
        #         move_x = self.width() - self.mapBlockSize[0] - self.children()[last_cursor].x()
        #         move_y = self.height() - self.mapBlockSize[0] - self.children()[last_cursor].y()
        #         move_x = 0 if move_x < 0 and self.canMove[0] else move_x
        #         move(move_x, move_y)
        #     else:
        #         # print('555')
        #         move(0 if not self.canMove[0] else x, 0 if not self.canMove[1] else y)

        border = 0   # 100
        def move(x, y):
            for i in self.findChildren(Geo):
                i.move(i.x() + x, i.y() + y)
            # for i in self.children():
            #     if not hasattr(i, 'move'):
            #         continue
            #     i.move(i.x() + x, i.y() + y)

        def moveTo(x_, y_):
            if x_ == None and y_ == None:
                return
            elif x_ == None:
                for i in self.findChildren((DW, Geo)):
                    i.move(i.x(), y_+i.mapId[0]*self.mapBlockSize[0])
            elif y_ == None:
                for i in self.findChildren((DW, Geo)):
                    i.move(x_+i.mapId[1]*self.mapBlockSize[0], i.y())
            else:
                for i in self.findChildren((DW, Geo)):
                    i.move(x_+i.mapId[1]*self.mapBlockSize[0], y_+i.mapId[0]*self.mapBlockSize[1])

        ##----------越界判断----------------#
        if isforce:
            move(x,y)

        else:
            moved_x, moved_y = None, None
            bg = self.pointer_geo[0][0]
            if self.canMove[0]:
                if bg.x() + x > 100:
                    moved_x = 100
                elif bg.x() + self.mapSize[0]*self.mapBlockSize[0] + x < self.width() - 100:
                    moved_x = self.width() - self.mapSize[0]*self.mapBlockSize[0] - 100
                else:
                    moved_x = x + bg.x()

            if self.canMove[1]:
                if bg.y() + y > 100:
                    moved_y = 100
                elif bg.y() + self.mapSize[1]*self.mapBlockSize[1] + y < self.height() - 100:
                    moved_y = self.height() - self.mapSize[1]*self.mapBlockSize[1] - 100
                else:
                    moved_y = y + bg.y()

            moveTo(moved_x, moved_y)

        for i in self.layers:
            i.setGeometry(self.pointer_geo[i.mapId[0]][i.mapId[1]].geometry())


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
        for i in self.layers:
            i.setGeometry(self.pointer_geo[i.mapId[0]][i.mapId[1]].geometry())

    #地图修改
    def modify(self, areaGroup, newTrack):
        # print(areaGroup)
        cols = len(self.pointer_geo[0]) - 1
        rows = len(self.pointer_geo) - 1
        direction = [(-1, 0), (0, 1), (1, 0), (0, -1)]

        direction_ = ['top', 'right', 'bottom', 'left']
        if newTrack['usage'] == 'dw':
            x1, y1 = areaGroup[0]
            x2, y2 = areaGroup[-1]
            dws = self.findChildren(DW)
            for i in dws:
                if  i.mapId[0] >= x1 and i.mapId[0] <= x2 and i.mapId[1] >= y1 and i.mapId[1] <= y2:
                    i.deleteLater()

            if newTrack['name'] == 'delete':
                return

            for i in areaGroup:
                if int(resource.basicData['move'][newTrack['name']][self.pointer_geo[i[0]][i[1]].track['name']]) >= 99:
                    continue
                newTrack['mapId'] = i
                dw = DW(self, newTrack)
                dw.scale(resource.mapScaleList[self.mapScalePoint])
                dw.move(self.pointer_geo[i[0]][i[1]].pos())
                dw.show()
        elif newTrack['usage'] == 'build':
            for i in areaGroup:
                tem_dw = self.pointer_dw[i[0]][i[1]]
                if tem_dw:
                    tem_dw.deleteLater()
                    self.pointer_dw[i[0]][i[1]] = None
                self.pointer_geo[i[0]][i[1]].change(track=newTrack)

        elif newTrack['usage'] == 'geo':
            if newTrack['name'] == 'sand':
                for i in areaGroup:
                    tem_dw = self.pointer_dw[i[0]][i[1]]
                    if tem_dw:
                        tem_dw.deleteLater()
                        self.pointer_dw[i[0]][i[1]] = None

                    should = []

                    for k1, k in enumerate(direction):
                        x, y = k[0] + i[0], k[1] + i[1]
                        if x <= 0 or x >= rows or y <= 0 or y >= cols:
                            continue
                        try:
                            if self.pointer_geo[x][y].track['name'] not in ['sea', 'rocks', 'sand']:
                                should.append(direction_[k1])
                        except:
                            print(x, y, 'error pre sand')
                    if len(should) in [0, 4]:
                        continue
                    self.pointer_geo[i[0]][i[1]].change(track=newTrack)
            else:
                for i in areaGroup:
                    tem_dw = self.pointer_dw[i[0]][i[1]]
                    if tem_dw:
                        tem_dw.deleteLater()
                        self.pointer_dw[i[0]][i[1]] = None
                    self.pointer_geo[i[0]][i[1]].change(track=newTrack)


        if newTrack['usage'] == 'geo':
            for i1, i in enumerate(self.pointer_geo):
                for j1, j in enumerate(i):
                    if j == None:
                        print(j, i1, j1, 'er')
                        continue
                    if j.track['name'] == 'road':
                        should = []
                        for k1, k in enumerate(direction):
                            x, y = k[0]+i1, k[1]+j1
                            if x <= 0 or x >= rows  or y <= 0 or y >= cols :
                                continue
                            if self.pointer_geo[x][y].track['name'] in ['road', 'bridge']:
                                should.append(direction_[k1])
                        length = len(should)
                        if length == 4:
                            j.change({'usage':'geo', 'name':'road', 'flag':'', 'action':'center'})
                        elif length == 3:
                            for p1 in direction_:
                                if p1 not in should:
                                    j.change({'usage':'geo', 'name':'road', 'flag':'', 'action':'no-'+p1})
                                    break
                        elif length == 2:
                            if 'top' in should and 'bottom' in should:
                                j.change({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'vertical'})
                            elif 'left' in should and 'right' in should:
                                j.change({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'across'})
                            else:
                                # print(should)
                                tem_dd = resource.find({'usage': 'geo', 'name': 'road', 'flag': '', 'action': should[0]+'-'+should[1]})
                                if not tem_dd:
                                    j.change({'usage': 'geo', 'name': 'road', 'flag': '', 'action': should[1]+'-'+should[0]})
                                else:
                                    j.change(track=tem_dd)
                        elif length == 1:
                            if should[0] in ['left', 'right']:
                                j.change({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'across'})
                            else:
                                j.change({'usage': 'geo', 'name': 'road', 'flag': '', 'action': 'vertical'})
                    elif j.track['name'] == 'bridge':
                        should = []
                        for k1, k in enumerate(direction):
                            x, y = k[0] + i1, k[1] + j1
                            if x <= 0 or x >= rows or y <= 0 or y >= cols:
                                continue
                            try:
                                if self.pointer_geo[x][y].track['name'] in ['road', 'bridge']:
                                    should.append(direction_[k1])
                            except TypeError:
                                print(x, y, 'error bridge')
                        length = len(should)
                        if length == 4:
                            j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'})
                        elif length == 1:
                            if should[0] in ['left', 'right']:
                                j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'})
                            else:
                                j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'vertical'})
                        elif length == 2:
                            if 'left' in should and 'right' in should:
                                j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'})
                            elif 'top' in should and 'bottom' in should:
                                j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'vertical'})
                            else:
                                j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'})
                        elif length == 3:
                            if 'left' in should and 'right' in should:
                                j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'across'})
                            else:
                                j.change({'usage':'geo', 'name':'bridge', 'flag':'', 'action':'vertical'})
                    elif j.track['name'] == 'sea':
                        should = []
                        for k1, k in enumerate(direction):
                            x, y = k[0] + i1, k[1] + j1
                            if x <= 0 or x >= rows or y <= 0 or y >= cols:
                                continue
                            try:
                                if self.pointer_geo[x][y].track['name'] not in ['sea', 'rocks', 'sand', 'river']:
                                    should.append(direction_[k1])
                            except:
                                print(x, y, 'error sea')
                        length = len(should)
                        if length == 4:
                            j.change({'usage':'geo', 'name':'sea', 'flag':'', 'action':'center'})
                        elif length == 3:
                            for p1 in direction_:
                                if p1 not in should:
                                    j.change({'usage':'geo', 'name':'sea', 'flag':'', 'action':'no-'+p1})
                                    break
                        elif length == 2:
                            if 'top' in should and 'bottom' in should:
                                j.change({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': 'across'})
                            elif 'left' in should and 'right' in should:
                                j.change({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': 'vertical'})
                            else:
                                tem_dd = resource.find({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': should[0]+'-'+should[1]})
                                if not tem_dd:
                                    j.change({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': should[1]+'-'+should[0]})
                                else:
                                    j.change(track=tem_dd)
                        elif length == 1:
                            j.change({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': should[0]})
                        elif length == 0:
                            j.change({'usage': 'geo', 'name': 'sea', 'flag': '', 'action': ''})
                    elif j.track['name'] == 'river':
                        should = []
                        for k1, k in enumerate(direction):
                            x, y = k[0] + i1, k[1] + j1
                            if x <= 0 or x >= rows or y <= 0 or y >= cols:
                                continue
                            try:
                                if self.pointer_geo[x][y].track['name'] not in ['sea', 'rocks', 'river']:
                                    should.append(direction_[k1])
                            except:
                                print(x, y, 'error river')
                        length = len(should)
                        if length == 4:
                            j.change({'action': 'center'})
                        elif length == 3:
                            for p1 in direction_:
                                if p1 not in should:
                                    if p1 in ['left', 'right']:
                                        j.change({'action': 'across'})
                                    else:
                                        j.change({'action': 'vertical'})
                                    break
                        elif length == 2:
                            if 'top' in should and 'bottom' in should:
                                j.change(
                                    {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'across'})
                            elif 'left' in should and 'right' in should:
                                j.change(
                                    {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'vertical'})
                            else:
                                tem_dd = resource.find(
                                    {'usage': 'geo', 'name': 'river', 'flag': '', 'action': should[0] + '-' + should[1]})
                                if not tem_dd:
                                    j.change({'usage': 'geo', 'name': 'river', 'flag': '',
                                                                  'action': should[1] + '-' + should[0]})
                                else:
                                    j.change(track=tem_dd)
                        elif length == 1:
                            if should[0] in ['left', 'right']:
                                j.change(
                                    {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'vertical'})
                            else:
                                j.change(
                                    {'usage': 'geo', 'name': 'river', 'flag': '', 'action': 'across'})
                        elif length == 0:
                                j.change(
                                    {'usage': 'geo', 'name': 'plain', 'flag': '', 'action':''})
                    elif j.track['name'] == 'sand':
                        should = []
                        for k1, k in enumerate(direction):
                            x, y = k[0] + i1, k[1] + j1
                            if x <= 0 or x >= rows or y <= 0 or y >= cols:
                                continue
                            try:
                                if self.pointer_geo[x][y].track['name'] not in ['sea', 'rocks', 'sand']:
                                    should.append(direction_[k1])
                            except TypeError:
                                print(x, y, 'error sand')
                        length = len(should)
                        if length == 4 or length == 3:
                            j.change(
                                {'usage': 'geo', 'name': 'plain', 'flag': '', 'action':''})
                        elif length == 2:
                            if 'top' in should and 'bottom' in should:
                                j.change(
                                    {'usage': 'geo', 'name': 'plain', 'flag': '', 'action':''})
                            elif 'left' in should and 'right' in should:
                                j.change(
                                    {'usage': 'geo', 'name': 'plain', 'flag': '', 'action':''})
                            else:
                                tem_dd = resource.find(
                                    {'usage': 'geo', 'name': 'sand', 'flag': '', 'action': should[0] + '-' + should[1]})
                                if not tem_dd:
                                    j.change({'usage': 'geo', 'name': 'sand', 'flag': '',
                                                                  'action': should[1] + '-' + should[0]})
                                else:
                                    j.change(track=tem_dd)
                        elif length == 1:
                            j.change(
                                {'usage': 'geo', 'name': 'sand', 'flag': '', 'action': should[0]})
                        elif length == 0:
                            j.change(
                                {'usage': 'geo', 'name': 'plain', 'flag': '', 'action':''})

        for i in self.pointer_geo:
            for j in i:
                if not j:
                    print('flush error')
                else:
                    if not j.track:
                        print('flush error')

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == 1 and not self.hasMove:
            if self.areaEditStatus == marketEditEvent.show:
                return
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
            # if self.areaEditStatus == marketEditEvent.show:
            #     return
            if not self.hasCircle:
                return
            self.circle.hide()
            self.circle.setParent(None)
            x2, y2 = a0.x(), a0.y()
            x1, y1 = self.hasCircle.x(), self.hasCircle.y()

            x1, x2 = (x1, x2) if x1<=x2 else (x2, x1)
            y1, y2 = (y1, y2) if y1<=y2 else (y2, y1)
            end = []
            for i in self.findChildren(Geo):
                # if hasattr(i, 'inRect'):
                if i.inRect(x1, x2, y1, y2):
                    if i.mapId[0] not in [0, self.mapSize[1]-1] and \
                        i.mapId[1] not in [0, self.mapSize[0]-1]:
                        end.append(i.mapId)

            if self.areaEditStatus == marketEditEvent.choose:
                for i in end:
                    for j in self.layers:
                        if tuple(j.mapId) == tuple(i):
                            break
                    else:
                        circle = QFrame(self)
                        circle.setStyleSheet('border-radius:5px;border:3px solid rgb(100, 100,200)')
                        circle.show()
                        circle.mapId = i
                        circle.setGeometry(self.pointer_geo[i[0]][i[1]].geometry())
                        self.layers.append(circle)

            elif self.edittool.getChoosedValue():
                try:
                    self.modify(end, self.edittool.getChoosedValue())
                finally:
                    pass

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
        if self.hasCircle or self.hasMove:
            return
        self.mapScale(True if a0.angleDelta().y()>0 else False)

    def event(self, a0: QtCore.QEvent) -> bool:
        if a0.type() == marketEditEvent.idType:
            self.areaEditData = a0.data
            self.areaEditStatus = a0.type_
            self.areaEditSaver = a0.obj
            if self.areaEditStatus == marketEditEvent.show:
                for i in self.layers:
                    i.deleteLater()
                self.layers = []
                for j in self.areaEditData:
                    circle = QFrame(self)
                    circle.setStyleSheet('border-radius:5px;border:3px solid rgb(100, 100,200)')
                    circle.show()
                    circle.mapId = j
                    circle.setGeometry(self.pointer_geo[j[0]][j[1]].geometry())
                    self.layers.append(circle)
        return super(EditMap, self).event(a0)

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if self.areaEditStatus == marketEditEvent.none:
            return
        if a0.key() == Qt.Key_Return:
            end = []
            for i in self.layers:
                end.append(i.mapId)
                i.deleteLater()
            self.layers = []
            if self.areaEditStatus == marketEditEvent.choose:
                post = marketEditEvent(data=end, type_=marketEditEvent.choose)
                QCoreApplication.postEvent(self.areaEditSaver, post)
                self.areaEditStatus = marketEditEvent.none

        elif a0.key() == Qt.Key_Escape:
            for i in self.layers:
                i.deleteLater()
            self.layers = []

            post = marketEditEvent(type_=self.areaEditStatus, data=None)
            QCoreApplication.postEvent(self.areaEditSaver, post)
            self.areaEditStatus = marketEditEvent.none

        else:
            pass
        # a0.accept()
            # return super(EditMap, self).keyReleaseEvent(a0)

    def myUpdate(self):
        for j in self.findChildren(DW):
            if j:
                j.flush()
                j.myUpdate()

    def collectMap(self):
        map = {}
        map['map'] = []
        geos = iter(self.findChildren(Geo))
        for i in range(self.mapSize[1]):
            com = []
            for j in range(self.mapSize[0]):
                tem = geos.__next__()
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
        return self.map.copy()


#------------------------------------------------

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
        self.vmapMode = None
        with open('resource/ini.json', 'r') as f:
            initData = json.load(f)
        self.initUI(initData['lastEditMap'])

    def initUI(self, mapName='default'):
        mapMenu = self.menuBar().addMenu('地图')
        mapMenu.addAction('打开').triggered.connect(self.skimMap)
        mapMenu.addSeparator()
        mapMenu.addAction('新建').triggered.connect(self.newMap)
        mapMenu.addAction('修改').triggered.connect(self.modifyMap)
        mapMenu.addAction('保存').triggered.connect(self.saveMap)

        mapMenu = self.menuBar().addMenu('素材')
        mapMenu.addAction('图片').triggered.connect(functools.partial(self.sourceCpu, 'images'))
        mapMenu.addAction('切换图片').triggered.connect(functools.partial(self.sourceCpu, 'swap'))
        mapMenu.addSeparator()
        mapMenu.addAction('音效').triggered.connect(functools.partial(self.sourceCpu, 'sounds'))

        mapMenu = self.menuBar().addMenu('规则')
        mapMenu.addAction('故事背景').triggered.connect(self.storyCpu)
        mapMenu.addAction('指挥官限制').triggered.connect(functools.partial(self.heroCpu, 'open'))
        mapMenu.addSeparator()
        mapMenu.addAction('制作游戏参数').triggered.connect(self.basicDataCpu)
        mapMenu.addAction('制作游戏加成').triggered.connect(self.backupCpu)
        mapMenu.addAction('制作台词').triggered.connect(self.linesCpu)
        mapMenu.addAction('制作触发器').triggered.connect(self.toggleCpu)
        mapMenu.addSeparator()
        mapMenu.addAction('合并数据(耗时操作)').triggered.connect(self.mergeCpu)

        self.center = QWidget(self)
        self.tool = QObject()
        self.vmap = EditMap(mapName, self.center)
        self.tool = EditTool(self, self.vmap)
        self.tool.setFixedWidth(400)
        self.vmap.edittool = self.tool
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addWidget(self.tool)
        layout.addWidget(self.vmap)
        self.center.setLayout(layout)
        self.setCentralWidget(self.center)

        self.modeLSView = self.modeSkim = self.modeModify = None
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
            self.modeModify = newWin()
            self.modeModify.initUI(brother=self, mapName=self.vmap.map['name'])
            self.modeModify.setWindowModality(Qt.ApplicationModal)
            self.modeModify.show()
        else:
            self.modeModify = newWin()
            self.modeModify.initUI(brother=self, mapName=mapName)
            self.modeModify.setWindowModality(Qt.ApplicationModal)
            self.modeModify.show()

    def saveMap(self):
        tem_v = self.findChild(EditMap)
        tem_map = tem_v.collectMap()
        resource.saveMap(tem_map['name'], map=tem_map)
        self.tool.save()

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
        self.vmap = EditMap(name, self.center, brother=self.tool)
        # self.vmap.initUI(name, self.center, brother=self.tool)
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addWidget(self.tool)
        layout.addWidget(self.vmap)
        self.center.setLayout(layout)
        self.vmap.move(self.tool.width(), 0)
        self.setCentralWidget(self.center)

    def linesCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        path = 'maps/'+self.vmap.map['name']+'/lines.json'
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)
        self.tmpView = linesEditWin(path)
        self.tmpView.setWindowTitle('台词设计')
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()
        # print(key, data)
        # '''
        #     开战前
        #     主城附近，
        #     收入支出，
        #     故事背景
        #     局势，
        #     单位：侦查，补给，下潜，隐身，计划补给，体力，油量，弹药，攻击范围，所在地形，安全系数+可攻击目标，
        #     随机
        # '''
        # key1 = ['随机', '开战前', '主城附近', '收入不足', '收入充足', '收入过多', '支出过多', '支出过少', \
        #         '故事背景', '局势', '侦查到', '侦查没到', '下潜没被发现', '下潜被发现', '隐身被发现', '隐身没被发现', '计划补给', \
        #         '规模低', '规模充足', '油量低', '油量充足', '弹药低', '弹药充足', '近战', '远程', '移动攻击',  \
        #         '单位被困且危险', '单位被困但安全', '单位安全', '可攻击目标少', '可攻击目标多']
        # key2 = ['random', 'beforebattle', 'nearhead', 'smallsalary', 'enoughsalary', 'muchsalary', \
        #         'storybackground', 'situation', 'watched', 'watching', 'diving', 'dived', 'stealthing', 'stealthed', \
        #         'plansupply', 'lessguimo', 'enoughguimo', 'lessoil', 'enoughoil', 'lessbullect', 'enoughbullect', \
        #         'shortrange', 'longrange', 'attackaftermove', 'trapped_danger', 'trapped_safe', 'untrapped', 'moretargets', 'lesstargets']
        #
        # for i in resource.findAll({'usage':'geo'}):
        #     if i['name'] not in key2:
        #         key2.append(i['name'])
        #         key1.append(resource.basicData['geo']['chineseName'][i['name']])
        # for i in resource.findAll({'usage':'build', 'flag':'red'}):
        #     key2.append(i['name'])
        #     key1.append(resource.basicData['geo']['chineseName'][i['name']])
        # for i in resource.findAll({'usage': 'dw', 'action': 'left', 'flag': 'red'}):
        #     key2.append(i['name'])
        #     key1.append(resource.basicData['money']['chineseName'][i['name']])
        #
        # if key == 'skim_double':
        #     if self.tmpView:
        #         try:
        #             self.tmpView.deleteLater()
        #         except RuntimeError:
        #             pass
        #     self.tmpView = QWidget()
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     self.tmpView.name = list(self.lines.keys())[data.row()]
        #     self.tmpView.data = self.lines[self.tmpView.name]
        #     self.tmpView.setWindowTitle('台词《'+self.tmpView.name+'》')
        #     # print(self.lines.keys())
        #     layout1 = QHBoxLayout()
        #     tem = QComboBox(self.tmpView)
        #     tem.before = key1[0]
        #     tem.isconnected = True
        #     tem.currentIndexChanged.connect(functools.partial(self.linesCpu, 'add_modify'))
        #     tem.addItems(key1)
        #     layout1_1 = QHBoxLayout()
        #     layout1_1.addWidget(tem)
        #     tem = QPushButton('上一个', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', 1))
        #     layout1_1.addWidget(tem)
        #     tem = QPushButton('下一个', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', -1))
        #     layout1_1.addWidget(tem)
        #     layout1.addLayout(layout1_1)
        #     tem = QPushButton('ok', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_ok'))
        #     layout1.addWidget(tem)
        #     layout = QHBoxLayout()
        #     layout.addLayout(layout1)
        #     tem = QTextEdit(self.tmpView)
        #     # tem.setReadOnly(True)
        #     layout.addWidget(tem)
        #     self.tmpView.setLayout(layout)
        #     self.tmpView.show()
        #     self.tmpView.findChild(QComboBox).setCurrentIndex(0)
        #
        # elif key == 'skim':
        #     if self.tmpView:
        #         try:
        #             self.tmpView.deleteLater()
        #         except RuntimeError:
        #             pass
        #     self.tmpView = QWidget()
        #     self.tmpView.setWindowTitle('浏览')
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     layout = QVBoxLayout()
        #     tem = QListWidget()
        #     tem.addItems(self.lines.keys())
        #     self.tmpView = QListWidget()
        #     self.tmpView.setWindowTitle('浏览')
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     self.tmpView.addItems(self.lines.keys())
        #     print(self.lines.keys())
        #     self.tmpView.show()
        #     self.tmpView.doubleClicked.connect(functools.partial(self.linesCpu, 'skim_double'))
        # elif key == 'delete':
        #     pass
        #
        # elif key == 'add':
        #     if self.tmpView:
        #         try:
        #             self.tmpView.deleteLater()
        #         except RuntimeError:
        #             pass
        #     self.tmpView = QWidget()
        #     self.tmpView.setWindowTitle('添加台词')
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     end = {}
        #     for i in key2:
        #         end[i] = []
        #     self.tmpView.data = end
        #     layout1 = QHBoxLayout()
        #     tem = QLineEdit(self.tmpView)
        #     tem.setPlaceholderText('名称')
        #     layout1.addWidget(tem)
        #     tem = QComboBox(self.tmpView)
        #     tem.before = key1[0]
        #     tem.isconnected = True
        #     tem.currentIndexChanged.connect(functools.partial(self.linesCpu, 'add_modify'))
        #     tem.addItems(key1)
        #     layout1_1 = QHBoxLayout()
        #     layout1_1.addWidget(tem)
        #     tem = QPushButton('上一个', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', 1))
        #     layout1_1.addWidget(tem)
        #     tem = QPushButton('下一个', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_updown', -1))
        #     layout1_1.addWidget(tem)
        #     layout1.addLayout(layout1_1)
        #     tem = QPushButton('ok', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.linesCpu, 'add_ok'))
        #     layout1.addWidget(tem)
        #     layout = QHBoxLayout()
        #     layout.addLayout(layout1)
        #     tem = QTextEdit(self.tmpView)
        #     # tem.setReadOnly(True)
        #     layout.addWidget(tem)
        #     self.tmpView.setLayout(layout)
        #     self.tmpView.show()
        #
        # elif key == 'add_updown':
        #     com = self.tmpView.findChild(QComboBox)
        #     com.isconnected = False
        #     view = self.tmpView.findChild(QTextEdit)
        #     id = com.currentText()
        #     for i1, i in enumerate(key1):
        #         if i == id:
        #             break
        #     com.before = id
        #     id = key2[i1]
        #     self.tmpView.data[id] = view.toPlainText().split('\n')
        #     if data == 1:
        #         if com.currentIndex() == 0:
        #             return
        #         com.setCurrentIndex(com.currentIndex()-1)
        #         text = ''
        #         for i in self.tmpView.data[key2[com.currentIndex()]]:
        #             text += '\n' + i
        #         view.setText(text)
        #     else:
        #         if com.currentIndex() == len(key2) -1:
        #             return
        #         com.setCurrentIndex(com.currentIndex()+1)
        #         text = ''
        #         for i in self.tmpView.data[key2[com.currentIndex()]]:
        #             text += '\n' + i
        #         view.setText(text)
        #     # com.currentIndexChanged.disconnect(functools.partial(self.linesCpu, 'add_modify'))
        #
        # elif key == 'add_modify':
        #     com = self.tmpView.findChild(QComboBox)
        #     view = self.tmpView.findChild(QTextEdit)
        #     if not com.isconnected:
        #         com.isconnected = True
        #         return
        #     id_ = com.before
        #     for i1, i in enumerate(key1):
        #         if i == id_:
        #             break
        #     try:
        #         self.tmpView.data[key2[i1]] = view.toPlainText().split('\n')
        #     except AttributeError:
        #         return
        #     id = com.currentText()
        #     for i1, i in enumerate(key1):
        #         if i == id:
        #             break
        #     com.before = id
        #     id = key2[i1]
        #     text = ''
        #     for i in self.tmpView.data[id]:
        #         text +=  i +'\n'
        #     view.setText(text)
        #
        # elif key == 'add_ok':
        #     id = self.tmpView.findChild(QComboBox).currentText()
        #     for i1, i in enumerate(key1):
        #         if i == id:
        #             break
        #     id = key2[i1]
        #     self.tmpView.data[id] = self.tmpView.findChild(QTextEdit).toPlainText().split('\n')
        #     #%%%%%%
        #     for i1, i in self.tmpView.data.items():
        #         newData = []
        #         for j in i:
        #             if j != '':
        #                 newData.append(j)
        #         self.tmpView.data[i1] = newData
        #     print(self.tmpView.data)
        #     if self.tmpView.findChild(QLineEdit):
        #         self.lines[self.tmpView.findChild(QLineEdit).text()] = self.tmpView.data
        #     else:
        #         self.lines[self.tmpView.name] = self.tmpView.data
        #     self.tmpView.deleteLater()
        #     resource.saveMap(self.vmap.map['name'], lines=self.lines)
        # # elif key == 'zz':
        # #     if not self.roles:
        # #         return
        # #     if self.tmpView:
        # #         try:
        # #             self.tmpView.deleteLater()
        # #         except RuntimeError:
        # #             pass
        # #     self.tmpView = QWidget()
        # #     self.tmpView.setWindowTitle('组装台词')
        # #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        # #     layout1 = QVBoxLayout()
        # #     items = self.roles.keys()
        # #     for i in items:
        # #         tem = QPushButton('    ', self.tmpView)
        # #         tem.setStyleSheet('background-color:'+str(i)+';')
        # #         layout1.addWidget(tem)
        # #     tem = QPushButton('ok', self.tmpView)
        # #     tem.clicked.connect(functools.partial(self.linesCpu, 'zz_ok'))
        # #     layout1.addWidget(tem)
        # #     layout2 = QVBoxLayout()
        # #     for i in items:
        # #         tem = QComboBox(self.tmpView)
        # #         tem.addItem('')
        # #         tem.addItems(self.lines.keys())
        # #         tem.flag = i
        # #         layout2.addWidget(tem)
        # #     layout = QHBoxLayout()
        # #     layout.addLayout(layout1)
        # #     layout.addLayout(layout2)
        # #     self.tmpView.setLayout(layout)
        # #     self.tmpView.show()
        # # elif key == 'zz_ok':
        # #     items = self.tmpView.findChildren(QComboBox)
        # #     for i in items:
        # #         self.roles[i.flag] = i.currentText()
        # #     self.tmpView.deleteLater()

    def basicDataCpu(self, data=None):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        path = 'maps/' + self.vmap.map['name'] + '/basicInfo.json'
        if not os.path.exists(path):
            with open('resource/basicInfo.json', 'r') as f:
                tem_d = json.load(f)
            with open(path, 'w') as f:
                json.dump(tem_d, f)
        self.tmpView = basicEditW(path)
        self.tmpView.setWindowTitle('参数设置')
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()

    def backupCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        path = 'maps/' + self.vmap.map['name'] + '/backup.json'
        self.tmpView = backupEditWin(path)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()

    def toggleCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        self.tmpView = TriggerEditWin(self.vmap.map['name'])
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()


    def sourceCpu(self, key):
        if key == 'swap':
            if self.tmpView:
                try:
                    self.tmpView.deleteLater()
                except RuntimeError:
                    pass
            resource.initMap(self.vmap.map['name'])
            self.swapMap(self.vmap.map['name'])
        elif key == 'sounds':
            file = QFileDialog.getExistingDirectory(self, '选择音效所在文件夹')
            resource.saveMap(self.vmap.map['name'], soundPath=file)
        elif key == 'images':
            file = QFileDialog.getExistingDirectory(self, '选择图片所在文件夹')
            resource.saveMap(self.vmap.map['name'], imagePath=file)

    def storyCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        path = 'maps/' + self.vmap.map['name'] + '/stories.json'
        self.tmpView = storyEditWin(path)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()

    #--> 没选则此势力没有指挥官 <--#
    def heroCpu(self, key):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        resource.initMap(self.vmap.map['name'], True)
        self.tmpView = herosEditWin(self.vmap.map['name'])
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()
        # path = 'maps/' + self.vmap.map['name'] + '/herosLimitation.json'
        # if key == 'open':
        #     if self.tmpView:
        #         try:
        #             self.tmpView.deleteLater()
        #         except RuntimeError:
        #             pass
        #     self.tmpView = QWidget()
        #     self.tmpView.setWindowModality(Qt.ApplicationModal)
        #     if not os.path.exists(path):
        #         tem_data = {}
        #         with open(path, 'w') as f:
        #             json.dump({}, f)
        #     else:
        #         with open(path, 'r') as f:
        #             tem_data = json.load(f)
        #     layout = QVBoxLayout()
        #     heros = []
        #     for i in resource.findAll({'usage':'hero', 'action':'head'}):
        #         heros.append(i['name'])
        #     for i in ['red', 'blue', 'green', 'yellow']:
        #         layout1 = QHBoxLayout()
        #         layout1.addWidget(QLabel(i, self.tmpView))
        #         for j in heros:
        #             tem = QCheckBox(j, self.tmpView)
        #             tem.data = i
        #             if i in tem_data:
        #                 if j in tem_data[i]:
        #                     tem.setChecked(True)
        #             layout1.addWidget(tem)
        #         layout.addLayout(layout1)
        #     tem = QPushButton('save', self.tmpView)
        #     tem.clicked.connect(functools.partial(self.heroCpu, 'save'))
        #     layout.addWidget(tem)
        #     self.tmpView.setLayout(layout)
        #     self.tmpView.show()
        #
        # elif key == 'save':
        #     end = {'red':[], 'blue':[], 'green':[], 'yellow':[]}
        #     for i in self.tmpView.findChildren(QCheckBox):
        #         if i.isChecked():
        #             end[i.data].append(i.text())
        #     for i, j in end.items():
        #         if not j:
        #             del end[i]
        #     with open(path, 'w') as f:
        #         json.dump(end, f)
        #     self.tmpView.deleteLater()
        #     self.tool.herosLimitationChange(path)

    def ruleCpu(self):
        if self.tmpView:
            try:
                self.tmpView.deleteLater()
            except RuntimeError:
                pass
        self.tmpView = ruleEditWin(self.vmap.map['name'])
        self.tmpView.setWindowModality(Qt.ApplicationModal)
        self.tmpView.show()

    ##------使用前必须切换images---------------懒啊---------------#
    def mergeCpu(self):
        ## lines, basicData
        with open('maps/'+self.vmap.map['name']+'/lines.json', 'r') as f:
            tem = json.load(f)
        with open('resource/lines.json', 'r') as f:
            tem_ = json.load(f)

        if 'default' not in tem:
            tem['default'] = tem_['default']
        else:
            for i, j in tem_['default'].items():
                if i not in tem['default']:
                    tem[i] = j

        with open('maps/'+self.vmap.map['name']+'/lines.json', 'w') as f:
            json.dump(tem, f)

        with open('maps/'+self.vmap.map['name']+'/basicInfo.json', 'r') as f:
            tem = json.load(f)
        with open('resource/basicInfo.json', 'r') as f:
            tem_ = json.load(f)
        if 'default' not in tem:
            tem['default'] = tem_['default']
        else:
            for i1, i in tem_['default'].items():
                if i1 not in tem['default']:
                    tem[i] = i
                else:
                    for j1, j in tem_['default'][i1].items():
                        if j1 not in tem['default'][i1]:
                            tem['default'][j1] = j
                        else:
                            for k1, k in tem_['default'][i1][j1].items():
                                if k1 not in tem_['default'][i1][j1]:
                                    tem_['default'][i1][j1][k1] = k

        with open('maps/'+self.vmap.map['name']+'/basicInfo.json', 'w') as f:
            json.dump(tem, f)

        resource.makeMapGeoImage()


    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() in [Qt.Key_Escape, Qt.Key_Return]:
            self.vmap.keyReleaseEvent(a0)
        return super(EditWin, self).keyReleaseEvent(a0)

    # def event(self, event: QtCore.QEvent) -> bool:
    #     if event.type() == toggleChooseEvent.idType:
    #         if event.type_ == 'toChoose':
    #             self.vmap.enterChooseMode(event.type_, event.data)
    #             self.tmpView.hide()
    #             self.vmapMode = event.type_
    #             self.findChild(QMenuBar).setEnabled(False)
    #         elif event.type_ == 'toShow':
    #             self.vmap.enterChooseMode(event.type_, event.data)
    #             self.tmpView.hide()
    #             self.vmapMode = event.type_
    #             self.findChild(QMenuBar).setEnabled(False)
    #         elif event.type_ == 'toChoosed':
    #             print(event.data, 'server')
    #             if event.data:
    #                 self.tmpView.choosed(event.data)
    #             self.tmpView.show()
    #             self.vmapMode = None
    #             self.findChild(QMenuBar).setEnabled(True)
    #         elif event.type_ == 'toShowed':
    #             self.tmpView.show()
    #             self.vmapMode = None
    #             self.findChild(QMenuBar).setEnabled(True)
    #     return super(EditWin, self).event(event)


##nav
class newWin(QWidget):
    def initUI(self, brother=None, mapName=None, winSize=(600, 400)):
        '''
        :param brother:
        :param mapName: 无名则为newMap
        :param winSize:
        :return:
        '''
        self.mapName = mapName
        self.map = {}
        self.isNewMap = True if mapName == None else False
        if self.mapName == None:
            self.mapName = hashlib.md5(str(time.time_ns()).encode()).hexdigest()[:8]
        else:
            self.mapName = mapName
        self.map = resource.makeMap(self.mapName, '地图描述')
        self.mapPriName = self.mapName if self.isNewMap else mapName

        self.setWindowTitle('新建地图' if self.isNewMap else '修改地图')
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
            if i['name'] not in tem_list_2:
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
        # if self.isNewMap:
        nowName = self.findChild(QLineEdit).text()
        if nowName == 'default' or nowName == '':
            return
        self.mapName = nowName
        # print(self.mapPriName, self.mapName)
        resource.saveMap(self.mapPriName, newName=self.mapName, map=self.map)
        if self.brother:
            self.brother.swapMap(self.mapName)
            self.close()
        # else:
        #     self.map['name'] = self.name_.text()
        #     resource.saveMap(self.map, self.mapPriName)
        #     if self.brother:
        #         self.brother.swapMap(self.map['name'])
        #         self.close()

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
            tem_label = QPushButton(i['name'])
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

##%%台词模板%% or 无模板
class linesEditWin(QWidget):
    def __init__(self, file):
        super(linesEditWin, self).__init__()
        self.key1 = ['随机', '开战前', '主城附近', '收入不足', '收入充足', '收入过多', '支出过多', '支出过少', \
                '故事背景', '局势', '侦查到', '侦查没到', '下潜没被发现', '下潜被发现', '隐身被发现', '隐身没被发现', '计划补给', \
                '规模低', '规模充足', '油量低', '油量充足', '弹药低', '弹药充足', '近战', '远程', '移动攻击', \
                '单位被困且危险', '单位被困但安全', '单位安全', '可攻击目标少', '可攻击目标多']
        self.key2 = ['random', 'beforebattle', 'nearhead', 'smallsalary', 'enoughsalary', 'muchsalary', \
                'storybackground', 'situation', 'watched', 'watching', 'diving', 'dived', 'stealthing', 'stealthed', \
                'plansupply', 'lessguimo', 'enoughguimo', 'lessoil', 'enoughoil', 'lessbullect', 'enoughbullect', \
                'shortrange', 'longrange', 'attackaftermove', 'trapped_danger', 'trapped_safe', 'untrapped',
                'moretargets', 'lesstargets']

        for i in resource.findAll({'usage': 'geo'}):
            if i['name'] not in self.key2:
                self.key2.append(i['name'])
                self.key1.append(resource.basicData['geo']['chineseName'][i['name']])
        for i in resource.findAll({'usage': 'build', 'flag': 'red'}):
            self.key2.append(i['name'])
            self.key1.append(resource.basicData['geo']['chineseName'][i['name']])
        for i in resource.findAll({'usage': 'dw', 'action': 'left', 'flag': 'red'}):
            self.key2.append(i['name'])
            self.key1.append(resource.basicData['money']['chineseName'][i['name']])
        self.data = {}
        self.nowName = None
        for i in self.key2:
            self.data[i] = []
        self.path = file
        with open(file, 'r') as f:
            self.lines = json.load(f)
        self.initUI()
        self.openEle(False)

    def initUI(self):
        tem = QListWidget(self)
        tem.addItems(self.lines.keys())
        tem.doubleClicked.connect(self.linesDouble)
        tem.itemClicked.connect(self.linesDouble)
        layout1 = QVBoxLayout()
        layout1.addWidget(tem)
        layout11 = QHBoxLayout()
        tem = QPushButton('delete', self)
        tem.clicked.connect(self.linesDelete)
        layout11.addWidget(tem)
        tem = QLineEdit(self)
        tem.setPlaceholderText('名称')
        layout11.addWidget(tem)
        tem = QPushButton('add', self)
        tem.clicked.connect(self.linesAdd)
        layout11.addWidget(tem)
        tem = QPushButton('rename', self)
        tem.clicked.connect(self.linesRename)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout2 = QVBoxLayout()
        tem = QComboBox(self)
        tem.before = self.key1[0]
        tem.isconnected = True
        tem.currentIndexChanged.connect(self.modify)
        tem.addItems(self.key1)
        layout2.addWidget(tem)
        tem = QPushButton('上一个(alt+&q)', self)
        tem.clicked.connect(functools.partial(self.upOrDown, 1))
        layout2.addWidget(tem)
        tem = QPushButton('下一个(alt+&w)', self)
        tem.clicked.connect(functools.partial(self.upOrDown, -1))
        layout2.addWidget(tem)
        tem = QPushButton('save(ctrl+s)', self)
        tem.setShortcut('ctrl+s')
        tem.clicked.connect(self.save)
        layout2.addWidget(tem)
        layout = QHBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        tem = QTextEdit(self)
        # tem.setReadOnly(True)
        layout.addWidget(tem)
        self.setLayout(layout)
        self.show()

    def upOrDown(self, data):
        com = self.findChild(QComboBox)
        com.isconnected = False
        view = self.findChild(QTextEdit)
        id = com.currentText()
        for i1, i in enumerate(self.key1):
            if i == id:
                break
        com.before = id
        id = self.key2[i1]
        self.data[id] = view.toPlainText().split('\n')
        if data == 1:
            if com.currentIndex() == 0:
                return
            com.setCurrentIndex(com.currentIndex()-1)
            text = ''
            for i in self.data[self.key2[com.currentIndex()]]:
                text += '\n' + i
            view.setText(text)
        else:
            if com.currentIndex() == len(self.key2) -1:
                return
            com.setCurrentIndex(com.currentIndex()+1)
            text = ''
            for i in self.data[self.key2[com.currentIndex()]]:
                text += '\n' + i
            view.setText(text)

    def modify(self):
        com = self.findChild(QComboBox)
        view = self.findChild(QTextEdit)
        if not com.isconnected:
            com.isconnected = True
            return
        id_ = com.before
        for i1, i in enumerate(self.key1):
            if i == id_:
                break
        try:
            self.data[self.key2[i1]] = view.toPlainText().split('\n')
        except AttributeError:
            return
        id = com.currentText()
        for i1, i in enumerate(self.key1):
            if i == id:
                break
        com.before = id
        id = self.key2[i1]
        text = ''
        for i in self.data[id]:
            text +=  i +'\n'
        view.setText(text)

    def openEle(self, should=True):
        # if should:
        self.findChild(QComboBox).setEnabled(should)
        tem = self.findChildren(QPushButton)
        for i in tem[-3:]:
            i.setEnabled(should)
        # QComboBox.setEnabled()

    def linesDouble(self, data:None):
        self.openEle(True)
        tem = self.findChild(QListWidget)
        tem.current = tem.currentItem()
        tem.index = tem.currentIndex().row()
        tem_ = tem.currentItem()
        if tem_.text() == self.nowName:
            return
        self.nowName = tem_.text()
        self.data = self.lines[tem_.text()]
        self.findChild(QComboBox).setCurrentIndex(0)
        text = ''
        tem_d = self.findChild(QComboBox).currentText()
        for i1, i in enumerate(self.key1):
            if i == tem_d:
                break
        for i in self.data[self.key2[i1]]:
            text += i +'\n'
        self.findChild(QTextEdit).setText(text)

    def linesDelete(self):
        tem = self.findChild(QListWidget)
        item = tem.current
        text = item.text()
        if text not in self.lines:
            return
        del self.lines[text]
        tem.takeItem(tem.index)

    def linesAdd(self):
        tem = self.findChild(QLineEdit)
        if tem.text() == '' or tem.text() in self.lines:
            return
        end = {}
        for i in self.key2:
            end[i] = []
        self.lines[tem.text()] = end
        self.findChild(QListWidget).addItem(QListWidgetItem(tem.text()))
        self.nowName = tem.text()
        self.findChild(QTextEdit).setText('')
        self.openEle(True)

    def linesRename(self):
        tem = self.findChild(QLineEdit)
        tem_ = self.findChild(QListWidget)
        if tem.text() == '' or self.nowName == None:
            return
        self.lines[tem.text()] = self.lines[self.nowName].copy()
        del self.lines[self.nowName]
        tem_.addItem(QListWidgetItem(tem.text()))
        tem_.takeItem(tem_.index)
        self.nowName = tem.text()

    def save(self):
        id = self.findChild(QComboBox).currentText()
        for i1, i in enumerate(self.key1):
            if i == id:
                break
        id = self.key2[i1]
        self.data[id] = self.findChild(QTextEdit).toPlainText().split('\n')
        #%%%%%%
        for i1, i in self.data.items():
            newData = []
            for j in i:
                if j != '':
                    newData.append(j)
            self.data[i1] = newData
        if self.nowName == None:
            return
        self.lines[self.nowName] = self.data
        with open(self.path, 'w') as f:
            json.dump(self.lines, f)


class backupEditWin(QWidget):
    def __init__(self, path, MAX=12):
        super(backupEditWin, self).__init__()
        self.path = path
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)
                self.data = {}
        else:
            with open(path, 'r') as f:
                self.data = json.load(f)
        self.MAX = MAX
        self.initUI()
        self.read()

    def initUI(self):
        self.setWindowTitle('制作加成')
        tem_table = QTableWidget(self)
        dws = resource.findAll({'usage': 'dw', 'flag': 'red', 'action': 'left'})
        tem_table.setColumnCount(len(dws) + 1)
        tem_table.setRowCount(self.MAX)
        tem_table.setHorizontalHeaderItem(0, QTableWidgetItem('id'))
        for i, j in enumerate(dws):
            tem_table.setHorizontalHeaderItem(i + 1, QTableWidgetItem(QIcon(j['pixmap']), j['name']))
        for i in range(self.MAX):
            for j in range(len(dws) + 1):
                tem_table.setItem(i, j, QTableWidgetItem(''))
        layout = QVBoxLayout()
        layout.addWidget(QLabel('加成的影响范围'))
        layout.addWidget(tem_table)
        tem_table = QTableWidget(self)
        dws = ['move_distance', 'view_distance', 'gf_g', 'gf_maxdistance', 'gf_mindistance', 'dsc']
        tem_table.setColumnCount(len(dws) + 1)
        tem_table.setRowCount(self.MAX)
        tem_table.setHorizontalHeaderItem(0, QTableWidgetItem('id'))
        for i, j in enumerate(dws):
            tem_table.setHorizontalHeaderItem(i + 1, QTableWidgetItem(j))
        for i in range(self.MAX):
            for j in range(len(dws) + 1):
                tem_table.setItem(i, j, QTableWidgetItem(''))
        layout.addWidget(QLabel('加成的实体'))
        layout.addWidget(tem_table)
        tem_table = QPushButton('ok', self)
        tem_table.clicked.connect(self.save)
        layout.addWidget(tem_table)
        self.setLayout(layout)
        self.resize(800, 400)
        self.show()

    def read(self):
        tables = self.findChildren(QTableWidget)
        for i, j in enumerate(self.data.keys()):
            tables[0].item(i, 0).setText(j)
            tables[1].item(i, 0).setText(j)
        for i1, i in enumerate(self.data.keys()):
            for j in range(1, tables[1].columnCount()):
                if tables[1].horizontalHeaderItem(j).text() in self.data[i]:
                    tables[1].item(i1, j).setText(str(self.data[i][tables[1].horizontalHeaderItem(j).text()]))
            for j in range(1, tables[0].columnCount()):
                if tables[0].horizontalHeaderItem(j).text() in self.data[i]['range']:
                    tables[0].item(i1, j).setText('1')

    def save(self):
        self.data = {}
        self.setWindowTitle('制作加成')
        tables = self.findChildren(QTableWidget)
        for i in range(tables[1].rowCount()):
            tem_data = tables[1].item(i, 0).text()
            if tem_data == '':
                continue
            self.data[tem_data] = {}
            for j in range(1, tables[1].columnCount()):
                try:
                    tem_data_1 = int(tables[1].item(i, j).text())
                except ValueError:
                    if tables[1].item(i, j).text() != '':
                        self.setWindowTitle('制作加成;error:格式不符')
                        return
                    continue
                if tem_data_1 == 0:
                    continue
                self.data[tem_data][tables[1].horizontalHeaderItem(j).text()] = tem_data_1
            for j in range(tables[0].rowCount()):
                tem_dd = tables[0].item(i, 0).text()
                if tem_dd == tem_data:
                    end = []
                    for k in range(1, tables[0].columnCount()):
                        if tables[0].item(j, k).text() in ['', '0']:
                            continue
                        end.append(tables[0].horizontalHeaderItem(k).text())
                    if end:
                        self.data[tem_data]['range'] = end
                    break
        with open(self.path, 'w') as f:
            json.dump(self.data, f)

class storyEditWin(QWidget):
    def __init__(self, path):
        super(storyEditWin, self).__init__()
        self.path = path
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)
                self.data = {}
        else:
            with open(path, 'r') as f:
                self.data = json.load(f)
        self.nowName = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('制作故事情节')
        layout1 = QVBoxLayout()
        tem = QListWidget()
        tem.addItems(self.data.keys())
        tem.clicked.connect(self.clicked)
        layout1.addWidget(tem)
        layout11 = QHBoxLayout()
        tem = QPushButton('delete', self)
        tem.clicked.connect(self.delete)
        layout11.addWidget(tem)
        layout11.addWidget(QLineEdit(self))
        tem = QPushButton('add', self)
        tem.clicked.connect(self.add)
        layout11.addWidget(tem)
        tem = QPushButton('rename', self)
        tem.clicked.connect(self.rename)
        layout11.addWidget(tem)
        layout1.addLayout(layout11)
        layout2 = QVBoxLayout()
        tem = QTextEdit(self)
        tem.setPlaceholderText('任务背景')
        layout2.addWidget(tem)
        tem = QTextEdit(self)
        tem.setPlaceholderText('任务目标')
        layout2.addWidget(tem)
        tem = QPushButton('save')
        tem.clicked.connect(self.save)
        layout2.addWidget(tem)
        layout = QHBoxLayout(self)
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)
        self.show()

    def clicked(self, data:None):
        self.save()
        tem_ = self.findChild(QListWidget)
        tem = tem_.currentItem().text()
        tem_.index = tem_.currentIndex().row()
        com = self.findChildren(QTextEdit)
        com[0].setText(self.data[tem]['command_bg'])
        com[1].setText(self.data[tem]['command'])
        self.nowName = tem

    def delete(self):
        if self.nowName == None:
            return
        tem = self.findChild(QListWidget)
        try:
            tem.takeItem(tem.currentIndex().row())
            # tem.takeItem(tem.index)
        except:
            print('nono')
        del self.data[self.nowName]
        com = self.findChildren(QTextEdit)
        com[0].setText('')
        com[1].setText('')
        self.nowName = None

    def add(self):
        tem = self.findChild(QListWidget)
        text = self.findChild(QLineEdit).text()
        if text in self.data or text == '':
            return
        tem.addItem(QListWidgetItem(text))
        self.data[text] = {'command_bg':'', 'command':''}

    def rename(self):
        if self.nowName == None:
            return
        text = self.findChild(QLineEdit).text()
        if text == '' or text in self.data:
            return
        tem = self.findChild(QListWidget)
        text_ = tem.currentItem().text()
        tem.takeItem(tem.currentIndex().row())
        tem.addItem(QListWidgetItem(text))
        self.data[text] = self.data[text_].copy()
        del self.data[text_]
        self.save()

    def save(self):
        if self.nowName == None:
            return
        com = self.findChildren(QTextEdit)
        self.data[self.nowName]['command_bg'] = com[0].toPlainText()
        self.data[self.nowName]['command'] = com[1].toPlainText()
        with open(self.path, 'w') as f:
            json.dump(self.data, f)

class herosEditWin(QWidget):
    def __init__(self, mapName):
        super(herosEditWin, self).__init__()
        self.mapName = mapName
        self.path = 'maps/'+mapName+'/heroAtrs.json'
        self.flags = ['red', 'bule', 'green', 'yellow']
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}
            for i in self.flags:
                self.data[i] = {'enemy':[], 'heros':[], \
                                'ctrl':'玩家', 'backup':'', 'lines':'', 'story':'', \
                                'oil':0, 'bullect':0, 'money':0, 'landmissile':0 ,\
                                'seamissile':0, 'skymissile':0, 'nuclear':0
                                }
            with open(self.path, 'w') as f:
                json.dump(self.data, f)

        self.initUI()
        self.nowflag = self.flags[0]
        self.swap(self.flags[0])

    def initUI(self):
        layout1 = QHBoxLayout()
        for i in self.flags:
            tem = QPushButton(i, self)
            tem.clicked.connect(functools.partial(self.swap, i))
            layout1.addWidget(tem)
        layout2 = QHBoxLayout()
        for i in range(3):
            tem = QCheckBox(str(i), self)
            layout2.addWidget(tem)
        layout3 = QHBoxLayout()
        for i in resource.findAll({'usage':'hero', 'action': 'head'}):
            print(i, 'i')
            tem = QPushButton(QIcon(i['pixmap']), i['name'], self)
            tem.clicked.connect(functools.partial(self.chooseHero, tem))
            tem.choosed = False
            tem.name = i['name']
            layout3.addWidget(tem)
        layout4 = QHBoxLayout()
        self.userBtn = QComboBox(self)
        self.userBtn.addItems(['玩家', '电脑', '无'])
        self.backupBtn = QComboBox(self)
        self.backupBtn.addItems(list(resource.storage_backup.keys()))
        self.linesBtn = QComboBox(self)
        self.linesBtn.addItems(list(resource.storage_lines.keys()))
        self.storyBtn = QComboBox(self)
        self.storyBtn.addItems(list(resource.storage_stories.keys()))
        layout4.addWidget(self.userBtn)
        layout4.addWidget(self.backupBtn)
        layout4.addWidget(self.linesBtn)
        layout4.addWidget(self.storyBtn)

        layout5 = QHBoxLayout()
        layout5.addWidget(QLabel('油量:', self))
        tem = QSpinBox(self)
        tem.data = 'oil'
        tem.setSingleStep(100)
        tem.setMaximum(999999)
        layout5.addWidget(tem)
        layout5.addWidget(QLabel('弹药:', self))
        tem = QSpinBox(self)
        tem.setSingleStep(10)
        tem.data = 'bullect'
        tem.setMaximum(99999)
        layout5.addWidget(tem)
        layout5.addWidget(QLabel('资金:', self))
        tem = QSpinBox(self)
        tem.data = 'money'
        tem.setSingleStep(1000)
        tem.setMaximum(999999999)
        layout5.addWidget(tem)
        layout5.addWidget(QLabel('对陆导弹:', self))
        tem = QSpinBox(self)
        tem.setSingleStep(1)
        tem.data = 'landmissile'
        tem.setMaximum(100)
        layout5.addWidget(tem)
        layout5.addWidget(QLabel('对空导弹:', self))
        tem = QSpinBox(self)
        tem.setSingleStep(1)
        tem.data = 'skymissile'
        tem.setMaximum(100)
        layout5.addWidget(tem)
        layout5.addWidget(QLabel('对舰导弹:', self))
        tem = QSpinBox(self)
        tem.setSingleStep(1)
        tem.data = 'seamissile'
        tem.setMaximum(100)
        layout5.addWidget(tem)
        layout5.addWidget(QLabel('核弹:', self))
        tem = QSpinBox(self)
        tem.data = 'nuclear'
        tem.setSingleStep(1)
        tem.setMaximum(100)
        layout5.addWidget(tem)

        layout = QFormLayout()
        layout.addRow('势力', layout1)
        layout.addRow('敌对势力', layout2)
        layout.addRow('可选英雄', layout3)
        layout.addRow('重要参数', layout4)
        layout.addRow('基础资源', layout5)
        tem = QPushButton('save', self)
        tem.clicked.connect(self.save)
        layout.addWidget(tem)
        self.setLayout(layout)

    def swap(self, flag):
        self.collect()
        flags = []
        self.nowflag = flag
        for i in self.flags:
            if i != flag:
                flags.append(i)
        for i, j in zip(self.findChildren(QCheckBox), flags):
            i.setText(j)
            if j in self.data[flag]['enemy']:
                i.setChecked(True)
            else:
                i.setChecked(False)
        btns = self.findChildren(QPushButton)
        for i in btns:
            if not hasattr(i, 'name'):
                continue
            if i.name in self.data[flag]['heros']:
                i.setText(i.name+'(已选)')
            else:
                i.setText(i.name)
        self.userBtn.setCurrentText(self.data[flag]['ctrl'])
        self.backupBtn.setCurrentText(self.data[flag]['backup'])
        self.linesBtn.setCurrentText(self.data[flag]['lines'])
        self.storyBtn.setCurrentText(self.data[flag]['story'])
        spins = self.findChildren(QSpinBox)
        for i in spins:
            i.setValue(self.data[flag][i.data])

    def chooseHero(self, arg:QPushButton):
        if arg.choosed:
            arg.choosed = False
            arg.setText(arg.name)
        else:
            arg.choosed = True
            arg.setText(arg.name+'(已选)')

    def collect(self):
        self.data[self.nowflag]['enemy'] = []
        self.data[self.nowflag]['heros'] = []
        checks = self.findChildren(QCheckBox)
        for i in checks:
            if i.isChecked():
                self.data[self.nowflag]['enemy'].append(i.text())
        for i in self.findChildren(QPushButton):
            if hasattr(i, 'choosed'):
                if i.choosed:
                    self.data[self.nowflag]['heros'].append(i.name)
        self.data[self.nowflag]['ctrl'] = self.userBtn.currentText()
        self.data[self.nowflag]['backup'] = self.backupBtn.currentText()
        self.data[self.nowflag]['lines'] = self.linesBtn.currentText()
        self.data[self.nowflag]['story'] = self.storyBtn.currentText()
        for i in self.findChildren(QSpinBox):
            if hasattr(i, 'data'):
                self.data[self.nowflag][i.data] = i.value()

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f)


''''
    指定单位：存活，规模，油量，弹药，占领，下潜/隐身
    指定建筑：占领
    指定区域：敌军进入
    资金：损失，造成，军队资金，
    指定回合，每个回合
    指挥官能量
    输入指令


    *** 回合延迟
    指定单位：规模，油量，弹药，加成，存活，所属，
    指定建筑：所属，改变
    资金：减少，增加，变为，
    触发：启动，删除，停止
    指挥官能量
    故事背景，台词，基本配置
    胜利，移交控制权限
    屏幕提示
'''

class TriggerEditWin(QWidget):
    def __init__(self, mapName):
        super(TriggerEditWin, self).__init__()
        self.mapName = mapName
        self.initUI()
        path = 'maps/' + self.mapName +'toggles.json'
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)
        with open(path, 'r') as f:
            data = json.load(f)
        self.rightView.updateToggles(data)


    def initUI(self):
        self.leftView = triggerEditWin(self.mapName, self)
        self.rightView = triggerEventEditWin(self.mapName, self)
        self.updateBtn = QPushButton('更新标记', self)
        self.updateBtn.clicked.connect(self.updateMarkets)
        layout = QVBoxLayout()
        layout.addWidget(self.leftView)
        layout.addWidget(self.updateBtn)
        layout.addWidget(self.rightView)
        self.setLayout(layout)

    def updateMarkets(self):
        path = 'maps/'+self.mapName+'/markets.json'
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)
            data = {}
        else:
            with open(path, 'r') as f:
                data = json.load(f)
        keys = list(data.keys())
        self.leftView.updateMarkets(keys)
        self.rightView.updateMarkets(keys)

    def saved(self, data):
        self.rightView.updateToggles(list(data.keys()))


class MyListWidget(QWidget):
    '''
    其父类需要有 getAddData(),save(self, track)
    '''
    def __init__(self, parent, data):
        super(MyListWidget, self).__init__(parent)
        self.data = data
        self.initUI()

    def initUI(self):
        self.listView = QListWidget(self)
        self.listView.addItems(self.data.keys())
        self.listView.clicked.connect(self.choose)
        self.deleteBtn = QPushButton('删除', self)
        self.deleteBtn.clicked.connect(self.listDelete)
        self.addBtn = QPushButton('添加', self)
        self.addBtn.clicked.connect(self.listAdd)
        self.nameInput = QLineEdit(self)
        self.renameBtn = QPushButton('重命名', self)
        self.renameBtn.clicked.connect(self.listRename)
        self.saveBtn = QPushButton('保存', self)
        self.saveBtn.clicked.connect(self.listSave)
        layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout1.addWidget(self.deleteBtn)
        layout1.addWidget(self.nameInput)
        layout1.addWidget(self.addBtn)
        layout1.addWidget(self.renameBtn)
        layout1.addWidget(self.saveBtn)
        layout.addWidget(self.listView)
        layout.addLayout(layout1)
        self.setLayout(layout)

    def choose(self):
        self.parent().choose(self.data[self.listView.currentItem().text()])

    def listAdd(self):
        text = self.nameInput.text()
        if text == '' or text in self.data:
            return
        self.listView.addItem(QListWidgetItem(text, self.listView))
        self.data[text] = self.parent().getAddData()

    def listDelete(self):
        if self.listView.currentItem() == None:
            return
        index = self.listView.currentIndex().row()
        del self.data[self.listView.currentItem().text()]
        self.listView.takeItem(index)

    def listRename(self):
        if self.listView.currentItem() == None:
            return
        if self.nameInput.text() == '' or self.nameInput.text() in self.data:
            return
        self.data[self.nameInput.text()] = self.data[self.listView.currentItem().text()].copy()
        del self.data[self.listView.currentItem().text()]
        self.listView.currentItem().setText(self.nameInput.text())

    def listSave(self):
        self.parent().save(self.data)


class triggerEditWin(QWidget):
    def __init__(self, mapName, parent):
        super(triggerEditWin, self).__init__(parent)
        self.mapName = mapName
        self.path = 'maps/'+mapName+'/toggles.json'
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({}, f)
        self.nowPoint = 0
        self.objs = ['单位', '区域', '建筑', '资金', '回合', '指令', '同盟']
        #self.objs_ = ['单位', '建筑', '区域', '资金', '触发器', '能量', '胜败', '指挥权', '消息']
        self.initUI()
        self.findChild(QPushButton).click()

    def initUI(self):
        with open(self.path, 'r') as f:
            tem_data = json.load(f)
        self.listView = MyListWidget(self, tem_data)
        layout1 = QHBoxLayout()
        for i in self.objs:
            tem = QPushButton(i, self)
            tem.clicked.connect(functools.partial(self.swap, i))
            layout1.addWidget(tem)
        self.dwView = triggerDw(self)
        self.areaView = triggerArea(self)
        self.buildView = triggerBuild(self)
        self.moneyView = triggerMoney(self)
        self.boutView = triggerBout(self)
        self.commandView = triggerCommand(self)
        self.alliance = triggerAlliance(self)
        self.views = [self.dwView, self.areaView, \
                      self.buildView, self.moneyView, self.boutView, \
                      self.commandView, self.alliance]
        layout = QVBoxLayout()
        layout.addWidget(self.listView)
        layout.addLayout(layout1)

        for i in self.views:
            layout.addWidget(i)
        self.setLayout(layout)

    def swap(self, arg):
        for i in self.views:
            i.hide()
        for i, j in zip(enumerate(self.objs), self.views):
            if i[1] == arg:
                j.show()
                self.nowPoint = i[0]
                break

    def getAddData(self):
        track = self.views[self.nowPoint].getData()
        track['obj'] = self.objs[self.nowPoint]
        return track

    def choose(self, track):
        self.swap(track['obj'])
        self.views[self.nowPoint].setData(track)

    def save(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f)
        if self.parent():
            self.parent().saved(data)

    def updateMarkets(self, keys):
        for i in self.views[:3]:
            i.updateMarkets(keys)

class triggerDw(QWidget):
    def __init__(self, parent):
        super(triggerDw, self).__init__(parent)
        self.attrs = ['规模', '油量', '弹药', '占领', '阵亡', '隐身', '下潜', '所属']
        self.initUI()
        self.swap(self.attrs[0])

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.typeBtn.currentTextChanged.connect(self.swap)
        self.compareBtn = QComboBox(self)
        self.compareBtn.addItems(['<', '>', '='])
        self.spinBtn = QSpinBox(self)
        self.isBtn = QCheckBox('yes?', self)
        self.marketsBtn = QComboBox(self)

        layout = QVBoxLayout()
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.compareBtn)
        layout.addWidget(self.spinBtn)
        layout.addWidget(self.isBtn)
        layout.addWidget(self.marketsBtn)
        self.setLayout(layout)

    def swap(self, text=None):
        for i1, i in enumerate(self.attrs):
            if i == text:
                break
        if i1 < 3:
            self.compareBtn.show()
            self.spinBtn.show()
            self.isBtn.hide()
        elif i1 < 7:
            self.compareBtn.hide()
            self.spinBtn.hide()
            self.isBtn.show()
        else:
            self.compareBtn.hide()
            self.spinBtn.hide()
            self.isBtn.hide()

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        for i1, i in enumerate(self.attrs):
            if i == track['type']:
                break
        if i1 < 3:
            self.compareBtn.setCurrentText(track['data'])
            self.spinBtn.setValue(track['value'])
            self.marketsBtn.setCurrentText(track['market'])
        elif i1 < 7:
            self.isBtn.setChecked(track['data'])

    def getData(self):
        track = {'type': self.typeBtn.currentText()}
        for i1, i in enumerate(self.attrs):
            if i == track['type']:
                break
        if i1 < 3:
            track['data'] = self.compareBtn.currentText()
            track['value'] = self.spinBtn.value()
            track['market'] = self.marketsBtn.currentText()
        elif i1 < 7:
            track['data'] = self.isBtn.isChecked()

        return track

    def updateMarkets(self, keys):
        self.marketsBtn.clear()
        self.marketsBtn.addItems(keys)

class triggerArea(QWidget):
    def __init__(self, parent):
        super(triggerArea, self).__init__(parent)
        self.attrs = ['己方单位进入', '己方单位移出', '己方单位阵亡', \
                      '友方单位进入', '友方单位移出', '友方单位阵亡', \
                      '敌方单位进入', '敌方单位移出', '敌方单位阵亡']
        self.initUI()

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.marketsBtn = QComboBox(self)

        layout = QVBoxLayout()
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.marketsBtn)

        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.marketsBtn.setCurrentText(track['market'])

    def getData(self):
        track = {'type': self.typeBtn.currentText(), \
                 'market':self.marketsBtn.currentText()}
        return track

    def updateMarkets(self, keys):
        self.marketsBtn.clear()
        self.marketsBtn.addItems(keys)

class triggerBuild(triggerArea):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.attrs = ['所属']
        self.initUI()

class triggerMoney(QWidget):
    def __init__(self, parent):
        super(triggerMoney, self).__init__(parent)
        self.attrs = ['资金', '回合支出', '损失', '造成损失', '军力', '总油耗', '总弹药消耗', '能量']
        self.initUI()

    def initUI(self):
        self.flagsBtn = QComboBox(self)
        self.flagsBtn.addItems(['red', 'blue', 'green', 'yellow', '触发者', '被触发者'])
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.compareBtn = QComboBox(self)
        self.compareBtn.addItems(['<', '>', '='])
        self.spinBtn = QSpinBox(self)

        layout = QVBoxLayout()
        layout.addWidget(self.flagsBtn)
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.compareBtn)
        layout.addWidget(self.spinBtn)
        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.compareBtn.setCurrentText(track['data'])
        self.spinBtn.setValue(track['value'])
        self.flagsBtn.setCurrentText(track['flag'])

    def getData(self):
        track = {'type': self.typeBtn.currentText()}
        track['data'] = self.compareBtn.currentText()
        track['value'] = self.spinBtn.value()
        track['flag'] = self.flagsBtn.currentText()
        return track

class triggerBout(QWidget):
    def __init__(self, parent):
        super(triggerBout, self).__init__(parent)
        self.attrs = ['指定回合', '间隔回合']
        self.flags = ['red', 'blue', 'green', 'yellow']
        self.initUI()

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.spinBtn = QSpinBox(self)
        layout = QHBoxLayout(self)
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.spinBtn)
        layout1 = QHBoxLayout()
        for i in self.flags:
            tem = QCheckBox(i, self)
            layout1.addWidget(tem)
        layout.addLayout(layout1)
        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.spinBtn.setValue(track['data'])
        for i in self.findChildren(QCheckBox):
            if i.text() in track['value']:
                i.setChecked(True)
            else:
                i.setChecked(False)

    def getData(self):
        track = {'type': self.typeBtn.currentText(), 'value':[]}
        track['data'] = self.spinBtn.value()
        for i in self.findChildren(QCheckBox):
            if i.isChecked():
                track['value'].append(i.text())
        return track

class triggerCommand(QWidget):
    def __init__(self, parent):
        super(triggerCommand, self).__init__(parent)
        self.attrs = ['指令']
        self.initUI()

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.inputBtn = QLineEdit(self)
        layout = QHBoxLayout(self)
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.inputBtn)
        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.inputBtn.setText(track['data'])

    def getData(self):
        track = {'type': self.typeBtn.currentText()}
        track['data'] = self.inputBtn.text()
        return track

class triggerAlliance(QWidget):
    def __init__(self, parent):
        super(triggerAlliance, self).__init__(parent)
        self.attr = ['结盟', '毁盟']
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attr)
        layout.addWidget(self.typeBtn)
        for i in ['red', 'blue', 'green', 'yellow']:
            tem = QCheckBox(i, self)
            layout.addWidget(tem)
        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        for i in self.findChildren(QCheckBox):
            if i.text() in track['data']:
                i.setChecked(True)
            else:
                i.setChecked(False)

    def getData(self):
        track = {'type': self.typeBtn.currentText(), 'data':[]}
        for i in self.findChildren(QCheckBox):
            if i.isChecked():
                track['data'].append(i.text())
        return track

##-------------------------------------------

class triggerEventEditWin(QWidget):
    def __init__(self, mapName, parent):
        super(triggerEventEditWin, self).__init__(parent)
        self.mapName = mapName
        self.path = 'maps/'+mapName+'/toggleEvents.json'
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({}, f)

        self.nowPoint = 0
        self.objs = ['单位', '区域', '建筑', '资金', '触发器', '胜败', '指挥权', '消息']
        # self.objs = ['单位', '建筑', '区域', '资金', '回合', '能量', '指令', '同盟']
        self.initUI()
        self.findChild(QPushButton).click()

    def initUI(self):
        with open(self.path, 'r') as f:
            tem_data = json.load(f)
        self.listView = MyListWidget(self, tem_data)
        layout1 = QHBoxLayout()
        for i in self.objs:
            tem = QPushButton(i, self)
            tem.clicked.connect(functools.partial(self.swap, i))
            layout1.addWidget(tem)
        self.responseBtn = QComboBox(self)
        layout1.addWidget(self.responseBtn)
        self.dwView = triggerEventDw(self)
        self.areaView = triggerEventArea(self)
        self.buildView = triggerEventBuild(self)
        self.moneyView = triggerEventMoney(self)
        self.toggleView = triggerEventtoggle(self)
        self.victoryView = triggerEventVictory(self)
        self.ctrlView = triggerEventCtrl(self)
        self.msgView = triggerEventMsg(self)
        self.views = [self.dwView, self.areaView, \
                      self.buildView, self.moneyView, self.toggleView, \
                      self.victoryView, self.ctrlView, self.msgView]
        layout = QVBoxLayout()
        layout.addWidget(self.listView)
        layout.addLayout(layout1)
        for i in self.views:
            layout.addWidget(i)
        self.setLayout(layout)

    def swap(self, arg):
        for i in self.views:
            i.hide()
        for i, j in zip(enumerate(self.objs), self.views):
            if i[1] == arg:
                j.show()
                self.nowPoint = i[0]
                break

    def getAddData(self):
        track = self.views[self.nowPoint].getData()
        track['obj'] = self.objs[self.nowPoint]
        track['response'] = self.responseBtn.currentText()
        return track

    def choose(self, track):
        self.swap(track['obj'])
        self.views[self.nowPoint].setData(track)
        self.responseBtn.setCurrentText(track['response'])

    def save(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f)

    def updateMarkets(self, keys):
        for i in self.views[:3]:
            i.updateMarkets(keys)

    def updateToggles(self, keys):
        self.responseBtn.clear()
        self.responseBtn.addItems(keys)
        self.toggleView.updateToggles(keys)

class triggerEventDw(QWidget):
    def __init__(self, parent):
        super(triggerEventDw, self).__init__(parent)
        self.attrs = ['规模', '油量', '弹药', '占领', '阵亡', '隐身', '下潜', '所属']
        self.initUI()
        self.swap(self.attrs[0])

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.typeBtn.currentTextChanged.connect(self.swap)
        self.compareBtn = QComboBox(self)
        self.compareBtn.addItems(['+', '-', '='])
        self.spinBtn = QSpinBox(self)
        self.isBtn = QCheckBox('yes?', self)
        self.flagsBtn = QComboBox(self)
        self.flagsBtn.addItems(['red', 'blue', 'green', 'yellow', '触发者', '被触发者'])
        self.marketsBtn = QComboBox(self)

        layout = QVBoxLayout()
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.compareBtn)
        layout.addWidget(self.spinBtn)
        layout.addWidget(self.isBtn)
        layout.addWidget(self.flagsBtn)
        layout.addWidget(self.marketsBtn)
        self.setLayout(layout)

    def swap(self, text=None):
        for i1, i in enumerate(self.attrs):
            if i == text:
                break
        if i1 < 3:
            self.compareBtn.show()
            self.spinBtn.show()
            self.isBtn.hide()
            self.flagsBtn.hide()
        elif i1 < 7:
            self.compareBtn.hide()
            self.spinBtn.hide()
            self.isBtn.show()
            self.flagsBtn.hide()
        else:
            self.compareBtn.hide()
            self.spinBtn.hide()
            self.isBtn.hide()
            self.flagsBtn.show()

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.marketsBtn.setCurrentText(track['market'])
        for i1, i in enumerate(self.attrs):
            if i == track['type']:
                break
        if i1 < 3:
            self.compareBtn.setCurrentText(track['data'])
            self.spinBtn.setValue(track['value'])
        elif i1 < 7:
            self.isBtn.setChecked(track['data'])
        else:
            self.flagsBtn.setCurrentText(track['data'])

    def getData(self):
        track = {'type': self.typeBtn.currentText()}
        for i1, i in enumerate(self.attrs):
            if i == track['type']:
                break
        if i1 < 3:
            track['data'] = self.compareBtn.currentText()
            track['value'] = self.spinBtn.value()
        elif i1 < 7:
            track['data'] = self.isBtn.isChecked()
        else:
            track['data'] = self.flagsBtn.currentText()
        track['market'] = self.marketsBtn.currentText()
        return track

    def updateMarkets(self, keys):
        self.marketsBtn.clear()
        self.marketsBtn.addItems(keys)

class triggerEventBuild(QWidget):
    def __init__(self, parent):
        super(triggerEventBuild, self).__init__(parent)
        self.attrs = ['所属']
        self.initUI()

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.flagsBtn = QComboBox(self)
        self.flagsBtn.addItems(['red', 'blue', 'green', 'yellow', '触发者', '被触发者'])
        self.marketsBtn = QComboBox(self)

        layout = QHBoxLayout()
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.flagsBtn)
        layout.addWidget(self.marketsBtn)

        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.flagsBtn.setCurrentText(track['data'])
        self.marketsBtn.setCurrentText(track['market'])

    def getData(self):
        track = {'type': self.typeBtn.currentText()}
        track['data'] = self.flagsBtn.currentText()
        track['market'] = self.marketsBtn.currentText()
        return track

    def updateMarkets(self, keys):
        self.marketsBtn.clear()
        self.marketsBtn.addItems(keys)

class triggerEventArea(QWidget):
    def __init__(self, parent):
        super(triggerEventArea, self).__init__(parent)
        self.attrs = ['阵亡', '大损伤', '中等损伤', '小损伤', '支援']
        self.data = {}
        self.supportView = editToolDwLSView(self)
        self.supportView.setWindowModality(Qt.ApplicationModal)
        self.supportView.hide()
        self.initUI()

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.supportBtn = QPushButton('选择单位', self)
        self.marketBtn = QComboBox(self)
        layout = QVBoxLayout()
        layout.addWidget(self.typeBtn)
        for i in ['red', 'blue', 'green', 'yellow', '触发者', '被触发者']:
            tem = QCheckBox(i, self)
            layout.addWidget(tem)
        layout.addWidget(self.supportBtn)
        layout.addWidget(self.marketBtn)

        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.marketBtn.setCurrentText(track['market'])
        for i in self.findChildren(QCheckBox):
            if i.text() in track['data']:
                i.setChecked(True)
            else:
                i.setChecked(False)
        self.data = track['value']

    def getData(self):
        track = {'type': self.typeBtn.currentText(), 'data':[], 'value':None }
        for i in self.findChildren(QCheckBox):
            if i.isChecked():
                track['data'].append(i.text())
        track['value'] = self.data
        track['market'] = self.marketBtn.currentText()
        return track

    def showSupport(self):
        self.supportView.show(self.data)

    def updateMarkets(self, keys):
        self.marketsBtn.clear()
        self.marketsBtn.addItems(keys)

class triggerEventMoney(QWidget):
    def __init__(self, parent):
        super(triggerEventMoney, self).__init__(parent)
        self.attrs = ['资金', '油', '弹药', '对空导弹', '对陆导弹', '对舰导弹', '核弹', '能量']
        self.initUI()

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.compareBtn = QComboBox(self)
        self.compareBtn.addItems(['+', '-', '='])
        self.spinBtn = QSpinBox(self)
        self.spinBtn.setMaximum(1000000)

        layout = QVBoxLayout()
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.compareBtn)
        layout.addWidget(self.spinBtn)
        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.compareBtn.setCurrentText(track['data'])
        self.spinBtn.setValue(track['value'])

    def getData(self):
        track = {'type': self.typeBtn.currentText()}
        track['data'] = self.compareBtn.currentText()
        track['value'] = self.spinBtn.value()
        return track

class triggerEventVictory(QWidget):
    def __init__(self, parent):
        super(triggerEventVictory, self).__init__(parent)
        self.attrs = ['胜', '败']
        self.initUI()

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.victoryBtn = QComboBox(self)
        self.victoryBtn.addItems(['red', 'bule', 'green', 'yellow', '触发者', '被触发者'])
        layout = QHBoxLayout()
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.victoryBtn)
        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.victoryBtn.setCurrentText(track['data'])

    def getData(self, track):
        track = {'type':self.typeBtn.currentText(), 'data':self.victoryBtn.currentText()}
        return track

class triggerEventCtrl(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.attrs = ['移交', '接管']
        self.initUI()

    def initUI(self):
        self.fromBtn = QComboBox(self)
        self.fromBtn.addItems(['red', 'blue', 'green', 'yellow', '触发者', '被触发者'])
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.victoryBtn = QComboBox(self)
        self.victoryBtn.addItems(['red', 'bule', 'green', 'yellow', '触发者', '被触发者'])
        layout = QHBoxLayout()
        layout.addWidget(self.fromBtn)
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.victoryBtn)
        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.victoryBtn.setCurrentText(track['value'])
        self.fromBtn.setCurrentText(track['data'])

    def getData(self, track):
        track = {'type':self.typeBtn.currentText(), \
                 'value':self.victoryBtn.currentText(), \
                 'data':self.fromBtn.currentText()}
        return track

class triggerEventMsg(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.attrs = ['red', 'blue', 'green', 'yellow', '触发者', '被触发者', '系统']
        self.initUI()

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.compareBtn = QComboBox(self)
        self.compareBtn.addItems(\
            ['所有人', '盟友们', '敌人们', 'red', 'blue', 'green', 'yellow', '触发者']\
            )
        self.spinBtn = QLineEdit(self)

        layout = QVBoxLayout()
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.compareBtn)
        layout.addWidget(self.spinBtn)
        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.compareBtn.setCurrentText(track['data'])
        self.spinBtn.setText(track['value'])

    def getData(self):
        track = {'type': self.typeBtn.currentText()}
        track['data'] = self.compareBtn.currentText()
        track['value'] = self.spinBtn.text()
        return track

class triggerEventtoggle(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.attrs = ['禁用', '开启']
        self.initUI()

    def initUI(self):
        self.typeBtn = QComboBox(self)
        self.typeBtn.addItems(self.attrs)
        self.compareBtn = QComboBox(self)

        # with open(self.path, 'r') as f:
        #     tem_d = list(json.load(f).keys())
        # self.compareBtn.addItems(tem_d)

        layout = QVBoxLayout()
        layout.addWidget(self.typeBtn)
        layout.addWidget(self.compareBtn)
        self.setLayout(layout)

    def setData(self, track):
        self.typeBtn.setCurrentText(track['type'])
        self.compareBtn.setCurrentText(track['data'])

    def getData(self):
        track = {'type': self.typeBtn.currentText()}
        track['data'] = self.compareBtn.currentText()
        return track

    def updateToggles(self, keys):
        self.compareBtn.clear()
        self.compareBtn.addItems(keys)

#-----------------------------------------------------------------
class marketEditEvent(QEvent):
    none = 0
    choose = 1
    show = 2
    idType = QEvent.registerEventType()
    def __init__(self, type_=None, obj=None, data=None):
        '''

        :param type_: show , choose
        :param data:{'flag':'none', 'usage':'red'}
        :param obj:
        '''
        super(marketEditEvent, self).__init__(marketEditEvent.idType)
        self.type_ = type_
        self.data = data
        self.obj = obj


class ruleEditWin(QWidget):
    def __init__(self, mapName):
        super(ruleEditWin, self).__init__()
        self.basic_path = ['stories', 'lines', 'basicInfo', 'backup', 'toggles', 'toggleEvents', 'rule']
        self.data = {}
        for i in self.basic_path:
            path = 'maps/'+mapName+'/'+i+'.json'
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump({}, f)
                    self.data[i] = {}
            else:
                with open(path, 'r') as f:
                    self.data[i] = json.load(f)
        self.ruleData = self.data['rule'].copy()
        del self.data['rule']
        self.path = 'maps/'+mapName+'/rule.json'
        self.initUI()

    def initUI(self):
        max_cols = 12
        layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout1.addWidget(QLabel('role', self))
        for i in self.basic_path[:-3]:
            layout1.addWidget(QLabel(i, self))
        layout.addLayout(layout1)
        for i in ['red', 'blue', 'green', 'yellow']:
            layout1 = QHBoxLayout()
            layout1.addWidget(QLabel(i, self))
            for j in self.basic_path[:-3]:
                tem = QComboBox(self)
                tem.addItems(self.data[j].keys())
                tem.data = j
                tem.key = i
                if i in self.ruleData:
                    if j in self.ruleData[i]:
                        tem.setCurrentText(self.ruleData[i][j])
                layout1.addWidget(tem)
            tem = QLineEdit(self)
            tem.setPlaceholderText('初始资金')
            tem.key = i
            tem.data = 'beginMoney'
            if i in self.ruleData:
                if 'beginMoney' in self.ruleData[i]:
                    tem.setText(self.ruleData[i]['beginMoney'])
            layout1.addWidget(tem)
            tem = QLineEdit(self)
            tem.setPlaceholderText('初始能量(%)')
            tem.key = i
            tem.data = 'beginEnergy'
            if i in self.ruleData:
                if 'beginEnergy' in self.ruleData[i]:
                    tem.setText(self.ruleData[i]['beginEnergy'])
            layout1.addWidget(tem)
            layout1.addWidget(QLabel('敌人', self))
            for j in ['red', 'blue', 'green', 'yellow']:
                tem = QCheckBox(j, self)
                tem.data = i
                if i in self.ruleData:
                    if 'enemy' in self.ruleData[i]:
                        if j in self.ruleData[i]['enemy']:
                            tem.setChecked(True)
                layout1.addWidget(tem)

            layout.addLayout(layout1)
        layout.addWidget(QLabel('启动触发器', self))
        if 'itIsOn' in self.ruleData:
            toggles_ = self.ruleData['itIsOn']
        else:
            self.ruleData['itIsOn'] = []
            toggles_ = []
        toggles = list(self.data['toggles'].keys())
        tLen = len(toggles)
        i = 0
        while 1:
            layout1 = QHBoxLayout()
            for j in toggles[i:i+max_cols if i+max_cols < tLen else tLen]:
                tem = QCheckBox(j, self)
                if j in toggles_:
                    tem.setChecked(True)
                layout1.addWidget(tem)
            layout.addLayout(layout1)
            i += max_cols
            if i >= tLen:
                break
        tem = QPushButton('save', self)
        tem.clicked.connect(self.save)
        layout.addWidget(tem)
        self.setLayout(layout)
        self.show()

    def save(self):
        end = {'red':{}, 'blue':{}, 'green':{} , 'yellow':{}, 'itIson':[]}
        for i in self.findChildren(QComboBox):
            end[i.key][i.data] = i.currentText()
        for i in self.findChildren(QLineEdit):
            end[i.key][i.data] = i.text()
        tems = self.findChildren(QCheckBox)
        for i in tems[:16]:
            if i.isChecked():
                if 'enemy' not in end[i.data]:
                    end[i.data]['enemy'] = []
                end[i.data]['enemy'].append(i.text())
        for i in tems[16:]:
            if i.isChecked():
                end['itIson'].append(i.text())
        self.ruleData = end
        with open(self.path, 'w') as f:
            json.dump(self.ruleData, f)


if __name__ == '__main__':
    window = EditWin()
    # window = triggerEditWin('default')
    # window = triggerEventEditWin('default')
    # window = TriggerEditWin('default')
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
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :mainWindow.py
# @Time      :2021/8/7 14:11
# @Author    :russionbear

from PyQt5.Qt import *
from PyQt5 import QtCore
import sys, time, functools, socket, json, zlib
from resource_load import resource
from map_load import DW, Geo
from net.netTool import findRooms, enterRoom, RoomServer, LOCAL_IP, BROADCAST_PORT, myThread

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

    def enterRoom(self, room:QtCore.QModelIndex, isOwner=False):
        if not isOwner:
            tem = self.findChild(SkimRoom)
            room = tem.ipsAndRooms[room.row()]
        self.setWindowTitle('等待玩家')
        self.fgFrame.deleteLater()
        # self.fgFrame.close()
        self.fgFrame = RoomInner(self, self.size(), room, isOwner)
        self.fgFrame.show()

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

        # self.updateRooms()
        self.timer = self.startTimer(5000)
        # self.timer = QTimer(self)
        # self.timer.start(5000)
        self.findRoomThread = None

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
        tem_btn.clicked.connect(self.skimMaps)
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
        try:
            newData = findRooms()
            # newData = [(('192.168.100.9', 1111), {'type': 'map', 'author': 'hula', 'authorid': '123',
            #                'map': {'name': 'netmap', 'map': [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], 'dw': [], 'dsc': 'just for test'}})]
            if self.roomPoint == -1:
                selected = None
            else:
                selected = self.ipsAndRooms[self.roomPoint]
            if selected:
                print(selected)
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
        except RuntimeError:
            pass
        finally:
            # print('finally error')
            pass

    def choosedMap(self, map:QtCore.QModelIndex):
        room = (LOCAL_IP, BROADCAST_PORT), {'type': 'map', 'author': resource.userInfo['username'], 'authorid': resource.userInfo['userid'],
         'map': resource.maps[map.row()]}
        self.skimMapsView.close()
        self.parent().enterRoom(room,True)

    def skimMaps(self):
        self.skimMapsView = SkimMaps(self)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        print('timer for updating rooms')
        if self.findRoomThread:
            self.findRoomThread.stop()
        del self.findRoomThread
        self.findRoomThread = myThread(target=self.updateRooms)
        self.findRoomThread.start()

    def deleteLater(self) -> None:
        print('page for rooms is closed')
        self.killTimer(self.timer)
        if self.findRoomThread:
            self.findRoomThread.stop()
        return super(SkimRoom, self).deleteLater()


class RoomInner(QWidget):
    def __init__(self, parent, winSize=QSize(800, 600), room=None, isOwer=False):
        super(RoomInner, self).__init__(parent=parent)
        # self.room = (('192.168.100.9', 1111), {'type': 'map', 'author': 'hula', 'authorid': '123',
        #                                        'map': {'name': 'netmap',
        #                                                'map': [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]],
        #                                                'dw': [], 'dsc': 'just for test', 'flags':['red', 'blue']}})
        self.room = room
        #####%%%%%特殊处理
        self.room[1]['map']['flags'] = ['red', 'blue']
        self.isOwner = isOwer
        self.user = resource.userInfo.copy()
        self.user['flag'] = 'none'
        self.user['hero'] = 'google'
        self.users = [self.user]
        self.initUI(winSize)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        if not self.isOwner:
            self.connected = True
            try:
                self.client.connect(self.room[0])
            except socket.timeout:
                self.parent().toIntranet()
                return
            except OSError:
                self.parent().toIntranet()
                return
            print('enterRoom ok')

            self.clientThread = myThread(target=self.handleServer)
            self.clientThread.start()
            requestion = {'type': 'enterroom', 'user': self.user.copy()}
            self.client.send(zlib.compress(json.dumps(requestion).encode('utf-8')))

    def initUI(self, winSize):
        self.setFixedSize(winSize)

        self.area = QScrollArea(self)
        self.miniMap = miniVMap(self.area, self.room[1]['map'])
        self.area.setWidget(self.miniMap)

        self.text_dsc = QTextEdit(self.room[1]['map']['dsc'], self)
        self.text_dsc.setReadOnly(True)

        layout = QFormLayout()
        heros = resource.findAll({'usage': 'hero', 'action': 'head'})

        self.flagBtns = []
        for i1, i in enumerate(self.room[1]['map']['flags']):
            tem_btn = QPushButton('    ', self)
            tem_btn.setStyleSheet('background-color:'+str(i)+';color:white;')
            tem_btn.color = i
            tem_btn.id = None
            com1 = QComboBox(self)
            for j in heros:
                com1.addItem(QIcon(j['pixmap']), j['name'])
            tem_btn.setFocusPolicy(Qt.ClickFocus)
            com1.setFocusPolicy(Qt.ClickFocus)
            tem_btn.clicked.connect(functools.partial(self.choose, i1))
            com1.currentIndexChanged.connect(functools.partial(self.choose, -1))
            layout.addRow(tem_btn, com1)
            self.flagBtns.append(tem_btn)

        layout4 = QBoxLayout(QBoxLayout.LeftToRight)
        if self.isOwner:
            self.invate = QPushButton('发布邀请')
            self.invate.clicked.connect(self.publish)
            layout4.addWidget(self.invate)
        tem_btn = QPushButton('返回')
        tem_btn.clicked.connect(self.parent().toIntranet)
        layout4.addWidget(tem_btn)

        layout3 = QBoxLayout(QBoxLayout.TopToBottom)
        self.messageShow = QTextEdit('<---  对话框   ---->', self)
        self.messageShow.setReadOnly(True)
        self.messageShow.setLineWrapMode(1)
        self.messageSend = QLineEdit(self)
        self.messageSend.editingFinished.connect(self.sendMessage)
        layout3.addWidget(self.messageShow)
        layout3.addWidget(self.messageSend)
        layout3.addLayout(layout4)

        tlayout = QBoxLayout(QBoxLayout.TopToBottom)
        layout1 = QBoxLayout(QBoxLayout.LeftToRight)
        layout2 = QBoxLayout(QBoxLayout.LeftToRight)
        layout1.addWidget(self.area)
        layout1.addWidget(self.text_dsc)
        layout2.addLayout(layout)
        layout2.addLayout(layout3)
        tlayout.addLayout(layout1)
        tlayout.addLayout(layout2)
        self.setLayout(tlayout)

    def choose(self, data=None):
        btns = self.flagBtns
        comboxs = self.findChildren(QComboBox)
        if data != -1:
            if self.flagBtns[data].id == None:
                for i1, i in enumerate(self.flagBtns):
                    if i.id == self.user['userid']:
                        self.flagBtns[i1].id = None
                        self.flagBtns[i1].setText('   ')
                self.flagBtns[data].id = self.user['userid']
                self.flagBtns[data].setText(self.user['username'])
        for i1, i in enumerate(btns):
            if i.id != None:
                for j1, j in enumerate(self.users):
                    if j['userid'] == i.id:
                        j['flag'] = i.color
                        j['hero'] = comboxs[i1].currentText()
                        break
        if self.connected:
            requestion = {'type': 'userupdate',
                          'user': self.user}
            self.client.send(zlib.compress(json.dumps(requestion).encode('utf-8')))

    def updateRols(self, users):
        self.users = users
        btns = self.findChildren(QPushButton)[0:len(self.room[1]['map']['flags'])]
        comboxs = self.findChildren(QComboBox)
        for i1, i in enumerate(btns):
            if i.id != None:
                for j1, j in enumerate(self.users):
                    if j['userid'] == i.id:
                        j['flag'] = i.color
                        j['hero'] = comboxs[i1].currentText()
                        break
        for i1, i in enumerate(self.users):
            for j1, j in enumerate(btns):
                if j.color == i['flag']:
                    # j.setText(i['name'])
                    # j.id = i['userid']
                    self.flagBtns[j1].setText(i['username'])
                    self.flagBtns[j1].id = i['userid']
                    break

    def handleServer(self):
        while 1:
            try:
                response = self.client.recv(3072)
                response = json.loads(zlib.decompress(response).decode('utf-8'))
            except (ConnectionResetError, zlib.error):
                print('direct to find rooms')
                self.client.close()
                self.parent().toIntranet()
                return
            # except zlib.error:
            #     self.client.close()
            #     break
            if response['type'] == 'userstatus':
                self.updateRols(response['users'])
                # print(response['users'])
            elif response['type'] == 'gamebegin':
                print('game begin')
                print('按钮点击失效，更新窗口')
            elif response['type'] == 'talk':
                text = self.messageShow.toPlainText()
                name = ':'
                for i in self.users:
                    if i['userid'] == response['fromid']:
                        name = i['username']+':'
                        break
                text = text + '\n' + name + response['context']
                self.messageShow.setText(text)
                print(response['context'])
            print(response)

    def publish(self):
        # self.user['userid'] = '0000'  ###%%%%%%%%%
        self.invate.setEnabled(False)
        self.invate.setText('已发布')
        self.roomServerThread = RoomServer(self.room[1], self.user.copy())
        self.roomServerThread.start()

        try:
            self.client.connect(self.room[0])
        except socket.timeout:
            self.parent().toIntranet()
            return
        except OSError:
            self.parent().toIntranet()
            return
        self.clientThread = myThread(target=self.handleServer)
        self.clientThread.start()
        requestion = {'type': 'enterroom', 'user': self.user.copy()}
        self.client.send(zlib.compress(json.dumps(requestion).encode('utf-8')))
        self.connected = True

    def sendMessage(self):
        text = self.messageShow.toPlainText()
        text = text + '\n' + self.user['username'] + ':' + self.messageSend.text()
        self.messageShow.setText(text)
        if self.connected:
            requestion = {'type': 'talk', 'fromid':self.user['userid'], 'context':self.messageSend.text()}
            self.client.send(zlib.compress(json.dumps(requestion).encode('utf-8')))
        self.messageSend.setText('')

    def deleteLater(self) -> None:
        if self.clientThread:
            self.clientThread.stop()
        if self.client:
            self.client.close()
        if self.roomServerThread:
            self.roomServerThread.endServer()
            # self.roomServerThread.stop()
        return super(RoomInner, self).deleteLater()

class SkimMaps(QWidget):
    def __init__(self, body):
        super(SkimMaps, self).__init__()
        self.body = body
        self.initUI()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle('选择地图')
        self.show()

    def initUI(self):
        self.setMinimumHeight(400)

        self.mapList = QListWidget(self)
        self.mapList.doubleClicked.connect(self.body.choosedMap)
        for i1, i in enumerate(resource.maps):
            self.mapList.addItem(QListWidgetItem(i['name']))
        self.mapList.clicked.connect(self.choose)

        self.area = QScrollArea(self)
        self.miniMap = miniVMap(self.area)
        self.area.setWidget(self.miniMap)

        self.text_dsc = QTextEdit('空空如也', self)
        self.text_dsc.setReadOnly(True)

        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout1 = QBoxLayout(QBoxLayout.TopToBottom)
        layout1.addWidget(self.area)
        layout1.addWidget(self.text_dsc)
        layout.addLayout(layout1)
        layout.addWidget(self.mapList)
        self.setLayout(layout)

    def choose(self):
        map = resource.maps[self.mapList.currentRow()]
        self.text_dsc.setText(map['dsc'])
        self.miniMap.deleteLater()
        self.miniMap = miniVMap(self.area, map)
        self.area.setWidget(self.miniMap)


if __name__ == "__main__":
    window = TopDirector()
    window.show()
    sys.exit(Qapp.exec_())

import random
import threading
import time

from PyQt5 import QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaContent, QMediaPlayer, QSound
from PyQt5.Qt import QApplication, QWidget, QLabel, QPixmap, QUrl, QPushButton
import sys
import os
import json
import re
import base64
import hashlib

ImagePath = 'resource/images'
BasicDataPath = 'configure/basic_info.json'
RecordsPath = 'configure/records.json'
MapsPath = 'configure/maps.json'
HafumanPath = 'configure/hafuman.json'
UserPath = 'configure/userInfo.json'
SoundPath = 'resource/sounds'

Qapp = QApplication(sys.argv)

class Resource():
    def __init__(self):
        self.imageRoot = ImagePath
        self.hafumanRoot = HafumanPath
        self.basicInfopath = BasicDataPath
        self.recordsPath = RecordsPath
        self.userPath = UserPath
        self.soundPath = SoundPath
        self.data = []
        self.hafuman = []
        self.maps = []
        self.records = []
        self.userInfo = None

        self.readImageData()

        # self.makeHafuman()
        self.readHafuman()
        # self.check()
        # print(self.findByHafuman('1'), self.hafuman)

        self.mapPath = MapsPath
        # self.maps.append(self.makeMap())
        # self.save()
        self.readMaps()
        # self.mapCheck()

        '''important data'''
        self.mapScaleList = [] #{'body':(100, 100),'font':30, 'tag':(40, 40)},
        for i in range(10,201,10):
            self.mapScaleList.append({'body':(i, i), 'font':10+i//5, 'tag':(i*2//5, i*2//5)})

        self.basicData = self.readBasicData()
        # print(self.basicData)

        self.readRecord()

        # self.makeUser()
        self.readUserInfo()

        self.initPlayer()

    def initPlayer(self):
        self.player = {}
        tem_data = os.listdir(self.soundPath)
        for i in tem_data:
            self.player[i[:-4]] = QSound(self.soundPath+'/'+i)
            if str(i[:-4]) in ['bao', 'btn']:
                self.player[i[:-4]].setLoops(1)
            else:
                self.player[i[:-4]].setLoops(999999)

    def readImageData(self):
        '''for developer'''
        keys = ['usage', 'name', 'flag', 'action']
        tem_data = os.listdir(self.imageRoot)
        for i in tem_data:
            com = re.sub('\..*', '', i)
            com = com.split('_')
            com_02 = {}
            if len(com) == 2:
                com.append('')
                com.append('')
            elif len(com) == 3:
                com.append('')
            for j in range(len(com)):
                com_02[keys[j]] = com[j]
            com_pm = QPixmap(self.imageRoot+'/'+i)
            com_02['pixmap'] = com_pm
            # com_02['base64'] = base64.b64encode(i.encode())
            com_02['base64'] = hashlib.md5(i.encode()).hexdigest()  ##[:8] 失误啊
            com_02['dsc'] = '步兵'
            self.data.append(com_02)

    def find(self, key={}):
        # print(key)
        # if 'hafuman' in key:
        #     del key['hafuman']
        for i in self.data:
            for j, k in key.items():
                if j not in i:
                    continue
                if i[j] != k:
                    break
            else:
                return i.copy()
        return None

    def findAll(self, key={}):
        end = []
        for i in self.data:
            for j, k in key.items():
                if j not in i:
                    continue  ###
                elif i[j] != k:
                    break
            else:
                end.append(i.copy())
        return end

    def check(self):
        '''for developer'''
        # for i in self.data:
        #     print(i)
        for i in self.hafuman:
            print(i)

    def makeHafuman(self):#provider
        end = []
        for i in range(len(self.data)):
            end.append((str(i), self.data[i]['base64']))
        with open(self.hafumanRoot, 'w') as f:
            json.dump(end, f)

    def addHafuman(self, base64):
        for i in range(len(self.hafuman)):
            if self.hafuman[i][1] == base64:
                break
        else:
            self.hafuman.append((len(self.hafuman), base64))

    def readHafuman(self):
        with open(self.hafumanRoot, 'r') as f:
            self.hafuman = json.load(f)

    def findHafuman(self, data, isBase64=True):
        if isBase64:
            for i in self.hafuman:
                if i[1] == data:
                    return i[0]
            else:
                return None
        else:
            for i in self.hafuman:
                if i[0] == data:
                    return i[1]
            else:
                return None

    def findByHafuman(self, hafuman):
        tem = self.findHafuman(hafuman, False)
        if not tem:
            return None
        for i in self.data:
            if i['base64'] == tem:
                return i.copy()
        else:
            return None

    def readMaps(self):
        with open(self.mapPath, 'r') as f:
            self.maps = json.load(f)

    ### 没有->一并改掉
    def saveMap(self, map=None, priName=None):
        if map:
            if priName:
                for i in range(len(self.maps)):
                    if self.maps[i]['name'] == priName:
                        self.maps[i] = map
                        break
            else:
                for i in range(len(self.maps)):
                    if self.maps[i]['name'] == map['name']:
                        self.maps[i] = map
                        break
                else:
                    self.maps.append(map)
        with open(self.mapPath, 'w') as f:
            json.dump(self.maps, f)

    ## waiting for updation
    def makeMap(self, name, dsc='', type='random', mapSize=(10, 10)):
        print(name, dsc, type, mapSize)
        hufumans = []
        if type == 'random':
            tem_data = self.findAll({'usage':'geo'})
            for i in tem_data:
                tem = self.findHafuman(i['base64'])
                if not tem:
                    print('hafuman error')
                    sys.exit()
                hufumans.append(tem)
        else:
            tem_data = self.find({'usage':'geo', 'name':type})
            if not tem_data:
                print('hafuman error')
                sys.exit()
            tem = self.findHafuman(tem_data['base64'])
            hufumans.append(tem)
        data = {}
        data['map'] = []
        for i in range(mapSize[1]):
            com = []
            for j in range(mapSize[0]):
                if type == 'random':
                    com.append(hufumans[random.randint(0, len(hufumans)-1)])
                else:
                    com.append(hufumans[0])
            data['map'].append(com)
        data['dsc'] = dsc
        data['dw'] = []
        data['name'] = name
        return data

    def deleteMap(self, name):
        for j, i in enumerate(self.maps):
            if i['name'] == name:
                self.maps.pop(j)

    def findMap(self, name):
        for i in self.maps:
            if i['name'] == name:
                return i.copy()
        else:
            return None

    def mapCheck(self):
        keys = ['map', 'name', 'dsc', 'dw']
        for k in self.maps:
            for i in k['map']:
                for j in i:
                    print('%-3d' % j, end='')
                print()
            for i in range(1, len(keys)):
                print(k[keys[i]])

    def readBasicData(self):
        with open(self.basicInfopath, 'r') as f:
            return json.load(f)

    def saveRecord(self, map):
        for j, i in enumerate(self.records):
            if i['recordName'] == map['recordName']:
                self.records[j] = map
        else:
            self.records.append(map)
        with open(self.recordsPath, 'w') as f:
            json.dump(self.records, f)

    def readRecord(self):
        with open(self.recordsPath, 'r') as f:
            self.records = json.load(f)
            # return json.dump(f)

    def makeUser(self):
        user = {'username':'bear', 'userid':'123', 'signal':'i can eat the stone without my body injured'}
        with open(self.userPath, 'w') as f:
            json.dump(user, f)

    def readUserInfo(self):
        with open(self.userPath, 'r') as f:
            self.userInfo = json.load(f)

resource = Resource()
resource.makeHafuman()

if __name__ == '__main__':
    # print(resource.mapScaleList)
    window = QWidget()
    window.show()
    btn = QPushButton('plaer1', window)
    btn.show()
    btn.clicked.connect(resource.player['move_car'].play)
    btn.move(0, 0)
    btn = QPushButton('player2', window)
    btn.show()
    btn.clicked.connect(resource.player['move_fighter'].play)
    btn.move(0, 30)

    btn = QPushButton('stop1', window)
    btn.show()
    btn.clicked.connect(resource.player['move_car'].stop)
    btn.move(0, 60)
    btn = QPushButton('stop2', window)
    btn.show()
    btn.clicked.connect(resource.player['move_fighter'].stop)
    btn.move(0, 90)
    # resource.player.play()
    sys.exit(Qapp.exec_())
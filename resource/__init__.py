#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :resource_loader.py
# @Time      :2021/9/4 13:51
# @Author    :russionbear

import random
import threading
import time

from PyQt5 import QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaContent, QMediaPlayer, QSound
from PyQt5.Qt import QApplication, QWidget, QLabel, QPixmap, QUrl, QPushButton
import sys
import os
import shutil
import json
import re
import base64
import hashlib


# from game import EVN
Qapp = QApplication(sys.argv)

'''图片，哈夫曼，单位配置，用户，声音'''

class Resource():
    def __init__(self):
        with open('resource/userInfo.json', 'r') as f:
            self.userInfo = json.load(f)

        self.maps = os.listdir('maps')

        self.mapScaleList = []  # {'body':(100, 100),'font':30, 'tag':(40, 40)},
        for i in range(10, 201, 10):
            self.mapScaleList.append({'body': (i, i), 'font': 10 + i // 5, 'tag': (i * 2 // 5, i * 2 // 5)})

        with open('resource/ini.json', 'r') as f:
            lastMap = json.load(f)['lastMap']
        self.initMap(lastMap)

    def initMap(self, mapName):
        self.mapName = mapName
        self.data = []
        self.initImageData(mapName)
        self.player = {}
        self.initPlayer(mapName)
        self.basicData = self.initBasicData(mapName)
        self.initRecords(mapName)
        with open('resource/ini.json', 'r') as f:
            tem_data = json.load(f)
        tem_data['lastMap'] = mapName
        with open('resource/ini.json', 'w') as f:
            json.dump(tem_data, f)

    def initImageData(self, mapName):
        '''for developer'''
        keys = ['usage', 'name', 'flag', 'action']
        tem_data = os.listdir('resource/images')
        tem_data = sorted(tem_data)
        tt_data = []
        if os.path.exists('maps/'+mapName+'/images'):
            td_data = os.listdir('maps/'+mapName+'/images')
            for i in td_data:
                if i in tem_data:
                    tt_data.append(i)
            tt_data = sorted(tt_data)

        for i1, i in enumerate(tem_data):
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
            if i in tt_data:
                com_pm = QPixmap('resource/'+i)
            else:
                com_pm = QPixmap('resource/images/'+i)
            # com_pm = QPixmap(self.imageRoot+'/'+i)
            com_02['pixmap'] = com_pm
            # com_02['base64'] = base64.b64encode(i.encode())
            # com_02['base64'] = hashlib.md5(i.encode()).hexdigest()[:8]  ##[:8] 失误啊
            com_02['base64'] = i1
            # com_02['dsc'] = '步兵'
            self.data.append(com_02)

    def initBasicData(self, mapName):
        if os.path.exists(mapName):
            path = 'maps/'+mapName+'/basicInfo.json'
        else:
            path = 'resource/basicInfo.json'
        with open(path, 'r') as f:
            return json.load(f)

    def initRecords(self, mapName):
        if os.path.exists('maps/'+mapName+'/records.json'):
            with open('maps/'+mapName+'/records.json', 'r') as f:
                self.records = json.load(f)
        else:
            self.records = []

    def initPlayer(self, mapName):
        tem_data = os.listdir('resource/sounds')
        # tt_data = os.listdir('maps/'+mapName+'/sounds')
        tt_data = []
        if os.path.exists('maps/' + mapName + '/sounds'):
            tt_data = os.listdir('maps/' + mapName + '/sounds')
        for i in tem_data:
            if i in tt_data:
                self.player[i[:-4]] = QSound('maps/'+mapName+'/sounds'+i)
            else:
                self.player[i[:-4]] = QSound('resource/sounds/'+i)
            if str(i[:-4]) in ['bao', 'btn']:
                self.player[i[:-4]].setLoops(1)
            else:
                self.player[i[:-4]].setLoops(999999)

    '''查找数据'''
    def find(self, key={}):
        key1 = ['usage', 'name', 'flag', 'action']
        for i in self.data:
            for j, k in key.items():
                if j not in key1:
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

    # def getSingleData(self):
    #     if i['name'] == 'sea' and i['action'] != '':
    #         continue
    #     elif i['name'] == 'road' and i['action'] != 'across':
    #         continue
    #     elif i['name'] == 'river' and i['action'] != 'across':
    #         continue
    #     elif i['action'] not in ['left', 'across', '', 'center']:
    #         continue
    #     elif i['usage'] == 'dw2':
    #         continue

    def findByHafuman(self, hafuman):
        for i in self.data:
            if i['base64'] == hafuman:
                return i
        else:
            return None
        # tem = self.findHafuman(hafuman, False)
        # if tem == None:
        #     # print(tem)
        #     return None
        # # print('rere')
        # for i in self.data:
        #     if i['base64'] == tem:
        #         return i.copy()
        # else:
        #     return None

    '''操作地图'''
    # ### 没有->一并改掉
    # def saveMap(self, map=None, priName=None):
    #     if map:
    #         if priName:
    #             for i in range(len(self.maps)):
    #                 if self.maps[i]['name'] == priName:
    #                     self.maps[i] = map
    #                     break
    #         else:
    #             for i in range(len(self.maps)):
    #                 if self.maps[i]['name'] == map['name']:
    #                     self.maps[i] = map
    #                     break
    #             else:
    #                 self.maps.append(map)
    #     with open(self.mapPath, 'w') as f:
    #         json.dump(self.maps, f)
    def saveMap(self, priName, newName=None, map=None, rule=None, imagePath=None, soundPath=None, basicInfo=None, lines=None):
        if not os.path.exists('maps/'+priName+'/map.json'):
            # print('map not exit')
            os.mkdir('maps/'+priName)
            # return
        if map:
            with open('maps/'+priName+'/map.json', 'w') as f:
                json.dump(map, f)
        if newName != None and priName != 'default':
            with open('maps/'+priName+'/map.json', 'r') as f:
                map_data = json.load(f)
            map_data['name'] = newName
            with open('maps/'+priName+'/map.json', 'w') as f:
                json.dump(map_data, f)
            os.rename('maps/'+priName, 'maps/'+newName)
            self.maps = os.listdir('maps')
        if rule != None:
            with open('maps/'+priName+'/rule.json', 'w') as f:
                json.dump(rule, f)
        if basicInfo:
            with open('maps/'+priName+'/basicInfo.json', 'w') as f:
                json.dump(basicInfo, f)
        if lines:
            with open('maps/'+priName+'/lines.json', 'w') as f:
                json.dump(lines, f)
        if imagePath:
            if os.path.exists(imagePath):
                shutil.copytree(imagePath, 'maps/'+priName+'/images')
        if imagePath:
            if os.path.exists(imagePath):
                if os.path.exists('maps/'+priName+'/images'):
                    shutil.rmtree('maps/'+priName+'/images')
                shutil.copytree(imagePath, 'maps/'+priName+'/images')
        if soundPath:
            if os.path.exists(soundPath):
                if os.path.exists('maps/'+priName+'/sounds'):
                    shutil.rmtree('maps/'+priName+'/sounds')
                shutil.copytree(soundPath, 'maps/'+priName+'/sounds')

    def getAllMaps(self):
        end = []
        for i in self.maps:
            with open('maps/'+i+'/map.json', 'r') as f:
                tem_data = json.load(f)
            end.append(tem_data)
        return end

    ####只用于创建json文件
    def makeMap(self, name, dsc='', type='random', mapSize=(10, 10)):
        print(name, dsc, type, mapSize)
        hufumans = []
        if type == 'random':
            tem_data = self.findAll({'usage':'geo'})
            for i in tem_data:
                tem = self.findByHafuman(i['base64'])
                if not tem:
                    print('hafuman error')
                    sys.exit()
                hufumans.append(tem)
        else:
            tem_data = self.find({'usage':'geo', 'name':type})
            if not tem_data:
                print('hafuman error')
                sys.exit()
            tem = self.findByHafuman(tem_data['base64'])
            hufumans.append(tem)
        data = {}
        data['map'] = []
        for i in range(mapSize[1]):
            com = []
            for j in range(mapSize[0]):
                if type == 'random':
                    com.append(hufumans[random.randint(0, len(hufumans)-1)]['base64'])
                else:
                    com.append(hufumans[0]['base64'])
            data['map'].append(com)
        data['dsc'] = dsc
        data['dw'] = []
        data['name'] = name
        return data

    def deleteMap(self, mapName):
        if mapName == 'default':
            return
        if os.path.exists('maps/'+mapName):
            shutil.rmtree('maps/'+mapName)
        else:
            return
        if mapName == self.mapName:
            self.initMap('default')
        self.maps = os.listdir('maps')
        # if mapName in self.maps:
        #     for i1, i in enumerate(self.maps):
        #         if i == mapName:
        #             self.maps.pop(i1)
        #             break

    def findMap(self, mapName):
        if mapName not in self.maps:
            return None
        path = 'maps/'+mapName+'/map.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        else:
            return None

    def findLines(self, mapName):
        pass

    def mapCheck(self):
        keys = ['map', 'name', 'dsc', 'dw']
        for k in self.maps:
            for i in k['map']:
                for j in i:
                    print('%-3d' % j, end='')
                print()
            for i in range(1, len(keys)):
                print(k[keys[i]])

    def saveRecord(self, map):
        for j, i in enumerate(self.records):
            if i['recordName'] == map['recordName']:
                self.records[j] = map
        else:
            self.records.append(map)
        with open(self.recordsPath, 'w') as f:
            json.dump(self.records, f)

    def makeUser(self):
        user = {'username':'bear', 'userid':'123', 'signal':'i can eat the stone without my body injured'}
        with open(self.userPath, 'w') as f:
            json.dump(user, f)

resource = Resource()

if __name__ == "__main__":
    # print(resource.findAll({'usage':'dw', 'flag':'red', 'action':'left', 'name':'aagun'}))
    # print(resource.basicData)
    # resource.makeHafuman()
    # print(resource.findMap('default'))
    # print(resource.findByHafuman(resource.data[0]['base64']), resource.data[0]['base64'])
    # print(resource.findHafuman(resource.data[0]['base64']))
    # print(resource.hafuman)
    print(resource.findByHafuman(89))
    # print(resource.findMap('default'))
    # data = None
    # with open('../maps/default/map.json', 'r') as f:
    #     data = json.load(f)
    #
    # for i1, i in enumerate(data['map']):
    #     for j1, j in enumerate(i):
    #         data['map'][i1][j1] = int(data['map'][i1][j1])
    # with open('../maps/default/map.json', 'w') as f:
    #     json.dump(data, f)
    # shutil.copytree('./sounds', './123')
    # shutil.copytree('./sounds', './123')


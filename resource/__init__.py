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
from PyQt5.Qt import QApplication, QWidget, QLabel, QPixmap, QUrl, QPushButton, QImage
import sys
import os
import shutil
import json
import re
import base64
import hashlib
import numpy
from PIL import Image


# from game import EVN
Qapp = QApplication(sys.argv)

'''图片，哈夫曼，单位配置，用户，声音'''

class Resource():
    def __init__(self):
        with open('resource/ini.json', 'r') as f:
            initData = json.load(f)

        with open('resource/userInfo.json', 'r') as f:
            self.userInfo = json.load(f)

        self.maps = os.listdir('maps')

        self.mapScaleList = []  # {'body':(100, 100),'font':30, 'tag':(40, 40)},
        self.mapScaleDoublePoint = initData['mapScalePoint']
        for i in range(10, 201, 10):
            self.mapScaleList.append({'body': (i, i), 'font': 10 + i // 5, 'tag': (i * 2 // 5, i * 2 // 5)})

        self.initMap(initData['lastMap'])

    def initMap(self, mapName, isTmp=False):
        basic_path = ['stories', 'lines', 'basicInfo', 'backup', 'toggles', 'toggleEvents', 'rule']
        for i in basic_path:
            path = 'maps/'+mapName+'/'+i+'.json'
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump({}, f)

        self.mapName = mapName
        self.data = []
        self.initImageData(mapName)
        self.player = {}
        self.initPlayer(mapName)

        self.initBasicData(mapName)
        self.initLines(mapName)
        self.initRecords(mapName)
        self.initBackup(mapName)
        self.initStories(mapName)
        self.initHeroAtrs(mapName)

        if not isTmp:
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
                com_pm = QPixmap('maps/'+mapName+'/images/'+i)
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
        path = 'maps/'+mapName+'/basicInfo.json'
        if not os.path.exists(path):
            path = 'resource/basicInfo.json'
        with open(path, 'r') as f:
            self.basicData = json.load(f)

    def initLines(self, mapName):
        path = 'maps/'+mapName+'/lines.json'
        if not os.path.exists(path):
            path = 'resource/lines.json'
        with open(path, 'r') as f:
            self.storage_lines = json.load(f)
            try:
                self.lines = self.storage_lines[list(self.storage_lines.keys())[0]]
            except (KeyError, IndexError):
                self.lines = {}

    def initStories(self, mapName):
        path = 'maps/' + mapName + '/stories.json'
        if not os.path.exists(path):
            path = 'resource/stories.json'
        with open(path, 'r') as f:
            self.storage_stories = json.load(f)
            try:
                self.story = self.storage_stories[list(self.storage_stories.keys())[0]]
            except (KeyError, IndexError):
                self.story = {}

    def initBackup(self, mapName):
        path = 'maps/' + mapName + '/backup.json'
        if not os.path.exists(path):
            path = 'resource/backup.json'
        with open(path, 'r') as f:
            self.storage_backup = json.load(f)
            try:
                self.backup = self.storage_backup[list(self.storage_backup.keys())[0]]
            except (KeyError, IndexError):
                self.backup = {}

    def initHeroAtrs(self, mapName):
        path = 'maps/' + mapName + '/heroAtrs.json'
        if not os.path.exists(path):
            self.heroAtrs = {}
        else:
            with open(path, 'r') as f:
                self.heroAtrs = json.load(f)

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

    def swapLines(self, key):
        self.lines = self.storage_lines[key]

    def swapBasicData(self, key):
        self.basicData = self.storage_basicData[key]

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

    def findByHafuman(self, hafuman):
        for i in self.data:
            if i['base64'] == hafuman:
                return i
        else:
            return None

    '''操作地图'''
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
                if os.path.exists('maps/'+priName+'/images'):
                    shutil.rmtree('maps/'+priName+'/images')
                    os.mkdir('maps/'+priName+'/images')
                # shutil.copytree(imagePath, 'maps/'+priName+'/images')
                tem_mode1 = os.listdir('resource/images')
                tem_mode2 = []
                for i in tem_mode1:
                    tem_data = i.split('.')
                    tem_data = tem_data[0].split('_')
                    if tem_data[0] == 'hero':
                        continue
                    tem_mode2.append(i)
                end1 = os.listdir(imagePath)
                end2 = []
                end3 = []
                end4 = []
                for i in end1:
                    if i in tem_mode2:
                        end2.append(i)
                    else:
                        tem_data = i.split('.')
                        if len(tem_data) != 2:
                            continue
                        tem_data = tem_data[0].split('_')
                        if len(tem_data) != 4:
                            continue
                        if tem_data[0] != 'hero' or tem_data[2] != '' or tem_data[3] not in ['head', 'post']:
                            continue
                        end3.append(i)
                for i in end3:
                    tem_data = i.split('.')
                    tem_data_ = tem_data[0].split('_')
                    if tem_data_[3] == 'post':
                        tem_data_[3] = 'head'
                    else:
                        tem_data_[3] = 'post'
                    newPath = '-'.join(tem_data_)+tem_data[1]
                    if newPath not in end3:
                        continue
                    end4.append(newPath)
                end3 = []
                end2 += end4
                for i in tem_mode2:
                    if i not in end2:
                        end3.append(i)
                for i in end2:
                    shutil.copy(imagePath+'/'+i, 'maps/'+priName+'/images/'+i)
                # for i in end3:
                #     shutil.copy('resource/images/'+i, 'maps/'+priName+'/images/'+i)
        if soundPath:
            if os.path.exists(soundPath):
                if os.path.exists('maps/'+priName+'/sounds'):
                    shutil.rmtree('maps/'+priName+'/sounds')
                    os.mkdir('maps/'+priName+'/sounds')
                tem_mode1 = os.listdir('resource/images')
                end1 = os.listdir(soundPath)
                end = []
                for i in end1:
                    if i in tem_mode1:
                        end.append(i)
                end_ = []
                for i in tem_mode1:
                    if i not in end:
                        end_.append(i)
                for i in end:
                    shutil.copy(imagePath + '/' + i, 'maps/' + priName + '/sounds/' + i)
                # for i in end_:
                #     shutil.copy('resource/sounds/' + i, 'maps/' + priName + '/sounds/' + i)

    def getAllMaps(self):
        end = []
        for i in self.maps:
            with open('maps/'+i+'/map.json', 'r') as f:
                tem_data = json.load(f)
            end.append(tem_data)
        return end

    ##-------------只用于创建json文件------------------
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

    ###------------------------------------#
    def makeMapGeoImage(self):
        tem_map = self.findMap(self.mapName)
        for scale_n_, scale_n in enumerate([self.mapScaleList[0]['body'], self.mapScaleList[self.mapScaleDoublePoint]['body']]):
            image = None
            for i1, i in enumerate(tem_map['map']):
                tem_image = None
                for j1, j in enumerate(i):
                    tem_track = self.findByHafuman(j)
                    tem_path_ = tem_track['usage']+'_'+tem_track['name']+'_'+tem_track['flag']+'_'+tem_track['action']+'.gif'
                    tem_path = 'maps/'+self.mapName+'/images/'+tem_path_
                    if j1 == 0:
                        if os.path.exists(tem_path):
                            img = Image.open(tem_path)
                            img = img.resize(scale_n)
                            img = img.convert('RGBA')
                            tem_image = numpy.array(img)
                        else:
                            img = Image.open('resource/images/'+tem_path_)
                            img = img.resize(scale_n)
                            img = img.convert('RGBA')
                            tem_image = numpy.array(img)
                    else:
                        if os.path.exists(tem_path):
                            img = Image.open(tem_path)
                            img = img.resize(scale_n)
                            img = img.convert('RGBA')
                            tem_image = numpy.concatenate((tem_image, numpy.array(img)), axis=1)
                        else:
                            img = Image.open('resource/images/'+tem_path_)
                            img = img.resize(scale_n)
                            img = img.convert('RGBA')
                            tem_image = numpy.concatenate((tem_image, numpy.array(img)), axis=1)

                if i1 == 0:
                    image = tem_image
                else:
                    image = numpy.concatenate((image, tem_image), axis=0)

            img = Image.fromarray(image)
            if scale_n_ == 0:
                img.save('maps/'+self.mapName+'/min_bg.gif')
            else:
                img.save('maps/'+self.mapName+'/bg.gif')


resource = Resource()

if __name__ == "__main__":
    pass
    # resource.makeMapGeoImage((100, 100))
    # window = QWidget()
    # for i in range(100):
    #     for j in range(100):
    #         tem = QPushButton(window)
    #         tem.move(i*100, j*30)
    # window.show()
    # sys.exit(Qapp.exec_())


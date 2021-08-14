#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :basic_info_edit.py
# @Time      :2021/7/21 19:48
# @Author    :russionbear
import json

from PyQt5.Qt import *
from PyQt5 import QtCore
from resource_load import resource
import sys

'''
移动：步行， 轮胎，履带；螺旋桨；直升机，飞机
移动距离
视野：雷达， 步兵，机甲，飞机，  
攻防，枪，炮，重炮，远程炮，火箭炮， 高射炮， 导弹， 鱼雷，空弹，轰炸， 
攻击距离，  
金钱

指挥官加成：兵种范围，地形范围， 参数类型

镜头
选择单位
行动：
	移动->路线(不可坐标定位)->面向->动漫
	移动攻击->选择单位->选择路线->单位
	战斗->选择->动漫
	说话，防御反向，，分兵，高级补给，运兵，(不可对空补给，可对地补给)，修铁路， 小地图
	AI(巡逻, 阵地/防御，群体 追击，群体死追，，)
	移动或攻击->目标点->位置/面向->是否联合？->路线

	show: none, area, paths, direction, 
	          	   costMap, dw,
		             paths,
			        targets
none, areashowd, pathshowed, targetshowd, gtargetshowed, 

文字图标：占领，下潜，装载（1，2），补给（transport），隐身，

money模板需要格式化
关键字transport  带有即可隐身
可以布雷
高级运兵： 最短路线，有金钱上限， 所有节点没有运兵且没有移动过，补给范围为2，优先回复体力低的，优先回复其他单位再回复自己, 车只能补给补给陆地， 船陆海都可以,
运输：被运输的单位自动回复oil和bullect
'''

Qapp = QApplication(sys.argv)
class basicEditW(QMainWindow):
    def initUI(self):
        self.setWindowTitle('基础数据编辑')
        self.setFixedSize(1280, 800)
        self.path = 'configure/basic_info.json'
        geos = self.getInitData()
        dws = self.getInitData('dw')
        hero = ['warhton', 'google']
        attrs = ['move_distance', 'view_distance', 'gf_g', 'gf_f', 'gf_mindistance', 'gf_maxdistance', 'money', 'oil', 'bullect', 'skill_dsc']
        attrs_1 = ['money', 'chineseName', 'classify', 'canoccupy', 'candiving', 'canloading', 'cansupply', 'canstealth', 'canlaymine', 'daycost', 'dsc']

        self.data_move = QTableWidget(self)
        self.data_move.setColumnCount(len(geos)+1)
        self.data_move.setRowCount(len(dws))
        # self.data_move.setFixedSize(1200, 800)
        for i, j in enumerate(geos):
            tem = resource.find({'name':j})
            self.data_move.setHorizontalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        self.data_move.setHorizontalHeaderItem(i+1, QTableWidgetItem('move_distance'))
        for i, j in enumerate(dws):
            tem = resource.find({'name':j})
            self.data_move.setVerticalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i in range(len(dws)):
            for j in range(len(geos)+1):
                self.data_move.setItem(i, j, QTableWidgetItem('1'))
                
        self.data_view = QTableWidget(self)
        self.data_view.setColumnCount(len(geos)+1)
        self.data_view.setRowCount(len(dws))
        for i, j in enumerate(geos):
            tem = resource.find({'name':j})
            self.data_view.setHorizontalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        self.data_view.setHorizontalHeaderItem(i+1, QTableWidgetItem('view_distance'))
        for i, j in enumerate(dws):
            tem = resource.find({'name':j})
            self.data_view.setVerticalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i in range(len(dws)):
            for j in range(len(geos)+1):
                self.data_view.setItem(i, j, QTableWidgetItem('1'))
                
        self.data_gf = QTableWidget(self)
        # self.data_gf.setColumnCount((len(dws)+1)*2+3)
        self.data_gf.setColumnCount(len(dws)+5)
        self.data_gf.setRowCount(len(dws))
        for i, j in enumerate(dws):
            tem = resource.find({'name':j})
            self.data_gf.setHorizontalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        self.data_gf.setHorizontalHeaderItem(i+1, QTableWidgetItem('gf_mindistance'))
        self.data_gf.setHorizontalHeaderItem(i+2, QTableWidgetItem('gf_maxdistance'))
        self.data_gf.setHorizontalHeaderItem(i+3, QTableWidgetItem('oil'))
        self.data_gf.setHorizontalHeaderItem(i+4, QTableWidgetItem('bullect'))
        self.data_gf.setHorizontalHeaderItem(i+5, QTableWidgetItem('attackAftermove'))
        for i, j in enumerate(dws):
            tem = resource.find({'name':j})
            self.data_gf.setVerticalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i, i1 in enumerate(dws):
            for j in range(len(dws)+5):
                self.data_gf.setItem(i, j, QTableWidgetItem('1'))

        self.data_gfGeo_g = QTableWidget(self)
        self.data_gfGeo_g.setColumnCount(len(geos))
        self.data_gfGeo_g.setRowCount(len(dws))
        for i, j in enumerate(geos):
            tem = resource.find({'name':j})
            self.data_gfGeo_g.setHorizontalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i, j in enumerate(dws):
            tem = resource.find({'name':j})
            self.data_gfGeo_g.setVerticalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i in range(len(dws)):
            for j in range(len(geos)):
                self.data_gfGeo_g.setItem(i, j, QTableWidgetItem('1'))
                
        self.data_gfGeo_f = QTableWidget(self)
        self.data_gfGeo_f.setColumnCount(len(geos))
        self.data_gfGeo_f.setRowCount(len(dws))
        for i, j in enumerate(geos):
            tem = resource.find({'name':j})
            self.data_gfGeo_f.setHorizontalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i, j in enumerate(dws):
            tem = resource.find({'name':j})
            self.data_gfGeo_f.setVerticalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i in range(len(dws)):
            for j in range(len(geos)):
                self.data_gfGeo_f.setItem(i, j, QTableWidgetItem('1'))

        self.data_money = QTableWidget(self)
        self.data_money.setColumnCount(len(dws))
        self.data_money.setRowCount(len(attrs_1))
        for i, j in enumerate(dws):
            tem = resource.find({'name':j})
            self.data_money.setHorizontalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i, j in enumerate(attrs_1):
            self.data_money.setVerticalHeaderItem(i,QTableWidgetItem(j))
        for j, j1 in enumerate(dws):
            for i, i1 in enumerate(attrs_1):
                self.data_money.setItem(i, j, QTableWidgetItem('1'))

        self.data_geo = QTableWidget(self)
        self.data_geo.setColumnCount(len(geos))
        self.data_geo.setRowCount(2)
        for i, j in enumerate(geos):
            tem = resource.find({'name': j})
            self.data_geo.setHorizontalHeaderItem(i, QTableWidgetItem(QIcon(tem['pixmap']), j))
        self.data_geo.setVerticalHeaderItem(0, QTableWidgetItem('canbuild'))
        self.data_geo.setVerticalHeaderItem(1, QTableWidgetItem('cansupply'))
        for j, j1 in enumerate(geos):
            self.data_geo.setItem(0, j, QTableWidgetItem('1'))
            self.data_geo.setItem(1, j, QTableWidgetItem('1'))
            
        self.data_hero_f = QTableWidget(self)
        self.data_hero_f.setColumnCount(len(dws)+2)
        self.data_hero_f.setRowCount(len(hero))
        for i, j in enumerate(dws):
            tem = resource.find({'name':j})
            self.data_hero_f.setHorizontalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        self.data_hero_f.setHorizontalHeaderItem(i+1, QTableWidgetItem('energy'))
        self.data_hero_f.setHorizontalHeaderItem(i+2, QTableWidgetItem('max_energy'))
        for i, j in enumerate(hero):
            tem = resource.find({'usage':'hero', 'name':j})
            self.data_hero_f.setVerticalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i, i1 in enumerate(hero):
            for j in range(len(dws)+2):
                self.data_hero_f.setItem(i, j, QTableWidgetItem('1'))

        self.data_hero_1 = QTableWidget(self)
        self.data_hero_1.setColumnCount(len(attrs))
        self.data_hero_1.setRowCount(len(hero))
        for i, j in enumerate(attrs):
            self.data_hero_1.setHorizontalHeaderItem(i,QTableWidgetItem(j))
        for i, j in enumerate(hero):
            tem = resource.find({'usage':'hero', 'name':j})
            self.data_hero_1.setVerticalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i, i1 in enumerate(hero):
            for j in range(len(attrs)+2):
                self.data_hero_1.setItem(i, j, QTableWidgetItem('1'))
                
        self.data_hero_2 = QTableWidget(self)
        self.data_hero_2.setColumnCount(len(attrs))
        self.data_hero_2.setRowCount(len(hero))
        for i, j in enumerate(attrs):
            self.data_hero_2.setHorizontalHeaderItem(i,QTableWidgetItem(j))
        for i, j in enumerate(hero):
            tem = resource.find({'usage':'hero', 'name':j})
            self.data_hero_2.setVerticalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i, i1 in enumerate(hero):
            for j in range(len(attrs)+2):
                self.data_hero_2.setItem(i, j, QTableWidgetItem('1'))
                
        self.data_hero_3 = QTableWidget(self)
        self.data_hero_3.setColumnCount(len(attrs))
        self.data_hero_3.setRowCount(len(hero))
        for i, j in enumerate(attrs):
            self.data_hero_3.setHorizontalHeaderItem(i,QTableWidgetItem(j))
        for i, j in enumerate(hero):
            tem = resource.find({'usage':'hero', 'name':j})
            self.data_hero_3.setVerticalHeaderItem(i,QTableWidgetItem(QIcon(tem['pixmap']), j))
        for i, i1 in enumerate(hero):
            for j in range(len(attrs)+2):
                self.data_hero_3.setItem(i, j, QTableWidgetItem('1'))

        btn_confirm = QPushButton('保存')
        btn_confirm.clicked.connect(self.saveData)

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addWidget(QLabel('单位对地形的耗油量'))
        layout.addWidget(self.data_move)
        layout.addWidget(QLabel('地形对单位视野的阻碍值'))
        layout.addWidget(self.data_view)
        layout.addWidget(QLabel('单位对单位的攻(左)防(右)'))
        layout.addWidget(self.data_gf)
        layout.addWidget(QLabel('地形对单位的攻击力的影响(%)'))
        layout.addWidget(self.data_gfGeo_g)
        layout.addWidget(QLabel('地形对单位的防御力的影响(%)'))
        layout.addWidget(self.data_gfGeo_f)
        layout.addWidget(QLabel('单位价格(默认一座建筑提供每回合提供1000)'))
        layout.addWidget(self.data_money)
        layout.addWidget(QLabel('地形的属性'))
        layout.addWidget(self.data_geo)
        layout.addWidget(QLabel('指挥官能够影响的单位(填1/0)及最大能量值'))
        layout.addWidget(self.data_hero_f)
        layout.addWidget(QLabel('常规状态指挥官的影响(+-)'))
        layout.addWidget(self.data_hero_1)
        layout.addWidget(QLabel('普通技能状态指挥官的影响(+-)'))
        layout.addWidget(self.data_hero_2)
        layout.addWidget(QLabel('超级技能状态指挥官的影响(+-)'))
        layout.addWidget(self.data_hero_3)
        layout.addWidget(btn_confirm)
        self.center = QWidget()
        self.center.setMinimumSize(1240, 800)
        self.center.setLayout(layout)
        self.area = QScrollArea(self)
        self.area.setWidget(self.center)
        self.setCentralWidget(self.area)

        self.readData()

    def getInitData(self, type='geo'):
        end = []
        if type == 'geo':
            for i in resource.data:
                if i['usage'] in ['build', 'geo'] and i['name'] not in end:
                    end.append(i['name'])
        elif type == 'dw':
            for i in resource.data:
                if i['usage'] == type and i['name'] not in end and i['name'] != 'delete':
                    end.append(i['name'])
        return end

    def saveData(self):
        main_data = [self.data_move, self.data_view, \
                     self.data_gf, self.data_gfGeo_g, self.data_gfGeo_f, self.data_money, self.data_geo, \
                     self.data_hero_f, self.data_hero_1, self.data_hero_2, self.data_hero_3]
        main_data_key = ['move', 'view', 'gf', 'gfGeo_g', 'gfGeo_f', 'money', 'geo', 'hero_f', 'hero_1', 'hero_2', 'hero_3']
        end = {}
        for k1, k in enumerate(main_data):
            end[main_data_key[k1]] = {}
            for i in range(0, k.rowCount()):
                end[main_data_key[k1]][k.verticalHeaderItem(i).text()] = {}
                # print(main_data_key[k1])
                for j in range(0, k.columnCount()):
                    # print(k.verticalHeaderItem(i), k.horizontalHeaderItem(j))
                    end[main_data_key[k1]][k.verticalHeaderItem(i).text()][k.horizontalHeaderItem(j).text()] = k.item(i, j).text()
        # print(end)
        with open(self.path, 'w') as f:
            json.dump(end, f)

    def readData(self):
        main_data = [self.data_move, self.data_view, \
                     self.data_gf, self.data_gfGeo_g, self.data_gfGeo_f, self.data_money, self.data_geo, \
                     self.data_hero_f, self.data_hero_1, self.data_hero_2, self.data_hero_3]
        main_data_key = ['move', 'view', 'gf', 'gfGeo_g', 'gfGeo_f', 'money', 'geo', 'hero_f', 'hero_1', 'hero_2', 'hero_3']
        with open(self.path, 'r') as f:
            begin = json.load(f)
        for k1, k in enumerate(main_data):
            for i in range(0, k.rowCount()):
                for j in range(0, k.columnCount()):
                    try:
                        if begin[main_data_key[k1]][k.verticalHeaderItem(i).text()][k.horizontalHeaderItem(j).text()] == '':
                            k.item(i, j).setText('0')
                        else:
                            k.item(i, j).setText(begin[main_data_key[k1]][k.verticalHeaderItem(i).text()][k.horizontalHeaderItem(j).text()])
                    except KeyError:
                        k.item(i, j).setText('')


if __name__ == '__main__':
    window = basicEditW()
    window.initUI()
    window.show()
    sys.exit(Qapp.exec_())

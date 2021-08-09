#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :server.py
# @Time      :2021/8/2 19:10
# @Author    :russionbear

import sys
from PyQt5.Qt import *
Qapp = QApplication(sys.argv)
from mainWindow import TopDirector

user1 = TopDirector()

user1.show()
user2 = TopDirector()
user2.show()

sys.exit(Qapp.exec_())




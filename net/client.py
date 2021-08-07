#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :client.py
# @Time      :2021/8/2 19:10
# @Author    :russionbear

# import time
#
# from netTool import RoomFinder
#
# finder = RoomFinder()
# finder.start()
#
#
# time.sleep(4)
# print('there')
# finder.chooseRoom(finder.rooms[0][2], 'userdata')
#
import time

from netTool import RoomClient

client = RoomClient()
client.start()

time.sleep(3)
client.sendServer({'type':'command', 'command':'hulala'})

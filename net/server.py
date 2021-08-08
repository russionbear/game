#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :server.py
# @Time      :2021/8/2 19:10
# @Author    :russionbear
import socket
import time, zlib, json, asyncio
from netTool import LOCAL_IP, BROADCAST_PORT, myThread, LOCK, RoomServer



if __name__ == '__main__':
    server = RoomServer()
    server.start()
    time.sleep(4)
    server.beginGame()




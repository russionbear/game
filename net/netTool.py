#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :netTool.py
# @Time      :2021/8/2 17:32
# @Author    :russionbear

import time, socket, json, threading, re, ctypes, inspect, hashlib, asyncio

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

class myThread(threading.Thread):
    def stop(self):
        def _async_raise(tid, exctype):
            """raises the exception, performs cleanup if needed"""
            tid = ctypes.c_long(tid)
            if not inspect.isclass(exctype):
                exctype = type(exctype)
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
            if res == 0:
                raise ValueError("invalid thread id")
            elif res != 1:
                # """if it returns a number greater than one, you're in trouble,
                # and you should call it again with exc=NULL to revert the effect"""
                ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
                raise SystemError("PyThreadState_SetAsyncExc failed")
        if self.is_alive():
            _async_raise(self.ident, SystemExit)

BROADCAST_PORT = 22222
LOCAL_IP = get_host_ip()

class RoomBuilder(myThread):
    def __init__(self, data=None, bind=None):
        super(RoomBuilder, self).__init__()
        bind = LOCAL_IP, BROADCAST_PORT
        self.bind = bind
        data = {'author':'king', 'map':{'a':'aaa', 'b':'bbbb'}, 'contains':1}
        self.data = data
        self.md5 = '123'
        self.room_accepted = []
        self.canClose = False
        self.root_canModify = True

    def run(self):
        self.room_broadcast_process = myThread(target=self.broadcast)
        self.room_server_process = myThread(target=self.roomServer)
        self.room_server_process.setDaemon(True)
        self.room_broadcast_process.setDaemon(True)
        self.room_broadcast_process.start()
        self.room_server_process.start()
        # self.room_broadcast_process.join()
        # self.room_server_process.join()
        while True:
            if self.canClose:
                break

    def broadcast(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            context = 'find users'+json.dumps(self.data)
            while True:
                server_socket.sendto(context.encode('utf-8'), ("<broadcast>", int(self.bind[1])))
                print('broadcast', self.bind[1])
                time.sleep(2)

    def roomServer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            self.room_server_socket = server_socket
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(self.bind)
            server_socket.listen(9)
            while True:
                conn, address = server_socket.accept()
                print('one connected')
                process = threading.Thread(target=self.roomServerHandle, args=(conn, address))
                process.start()

    def roomServerHandle(self, conn, addr):
        # while True:
        try:
            data = conn.recv(1024).decode('utf-8')
        except ConnectionResetError:
            print('close it!')
            conn.close()
            return
            # break
        # print(data)
        if re.match('i am going.*', data.lower()) and self.data['contains'] - len(self.room_accepted) > 0:
            print('one accepted')
            while True:
                if self.root_canModify:
                    self.root_canModify = False
                    response = 'you were in'
                    conn.send(response.encode())
                    self.room_accepted.append((addr, data))
                    self.root_canModify = True
                    if self.data['contains'] == len(self.room_accepted):
                        # self.room_server_process.join()
                        # self.room_broadcast_process.join()
                        self.room_server_process.stop()
                        self.room_broadcast_process.stop()
                        self.canClose = True
                    break

        # break
        conn.close()


class RoomFinder(myThread):
    def __init__(self, bind=None):
        super(RoomFinder, self).__init__()
        bind = "0.0.0.0", BROADCAST_PORT
        self.bind = bind
        self.rooms = []
        self.canModify = True
        self.canClose = False
        self.updateTime = time.time()


    def run(self):
        self.getroom_process = myThread(target=self.getAllroom)
        self.updateroom_process = myThread(target=self.updateRoom)
        self.getroom_process.setDaemon(True)
        self.updateroom_process.setDaemon(True)
        self.getroom_process.start()
        self.updateroom_process.start()
        while True:
            if self.canClose:
                break

    def getAllroom(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            self.client_socket = client_socket
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            client_socket.bind(self.bind)
            while True:
                message, address = client_socket.recvfrom(1024)
                message = message.decode('utf-8')
                if re.match('find users.*', message):
                    hasOne = False
                    for i in self.rooms:
                        if i[1] == address:
                            hasOne = True
                            break
                    if hasOne:
                        continue
                    print('find one', message, address)
                    while True:
                        print('fsdf345')
                        if self.canModify:
                            self.canModify = False
                            self.rooms.append((message, address, time.time()))
                            self.canModify = True
                            print('渲染窗口')
                            break

    def updateRoom(self):
        while True:
            if time.time() - self.updateTime > 10 and self.canModify:
                print('clear', self.rooms)
                self.canModify = False
                self.rooms = []
                self.canModify = True
                self.updateTime = time.time()

    def chooseRoom(self, get_time, userData):
        while True:
            if self.canModify:
                self.canModify = False
                for i in self.rooms:
                    print(i[2], get_time, i)
                    if i[2] == get_time:
                        self.canModify = False
                        # self.getroom_process.join()
                        # self.updateroom_process.join()
                        self.getroom_process.stop()
                        self.updateroom_process.stop()
                        # for j in self.processes:
                        #     j.stop()
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            client_socket.connect((i[1][0], BROADCAST_PORT))
                            requestion = 'i am going'+json.dumps(userData)
                            client_socket.send(requestion.encode('utf-8'))
                            response = client_socket.recv(100).decode('utf-8')
                            if re.match('you were in.*', response):
                                print('choosed ok!!!!(渲染)')
                                client_socket.close()
                                self.canClose = True
                                return
                            break


'''begin_server, send, accept, end'''
                    
class RoomServer(myThread):
    def __init__(self, bind=(LOCAL_IP, BROADCAST_PORT), users=None, map=None):
        users = [{'address':('192.168.142.15', BROADCAST_PORT), 'userInfo':'none'}]
        self.serverSocket = None
        self.serverBind = bind
        self.users = users
        self.canModify = True
        self.md5 = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()[:8]
        self.map = map
        self.handleProcesses = []

        self.buildServer()

    def buildServer(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket = server_socket
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(self.serverBind)
        server_socket.listen(5)
        count = 0
        while True:
            print('waiting')
            conn, address = server_socket.accept()
            for i in range(len(self.users)):
                # print(self.users[i]['address'], address)
                if self.users[i]['address'][0] == address[0]:
                    tem_process = myThread(target=self.serverHandle, args=(conn, address))
                    tem_process.start()
                    self.users[i]['status'] = 0
                    self.users[i]['conn'] = conn
                    self.users[i]['address'] = address
                    count += 1
                    self.handleProcesses.append(tem_process)
                    break
            # print(count, len(self.users))
            if count == len(self.users):
                break

    def serverHandle(self, conn, address):
        def endConnect(addr43):
            for i in range(len(self.users)):
                if self.users[i]['address'] == addr43:
                    while True:
                        if self.canModify:
                            self.canModify = False
                            self.users[i]['status'] = 0
                            self.canModify = True
                            break
                    break
        try:
            data = conn.recv(100).decode('utf-8')
        except ConnectionResetError:
            endConnect(address)
            return
        if data != 'accepted':
            endConnect(address)
            return
        print('connected')
        for i in range(len(self.users)):
            if self.users[i]['address'] == address:
                self.users[i]['status'] = 1
                break
        else:
            print('no connection')
            return
        while True:
            try:
                # print(conn.recv(102))
                data = json.loads(conn.recv(1024).decode('utf-8'))
            except ConnectionResetError:
                print('hhhfsd')
                endConnect(address)
                return
            # print('recive', data)
            if data['type'] == 'map':
                # conn.send(self.map)
                print('send the map')
            elif data['type'] == 'command':
                tem_process = myThread(target=self.serverSend, args=(data, address))
                tem_process.start()


    def serverSend(self, command, address=None):
        ###{'type':'command','md5':self.md5, 'command':command}
        async def send(i):
            if self.users[i]['status'] == 0:
                return
            tem = self.users[i]['conn']
            tem.send(json.dumps(command).encode('utf-8'))

        tasks = []
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()

        for i1, i in enumerate(self.users):
            if i['address'] == address:
                continue
            tasks.append(asyncio.ensure_future(send(i1)))
        try:
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError:
            pass

    def endServer(self):
        if self.serverSocket:
            self.serverSocket.close()
        for i in self.handleProcesses:
            i.stop()
        
class RoomClient(myThread):
    def __init__(self, bind=(LOCAL_IP, BROADCAST_PORT), server=('192.168.142.15', BROADCAST_PORT)):
        super(RoomClient, self).__init__()
        self.clientSocket = None
        self.bind = bind
        self.serverBind = server
        self.canModify = True

    def run(self) -> None:
        self.recevieServer()

    def recevieServer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            self.clientSocket = client_socket
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                client_socket.connect(self.bind)
            except ConnectionRefusedError:
                print('房主跑了')
                return
            client_socket.send('accepted'.encode('utf-8'))
            print('ok,connected', self.bind)
            while client_socket:
                try:
                    ddfs = client_socket.recv(1024).decode('utf-8')
                    print(ddfs, 'ddfs')
                    response = json.loads(ddfs)
                except ConnectionResetError:
                    print('the game is over')
                    return
                print('recive', response)
                if response['type'] == 'command':
                    print('获得指令')
                    
    def sendServer(self, command):
        self.clientSocket.send(json.dumps(command).encode('utf-8'))

# if __name__ == '__main__':
#     print(get_host_ip())


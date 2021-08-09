#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :netTool.py
# @Time      :2021/8/2 17:32
# @Author    :russionbear

import time, socket, json, threading, re, ctypes, inspect, hashlib, asyncio
import zlib


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
LOCK = threading.RLock()


class RoomServer(myThread):
    def __init__(self, map={'type': 'map', 'author': 'hula', 'authorid':'123',
                            'map': {'name': 'netmap', 'map': [1, 1, 1, 1], 'dw': [], 'dsc': 'just for test', 'flags':['red', 'blue']}},
                 localUser=None):
        super(RoomServer, self).__init__()
        # self.localUser = {'addr': (LOCAL_IP, BROADCAST_PORT), 'flag': 'none', 'hero': 'google', 'username': 'aaaa',
        #                   'userid': '123', 'status': 1}
        # self.users = [self.localUser]
        self.localUser = localUser
        self.localUser['userid'] = '0000' ##%%%%%%%
        self.users = []
        self.contains = len(map['map']['flags'])
        self.canModify = True
        self.map = map

        self.serverSocket = None
        self.serverBind = (LOCAL_IP, BROADCAST_PORT)
        self.handleProcesses = []
        self.serverThread = None
        self.canEnd = False
        self.isInGame = False

    def run(self) -> None:
        self.serverThread = myThread(target=self.buildServer)
        self.serverThread.start()
        while 1:
            if self.canEnd:
                break

    def buildServer(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket = server_socket
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(self.serverBind)
        server_socket.listen(9)
        while True:
            conn, address = server_socket.accept()
            if self.contains <= len(self.users):
                conn.close()
            if self.isInGame:
                for i in self.users:
                    if i['addr'][0] == address[0]:
                        break
                else:
                    conn.close()
                    continue
            tem_process = myThread(target=self.serverHandle, kwargs={'conn': conn, 'address': address})
            self.handleProcesses.append((tem_process, conn))
            tem_process.start()

    def serverHandle(self, conn, address):
        try:
            def updateUsers(addr43, new=None):
                for i1, i in enumerate(self.users):
                    if i['addr'][0] == addr43:
                        while 1:
                            if self.canModify:
                                self.canModify = False
                                self.users.pop(i1)
                                if new != None:
                                    self.users.append(new)
                                self.canModify = True
                                break
                        break
                else:
                    self.users.append(new)
                info = {'type': 'userstatus', 'users': []}
                for i in self.users:
                    info['users'].append(i.copy())
                    del info['users'][-1]['conn']
                    # print(i['conn'])
                self.serverSend(info)
            print('netTool', address)
            while 1:
                try:
                    requstion = conn.recv(1024)
                    requstion = json.loads(zlib.decompress(requstion).decode('utf-8'))
                except (ConnectionResetError, zlib.error):
                    if not self.isInGame:
                        updateUsers(address[0])
                    else:
                        while 1:
                            if self.canModify:
                                for j1, j in enumerate(self.users):
                                    if j['addr'][0] == address[0]:
                                        self.users[j1]['status'] = 0
                                        break
                                print('更新按钮')
                                break
                    conn.close()
                    break
                else:
                    if self.isInGame:
                        while 1:
                            if self.canModify:
                                for j1, j in enumerate(self.users):
                                    if j['addr'][0] == address[0]:
                                        self.users[j1]['status'] = 1
                                        self.users[j1]['conn'] = conn
                                        break
                                break

                if self.isInGame:
                    pass
                else:
                    if requstion['type'] == 'findroom':
                        conn.send(zlib.compress(json.dumps(self.map).encode('utf-8')))
                    elif requstion['type'] == 'enterroom':
                        requstion['user']['conn'] = conn
                        requstion['user']['addr'] = address
                        requstion['user']['status'] = 1
                        updateUsers(address[0], requstion['user'])
                    elif requstion['type'] == 'userupdate':
                        requstion['user']['conn'] = conn
                        requstion['user']['addr'] = address
                        requstion['user']['status'] = 1
                        updateUsers(address[0], requstion['user'])
                    elif requstion['type'] == 'talk':
                        # self.serverSend(requstion, address[0])
                        self.serverSend(requstion, address[0])
        finally:
            conn.close()
            return

    def serverSend(self, command, addressIp=None):
        async def send(i):
            if self.users[i]['status'] == 0:
                return
            tem = self.users[i]['conn']
            tem.send(zlib.compress(json.dumps(command).encode('utf-8')))

        tasks = []
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()

        for i1, i in enumerate(self.users):
            if i['addr'][0] == addressIp:
                continue
            tasks.append(asyncio.ensure_future(send(i1)))
        try:
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError:
            pass

    def endServer(self):
        self.serverThread.stop()
        if self.serverSocket:
            self.serverSocket.close()
        for i in self.handleProcesses:
            i[0].stop()
            i[1].close()
        self.canEnd = True

    def beginGame(self):
        # if len(self.users) != self.contains:
        #     return
        print('抛出开始游戏事件 >> qt界面')
        command = {'type': 'gamebegin'}
        self.serverSend(command)
        self.isInGame = True

def findRooms():
    prefix = LOCAL_IP.split('.')
    prefix = prefix[0]+'.'+prefix[1]+'.'+prefix[2]+'.'
    ips = []
    def ping(ii):
        ip = prefix+str(ii)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.settimeout(3)
        try:
            client.connect((ip, BROADCAST_PORT))
        except socket.timeout:
            return
        except OSError:
            return
        requstion = {'type':'findroom'}
        client.send(zlib.compress(json.dumps(requstion).encode('utf-8')))
        try:
            response = client.recv(3072)
        except:
            client.close()
            return
        response = json.loads(zlib.decompress(response).decode('utf-8'))
        client.close()
        ips.append((ip, response))
    processes = []
    for i in range(1, 255):
        tt = myThread(target=ping, kwargs={'ii':i})
        processes.append(tt)
    for i in processes:
        i.start()
    for i in processes:
        i.join()
    return ips

# gameNet =

def enterRoom(addr):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(addr)
    except socket.timeout:
        print('room error')
        return
    except OSError:
        print('roos error')
        return
    print('enterRoom ok')
    def updateUsers():
        while 1:
            try:
                response = client.recv(3072)
                response = json.loads(zlib.decompress(response).decode('utf-8'))
            # except (ConnectionResetError, zlib.error):
            #     print('direct to find rooms')
            #     client.close()
            #     return
            except zlib.error:
                client.close()
                break
            if response['type'] == 'userstatus':
                print(response['users'])
            elif response['type'] == 'gamebegin':
                print('game begin')
                print('按钮点击失效，更新窗口')
            elif response['type'] == 'talk':
                print(response['context'])
            # print(response)
    tt = myThread(target=updateUsers)
    tt.start()
    requestion = {'type':'enterroom', 'user':{'flag': 'none', 'hero': 'google', 'username': 'bbb', 'userid': '222'}}
    client.send(zlib.compress(json.dumps(requestion).encode('utf-8')))
    time.sleep(1)
    requestion = {'type': 'userupdate', 'user': {'flag': 'red', 'hero': 'google', 'username': 'bbb', 'userid': '222'}}
    def chooseRol():
        client.send(zlib.compress(json.dumps(requestion).encode('utf-8')))
    chooseRol()

    time.sleep(1)
    requestion = {'type': 'talk', 'fromid':'222', 'context':'talk'}   ### fromid
    def sendMessage():
        client.send(zlib.compress(json.dumps(requestion).encode('utf-8')))
    sendMessage()

    tt.join()



if __name__ == '__main__':
    # print(get_host_ip())
    # print(findRooms())
    enterRoom((LOCAL_IP, BROADCAST_PORT))




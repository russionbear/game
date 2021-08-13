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
ROOMSERVER = None


class RoomServer(myThread):
    # def __init__(self, map={'type': 'map', 'author': 'hula', 'authorid':'123',
    #                         'map': {'name': 'netmap', 'map': [1, 1, 1, 1], 'dw': [], 'dsc': 'just for test', 'flags':['red', 'blue']}},
    #              localUser=None):
        # self.localUser = {'addr': (LOCAL_IP, BROADCAST_PORT), 'flag': 'none', 'hero': 'google', 'username': 'aaaa',
        #                   'userid': '123', 'status': 1}
        # self.users = [self.localUser]
    def __init__(self):
        super(RoomServer, self).__init__()
        self.ownerId = None
        # self.localUser['userid'] = '0000' ##%%%%%%%
        self.users = []
        # self.contains = len(map['map']['flags'])
        self.contains = 0
        self.canModify = True
        self.map = {}

        self.serverSocket = None
        self.serverBind = (LOCAL_IP, BROADCAST_PORT)
        self.handleProcesses = []
        self.serverThread = None
        self.canEnd = False
        self.isInGame = False


        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket = server_socket
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(self.serverBind)
        server_socket.listen(9)

    def run(self) -> None:
        while True:
            conn, address = self.serverSocket.accept()
            # if self.canEnd:
            #     break
            tem_process = myThread(target=self.serverHandle, kwargs={'conn': conn, 'address': address})
            self.handleProcesses.append((tem_process, conn))
            tem_process.start()

    def serverHandle(self, conn, address):
        try:
            def updateUsers(addr43, new=None):
                for i1, i in enumerate(self.users):
                    if i['addr'][0] == addr43[0] and i['addr'][1] == addr43[1]:
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
                    if new != None:
                        self.users.append(new)
                info = {'type': 'userstatus', 'users': []}
                for i in self.users:
                    info['users'].append(i.copy())
                    del info['users'][-1]['conn']
                self.serverSend(info)
            while 1:
                try:
                    requstion = conn.recv(3072)
                    requstion = json.loads(zlib.decompress(requstion).decode('utf-8'))
                except (ConnectionResetError, zlib.error):
                    if not self.isInGame:
                        updateUsers(address)
                    else:
                        while 1:
                            if self.canModify:
                                for j1, j in enumerate(self.users):
                                    if j['addr'][0] == address[0] and j['addr'][1] == address[1]:
                                        self.users[j1]['status'] = 0
                                        break
                                print('玩家断开连接')
                                break
                    print('这里')
                except OSError:
                    print('oserror')
                    break
                else:
                    if self.isInGame:
                        while 1:
                            if self.canModify:
                                for j1, j in enumerate(self.users):
                                    if j['addr'][0] == address[0] and j['addr'][1] == address[1]:
                                        self.users[j1]['status'] = 1
                                        print('玩家重新连接')
                                        break
                                else:
                                    print('游戏已开始，拒绝新玩家')
                                    conn.close()
                                break
                # print('her', requstion)
                if self.isInGame:
                    print('isInGame')
                    if requstion['type'] == 'command':
                        self.serverSend(requstion, address)
                        print('sended')
                    elif requstion['type'] == 'bout':
                        self.serverSend(requstion, address)
                        for i1, i in enumerate(self.users):
                            if i['userid'] != '-1':
                                if tuple(i['addr']) == tuple(address):
                                    if self.users[(i1+1)%len(self.users)]['userid'] == '-1':
                                        print('电脑AI运行中')
                                        time.sleep(2)
                                        self.serverSend(requstion)
                                        print('电脑谋划结束')
                                    break
                else:
                    if requstion['type'] == 'buildserver':
                        requstion['user']['addr'] = address
                        requstion['user']['conn'] = conn
                        requstion['user']['status'] = 1
                        self.users.append(requstion['user'])
                        self.contains = len(requstion['map']['flags'])
                        self.ownerId = requstion['user']['userid']
                        self.map['map'] = requstion['map']
                        self.map['author'] = requstion['user']['username']
                        self.map['authorid'] = requstion['user']['userid']
                        self.map['type'] = 'map'
                        updateUsers(address, requstion['user'])
                    elif requstion['type'] == 'findroom':
                        if self.contains > len(self.users):
                            conn.send(zlib.compress(json.dumps(self.map).encode('utf-8')))
                        conn.close()
                        return
                    elif requstion['type'] == 'enterroom':
                        requstion['user']['conn'] = conn
                        requstion['user']['addr'] = address
                        requstion['user']['status'] = 1
                        updateUsers(address, requstion['user'])
                    elif requstion['type'] == 'userupdate':
                        requstion['user']['conn'] = conn
                        requstion['user']['addr'] = address
                        requstion['user']['status'] = 1
                        updateUsers(address, requstion['user'])
                    elif requstion['type'] == 'talk':
                        self.serverSend(requstion)
                    elif requstion['type'] == 'gamebegin':
                        self.isInGame = True
                        newUsers = []
                        newUsers_ = []
                        for i in self.map['map']['flags']:
                            for j in self.users:
                                if j['flag'] == i:
                                    newUsers.append(j.copy())
                                    del newUsers[-1]['conn']
                                    newUsers_.append(j)
                                    break
                            else:
                                tem_user = {'flag': i, 'hero': 'google', 'username': 'computer', 'userid': '-1', 'status': 1}
                                newUsers.append(tem_user)
                                newUsers_.append(tem_user)
                        while True:
                            if self.canModify:
                                self.canModify = False
                                self.users = newUsers_
                                self.canModify = True
                                break
                        info = {'type': 'userstatus', 'users': newUsers}
                        self.serverSend(info)
                        requstion['users'] = newUsers
                        self.serverSend(requstion)
                        print('gamebegin')

            print('breakkkkkk')

        finally:
            # conn.close()
            # return
            pass

    def serverSend(self, command, addressIp=None):
        async def send(i):
            tem = self.users[i]['conn']
            tem.send(zlib.compress(json.dumps(command).encode('utf-8')))

        tasks = []
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()

        for i1, i in enumerate(self.users):
            if i['userid'] != '-1':
                if i['status'] == 0 and 'conn' not in i:
                    continue
                elif addressIp != None:
                    if tuple(i['addr']) == tuple(addressIp):
                        continue
            else:
                continue
            tasks.append(asyncio.ensure_future(send(i1)))
        try:
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError:
            pass

    def stop(self):
        print('s stop')
        self.canEnd = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((LOCAL_IP, BROADCAST_PORT))
        super(RoomServer, self).stop()
        for i in self.handleProcesses:
            i[0].stop()
            i[1].close()

    def beginGame(self):
        print('抛出开始游戏事件 >> qt界面')
        command = {'type': 'gamebegin'}
        self.isInGame = True
        self.serverSend(command)

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
            client.close()
        except:
            return
        response = json.loads(zlib.decompress(response).decode('utf-8'))
        ips.append(((ip, BROADCAST_PORT), response))
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




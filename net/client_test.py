#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :net_2.py
# @Time      :2021/8/1 16:16
# @Author    :russionbear
import time
import socket
import asyncio


def tcp():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('127.0.0.1', 80))
        while client_socket:
            client_socket.send(input('输入:').encode('utf-8'))
            # client_socket.send('hehehehehhehehe!!!!'.encode())
            time.sleep(1)
            response = client_socket.recv(100).decode('utf-8')
            if response.upper() == 'EXIT':
                client_socket.close()
                break
            else:
                print(response)


def udp():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.connect(('127.0.0.1', 80))
        while True:
            data = input('输入')
            # data = 'lallalalalllalla方法'
            client.send(data.encode('utf-8'))
            response = client.recv(100).decode('utf-8')
            if response.upper() == 'EXIT':
                client.close()
                break
            else:
                print(response)

def broadcast():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client_socket.bind(("0.0.0.0", 21576))
        while True:
            message, address = client_socket.recvfrom(100)
            print(message.decode('utf-8'), address)

if __name__ == '__main__':
    tcp()

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :net.py
# @Time      :2021/8/1 15:55
# @Author    :russionbear


import multiprocessing
import socket


def tcp():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', 80))
        server_socket.listen(5)
        while True:
            conn, address = server_socket.accept()
            while True:
                try:
                    data = conn.recv(100).decode('utf-8')
                except ConnectionResetError:
                    print('close it!')
                    break
                print(data)
                if data.upper() != 'BYE':
                    conn.send('hulahual'.encode())
                else:
                    conn.send('exit'.encode())
                    break
            conn.close()
            break

def udp():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 80))
        while True:
            data, addr = server.recvfrom(30)
            print(data, addr)
            if data.decode('utf-8') == 'BYE':
                server.sendto('exit'.encode('utf-8'), addr)
                server.close()
                break
            else:
                server.sendto('huhuhuhlalla'.encode('utf-8'), addr)
def broadcast():
    import time
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            server_socket.sendto('hi'.encode('utf-8'), ("<broadcast>", 21576))
            time.sleep(1)



if __name__ == '__main__':
    tcp()
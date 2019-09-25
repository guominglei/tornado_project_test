# -*- coding:utf-8 -*-

import socket
HOST = 'localhost'
PORT = 9000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 定义socket类型，网络通信，TCP
s.connect((HOST, PORT))  # 要连接的IP与端口
s.sendall("/websocke/test")  # 把命令发送给对端
print s.recv(1024)
s.close()  # 关闭连接

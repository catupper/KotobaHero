#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import Queue
import socket
from time import time as get_time
from random import randint as rr
host = 'localhost'
port = 11123

def getboard():
    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsock.connect((host,port))
    comand = 'getboard'
    clientsock.sendall(comand)
    rcvmsg = clientsock.recv(1<<17).strip()
    clientsock.close()
    board,wordlist = rcvmsg.split('|')
    return eval(board), eval(wordlist)






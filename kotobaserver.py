#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import Queue
from time import time as get_time
from time import sleep
from random import randint as rr
import socket

host = 'localhost'
port = 11123
LEAST_LEN = 3
LEAST_BONUS = 2
LONGEST_LEN = 6
PLAY_TIME = 100
SCORE_TIME = 20
RANK_TIME = 10
TOTAL_TIME = PLAY_TIME + SCORE_TIME+RANK_TIME
Dictfile = "dictionary/butadict"
characters = list( u"あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽやゆよわん" )
charo = [x + y  for x in "akstnhmgzdbp" for y in "aiueo"] + ["ya","yu","yo","wa","nn"]

point = [rr(1, 9) for x in characters]
BOARD_QUEUE = []
ranksorted = False
ranking = []


##文字列をスコアに変換
def wordpoint(word):
    return sum(point[characters.index(x)] for x in word) + (len(word)  ** 5) / 150


##辞書作成
def makedic(filename):
    global WORD__, WORDLIST
    f = open(filename, "r")
    res = set()
    for x in f:
        x = x.strip()
        if len(x.decode('utf-8').split(',')[0]) >= LEAST_LEN :
            res.add(x.decode('utf-8'))
    res = sorted(list(set(res)))
    WORD__ = res
    WORDLIST = map(lambda x:x.split(',')[0], WORD__)

##16マスの隣接リスト
def sixteenmap():
    res=[[] for x in xrange(16)]
    for x in xrange(4):
        for y in xrange(4):
            for i in xrange(-1, 2):
                for j in xrange(-1, 2):
                    if i == j == 0:continue
                    if 0 <= x+i < 4 and 0 <= y+j < 4:
                        res[x * 4 + y].append((x + i) * 4 + y + j)
    return res

### 探索　1:みつかった 2:まだまだあるよ 3:つかった 4:見当違い
def search(word, wordlist, used = None):
    lists = wordlist
    down = 0
    up = len(lists) - 1
    while up > down + 2:
        mid = (up + down) / 2
        if lists[mid] < word :
            down = mid
        else:
            up = mid
    res = down
    while res < len(lists)-1 and lists[res] < word:
        res += 1
    if word == lists[res]:
        if used == None: 
            return 1
        if not used[res]:
            used[res] = True
            return 1
        else:
            return 3
    if word in lists[res]:
        return 2
    return 0

##ランダムなひらがな
def randhi():
    return characters[rr(0, len(characters)-1)]

##ボードに含まれる単語全列挙 [単語,[マスにおける場所の配列]]
def mkwordlist(board):
    longest = 0
    two_used = [0] * 16
    used = [False] * 16
    res = []
    fm = sixteenmap()
    least = 18
    def dfs(x, word, index):
        p = search(word, WORDLIST)
        ok = 0
        if p == 0:return ok
        used[x] = True
        if p == 1:
            res.append([word, index])
            ok += 1
        for n in fm[x]:
            if used[n]:continue
            ok += dfs(n, word + board[n], index + [n])
        used[x] = False
        two_used[x] += ok
        return ok
    
    for x in xrange(16):dfs(x, board[x], [x])
    if len(res) == 0:return res,-1,-1
    ret = [[x for x in res if y in x[1]]for y in xrange(16)] + [res]
    for x in res:
        longest = max(longest, len(x[0]))
    for x in xrange(17):
        if(ret[x] == []):continue
        last = '111'
        p = 1
        tmp = []
        ret[x].sort()
        for p in range(len(ret[x])):
            if(ret[x][p][0] == last):continue
            tmp.append(ret[x][p])
            last = ret[x][p][0]
        ret[x] = tmp
        ret[x].sort(key = lambda n:wordpoint(n[0]),reverse = True)
    return ret, longest, least


##盤作成　条件付き q はスレッドのきゅー
def makeboard(q=None):
    while True:
        board=[randhi() for x in xrange(16)]
        wordlist, longest, least = mkwordlist(board)
        if any(len(x) < LEAST_BONUS for x in wordlist):continue
        if longest >= LONGEST_LEN:

            if q != None:
                q.put([board, wordlist])
                return
            else:
                return board, wordlist

def change_time():
    time = get_time() + RANK_TIME + SCORE_TIME + 5
    g = int(time / TOTAL_TIME)
    return (g + 1) * TOTAL_TIME - SCORE_TIME - RANK_TIME - 5

def recive(ct):
    global ranking ,ranksorted
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversock.bind((host,port))
    serversock.listen(5)
    clientsock, client_address = serversock.accept()    
    rcvmsg = clientsock.recv(4096)
    if get_time() > ct:
        BOARD_QUEUE.pop(0)
        ct = change_time()
        ranking = []
        ranksorted = False
    return_message=None
    if rcvmsg == 'getboard':
        return_message = BOARD_QUEUE[0]
    if rcvmsg.split('|')[0] == 'sendscore':
        ranking.append(eval(rcvmsg.split('|')[1]))
    if rcvmsg == 'getranking':
        if not ranksorted:
            ranking.sort(key = lambda x: x[1])
            ranksorted = True
        return_message = str(ranking)
    if return_message != None:
        clientsock.sendall(return_message)
    clientsock.close()
    return ct


ct = change_time()
calling = False
makedic(Dictfile)
q = Queue.Queue()
for _ in xrange(4):
    BOARD_QUEUE.append("|".join(map(str,makeboard())))
while True: 
    if not calling and len(BOARD_QUEUE) < 4:
        p = threading.Thread(target = makeboard, args=(q,))
        p.start()
        calling = True
    if calling and not p.isAlive():
        BOARD_QUEUE.append("|".join(map(str,q.get())))
        calling = False
    ct = recive(ct)

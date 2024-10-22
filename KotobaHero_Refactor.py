#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import socket
import pygame
import threading
import Queue
import simplejson

import time
from time import sleep
from pygame.locals import *
from random import randint as rr

WIDTH = 800
HEIGHT = 700
BOARD_SIZE = 550

LEAST_LEN = 3
LEAST_BONUS = 2
LONGEST_LEN = 6

COLOR = {
    'WHITE': (255, 255, 255),
    'RED': (200, 100, 10),
    'GREEN': (100, 200, 10),
    'YAMABUKI': (200, 200, 100),
    'DARK_BLUE': (200, 200, 255),
    'SKY_BLUE': (100, 100, 255),
    'BLUE': (0, 0, 255),
    'BLACK': (0, 0, 0),
    'VIOLET': (150, 100, 200),
    'LIGHT_BLUE': (150, 255, 255),
    'YELLOW': (255, 255, 100),
    'BACKGROUND': (130, 70, 30)
}

characters = list( u"あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもらりるれろがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽやゆよわん" )
charo = [x + y  for x in "akstnhmgzdbp" for y in "aiueo"] + ["ya","yu","yo","wa","nn"]
point = [3,1,1,5,3,2,2,1,5,2,4,1,4,4,8,3,4,2,6,3,6,8,12,10,6,7,8,7,12,9,5,6,9,7,8,11,6,14,10,9,5,9,10,9,9,11,3,11,12,12,7,13,13,10,6,8,10,7,11,10,11,13,11,13,12,5,4,2,8,1]
HINSICOLOR = {
    u'形容動詞語幹': 'YAMABUKI',
    u'接尾動詞': 'VIOLET',
    u'接続詞': 'LIGHT_BLUE',
    u'自立形容詞': 'YELLOW',
    u'一般名詞': 'GREEN',
    u'接尾名詞': 'LIGHT_BLUE',
    u'一般記号': 'YELLOW',
    u'非自立動詞': 'GREEN',
    u'副詞可能名詞': 'LIGHT_BLUE',
    u'アルファベット': 'YELLOW',
    u'非自立形容詞': 'YELLOW',
    u'接尾形容詞': 'YELLOW',
    u'ナイ形容詞語幹': 'RED',
    u'助詞類接続副詞': 'BLUE',
    u'一般副詞': 'BLUE',
    u'サ変接続名詞': 'RED',
    u'固有名詞': 'RED',
    u'自立動詞': 'GREEN',
    u'連体詞': 'RED'
}
host = '192.168.1.51'
port = 11123

##時間をゲット
def get_time():
    global TIME_GAP
    return time.time() + TIME_GAP

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


##文字列をスコアに変換
def wordpoint(word):
    if word == u'None':return 0
    return sum(point[characters.index(x)] for x in word) + (len(word)  ** 5) / 150



##なぞってる文字を出力
def putword(board, word):
    tmp = ind_word(board, word)
    size = 6
    while len(tmp) * (size + 1) * 10 > 480:size -= 1
    screen.blit(sysfont[6].render(ind_word(board, word), False, WHITE)
                                  ,(220, 580))




##正解した文字の表示と説明
def outputfoundword(lastword, pos):
    if(lastword == 'NIL'):return
    pos *= 90 / 0.1
    pos = 90 - pos
    pos = min(pos, 90)
    color = HINSICOLOR[WORDLIST_HINSI[lastword]]
    screen.blit(sysfont[2].render(u"読み:%s" % lastword, False, color)
                ,(110 - pos, 663))
    size = 4
    while (size + 1) * 10 * len(WORDLIST_ORIGIN[lastword]) > 110:size-=1
    screen.blit(sysfont[4].render(WORDLIST_ORIGIN[lastword], False, color)
                ,(110 - pos, 613))
    screen.blit(sysfont[2].render(WORDLIST_HINSI[lastword], False, color)
                ,(110 - pos, 583))
    




###盤面上のます目の場所の配列から文字列への変換
def ind_word(board,indexes):
    return "".join(board[x] for x in indexes)

###残り時間出力
def timer(time,pos = (650, 0)):
    time = int( time - get_time() )
    col = (100,100,255)
    if time < 10:
        col = (255,50,50)
    screen.blit(sysfont[2].render(u"残り%d秒"%time, False, col),
                pos)    

###現在のスコア出力
def pointer(points):
    screen.blit(sysfont[2].render(u"%04d点"%points, False, YAMABUKI),
                (150, 0))
    
    
###たてに文字を列挙　ポイントもしてくれる
def outputwords(words, pos, gap, size, color, limit= 500, used = None):
    height = 0
    k = 0
    while k < len(words) and pos[1] + height + (size + 1) * 10< limit:
        if words[k][0] == "Bonus":
            screen.blit(
                sysfont[size].render("%s %dpt" % (words[k][0],words[k][1]),
                                     False, (255, 100 + words[k][1], 100)),
            (pos[0], pos[1]+height))
        else:
            if(used != None and words[k][0] in used):
                colors = YAMABUKI
            elif(used != None):
                colors = color
            else:
                colors =  HINSICOLOR[WORDLIST_HINSI[words[k][0]]]
            ss = size
            while (1 + ss) * 10 * len("%s %dpt"%(words[k][0], wordpoint(words[k][0]))) > 110: ss -= 1
            screen.blit(
                sysfont[size].render(
                    "%s %dpt"%(words[k][0], wordpoint(words[k][0])),
                    False, colors)
                ,(pos[0],pos[1]+height))

                    
        height += size * 10 + gap
        k += 1

#たてに文字を列挙　スクロール可
def scrolloutput(words, pos, color, used, scroll, selectedword, keymove):
    selectedword = min(selectedword, len(words) - 1)
    selectedword = max(0, selectedword)
    if keymove:
        if 35 * selectedword - scroll < 250:
            scroll = (35 * selectedword -250 + scroll * 2 ) / 3 - 2
        elif 35 * selectedword - scroll > 253:
            scroll = (35 * selectedword + scroll * 2 - 253) / 3 + 2
    scroll = max(min(scroll,len(words) * 35 - 585), 0)
    tmp = pygame.Surface((350, 640), flags=0)
    tmp.set_colorkey((0,0,0))
    nums = 700 / 35
    height = -scroll
    k = 0
    while height <= 650 and k < len(words):
        size = 2
        nopoint = False
        if used != None and k == selectedword:
            size = 3
            nopoint = True
        if(used != None and words[k][0] in used):
            colors = YAMABUKI
        elif(used != None and k == selectedword):
            colors = GREEN
        elif(used != None):
            colors = color
        else:
            colors =  HINSICOLOR[WORDLIST_HINSI[words[k][0]]]
        while 10 * (size + 1) * len(words[k][0]) > 250:size -= 1
        if k == selectedword + 1:
            height += 10
        if not nopoint:
            while 10 * (size + 1) * len(words[k][0]) > 200:size -= 1
            tmp.blit(
                sysfont[size].render("%s %dpt" % (words[k][0], wordpoint(words[k][0])),
                                     False, colors),
                (pos[0] - 242, pos[1]+height))
        else:
            tmp.blit(
                sysfont[size].render("%s" % words[k][0],
                                     False, colors),
                (pos[0] - 242, pos[1]+height))
                
        height += 35
        k += 1   
    screen.blit(tmp, pos)
    return scroll, selectedword


#たてに文字を列挙　スクロール可 ランキング用
def scrolloutputrank(rank, pos, scroll):
    res = -1
    scroll = max(min(scroll,len(rank) * 35 - 585), 0)
    tmp = pygame.Surface((350, 640), flags=0)
    tmp.set_colorkey((0,0,0))
    nums = 700 / 35
    height = -scroll
    k = 0
    while height <= 650 and k < len(rank):
        size = 2
        color = SKY_BLUE
        if rank[k][0] == user_name:
            color = YAMABUKI
            res = rank[k]+[k]
        tmp.blit(
            sysfont[2].render(u"%d位" % (k + 1),
            False, color),
            (pos[0] - 242, pos[1]+height))                
        tmp.blit(
            sysfont[1].render(u"%4dpt" % (rank[k][1]),
            False, color),
            (pos[0] - 45, pos[1]+height+10))                
        while (size ) * 10 * len(rank[k][0]) > 214: size -= 1
        tmp.blit(
            sysfont[size].render(rank[k][0],
            False, color),
            (pos[0] - 192, pos[1]+height))                
        height += 35
        k += 1   

    screen.blit(tmp, pos)
    return scroll, res

#単語の説明
def outputdictionary(word):
    word = word[0]
    tmp = pygame.Surface((280, 300), flags=0)
    tmp.set_colorkey((0,0,0))
    color = HINSICOLOR[WORDLIST_HINSI[word]]
    tmp.blit(
        sysfont[2].render(WORDLIST_HINSI[word], False, color),
        (10, 20))
    tmp.blit(
        sysfont[3 if len(word) <= 6 else 2].render(word, False, color),
        (10, 65))
    size = 3
    while len(WORDLIST_ORIGIN[word]) * 10 * (size + 1) > 250: size -= 1
    tmp.blit(
        sysfont[size].render(WORDLIST_ORIGIN[word], False, color),
        (10, 130))
    tmp.blit(
        numfont[3].render(u"%dpt"%wordpoint(word), False, color),
        (10, 180))
    screen.blit(tmp, (525, 25))

#ゲームの情報出力
def outputgamestatus(word, total):
    highest = word[0][0]
    length = len(word)
    tmp = pygame.Surface((280, 340), flags=0)
    tmp.set_colorkey((0,0,0))
    color = HINSICOLOR[WORDLIST_HINSI[highest]]
    tmp.blit(
        sysfont[1].render(u"最高得点の単語", False, WHITE),
        (10, 25))
    tmp.blit(
        sysfont[3 if len(highest) <= 6 else 2].render(highest, False, color),
        (10, 55))
    tmp.blit(
        numfont[3].render(u"%dpt"%wordpoint(highest), False, color),
        (10, 100))
    tmp.blit(
        sysfont[1].render(u"単語数", False, WHITE),
        (10, 160))
    tmp.blit(
        numfont[3].render(u"%d個"% length, False, GREEN),
        (10, 185))
    tmp.blit(
        sysfont[1].render(u"合計点数", False, WHITE),
        (10, 240))
    tmp.blit(
        numfont[3].render(u"%dpt"%total, False, RED),
        (10, 260))
    
    
    screen.blit(tmp, (525, 330))


#自分の情報を出力
def outputmystatus(myrank, point, length):
    rank = myrank[3] + 1
    highest = myrank[2]    
    if highest == u'None':
        color = RED
    else:
        color = HINSICOLOR[WORDLIST_HINSI[highest]]
    tmp = pygame.Surface((280, 650), flags=0)
    tmp.set_colorkey((0,0,0))
    tmp.blit(
        sysfont[3].render(u"あなたの成績", False, WHITE),
        (10, 25))
    tmp.blit(
        sysfont[1].render(u"順位", False, WHITE),
        (10, 85))
    tmp.blit(
        sysfont[3].render(u"%d位"% rank, False, YAMABUKI),
        (10, 115))
    tmp.blit(
        numfont[1].render(u"見つけた中の最高得点", False, WHITE),
        (10, 190))
    tmp.blit(
        sysfont[3 if len(highest) <= 6 else 2].render(highest, False, color),
        (10, 220))
    tmp.blit(
        numfont[3].render(u"%dpt"% wordpoint(highest), False, color),
        (10, 265))
    tmp.blit(
        sysfont[1].render(u"見つけた単語数", False, WHITE),
        (10, 340))
    tmp.blit(
        numfont[3].render(u"%d個"% length, False, GREEN),
        (10, 370))
    tmp.blit(
        sysfont[1].render(u"合計得点", False, WHITE),
        (10, 445))
    tmp.blit(
        numfont[3].render(u"%dpt"% point, False, RED),
        (10, 475))
    screen.blit(tmp, (525, 25))

#開始待ち

#次のゲームの開始時間

###あそび
def play(board, countdown, wordlist):
    wordlists = sorted([x[0] for x in wordlist])
    nowword = []
    foundword = []
    mouse_pressed = False
    sx=sixteenmap()
    square = [swit(x / 4, x % 4, board[x], point[characters.index(board[x])], (220, 30)) for x in xrange(16)]
    used = [False] * len(wordlists)
    checking = False
    finish_time = next_time() - RANK_TIME - SCORE_TIME 
    nowpoint = 0
    bonus1 = False
    bonus2 = False
    lastword = 'NIL'
    lastlimit = 0
    while get_time() < finish_time:
        gt = get_time()
        screen.fill(BACK_GROUND)
        clock.tick(60)

        mouse_press = pygame.mouse.get_pressed()[0]
        if mouse_pressed == True and mouse_press == False or checking:
            p=search(ind_word(board, nowword), wordlists, used)
            if p == 1:
                foundword = [["".join(board[x] for x in  nowword)]] + foundword
                nowpoint += wordpoint("".join(board[x] for x in nowword))
                lastword = ind_word(board, nowword)

                lastlimit = gt + 0.1
            for x in xrange(16):
                if square[x].mode == 1:
                    if p == 1:
                        square[x].mode = 102
                        square[x].limit = gt + 0.4
                        square[x].used += 1
                    elif p == 3:
                        square[x].mode = 104
                        square[x].limit = gt + 0.4
                    else:
                        square[x].mode = 103
                        square[x].limit = gt + 0.4
            nowword = []
            checking = False
        
        else:
            mouse_pressed = mouse_press
            if mouse_pressed:
                x, y = pygame.mouse.get_pos()
                x = x * 800 / WIDTH
                y = y * 700 /HEIGHT
                x -= 220
                y -= 30
                xx, yy = x, y
                x /= Square_size
                y /= Square_size
                xx %= Square_size
                yy %= Square_size
                if 0 <= x < 4 and 0 <= y < 4:
                    if 25 < xx < 125 and 25 < yy < 125:
                        if square[x*4+y].mode == 0:
                            while len(nowword) > 0 and x * 4 + y not in sx[nowword[-1]]:
                                square[nowword[-1]].mode = 0
                                del nowword[-1]                
                            square[x * 4 + y].mode = 1
                            nowword.append(x * 4 + y)
                        elif square[x * 4 + y].mode == 1:
                            if len(nowword) > 1 and nowword[-2] == x * 4 + y:
                                square[nowword[-1]].mode = 0
                                del nowword[-1]
                else:
                    checking = True
        if not bonus1:
            for x in xrange(16):
                if square[x].used == 0:break
            else:
                bonus1 = True
                nowpoint += 25
                foundword = [["Bonus", 25]] + foundword
        if bonus1 and not bonus2:
            for x in xrange(16):
                if square[x].used == 1:break
            else:
                bonus2 = True
                nowpoint += 100
                foundword = [["Bonus", 100]] + foundword
        for x in xrange(16):
            square[x].update(gt)
            square[x].draw(screen)
        screen.blit(foundwordback, (0, 30))
        screen.blit(under_field, (0, 580))
        outputfoundword(lastword, lastlimit - gt)
        pointer(nowpoint)
        putword(board, nowword)
        outputwords(foundword, (10, 90), 10, 2, SKY_BLUE)
        real_screen.blit(pygame.transform.scale(screen, (WIDTH, HEIGHT)),(0,0))
        pygame.display.flip()
        quitcheck()
    return nowpoint, foundword


###スコア表示
def score(board, nowlist, points, foundword):
    square = [swit(x / 4, x % 4, board[x], point[characters.index(board[x])], (15, 0), 50) for x in xrange(16)]
    finish_time = next_time() - RANK_TIME
    selected = 16
    foundword = [x for x in foundword if x[0] != 'Bonus']
    foundword.sort(key = lambda x : wordpoint(x[0]),reverse = True)
    total = sum(wordpoint(x[0]) for x in nowlist[16])
    scroll = 0
    down_pressed = False
    up_pressed = False
    mouse_pressed = False
    mouse_pos = 'NIL'
    selectedword = 0
    keymove = 0
    dest = 0
    while get_time() < finish_time:
        gt = get_time()
        screen.fill(BACK_GROUND)
        timer(finish_time)
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        up_press = keys[K_UP]
        down_press = keys[K_DOWN]
        mouse_press = pygame.mouse.get_pressed()[0]
        dest = max(min(dest,len(nowlist[selected]) * 35 - 585), 0)
        if keymove:
            dest = scroll
        for event in events:
            if event.type == MOUSEMOTION:
                keymove = 0
            if event.type == MOUSEBUTTONDOWN and event.button == 4:
                dest -= 50
            if event.type == MOUSEBUTTONDOWN and event.button == 5:
                dest += 50
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN and event.key  == K_ESCAPE:
                exit()
        if up_press and up_pressed and gt - keymove > 0.5:
            keymove += 0.08
            selectedword -= 1
        if down_press and down_pressed and gt - keymove > 0.5:
            keymove += 0.08
            selectedword += 1
        if up_press and not up_pressed:
            selectedword -= 1
            keymove = gt
        if down_press and not down_pressed:
            selectedword += 1
            keymove = gt
        if mouse_press and not mouse_pressed:
            x,y = pygame.mouse.get_pos()       
            x *= 800 / WIDTH
            y *= 700 / HEIGHT
            if 220 < x < 530:
                selectedword = (scroll + y - 70) / 35
            x -= 15
            x /= 50
            y /= 50
            if 0 <= x < 4 and 0 <= y < 4:
                if square[x * 4 + y].mode == -3:
                    selected = 16
                    square[x * 4 + y].mode = 0
                    scroll = 0
                    dest = 0
                else:
                    selected = x * 4 + y
                    square[x * 4 + y].mode = -3
                    for j in xrange(16):
                        if j != x*4+y:
                            square[j].mode = 0
                    scroll = 0
                    dest = 0
        if mouse_press:
            x,y = pygame.mouse.get_pos()       
            x *= 800 / WIDTH
            y *= 700 / HEIGHT
            if 220 < x < 530:
                if mouse_pos == 'NIL':
                    mouse_pos = dest + y
                else:
                    dest = mouse_pos - y
            else:
                mouse_pos = 'NIL'
        else:
            mouse_pos = 'NIL'

                
        scroll = (dest  + scroll * 3 ) / 4
        mouse_pressed = mouse_press
        up_pressed = up_press
        down_pressed = down_press
        for x in xrange(16):
            square[x].update(gt)
            square[x].draw(screen)
        screen.blit(allwordsback, (230, 30))
        screen.blit(wordinfoback, (525, 30))
        screen.blit(gameinfoback, (525, 335))
        screen.blit(playinfoback, (5, 205))
        scroll, selectedword = scrolloutput(nowlist[selected], (250, 35), SKY_BLUE, used = map(lambda x:x[0], foundword), scroll = scroll, selectedword = selectedword, keymove = keymove)
        outputgamestatus(nowlist[16], total)
        outputdictionary(nowlist[selected][selectedword])
        outputwords(foundword, (20,280), 10, 1, YAMABUKI, limit = 700)
        screen.blit(numfont[3].render("%dpt"%points, False, DARK_BLUE),(20,220))
        real_screen.blit(pygame.transform.scale(screen, (WIDTH, HEIGHT)),(0,0))
        pygame.display.flip()

###ランキングにデータを投稿してランキングを返してもらう
def get_ranking(foundword,point,q):
    maxpoint = 0
    maxword = u'None'
    for x in foundword:
        if(x[0] == 'Bonus'):continue
        p = wordpoint(x[0])
        if(p > maxpoint):
            maxpoint = p
            maxword = x[0]

    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            clientsock.connect((host,port))
            break
        except:
            pass
    
    comand = u'sendscore|%s'%str([user_name,point,maxword])
    clientsock.sendall(comand)
    clientsock.close()
    sleep(5)
    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            clientsock.connect((host,port))
            break
        except:
            pass
    comand = 'getranking'
    clientsock.sendall(comand)
    recm = ''
    while True:
        s = clientsock.recv(1024)
        if not s:
            break
        recm += s
    clientsock.close()
    q.put(eval(recm))
    
##ランキングの表示
def ranking(board, nowlist, points, foundword, rank):
    length = len(foundword)
    square = [swit(x / 4, x % 4, board[x], point[characters.index(board[x])], (15, 0), 50) for x in xrange(16)]
    finish_time = next_time()
    selected = 16
    foundword = [x for x in foundword if x[0] != 'Bonus']
    foundword.sort(key = lambda x : wordpoint(x[0]),reverse = True)
    total = sum(wordpoint(x[0]) for x in nowlist[16])
    scroll = 0
    down_pressed = False
    up_pressed = False
    mouse_pressed = False
    mouse_pos = 'NIL'
    dest = 0
    while get_time() < finish_time:
        gt = get_time()
        screen.fill(BACK_GROUND)
        timer(finish_time)
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        up_press = keys[K_UP]
        down_press = keys[K_DOWN]
        mouse_press = pygame.mouse.get_pressed()[0]
        for event in events:
            if event.type == MOUSEMOTION:
                keymove = 0
            if event.type == MOUSEBUTTONDOWN and event.button == 4:
                dest -= 50
            if event.type == MOUSEBUTTONDOWN and event.button == 5:
                dest += 50
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN and event.key  == K_ESCAPE:
                exit()
        if up_press:
            scroll += 20
            dest = scroll
        if down_press:
            scroll -= 20
            dest = scroll
        if mouse_press:
            x,y = pygame.mouse.get_pos()       
            x *= 800 / WIDTH
            y *= 700 / HEIGHT
            if 220 < x < 530:
                if mouse_pos == 'NIL':
                    mouse_pos = dest + y
                else:
                    dest = mouse_pos - y
            else:
                mouse_pos = 'NIL'
        else:
            mouse_pos = 'NIL'

        scroll = (dest + scroll * 5 ) / 6
        mouse_pressed = mouse_press
        up_pressed = up_press
        down_pressed = down_press
        for x in xrange(16):
            square[x].update(gt)
            square[x].draw(screen)
        screen.blit(allwordsback, (230, 30))
        screen.blit(myinfoback, (525, 30))
        screen.blit(playinfoback, (5, 205))
        scroll, myrank = scrolloutputrank(rank, (245, 35), scroll = scroll)
        outputmystatus(myrank, points, length)
        outputwords(foundword, (20,280), 10, 1, YAMABUKI, limit = 700)
        screen.blit(numfont[3].render("%dpt"%points, False, DARK_BLUE),
                    (20,220))
        real_screen.blit(pygame.transform.scale(screen, (WIDTH, HEIGHT)),(0,0))
        pygame.display.flip()


    
        

###ボードの各盤のクラス
class swit(pygame.sprite.Sprite):
    def __init__ (self,x,y,char,point,(left,top),size = 550 / 4):
        pygame.sprite.Sprite.__init__(self)
        self.used = 0
	self.char = charo[characters.index(char)]
        self.color = (0, 0, 0)
        self.limit = 0
        self.norm = pygame.transform.scale(
                      pygame.image.load("images/%s.png"%self.char),
                      (size - 1,size - 1))
        self.blue = pygame.transform.scale(
                      pygame.image.load("images/%sBlue.png"%self.char),
                      (size - 1, size - 1))
        self.green = pygame.transform.scale(
                      pygame.image.load("images/%sGreen.png"%self.char),
                      (size - 1, size - 1))
        self.yellow = pygame.transform.scale(
                      pygame.image.load("images/%sYello.png"%self.char),
                      (size - 1, size - 1))
        self.red = pygame.transform.scale(
                      pygame.image.load("images/%sRed.png"%self.char),
                      (size - 1, size - 1))
        self.rect  = pygame.Rect(left + x * size + 2,top + y * size + 2, size, size)
        self.mode  = 0
        self.point = point
        self.size  = lambda x: x * size / 150
        self.image = self.norm
    
    def update(self, gtime):
        if(self.mode == 0): self.image = self.norm      #Nothing
        if(self.mode == 1): self.image = self.blue      #selected
        if(self.mode % 5 == 2): self.image = self.green     #correctword
        if(self.mode % 5 == 3): self.image = self.red       #wrong
        if(self.mode % 5 == 4): self.image = self.yellow    #wrong

        if(self.mode > 1 and self.limit < gtime):
                self.mode = 0

        self.image.blit(
            numfont[self.size(2)].render(str(self.point), False, WHITE),
            (self.size(10),self.size(120)))

        if(self.used > 0):
            pygame.draw.circle(self.image, GREEN,
                               (self.size(120), self.size(140)),
                               self.size(4))
        if(self.used > 1):
            pygame.draw.circle(self.image, RED,
                               (self.size(130), self.size(140)),
                               self.size(4))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def getboard(q=None):
    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    comand = 'getboard'
    while True:
        try:
            clientsock.connect((host,port))
            clientsock.sendall(comand)
            recm = ''
            while True:
                s = clientsock.recv(1<<17)
                print s
                if not s:
                    break
                recm += s
            print recm
            clientsock.close()
            rcvmsg = recm.strip()
            board, wordlist = map(eval, rcvmsg.split('|'))
            break
        except:
            pass

        
    if q == None:
        return board, wordlist
    else:
        q.puts([board, wordlist])

class ServerConnection():
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def sendCommand(self, command):
        self.socket.sendall(command)

        res = ''
        while True:
            s = self.socket.recv(1024)
            if not s:
                break
            res += s
        return simplejson.loads(res.strip())

class Game(threading.Thread):
    def __init__(self, basepath):
        self.socket = ServerConnection(host, port)
        self.setTime()
        self.loadDict(basepath + '/dictonary/newdict')

        self.board = None
        self.wordlist = None
        self.adjacent = makeAdjacent()

        self.UI = UI()

    def makeAdjacent():
        res = [[] for i in range(16)]
        for x in range(4):
            for y in range(4):
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i == j == 0:
                            continue
                        if -1 < x + i < 4 and -1 <  y + j < 4:
                            res[x * 4 + y].append((x + i) * 4 + (y + j))
        return res

    def setTime(self):
        response = self.socket.sendCommand('gettime')

        self.TIME_GAP = response['TIME'] - time.time()
        self.PLAY_TIME = response['PLAY_TIME']
        self.SCORE_TIME = response['SCORE_TIME']
        self.RANK_TIME = response['RANK_TIME']

    def getBoard(self):
        response = self.socket.sendCommand('getboard')

        self.board = response['BOARD']
        self.wordlist = response['WORDLIST']

    def getNextTurn(self):
        total = self.PLAY_TIME + self.SCORE_TIME + self.RANK_TIME
        turn = (time.time() + self.TIME_GAP) / total
        return (turn + 1) * total

    def loadDict(self, filename):
        f = open(filename, 'r')

        res = set()
        for i in f:
            line = i.strip().decode('UTF-8')
            if len(line.split(',')[0]) < LEAST_LEN :
                continue
            res.add(line)

        self.wordlist.hinsi = {}
        self.wordlist.origin = {}
        for line in sorted(list(set(res))):
            word = line.split(',')
            self.wordlist.hinsh[word[0]] = word[-1]
            self.wordlist.origin[word[0]] = word[1]

    def run(self):
        self.UI.start()

        user_name = self.UI.getName()
        self.nextTurn = self.getNextTurn()

        loading = self.UI.Loading()
        loading.start()
        while time.time() + self.TIME_GAP < self.nextTurn:
            if not self.board and not self.wordlist:
                self.getBoard()
        loading.terminate()

        while True:
            playGame()
            p = threading.Thread(target = get_ranking,args = (foundword,playpoint,q,))
            p.start()
            score(board, lists, playpoint, foundword)
            rank = q.get()
            print rank
            ranking(board, lists, playpoint, foundword, rank)
            board, lists = getboard()

    class UI(threading.Thread):    
        def __init__(self, basepath):    
            threading.Thread.__init__(self)    
        
            self.basePath = basepath    
            self.panelSize = BOARD_SIZE / 4
            self.clock = pygame.time.Clock()
        
            self.loadBackground()    
            self.loadFont()    
        
        def getPath(self, filename):    
            return self.basePath + '/' + filename    
        
        def loadBackground(self):    
            self.background.foundWord = pygame.image.load(self.getPath('images/foundwords.png'))    
            self.background.underFrame = pygame.image.load(self.getPath('images/under_field.png'))    
            self.background.allWords = pygame.image.load(self.getPath('images/foundwordback.png'))    
            self.background.wordInfo = pygame.image.load(self.getPath('images/wordinformation.png'))    
            self.background.gameInfo = pygame.image.load(self.getPath('images/gameinfo.png'))    
            self.background.playerInfo = pygame.image.load(self.getPath('images/playerinfo.png'))    
            self.background.playInfo = pygame.image.load(self.getPath('images/playwords.png'))    
        
        def loadFont(self):    
            self.sysfont = [pygame.font.Font(self.getPath('font/ume-tgc5.tff', 5))]    
            for i in range(10, 200, 10):    
                self.sysfont.append(pygame.font.Font(self.getPath('font/ume-tgc5.ttf'), i))    
        
            self.numfont = [pygame.font.Font(self.getPath('font/ipag.ttf', 5))]    
            for i in range(10, 200, 10):    
                self.numfont.append(pygame.font.Font(self.getPath('font/ipag.ttf'), i))    
        
        def getName(self):    
            inputs = ''    
            keys = [eval('pygame.locals.K_' + chr(i)) for i in range(ord('0'), ord('9') + 1) + range(ord('a'), ord('z') + 1)]    
            pressed = pygame.key.get_pressed()    
        
            while True:    
                now_pressed = pygame.key.get_pressed()    
                self.screen.fill(COLOR['BACKGROUND'])    
                self.screen.blit(self.sysfont[2].render(u"名前:%s" % inputs, False, COLOR['WHITE']), (100, 100))    
        
                for key in keys:    
                    if key == pygame.locals.K_BACKSPACE:    
                        continue    
                    if not pressed[key] and now_pressed[key]:    
                        char = key[-1]    
                        if now_pressed[pygame.locals.K_RSHIFT] or now_pressed[pygame.locals.K_LSHIFT]:    
                            char = char.upper()    
                        inputs += char    
        
                if not pressed[pygame.locals.K_BACKSPACE] and now_pressed[pygame.locals.K_BACKSPACE]:    
                    inputs = inputs[:-1]    
                if now_pressed[pygame.locals.K_RETURN] and inputs != "":    
                    break    
        
                inputs = inputs[:15]    
                self.window.blit(pygame.transform.scale(screen, (WIDTH, HEIGHT)), (0, 0))          
                pygame.display.flip()    
        
                quitcheck()    
                pressed = now_pressed[:]    
        
            return inputs    

        def playGame(self):
            wordlists = sorted([word[0] for word in UI.wordlist])
    
            square = [Panel(self.board[i], (x / 4, x % 4), (220, 30)) for i in range(16)]
            finishTime = Game.nextTurn - Game.RANK_TIME - Game.SCORE_TIME

            nowword = []
            foundword = []
            mouse_pressed = False
            used = [False] * len(wordlists)
            checking = False
            nowpoint = 0
            bonus1 = False
            bonus2 = False
            lastword = 'NIL'
            lastlimit = 0
    
            while time.time() + Game.TIME_GAP < finishTime:
                UI.screen.fill(BACK_GROUND)
                UI.clock.tick(60)

                mouse_press = pygame.mouse.get_pressed()[0]
                if mouse_pressed == True and mouse_press == False or checking:
                    p = search(ind_word(board, nowword), wordlists, used)
                    if p == 1:
                        foundword = [["".join(board[x] for x in  nowword)]] + foundword
                        nowpoint += wordpoint("".join(board[x] for x in nowword))
                        lastword = ind_word(board, nowword)
    
                        lastlimit = gt + 0.1
                    for x in xrange(16):
                        if square[x].mode == 1:
                            if p == 1:
                                square[x].mode = 102
                                square[x].limit = gt + 0.4
                                square[x].used += 1
                            elif p == 3:
                                square[x].mode = 104
                                square[x].limit = gt + 0.4
                            else:
                                square[x].mode = 103
                                square[x].limit = gt + 0.4
                    nowword = []
                    checking = False
            
                else:
                    mouse_pressed = mouse_press
                    if mouse_pressed:
                        x, y = pygame.mouse.get_pos()
                        x = x * 800 / WIDTH
                        y = y * 700 /HEIGHT
                        x -= 220
                        y -= 30
                        xx, yy = x, y
                        x /= Square_size
                        y /= Square_size
                        xx %= Square_size
                        yy %= Square_size
                        if 0 <= x < 4 and 0 <= y < 4:
                            if 25 < xx < 125 and 25 < yy < 125:
                                if square[x*4+y].mode == 0:
                                    while len(nowword) > 0 and x * 4 + y not in UI.adjacent[nowword[-1]]:
                                        square[nowword[-1]].mode = 0
                                        del nowword[-1]                
                                    square[x * 4 + y].mode = 1
                                nowword.append(x * 4 + y)
                                elif square[x * 4 + y].mode == 1:
                                    if len(nowword) > 1 and nowword[-2] == x * 4 + y:
                                        square[nowword[-1]].mode = 0
                                        del nowword[-1]
                        else:
                            checking = True
                if not bonus1:
                    for x in xrange(16):
                        if square[x].used == 0:break
                    else:
                        bonus1 = True
                        nowpoint += 25
                        foundword = [["Bonus", 25]] + foundword
                if bonus1 and not bonus2:
                    for x in xrange(16):
                        if square[x].used == 1:break
                    else:
                        bonus2 = True
                        nowpoint += 100
                        foundword = [["Bonus", 100]] + foundword
                for x in xrange(16):
                    square[x].update(gt)
                    square[x].draw(screen)
                screen.blit(foundwordback, (0, 30))
                screen.blit(under_field, (0, 580))
                outputfoundword(lastword, lastlimit - gt)
                pointer(nowpoint)
                putword(board, nowword)
                outputwords(foundword, (10, 90), 10, 2, SKY_BLUE)
                real_screen.blit(pygame.transform.scale(screen, (WIDTH, HEIGHT)),(0,0))
                pygame.display.flip()
                quitcheck()
            return nowpoint, foundword
        
        def run(self):    
            pygame.init()    
            self.window = pygame.display.setmode((WIDTH, HEIGHT))    
            self.screen = pygame.Surface((800, 700))    
            pygame.display.set_caption("Kotoba Hero")    
        
            while True:    
                remainingTime = int(Game.nextTurn - time.time() - self.TIME_GAP)    
                color = COLOR['SKY_BLUE']    
                if time < 10:    
                    color = COLOR['RED']    
                self.screen.blit(self.sysfont[2].render(u"残り%d秒" % time, False, color), (650, 0))    
        
                events = pygame.event.get()    
                for event in events:    
                    if event.type == pygame.locals.QUIT:    
                        exit()    
                if event.type == pygame.locals.KEYDOWN and event.key == pygame.locals.K_ESCAPE:    
                    exit()    
        
        class Loading(threading.Thread):    
            def __init__(self):    
                threading.Thread.__init__(self)    
        
                self.panels = []    
                for i in list(u'ちよつとまつてね'):    
                    normal = pygame.image.load(UI.getPath('images/%s.png') % x)    
                    green = pygame.image.load(UI.getPath('images/%sGreen.png') % x)    
                    UI.panels.append([pygame.transform.scale(j, (100, 100)) for j in [normal, green]])    
        
                self.running = True    
        
            def terminate(self):    
                self.running = False    
        
            def run(self, time):    
                count = 0    
        
                while self.running:    
                    UI.screen.fill(COLOR['BACKGROUND'])    
                    UI.screen.blit(UI.sysfont[5].render('Please wait' + '.' * (count % 4), False, COLOR['DARK_BLUE']), (140, 500))    
        
                for i in range(8):    
                    if i == count:    
                        panel = self.panels[i][1]    
                    else:    
                        panel = self.panels[i][0]    
        
                    if i < 5:    
                        UI.screen.blit(panel, (100 + 110 * i, 100))    
                    else:    
                        UI.screen.blit(panel, (100 + 110 * (i - 5), 210))    
            
                UI.window.blit(pygame.transform.scale(UI.screen, (WIDTH, HEIGHT)), (0, 0))    

        class Panel(pygame.sprite.Sprite):
            def __init__ (self, char, (x, y), (left,top), size = UI.panelSize):
                pygame.sprite.Sprite.__init__(self)

                self.mode = 0
                self.used = 0
                self.limit = 0

                self.point = self.characters[char]
                self.panelSize = size

                self.panel = {}
                for color in ['Normal', 'Blue', 'Green', 'Yellow', 'Red']:
                    if color == 'Normal':
                        image = pygame.image.load(ui.getpath('images/%s.png' % (char))
                    else:
                        image = pygame.image.load(ui.getpath('images/%s%s.png' % (char, color))
                    self.panel[color] = pygame.transform.scale(image, (size - 1, size - 1))
                self.rect = pygame.Rect(left + x * size + 2, top + y * size + 2, size, size)
                self.image = self.panel['Normal']

            def getSize(self, percent):
                return size * percent / 100
            
            def update(self, gtime):
                if(self.mode == 0):
                    self.image = self.panel['Normal']    # Normal
                if(self.mode == 1):
                    self.image = self.panel['Blue']      # Selected
                if(self.mode % 5 == 2):
                    self.image = self.panel['Green']     # Correct
                if(self.mode % 5 == 3):
                    self.image = self.panel['Red']       # Wrong (japlj)
                if(self.mode % 5 == 4):
                    self.image = self.panel['Yellow']    # Already Used
        
                if(self.mode > 1 and self.limit < gtime):
                        self.mode = 0
        
                self.image.blit(UI.numfont[self.getSize(2)].render(str(self.point), False, COLOR['WHITE']), (self.getSize(7), self.getSize(80))
        
                if(self.used > 0):
                    pygame.draw.circle(self.image, GREEN, (self.getSize(80), self.getSize(93)), self.getSize(3))
                if(self.used > 1):
                    pygame.draw.circle(self.image, RED, (self.size(87), self.size(93)), self.size(3))
        
            def draw(self, screen):
                screen.blit(self.image, self.rect)

def main():
    game = Game(os.path.dirname(os.path.abspath(__file__)))
    game.start()

    pygame.init()
    real_screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
    screen = pygame.Surface((800, 700), flags=0)
    clock = pygame.time.Clock()
    user_name = get_name()
    board, lists = waitfor(next_time())
    q = Queue.Queue()
    while True:
        playpoint, foundword = play(board, PLAY_TIME, lists[16])
        p = threading.Thread(target = get_ranking,args = (foundword,playpoint,q,))
        p.start()
        score(board, lists, playpoint, foundword)
        rank = q.get()
        print rank
        ranking(board, lists, playpoint, foundword, rank)
        board, lists = getboard()



if __name__ == "__main__" :
    main()

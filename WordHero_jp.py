#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from random import randint as rr


Board_size = 550
PLAY_TIME  = 100
SCORE_TIME = 20
Dictfile   = "dictionary/mydicth"
romaji     = list( u"あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽやゆよわん" )
charo      = [x+y  for x in "akstnhmgzdbp" for y in "aiueo"] + ["ya","yu","yo","wa","nn"]
point      = [rr(1, 9) for x in romaji]


def quitcheck():
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == KEYDOWN and event.key  == K_ESCAPE:
            exit()


def makedic(filename):
    f = open(filename, "r")
    res = set()
    for x in f:
        x = x.strip()
        if len(x.decode('euc_jp')) > 1 :
            res.add(x.decode('euc_jp'))
    return list(res)

WORDLIST = sorted( makedic(Dictfile) )


def search(word, used = None):
    lists = WORDLIST
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


def sixteenmap():
    res=[[] for x in xrange(16)]
    for x in xrange(4):
        for y in xrange(4):
            for i in xrange(-1, 2):
                for j in xrange(-1, 2):
                    if i == j == 0:continue
                    if 0 <= x+i < 4 and 0 <= y+j < 4:
                        res[x*4+y].append((x+i)*4+y+j)
    return res

sx=sixteenmap()

def wordpoint(word):
    return sum(point[romaji.index(x)] for x in word)


def mkwordlist(board):
    longest = 0
    two_used = [0]*16
    used = [False]*16
    res = []
    fm = sixteenmap()
    def dfs(x,word,index):
        p = search(word)
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
    if len(res) == 0:return res,False
    ret = [[x for x in res if y in x[1]]for y in xrange(16)] + [res]
    for x in res:
        longest = max(longest,len(x[0]))
    for x in xrange(17):
        if(ret[x] == []):continue
        last = ret[x][0][0]
        p = 1
        ret[x].sort()
        while p < len(ret[x]):
            if ret[x][p][0] == last:
                del ret[x][p]
            else:
                last = ret[x][p][0]
                p += 1
        ret[x].sort(key = lambda n:wordpoint(n[0]),reverse = True)
    return ret, longest
    

def randhi():
    return romaji[rr(0, len(romaji)-1)]

def putword(board, word):
    screen.blit(sysfont[6].render(ind_word(board,word),False,(255,255,255)),(10,550))    
def makeboard():
    while True:
        board=[randhi() for x in xrange(16)]
        wordlist,longest=mkwordlist(board)
        if all(len(x) > 2 for x in wordlist) and longest>5:return board,wordlist

def ind_word(board,indexes):
    return "".join(board[x] for x in indexes)

def timer(time):
    col = (100,100,255)
    if time < 10:
        col = (255,50,50)
    screen.blit(sysfont[6].render(u"残り%d秒"%time,False,col),(300,610))    

def pointer(points):
    screen.blit(sysfont[2].render(u"%04d点"%points,False,(200,200,100)),(550,100))
    
    

def outputwords(words,pos,gap,size,color,limit=600):
    height=0
    k=0
    while k<len(words) and pos[1]+height<limit:
        if words[k][0] == "Bonus":
            screen.blit(sysfont[size].render(words[k][0]+" "+"%dpt"%words[k][1],False,(255,100+words[k][1],100)),(pos[0],pos[1]+height))
        else:
            screen.blit(sysfont[size].render(words[k][0]+" "+"%dpt"%wordpoint(words[k][0]),False,color),(pos[0],pos[1]+height))
        height += size*10+gap
        k += 1

def play(board, countdown):
    nowword = []
    foundword = []
    mouse_pressed = False
    square = [swit(x/4,x%4,board[x],point[romaji.index(board[x])]) for x in xrange(16)]
    used = [False]*len(WORDLIST)
    checking = False
    countdown *= 60
    nowpoint = 0
    bonus1 = False
    bonus2 = False
    while countdown:
        screen.fill((0,0,0))
        clock.tick(60)
        countdown -= 1
        timer(countdown/60)
        mouse_press=pygame.mouse.get_pressed()[0]
        if mouse_pressed == True and mouse_press == False or checking:
            p=search(ind_word(board,nowword),used)
            if p == 1:
                foundword = [["".join(board[x] for x in  nowword)]]+foundword
            for x in xrange(16):
                if square[x].mode == 1:
                    if p == 1:
                        square[x].mode = 102
                        square[x].used += 1
                        nowpoint += square[x].point
                    elif p == 3:
                        square[x].mode = 104
                    else:
                        square[x].mode = 103
            nowword = []
            checking = False
        
        else:
            mouse_pressed = mouse_press
            if mouse_pressed:
                xx,yy = x,y = pygame.mouse.get_pos()       
                x /= Square_size
                y /= Square_size
                xx %= Square_size
                yy %= Square_size
                if 0 <= x < 4 and 0 <= y < 4:
                    if 25 < xx < 125 and 25 < yy < 125:
                        if square[x*4+y].mode == 0:
                            while len(nowword)>0 and x*4+y not in sx[nowword[-1]]:
                                square[nowword[-1]].mode = 0
                                del nowword[-1]                
                            square[x*4+y].mode = 1
                            nowword.append(x*4+y)
                        elif square[x*4+y].mode == 1:
                            if len(nowword)>1 and nowword[-2] == x*4+y:
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
                foundword = [["Bonus",25]]+foundword
        if bonus1 and not bonus2:
            for x in xrange(16):
                if square[x].used == 1:break
            else:
                bonus2 = True
                nowpoint += 100
                foundword = [["Bonus",100]]+foundword
        for x in xrange(16):
            square[x].update()
            square[x].draw(screen)
        pointer(nowpoint)
        putword(board, nowword)
        outputwords(foundword, (550,150), 10, 2, (100,100,255))
        pygame.display.update()
        quitcheck()
    return nowpoint



def score(board, nowlist, points, countdown):
    square = [swit(x/4, x%4, board[x], point[romaji.index(board[x])], 50) for x in xrange(16)]
    countdown *= 60
    selected = 16
    mouse_pressed = False
    while countdown:
        screen.fill((0,0,0))
        clock.tick(60)
        countdown -= 1
        timer(countdown/60)
        mouse_press = pygame.mouse.get_pressed()[0]
        if mouse_pressed and not mouse_press:
            x,y = pygame.mouse.get_pos()       
            x /= 50
            y /= 50
            if 0 <= x < 4 and 0 <= y < 4:
                if square[x*4 + y].mode == -3:
                    selected = 16
                    square[x*4 + y].mode = 0
                else:
                    selected = x*4 + y
                    square[x*4+y].mode = -3
                    for j in xrange(16):
                        if j != x*4+y:
                            square[j].mode = 0
        mouse_pressed = mouse_press
        for x in xrange(16):
            square[x].update()
            square[x].draw(screen)
        outputwords(nowlist[selected], (240,100), 10, 2, (200,200,100))
        screen.blit(numfont[3].render("%dpt"%points, False, (200,200,255)), (20,220))
        quitcheck()
        pygame.display.flip()
        


class swit(pygame.sprite.Sprite):
    def __init__ (self,x,y,char,point,size = Board_size / 4):
        pygame.sprite.Sprite.__init__(self)
        self.used  = 0
	self.char  = charo[romaji.index(char)]
        self.color = (0, 0, 0)
        self.norm  = pygame.transform.scale(pygame.image.load("images/"+ self.char +".png") ,(size,size) )
        self.blue  = pygame.transform.scale(pygame.image.load("images/"+ self.char +"Blue.png") ,(size,size) )
        self.green = pygame.transform.scale(pygame.image.load("images/"+ self.char +"Green.png") ,(size,size) )
        self.yellow= pygame.transform.scale(pygame.image.load("images/"+ self.char +"Yello.png") ,(size,size) )
        self.red   = pygame.transform.scale(pygame.image.load("images/"+ self.char +"Red.png") ,(size,size) )
        self.rect  = pygame.Rect(x * size, y * size , size-20, size-20)
        self.mode  = 0
        self.point = point
        self.size  = lambda x: x * size / 150
        self.image = self.norm
    
    def update(self):
        if(self.mode   == 0): self.image = self.norm      #Nothing
        if(self.mode   == 1): self.image = self.blue      #selected
        if(self.mode%5 == 2): self.image = self.green     #correctword
        if(self.mode%5 == 3): self.image = self.red       #wrong
        if(self.mode%5 == 4): self.image = self.yellow    #wrong

        if(self.mode > 1): self.mode = max(self.mode-5, 0)
        self.image.blit(numfont[self.size(2)].render(str(self.point),False,(255,255,255)),(self.size(10),self.size(120)))
        if(self.used > 0):pygame.draw.circle(self.image,(200,100,9),(self.size(120),self.size(140)),self.size(4))
        if(self.used > 1):pygame.draw.circle(self.image,(100,200,9),(self.size(130),self.size(140)),self.size(4))



    def draw(self, screen):
        screen.blit(self.image, self.rect)
         




def main():
    global screen,sysfont,numfont,Square_size,clock
    pygame.init()
    screen = pygame.display.set_mode( (800,700) )
    pygame.display.set_caption("Kotoba Hero")
    sysfont =[ pygame.font.Font("font/ume-tgc5.ttf", x) for x in xrange(10, 200, 10)]
    numfont = [ pygame.font.Font("font/ipag.ttf", x ) for x in xrange(10, 200, 10)]
    clock = pygame.time.Clock()
    Square_size = Board_size / 4
    while True:
        board,lists = makeboard()
        playpoint   = play(board, countdown = PLAY_TIME)
        score(board, lists, playpoint, countdown = SCORE_TIME)



main()

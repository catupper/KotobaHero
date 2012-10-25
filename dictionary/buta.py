#!/usr/bin/env python
# coding: UTF-8
k = open('dict', 'r')
kk = open('butadicts', 'r')
kkk = open('newdict', 'w')
butadb = open('bbdicts','r')
butachange = {}
for x in butadb:
    l,r = x.decode('utf-8').strip().split(',')
    butachange[l] = r

wordlist = []
isther = []
for x in k:
    wordlist.append(x.strip())
    isther.append(x.split(',')[0])

isther = set(isther)

for x in kk:
    x = x.strip()
    if x in isther:continue
    try:
        wordlist.append(x+','+butachange[x.decode('utf-8')].encode('utf-8')+',名詞,一般')
    except:
        pass

wordlist=sorted(list(set(wordlist)))
last = 'aa'
for x in wordlist:
    if(x.split(',')[0] == last):continue
    last = x.split(',')[0]
    kkk.write(x +'\n')

k.close()
kk.close()
kkk.close()

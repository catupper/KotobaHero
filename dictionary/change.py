#!/usr/bin/env python
# coding: UTF-8
k = open('dict', 'r')
kk = open('butadicts', 'r')
kkk = open('butadict', 'w')
wordlist = []
for x in k:
    wordlist.append(x.strip())

for x in kk:
    x = x.strip()
    x += ',' + x + ',名詞,一般'
    wordlist.append(x)

wordlist.sort()


last = 'aaa'
for x in wordlist:
    if x.split(',')[0] == last:continue
    kkk.write(x + '\n')
    last = x.split(',')[0]



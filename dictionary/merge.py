#!/usr/bin/env python
# coding: UTF-8

k = open('dict', 'r')
kk = open('onlybuta','r')
z = []
for x in k:
    z.append(x)

for x in kk:
    z.append(x)
k.close()
kk.close()
z.sort()
k = open('dict', 'w')
for x in z:
    k.write(x)
    

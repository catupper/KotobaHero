k = open('dict', 'r')
kk = open('newdict', 'w')
for x in k:
    kk.write(x.split(',')[0] + '\n')

k.close()
kk.close()

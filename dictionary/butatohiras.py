# coding: utf-8
a = open('budb13av','r')
b = open('kotoba','w')
for x in a:
    try:
        k = x.decode('shift-jis').strip()
        r,l = k.split(u'　',1)
        l = l.split(u'}')[-1].strip()
        b.write((r+u','+l+u'名詞,一般\n').encode('utf-8'))
    except:
        pass
a.close()
b.close()

    
    

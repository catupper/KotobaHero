#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib

def getc(keyword):
    qouted_keyword = urllib.quote_plus(keyword)
    url = 'http://ajax.googleapis.com/ajax/services/search/web?q=' + qouted_keyword + '&v=1.0'
    search_result = urllib.urlopen(url).read()
    json_data = json.read(search_result)
    print json_data['responseData']['cursor']['estimatedResultCount']

getc('ああ')


characters = [3,1,1,5,3,2,2,1,5,2,4,1,4,4,8,3,4,2,6,3,6,8,12,10,6,7,8,7,12,9,5,6,9,7,8,5,9,10,9,9,11,3,11,12,12,7,13,13,10,6,8,10,7,11,10,11,13,11,13,12,5,4,2,8,1]

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

#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[export] Function for export, Email via restful api.
"""
"""
[input][ex]
njInfo = {
    'status':True,
    'errLog':'',
    'date':'20160324-102034',
    'inventory':['x.x.x.x','y.y.y.y',],
    'content':{
        <custom>
    }
}
"""
import urllib2,urllib,json
import os,sys

# Get the global config
sys.path.append(".")
from base.configParse import CONFIG

ident = 0
exportData = ''

def export(input):
    # init print format
    global exportData
    try:
        input = eval(input)
    except:
        pass
    dictPrintHtml('njInfo',input)

    # init email parameters
    configInstance = CONFIG()
    url = configInstance.getConfig('mail','restfulUrl')
    try:
        sendTo = input['content']['mail']['sendTo']
        title = input['content']['mail']['title']
    except:
        sendTo = '13802880354@139.com'
        title = 'Forward_' + input['date']
    values = {'data':exportData,'email':sendTo,'title':title}
    #data = json.dumps(values)
    data = urllib.urlencode(values)
    req = urllib2.Request(url,data)
    response = urllib2.urlopen(req)

def dictPrintHtml(key,value):
    global ident
    global exportData
    fmtText = '%-18s: %s'
    fmt = '<br />'+'&nbsp;'*2*ident+fmtText
    exportData += fmt % (key,'')
    ident+=1
    for i in value:
        fmt = '<br />'+'&nbsp;'*2*ident+fmtText
        if type(value[i])!=dict:
            exportData += fmt % (i,str(value[i]))
        else:
            dictPrintHtml(i,value[i])
    ident-=1

if __name__ == '__main__':
	# [CLI][rootPath]python exportMail.py "xxxx"
    export(sys.argv[1])

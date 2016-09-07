#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[export][forward] Function for export, Print.
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

import sys

def export(input):
    # tranform
    try:
      input = eval(input)
    except:
      pass

    # init print format
    fmtSubTitle = '\033[32m-> %s ......\033[0m'
    fmtText = '%-22s: \033[94m%s\033[0m'
    fmtError = '\033[91m%-22s: %s\033[0m'
    fmtComplete = '\033[32mComplete!\033[0m\r\n'

    if input['status']:
        print fmtText % ('Execution status',str(input['status']))
        print fmtText % ('Error log',input['errLog'])
    else:
        print fmtError % ('Execution status',str(input['status']))
        print fmtError % ('Error log',input['errLog'])
    print fmtText % ('Execution end date',input['date'])

    dictPrint('Content',input['content'])

ident = 0
def dictPrint(key,value):
    global ident
    fmtText = '%-18s: \033[94m%s\033[0m'
    fmt = '\t'*ident+fmtText
    print fmt % (key,'')
    ident+=1
    for i in value:
        fmt = '\t'*ident+fmtText
        if type(value[i])!=dict:
            print fmt % (i,str(value[i]))
        else:
            dictPrint(i,value[i])
    ident-=1

if __name__ == '__main__':
    # [CLI][rootPath]python exportPrint.py "xxxx"
    export(sys.argv[1])

#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Function for sshv2, by using paramiko module.
"""

import paramiko

def sshv2(ip='',username='',password='',timeout=30,port=22):
    njInfo = {
        'status':True,
        'errLog':'',
        'content':''
    }
    try:
        port = int(port)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,port,username,password,timeout=timeout)
        #return SSH channel, use ssh.invoke_shell() to active a shell
        njInfo['content'] = ssh
    except Exception,e:
        njInfo['status'] = False
        njInfo['errLog'] = str(e)
    return njInfo

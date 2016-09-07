#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for bclinux7.
"""

import re
# from base.sshv2 import sshv2
from forward.models.baseSSHV2 import BASESSHV2

class BCLINUX7(BASESSHV2):
    pass

# class BCLINUX7:
#     def __init__(self,ip,loginMethod,port):
#         self.ip = ip
#         self.loginMethod = loginMethod
#         self.port = port
#         self.channel = ''
#         self.shell = ''
#         # loginInfo use for save the device login info, [ex]Last login: Mon Mar 21 20:29:26 2016 from 10.0.1.213
#         self.loginInfo = ''
#         # command prompt means this device is ready to receive commands, also means the last command is executed.
#         # [ex][wangzhe@cloudlab ~]$
#         self.prompt = '\$'
#         self.njInfo = {
#             'status':False,
#             'errLog':'',
#         }
#     def login(self,username,password):
#         sshChannel = sshv2(self.ip,username,password,self.port)
#         if sshChannel['status']:
#             # Login succeed, init shell
#             self.njInfo['status'] = True
#             self.channel = sshChannel['content']
#             self.shell = self.channel.invoke_shell()
#             loginInfo = ''
#             while not re.search(self.prompt,loginInfo):
#                 loginInfo += self.shell.recv(1024)
#         else:
#             # Login failed
#             self.njInfo['errLog'] = sshChannel['errLog']
#         return self.njInfo
#     def enable(self,secondPassword):
#         pass
#     def logout(self):
#         try:
#             self.channel.close()
#         except Exception as e:
#             self.njInfo['status'] = False
#             self.njInfo['errLog'] = str(e)
#         return self.njInfo
#     def execute(self,cmd):
#         data = {
#             'status':True,
#             'content':'',
#             'errLog':''
#         }
#         if self.njInfo['status']:
#             # check login status
#             # [ex] when send('ls\r'),get 'ls\r\nroot base etc \r\n[wangzhe@cloudlab100 ~]$ '
#             # [ex] data should be 'root base etc '
#             self.shell.send(cmd+"\r")
#             dataPattern = re.escape(cmd+'\r\n([\s\S]*)\r\n.+'+self.prompt)
#             while not re.search(self.prompt,data['content']):
#                 data['content'] += self.shell.recv(1024)
#             try:
#                 # try to extract the return data
#                 tmp = re.search(dataPattern,data['content']).group(1)
#                 data['content'] = tmp
#             except Exception as e:
#                 # pattern not match
#                 data['status'] = False
#                 data['content'] = data['content']
#                 data['errLog'] = str(e)
#         else:
#             # not login
#             data['status'] = False
#             data['errLog'] = 'ERROR:device not login'
#         return data

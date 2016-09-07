#!/usr/bin/evn python
#coding:utf-8
"""     It applies only to models of network equipment  mx960
        See the detailed comments C6506.py
"""
import sys,re,os
from forward.models_utils.telnet import telnet
from forward.models_utils.forwardError import ForwardError
import forward.models_utils.ban as BAN

class BASETELNET(object):
        def  __init__(self,ip = '',port = 23,timeout = 30,datas = {}):
                self.ip = ip
                self.basePrompt = r"(>|#|\]|\$|\)) *$"
                self.timeout = timeout
                self.port = port
                self.moreFlag = '(\-)+( |\()?[Mm]ore.*(\)| )?(\-)+'
                self.njInfo = {
                        'status':False,
                        'errLog':"",
                        "content":""
                        }
                """
                - parameter ip: device's ip
                - parameter port : device's port
                - parameter timeout : device's timeout(Only for login,not for execute)
                - parameter channel: storage device connection channel session
                - parameter shell: paramiko shell, used to send(cmd) and recv(result)
                - parameter prompt: [ex][wangzhe@cloudlab100 ~]$
                - parameter njInfo : return interactive data's format
                """

        def login(self,username = '',password = ''):
                sshChannel = telnet(ip = self.ip,username = username,password = password,port = self.port,timeout = self.timeout)
                if sshChannel['status']:
                        self.njInfo['status'] = True
                        self.channel = sshChannel['content']
                        self.getPrompt()
                else:
                        self.njInfo['errLog'] = sshChannel['errLog']
                return self.njInfo

        def __del__(self):
                self.logout()

        def logout(self):
                try:
                        self.channel.close()
                        print '+logout'
                except Exception,e:
                        self.njInfo['status'] = False
                        self.njInfo['content'] = str(e)
                return self.njInfo

        def execute(self,cmd):
                self.cleanBuffer()
                dataPattern = '[\r\n]+([\s\S]*)[\r\n]+' + self.prompt #Spaces will produce special characters and re.escape('show ver') --> show \\ ver
                data = {
                        'status':False,
                 	'content':'',
                        'errLog':''
                }
                if self.njInfo['status']:
                        self.channel.write(cmd +   "\n")
                        i = self.channel.expect([r'%s' %self.moreFlag,r"%s"%self.prompt],timeout = self.timeout)
                        result = i[-1]
                        if i[0] == 0:
                                result += self.getMore()
                        elif i[0] == -1:
                                data['errLog'] = 'Error: receive timeout '
                        data['content'] += result
                        data['status'] = True
                        try:
                                tmp = re.search(dataPattern,data['content']).group(1)
                                data['content'] = tmp
                        except Exception,e:
                                data['status'] = False
                                data['errLog'] = data['errLog'] +'not found host prompt Errorr(%s)' %str(e)
                else:
                        data['status'] = False
                        data['content'] = 'ERROR:device not login'
                return data

        def getMore(self):
                result = ''
                while True:
                        self.channel.send(' ')
                        i = self.channel.expect([r'%s' %self.moreFlag,self.prompt],timeout=self.timeout)
                        result += i[-1]
                        if i[0] == 1:break
                return result

        def getPrompt(self):
                self.channel.send('\n')
                i = self.channel.expect([r"%s"%self.basePrompt],timeout = self.timeout)
                self.prompt = re.escape(i[-1].split('\n')[-1])
                return self.prompt

        def cleanBuffer(self):
                self.channel.send('\n')
                i = self.channel.expect([r"%s"%self.prompt],timeout = self.timeout)
                result = i[-1]
                return result

        def privilegeMode(self,secondPassword = '',deviceType = 'cisco'):
                if  len(secondPassword) == 0:
                        return self.njInfo
                self.njInfo['content'] = '' #Clear the previous content
                self.cleanBuffer()
                deviceType = deviceType.lower()
                if  deviceType == 'huawei':
                        self.privilegeModeCommand = 'super'
                else:
                        self.privilegeModeCommand = 'enable'
                self.channel.send('%s\n'%(self.privilegeModeCommand))
                i = self.channel.expect([r"assword",r"%s"%self.basePrompt],timeout = self.timeout)
                try:
                        if i[0] == 0:
                                self.channel.send('%s\n'%sencondPassword)
                                tmpI = self.channel.expect([r"assword",r"%s"%self.basePrompt],timeout = self.timeout)
                                if tmpI[0] == 0:
                                        raise ForwardError('secondPassword wrong.')
                                elif tmpI == 1:
                                        # Switch mode succeed
                                        pass
                                else:
                                        raise ForwardError("Switch mode failed, it was timed out.")
                        elif i[0] == 1:
                                # switch mode's command incorrect
                                result = i[-1]
                                if re.search('%|Invalid|\^',result):
                                        raise ForwardError('Privileged mode command incorrect')
			elif i[0] == -1:
                                raise ForwardError("Switch mode failed, received prompt it was timed out.")
                        self.getPrompt() #Again get host's prompt
                        self.njInfo['status'] = True
                except ForwardError,e:
                        self.logout()
                        self.njInfo['status'] = False
                        self.njInfo['errLog'] = str(e)
                return self.njInfo

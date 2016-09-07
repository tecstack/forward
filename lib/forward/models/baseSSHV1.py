#!/usr/bin/evn python
#coding:utf-8
"""     It applies only to models of network equipment  e1000e
        See the detailed comments C6506.py
"""
import sys,re,os,time
from forward.models_utils.sshv1 import sshv1
from forward.models_utils.forwardError import ForwardError
import forward.models_utils.ban as BAN
import pexpect

class BASESSHV1(object):
        def  __init__(self,ip = '',datas = {},port = 23,timeout = 30):
		self.njInfo={
                            "content":"",
                            "status":False,
                            "errLog":""
                }
		self.ip = ip
		self.timeout = timeout
		self.port = port
		self.channel = ""
		self.basePrompt = ">|#|\]|\$|\) *$"
		self.moreFlag = '(\-)+( |\()?[Mm]ore.*(\)| )?(\-)+'

        def login(self,username = '',password = ''):
                sshChannel = sshv1(ip = self.ip,username = username,password = password,port = self.port,timeout = self.timeout)
                if sshChannel['status']:
                        self.njInfo['status'] = True
                        self.channel = sshChannel['content']
                        self.getPrompt()
                        self.cleanBuffer()
                else:
                        self.njInfo['errLog'] = sshChannel['errLog']
                return self.njInfo

        def __del__(self):
                self.logout()

        def logout(self):
                try:
                        self.channel.close()
                        # print '+logout'
                except Exception,e:
                        self.njInfo['status'] = False
                        self.njInfo['errLog'] = str(e)
                return self.njInfo

        def enable(self,password):
		pass

        def execute(self,cmd):
                self.cleanBuffer()
                #dataPattern = re.escape(cmd)+'.*\r\n([\s\S]*)\r\n'+self.prompt
                dataPattern = '[\r\n]+([\s\S]*)[\r\n]+'	# SSHV1 pexpect not have self.prompt end
                data = {
                        'status':False,
                        'content':'',
                        'errLog':''
                }
                if self.njInfo['status']:
                        self.channel.send(cmd+'\n')
                        i = self.channel.expect([r'%s' %self.moreFlag,r"%s"%self.prompt,pexpect.TIMEOUT],timeout = self.timeout)
                        result = ''
                        if i == 0:
                                result = self.channel.before # get result
                                result += self.getMore() # get more result
                        elif i == 2:
                                data['errLog'] = 'Error: receive timeout '
                        else:
                                result = self.channel.before
                        data['content'] += result
                        data["status"] = True
                        self.njInfo = data
                        try:
                                tmp = re.search(dataPattern,data['content']).group(1)
                                self.njInfo['content'] = tmp
                        except Exception,e:
                                self.njInfo['status'] = False
                                self.njInfo['errLog'] = data['errLog'] + "not fond host prompt:Error(%s)" % str(e)
                else:
                        self.njInfo['status'] = False
                        self.njInfo['errLog'] = 'ERROR:device not login'
                return self.njInfo

        def getMore(self):
                result = ''
                while True:
                        self.channel.send(' ')
                        i = self.channel.expect([r'%s' %self.moreFlag,r"%s"%self.prompt,pexpect.TIMEOUT],timeout = self.timeout)
                        if i == 0:
                                result += self.channel.before # After the encounter `moreFlag`, need to get the message
                        elif i == 1:
                                result += self.channel.before #After the encounter prompt, need to get the result
                                break
                        else:
                                break
                return result

        def getPrompt(self):
                self.channel.send('\n')
                self.channel.expect([r"%s"%self.basePrompt,pexpect.TIMEOUT],timeout = self.timeout)
                self.prompt = self.channel.before.split('\n')[-1]+"(>|#|\$|\]|\)) *$" # expect  prompt
                return self.prompt

        def cleanBuffer(self):
                self.channel.send('\n')
                try:
                        return self.channel.expect(self.prompt,timeout = self.timeout)
                except pexpect.TIMEOUT:
                        return ''

        def privilegeMode(self,secondPassword = '',deviceType = 'cisco'):
                if len(secondPassword) == 0:
                        return self.njInfo
                self.njInfo['content'] = '' # Clear the previous content
                self.cleanBuffer()
                deviceType = deviceType.lower()
                if deviceType == 'huawei':
                        self.privilegeModeCommand = 'super'
                else:
                        self.privilegeModeCommand = 'enable'
                self.channel.send('%s\n'%(self.privilegeModeCommand))
                try:
                        i = self.channel.expect([r"assword",r"%s"%self.basePrompt,pexpect.TIMEOUT],timeout = self.timeout)
                        if i == 0:
                                # need secondPassword
                                self.channel.send('%s\n'%secondPassword)
                                tmpI = self.channel.expect([r"assword",r"%s"%self.basePrompt,pexpect.TIMEOUT],timeout = self.timeout)
                                if tmpI == 0:
                                        raise ForwardError('secondPassword wrong.')
				elif tmpI == 1:
                                        # Switch mode succeed
                                        pass
                                else:
                                        raise ForwardError("Switch mode failed, it was timed out.")
                        elif i == 1:
                                # switch mode's command incorrect
                                result = self.channel.before
                                if re.search('%|Invalid|\^',result):
                                        raise ForwardError('Privileged mode command incorrect')
                        else:
                                raise ForwardError("Switch mode failed, received prompt it was timed out.")
                        self.getPrompt()
                        self.njInfo['status'] = True
                except ForwardError,e:
                        self.logout() #Switch mode failed,then logout device
                        self.njInfo['status'] = False
                        self.njInfo['errLog'] = str(e)
                return self.njInfo

#!/usr/bin/evn python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Base device class for sshv2 method, by using paramiko module.
"""

import re,time,sys
from forward.models_utils.sshv2 import sshv2
from forward.models_utils.forwardError import ForwardError
import forward.models_utils.ban as BAN
from forward.models_utils.ban import adminPermissionCheck

class BASESSHV2(object):
    def __init__(self,ip,port,timeout,datas={}):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.channel = ''
        self.shell = ''
        self.basePrompt = r'(>|#|\]|\$|\)) *$'
        self.prompt = ''
        self.moreFlag = '(\-)+( |\()?[Mm]ore.*(\)| )?(\-)+'
        self.njInfo = {
            'status':False,
            'errLog':'',
            'content':{}
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

    def login(self,username,password):
        # sshv2(ip,username,password,timeout,port=22)
        sshChannel = sshv2(self.ip,username,password,self.timeout,self.port)
        if sshChannel['status']:
            # Login succeed, init shell
            try:
                self.njInfo['status'] = True
                self.channel = sshChannel['content']
                self.shell = self.channel.invoke_shell(width=1000,height=1000)
                tmpBuffer=''
                while not re.search(self.basePrompt,tmpBuffer.split('\n')[-1]):
                    tmpBuffer+=self.shell.recv(1024)
                self.shell.settimeout(self.timeout)
                self.getPrompt()
            except Exception as e:
                self.njInfo['status'] = False
                self.njInfo['errLog'] = str(e)
        else:
            # Login failed
            self.njInfo['errLog'] = sshChannel['errLog']
        return self.njInfo

    def logout(self):
        try:
            self.channel.close()
            # print '+logout'
        except Exception as e:
            self.njInfo['status'] = False
            self.njInfo['errLog'] = str(e)
        return self.njInfo

    def enable(self,enablePassWord):
        pass

    def execute(self,cmd):
        data = {
            'status':True,
            'content':'',
            'errLog':''
        }
        self.cleanBuffer()
        if self.njInfo['status']:
            # check login status
            # [ex] when send('ls\r'),get 'ls\r\nroot base etc \r\n[wangzhe@cloudlab100 ~]$ '
            # [ex] data should be 'root base etc '
            self.shell.send(cmd+"\r")
            #dataPattern = re.escape(cmd)+'.*\r\n([\s\S]*)\r\n'+self.prompt
            dataPattern = '[\r\n]+([\s\S]*)[\r\n]+'+self.prompt
            try:
                tmpData=''
                while not re.search(self.prompt,data['content'].split('\n')[-1]):
                    self.getMore(data['content'])
                    data['content'] += self.shell.recv(1024)
                # self.progress('done\n')
                # try to extract the return data
                tmp = re.search(dataPattern,data['content']).group(1)
                data['content'] = tmp
            except Exception as e:
                # pattern not match
                data['status'] = False
                data['content'] = data['content']
                data['errLog'] = str(e)
        else:
            # not login
            data['status'] = False
            data['errLog'] = 'ERROR:device not login'
        return data

    def getPrompt(self):
        if self.njInfo['status']:
            # login status True
            result = ''
            self.cleanBuffer()
            self.shell.send('\n')
            # set recv timeout to self.timeout/10 fot temporary
            while not re.search(self.basePrompt,result):
                result += self.shell.recv(1024)
            if result:
                # recv() get something
                self.prompt = result.split('\n')[-1]      # select last line character,[ex]' >[localhost@labstill019~]$ '
            	# self.prompt=self.prompt.split()[0]      # [ex]'>[localhost@labstill019~]$'
            	# self.prompt=self.prompt[1:-1]           # [ex]'[localhost@labstill019~]'
            	self.prompt = re.escape(self.prompt)  	 # [ex]'\\[localhost\\@labstill019\\~\\]$'
                return self.prompt
            else:
                # timeout,get nothing,raise error
                raise TypeError('Timeout,can not get prompt.')
        else:
            # login status failed
            raise TypeError('Not login yet.')

    def getMore(self,bufferData):
        if re.search(self.moreFlag,bufferData.split('\n')[-1]):	# if check buffer data has 'more' flag, at last line.
            self.shell.send(' ')                                # can't used to \n and not use ' \r' ,because product enter character

    def cleanBuffer(self):
            if self.shell.recv_ready():
                self.shell.recv(4096)
            #self.shell.send('\r\n')
            self.shell.send('\n')
            buff=''
            while not re.search(self.basePrompt,buff.split('\n')[-1]): # When after switching mode, the prompt will change, it should be based on basePrompt to check and at last line
                try:
                   buff+=self.shell.recv(1024)
                except:
                   raise ForwardError('Receive timeout [%s]' %(buff))

    def privilegeMode(self,secondPassword='',deviceType='cisco'):
        if self.njInfo['status'] and (len(secondPassword)>0):
            # (login succeed status) and (secondPassword exist)
            deviceType=deviceType.lower()
            if  deviceType=='huawei':
                self.privilegeModeCommand='super'
            else:
                self.privilegeModeCommand='enable'

            self.cleanBuffer()
            self.shell.send('%s\n'%(self.privilegeModeCommand))
            enableResult = ''
            while not re.search('assword',enableResult) and  not ( re.search(self.prompt,enableResult) and  re.search(self.privilegeModeCommand,enableResult) ) and not re.search('%|Invalid|\^',enableResult): #When appeared baseprompt, may have a password prompt hasn't been the case
                # recv not finished
                enableResult += self.shell.recv(1024)
            if re.search('assword',enableResult):
                # need password
                self.shell.send("%s\n"%secondPassword)
                result=''
                while not re.search(self.basePrompt,result) and (not re.search('assword|denied',result)):
                    result+=self.shell.recv(1024)
                if re.search('assword|denied',result):
                    # When send the secondPassword, once again encountered a password hint password wrong.
                    self.njInfo['status'] = False
                    self.njInfo['errLog'] = 'Switch mode failed: Password incorrect'
                elif re.search(self.basePrompt,result):
                    #Switch mode succeed
                    self.getPrompt()
                    self.njInfo['status'] = True
            elif re.search(self.basePrompt,enableResult):
                # Switch mode succeed, don't need password
                self.getPrompt()
                self.njInfo['status'] = True
            elif re.search('%|Invalid|\^',enableResult):
                # bad enable command
                self.njInfo['status'] = False
                self.njInfo['errLog'] = 'Switch mode failed: Privileged mode command incorrect'
            else:
                self.njInfo['stauts'] = False
                self.njInfo['errLog']='Unknown device status'

        elif not self.njInfo['status']:
            # login failed
            self.njInfo['status'] = False
            self.njInfo['errLog'] = 'Switch mode failed: not login'
        elif len(secondPassword)==0:
            # secondPassword dosen't exist, do nothing
            pass
        return self.njInfo

    def __del__(self):
        self.logout()

    def _configMode(self,cmd = 'conf term'):
        self.isConfigMode = False
        data={
            "status":False,
            "content":"",
            "errLog":""
        }
	self.cleanBuffer()
	self.shell.send("%s\n"%(cmd))
	while not re.search(self.basePrompt,data['content'].split('\n')[-1]):
		data['content'] += self.shell.recv(1024)
	self.getPrompt() # release host prompt
	
	self.isConfigMode = True
	data['status'] = True
	return data

    def _exitConfigMode(self,cmd = 'end'):
        data={
               "status":False,
               "content":"",
               "errLog":""
        }
        try:
                if self.isConfigMode:   # Check current status
                        self.shell.send("%s\n"%(cmd))
                        while not re.search(self.basePrompt,data['content'].split('\n')[-1]):
                                data['content'] += self.shell.recv(1024)
                        if data['status']:
                                self.isConfigMode = False
		else:
                        raise ForwardError('Error: The current state is not configuration mode')
        except ForwardError,e:
                data['errLog'] = str(e)
        self.getPrompt()        # release host prompt
        return data

    def _commit(self,saveCommand = 'write',exitCommand = 'end'):
        data={
               "status":False,
               "content":"",
               "errLog":""
        }
        try:
                if self.isConfigMode:
                        self._exitConfigMode(exitCommand)
                        self.shell.send('%s\n' % (saveCommand))	# save setup to system
                        while not re.search(self.prompt,data['content'].split('\n')[-1]):
                                data['content'] += self.shell.recv(1024)
                        if re.search('(\[OK\])|(Copy complete)|(successfully)',data['content'],flags = re.IGNORECASE):
                                data['status'] = True
                else:
                        raise ForwardError('Error: The current state is not configuration mode')
        except ForwardError,e:
                data['errLog'] = str(e)
                data['status'] = False
        return data

    def addUser(self,username = '',password = '',addCommand = '',admin=False):
        data={
               "status":False,
               "content":"",
               "errLog":""
        }
        try:
                if not addCommand:
                        raise ForwardError("Please specify the add user's command")
                if not username or not password:
                        raise ForwardError('Please specify the username = your-username and password = your-password')  # Specify a user name and password parameters here.
                checkPermission = self._configMode()    # swith to config terminal mode.
                if not checkPermission['status']:
                        raise ForwardError(checkPermission['errLog'])
                if self.isConfigMode:   # check terminal status
                        self.cleanBuffer()
                        self.shell.send(addCommand.format(username = username,password = password))     # adduser
                        while not re.search(self.prompt,data['content'].split('\n')[-1]):
                                data['content'] += self.shell.recv(1024)
                        if re.search('error|invalid',data['content'],flags = re.IGNORECASE):
                                data['content'] = ''
                                raise ForwardError(data['content'])
                        else:
                                # set password is successed.
                                data = self._commit()
                else:
                        raise ForwardError('Has yet to enter configuration mode')
        except ForwardError,e:
                data['status'] = False
                data['errLog'] = str(e)
        return data

    def deleteUser(self,username=''):
        data = {
               "status":False,
               "content":"",
               "errLog":""
        }
        try:
                if not username:
                        raise ForwardError("Please specify a username")
                checkPermission = self._configMode()
                if not checkPermission['status']:
                        raise ForwardError(checkPermission['errLog'])
                if self.isConfigMode:   # check terminal status
                        self.cleanBuffer()
                        self.shell.send("no username {username}\n".format(username = username))        #delete username
                        while not re.search(self.prompt,data['content'].split('\n')[-1]):
                                data['content'] += self.shell.recv(1024)
                        if re.search('error|invalid',data['content'],flags = re.IGNORECASE):
                                raise ForwardError(data['content'])
                        else:
                                # deleted username
                                data = self._commit()
                                data['status'] = True
                else:
                        raise ForwardError('Has yet to enter configuration mode')
        except ForwardError,e:
                data['status'] = False
                data['errLog'] = str(e)
        return data

    def progress(self,tag='.'):
        sys.stdout.write(tag)
        sys.stdout.flush()

    def getUser(self,command = "show running-config | in username"):
        data = {
               "status":False,
               "content":"",
               "errLog":""
        }
        try:
                userList=[] # [{"username":"zhang-qichuan","secret":5},{}....]
                # execute query command
                info = self.execute(command)
                if not info["status"]:
                    raise ForwardError("Error:get user list failed: %s" %info["errLog"])
                # process data
                result = info["content"]
                for line in result.split('\n'):
                    # Each line
                    index=0
                    segments=line.split() # ['username' , 'test-user' , 'secret', '5','$.........']
                    for segment in segments:
                        if index <= 1:
                            index += 1
                            # Check after second fields username my-username secret/password .....
                            continue
                        else:
                            if segment == "secret" or segment == "password":
                                userData = {"username":segments[1],"secret":segments[index+1]} # get secret level
                                userList.append(userData)
                                break
                        index += 1
                data["content"] = userList
                data["status"] = True
        except ForwardError,e:
                data['status'] = False
                data['errLog'] = str(e)
        return data

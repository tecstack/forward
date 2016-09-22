#!/usr/bin/evn python
#coding:utf-8
"""     It applies only to models of network equipment  mx960
        See the detailed comments C6506.py
"""
import sys,re,os
from forward.models.telnet.baseTELNET import BASETELNET
from forward.models_utils.forwardError import ForwardError
from forward.models_utils.ban import BAN,adminPermissionCheck
from forward.models.telnet.bandwidthConfig import Bandwidth
class MX960(BASETELNET):

        def _recv(self,_prompt):
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                i = self.channel.expect([r"%s"%_prompt],timeout = self.timeout)
                try:
                        if i[0] == -1:
                                raise ForwardError('Error: receive timeout')
                        data['status'] = True
                        data['content'] = i[-1]
                except ForwardError,e:
                        data['errLog'] = str(e)
                return data

        # @adminPermissionCheck
        def _configMode(self):							# private method
                self.isConfigMode = False
                data = {
                          "status":False,
                          "content":"",
                          "errLog":""
                }
                self.cleanBuffer()
                self.channel.write("configure\n")
                data = self._recv(self.basePrompt)
                if data['status']:
                        self.isConfigMode = True
                self.getPrompt()
                return data

        def _exitConfigMode(self):
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                try:
                        if self.isConfigMode: # Check current status
                                self.channel.write("exit\n")
                                data = self._recv(self.basePrompt)
                                if data['status']:
                                        self.isConfigMode = False
                        else:
                                raise ForwardError('Error: The current state is not configuration mode')
		except ForwardError,e:
                        data['errLog'] = str(e)
                self.getPrompt()
                return data

        def _commit(self):
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                try:
                        if self.isConfigMode:
                                self.channel.write('commit\n')
                                result = self._recv(self.prompt)
                                if re.search('succeeds',result['content'],flags = re.IGNORECASE):
                                        data['status'] = True
                                else:
                                        data['content'] = result['content']
                        else:
                                raise ForwardError('Error: The current state is not configuration mode')
                except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                return data
		
        def addUser(self,username = '',password = '',admin=False):
                if admin:
                        command="set system login user {username} class read-only\n".format(username=username)
                else:
                        command="set system login user {username} class  ABC\n".format(username=username)
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                try:
                        if not username or not password:
                                raise ForwardError('Please specify the username = your-username and password = your-password') # Specify a user name and password parameters here.
                        checkPermission = self._configMode()   # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode:   # check terminal status
                                self.channel.write(command)	# adduser
                                data = self._recv(self.prompt)	#recv result
                                if not  data['status']:
                                        raise ForwardError(data['errLog']) # break
                                self.channel.write('set system login user {username} authentication plain-text-password\n'.format(username = username))	# execute useradd command
	
                                i = self.channel.expect([r"New password:",r"%s"%self.prompt],timeout = self.timeout)
                                result = i[-1]
                                if re.search('error|invalid',result,flags = re.IGNORECASE):
                                        raise ForwardError(result) # command failure 
                                self.channel.write("{password}\n".format(password = password)) # Enter password
                                i = self.channel.expect([r"Retype new password:",r"%s"%self.prompt],timeout = self.timeout) # check password
                                if i[0] == 0: # repassword
                                        self.channel.write("{password}\n".format(password = password))
                                        i = self.channel.expect([r"%s"%self.prompt],timeout = self.timeout) # check password
                                        if i[0] == 0:
                                                result = i[-1]
                                                if re.search('error|invalid',result,flags = re.IGNORECASE):
                                                        raise ForwardError(result)
                                                else:
                                                        # set password is successed.
                                                        data = self._commit()
                                                        self._exitConfigMode() # exit config terminal mode.
                                        elif i[0] == -1:
                                                raise ForwardError('Error: receive timeout')
                                elif i[0] == 1: # password wrong
                                        raise ForwardError(i[-1])
                                elif i[0] == -1: # timeout
                                        raise ForwardError('Error: receive timeout')
                        else:
                                raise ForwardError('Has yet to enter configuration mode')
                except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                return data
        def deleteUser(self,username=''):
                   data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                   }
                   try:
                        if not username:
                                raise ForwardError('Please specify a username')
                        checkPermission = self._configMode()   # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode:   # check terminal status
                                self.channel.write('delete system login user {username}\n'.format(username = username))	# adduser
                                i = self.channel.expect([r"%s"%self.prompt],timeout = self.timeout)
                                result = i[-1]
                                if re.search('error|invalid',result,flags = re.IGNORECASE):
                                        raise ForwardError(result) # command failure 
				else:
                                        data = self._commit()
                                        self._exitConfigMode() # exit config terminal mode.
                        else:
                                raise ForwardError('Has yet to enter configuration mode')
                   except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                   return data

        def changePassword(self,username = '',password = ''):
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                try:
                        if not username or not password:
                                raise ForwardError('Please specify the username = your-username and password = your-password') # Specify a user name and password parameters here.
                        checkPermission = self._configMode()   # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode:   # check terminal status
                                self.channel.write('set system login user {username} authentication plain-text-password\n'.format(username = username))	# execute useradd command
	
                                i = self.channel.expect([r"New password:",r"%s"%self.prompt],timeout = self.timeout)
                                result = i[-1]
                                if re.search('error|invalid',result,flags = re.IGNORECASE):
                                        raise ForwardError(result) # command failure 
                                self.channel.write("{password}\n".format(password = password)) # Enter password
                                i = self.channel.expect([r"Retype new password:",r"%s"%self.prompt],timeout = self.timeout) # check password
                                if i[0] == 0: # repassword
                                        self.channel.write("{password}\n".format(password = password))
                                        i = self.channel.expect([r"%s"%self.prompt],timeout = self.timeout) # check password
                                        if i[0] == 0:
                                                result = i[-1]
                                                if re.search('error|invalid',result,flags = re.IGNORECASE):
                                                        raise ForwardError(result)
                                                else:
                                                        # change password is successed.
                                                        data = self._commit()
                                                        self._exitConfigMode() # exit config terminal mode.
                                        elif i[0] == -1:
                                                raise ForwardError('Error: receive timeout')
                                elif i[0] == 1: # password wrong
                                        raise ForwardError(i[-1])
                                elif i[0] == -1: # timeout
                                        raise ForwardError('Error: receive timeout')
                        else:
                                raise ForwardError('Has yet to enter configuration mode')
                except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                return data

        def bindBandwidth(self,ip='',bandwidth=''):
                njInfo = {
                           "status":False,
                           "content":"",
                           "errLog":""
                }
                mx960Bandwidth=Bandwidth(ip=ip,bandwidth=bandwidth,shell=self)
                njInfo=mx960Bandwidth.bindBandwidth()
                return njInfo
       
        def deleteBindIPAndBandwidth(self,ip='',bandwidth=''):
                njInfo = {
                           "status":False,
                           "content":"",
                           "errLog":""
                }
                mx960Bandwidth=Bandwidth(ip=ip,bandwidth=bandwidth,shell=self)
                njInfo=mx960Bandwidth.deleteBindIPAndBandwidth()
                return njInfo

#!/usr/bin/evn python
#coding:utf-8
"""
-----Introduction-----
[Core][forward] Device class for USG1000.
"""
import sys,re,os
from forward.models.telnet.baseTELNET import BASETELNET
from forward.models_utils.forwardError import ForwardError
from forward.models_utils.ban import BAN,adminPermissionCheck
from forward.models.telnet.usgFirewallPolicyAdmin import USGFirewallPolicyAdmin
class USG1000(BASETELNET,USGFirewallPolicyAdmin):

        @adminPermissionCheck
        def _configMode(self,cmd = 'conf term'):
                self.isConfigMode = False
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                self.cleanBuffer()
                self.channel.write("%s\n" %(cmd))
                data = self._recv(self.basePrompt)
                if data['status']:
                        self.isConfigMode = True
                self.getPrompt()
                return data

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
		
        def _exitConfigMode(self):
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                try:
                        if self.isConfigMode: # Check current status
                                self.channel.write("end\n")
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
                                self._exitConfigMode()  # exit config terminal mode.
                                self.channel.write('copy running-config startup-config\n')
                                result = self._recv(self.prompt)
                                if re.search('Current configuration:',result['content'],flags = re.IGNORECASE):
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
                        command="""user administrator {username} local {password} authorized-table admin\n""".format(username = username,password = password)
                else:
                        command="""user administrator {username} local {password} authorized-table admsee\n""".format(username = username,password = password)
                        
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                try:
                        if not username or not password:
                                raise ForwardError('Please specify the username = your-username and password = your-password')  # Spcify a user name and password parameters here.
                        checkPermission = self._configMode()    # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode:   # check terminal status
                                self.channel.write(command)     # adduser
                                data = self._recv(self.prompt)    #recv result
                                if not  data['status']:
                                        raise ForwardError(data['errLog'])       # break
                                result = data['content']
                                if re.search('error|invalid|assword',result,flags = re.IGNORECASE):
                                        raise ForwardError(result)     # command failure 
                                # set password is successed.
                                data = self._commit()
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
                        checkPermission = self._configMode()    # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode:   # check terminal status
                                self.channel.write("""no user administrator {username}\n""".format(username = username))     # deleteUser
                                data = self._recv(self.prompt)    #recv result
                                if not  data['status']:
                                        raise ForwardError(data['errLog'])       # break
                                result = data['content']
                                if re.search('error|invalid|assword',result,flags = re.IGNORECASE):
                                        raise ForwardError(result)     # command failure 
                                # delete user is successed.
                                data = self._commit()
                        else:
                                raise ForwardError('Has yet to enter configuration mode')
                except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                return data
        def changePassword(self,username='',password=''):
                return self.addUser(username=username,password=password)

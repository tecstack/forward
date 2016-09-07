
#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for s9303.
"""

import re
# from base.sshv2 import sshv2
from forward.models.baseSSHV2 import BASESSHV2
from forward.models_utils.forwardError import ForwardError
from forward.models_utils.ban import BAN,adminPermissionCheck
class S9303(BASESSHV2):

        def _configMode(self):
                return BASESSHV2._configMode(self,"""sys\naaa""")

        def _commit(self):
                self.cleanBuffer()
                self.saveCommand = 'save'
                self.exitCommand = 'return'
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                try:
                        if self.isConfigMode:
                                self._exitConfigMode(cmd = self.exitCommand)
                                self.shell.send('%s\n' % (self.saveCommand)) # save setup to system
                                i = 1
                                while True:
                                        if  re.search("continue\?",data['content'].split('\n')[-1]): #In interactive prompt
                                                self.shell.send('y\n')
						while not re.search(self.prompt,data['content'].split('\n')[-1]):
                                                        data['content'] += self.shell.recv(1024)
                                                if re.search('successfully',data['content'],flags = re.IGNORECASE):
                                                        data['status'] = True
                                                break
                                        else:
                                                data['content'] += self.shell.recv(1024)
                                        i += 1
                        else:
                                raise ForwardError('Error: The current state is not configuration mode')
                except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                return data

	def addUser(self,username = '',password = '',userLevel = 1):
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                # user leve default 1
                try:
                        if not username or not password:
                                raise ForwardError('Please specify the username = your-username and password = your-password') # Specify a user name and password parameters here.
                        checkPermission = self._configMode() # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode:   # check terminal status
                                self.shell.send('local-user {username} password cipher {password}\n'.format(username = username,password = password))
                                while True:
                                        if ( re.search(self.prompt,data['content'].split('\n')[-1])) and ( re.search('local-user .* password cipher[\s\S]+%s'%self.prompt,data['content'])):
                                                break
                                        else:
                                                data['content'] += self.shell.recv(1024)
                                
                                self.shell.send('local-user {username} privilege level  {userLevel}\n'.format(username = username,userLevel = userLevel))
                                data['content'] = ''
                                while True:
                                        if ( re.search(self.prompt,data['content'].split('\n')[-1])) and ( re.search('local-user .* privilege level[\s\S]+%s'%self.prompt,data['content'])):
                                                break
                                        else:
                                                data['content'] += self.shell.recv(1024)
                                self.shell.send("local-user {username} service-type terminal ssh\n".format(username = username))
                                data['content'] = ''
                                while True:
                                        if ( re.search(self.prompt,data['content'].split('\n')[-1])) and ( re.search('local-user .* service-type terminal ssh[\s\S]+%s'%self.prompt,data['content'])):
                                                break
                                        else:
                                                data['content'] += self.shell.recv(1024)
                                self.shell.send("quit\n")
                                data['content'] = ''
                                while True:
                                        if ( re.search(self.basePrompt,data['content'].split('\n')[-1])) and ( re.search('quit.*[\s\S]+%s'%self.basePrompt,data['content'])):
                                                break
                                        else:
                                                data['content'] += self.shell.recv(1024)
                                self.getPrompt()
                                self.shell.send("ssh user {username} authentication-type password\n".format(username=username))
                                data['content'] = ''
                                while True:
                                        if ( re.search(self.prompt,data['content'].split('\n')[-1])) and ( re.search('ssh user .* authentication-type password[\s\S]+%s'%self.prompt,data['content'])):
                                                break
                                        else:
                                                data['content'] += self.shell.recv(1024)
                                self.shell.send("ssh user {username} service-type all\n".format(username=username))
                                data['content'] = ''
                                while True:
                                        if ( re.search(self.prompt,data['content'].split('\n')[-1])) and ( re.search('ssh user .* service-type all[\s\S]+%s'%self.prompt,data['content'])):
                                                break
                                        else:
                                                data['content'] += self.shell.recv(1024)
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
                # user leve default 1
                try:
                        if not username:
                                raise ForwardError('Please specify a username')
                        checkPermission = self._configMode() # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode:   # check terminal status
                                self.cleanBuffer()
                                self.shell.send('undo local-user {username}\n'.format(username = username))
                                while True:
                                        if ( re.search(self.prompt,data['content'].split('\n')[-1])) and ( re.search('undo local-user[\s\S]+%s'%self.prompt,data['content'])):
                                                break
                                        else:
                                                data['content'] += self.shell.recv(1024)
                                if re.search('error|invalid',data['content'],flags = re.IGNORECASE):
                                        raise ForwardError(data['content'])
                                data = self._commit()
                        else:
                                raise ForwardError('Has yet to enter configuration mode')
                except ForwardError,e:
                        data['status'] = False
                        data['errLog'] = str(e)
                return data
	def changePassword(self,username = '',password = '',userLevel = 1):
                data = {
                        "status":False,
                        "content":"",
                        "errLog":""
                }
                # user leve default 1
                try:
                        if not username or not password:
                                raise ForwardError('Please specify the username = your-username and password = your-password') # Specify a user name and password parameters here.
                        checkPermission = self._configMode() # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode:   # check terminal status
                                self.shell.send('local-user {username} password cipher {password}\n'.format(username = username,password = password))
                                while True:
                                        if ( re.search(self.prompt,data['content'].split('\n')[-1])) and ( re.search('local-user .* password cipher[\s\S]+%s'%self.prompt,data['content'])):
                                                break
                                        else:
                                                data['content'] += self.shell.recv(1024)
                                data = self._commit()
                        else:
                                raise ForwardError('Has yet to enter configuration mode')
                except ForwardError,e:
                        data['status'] = False
                        data['errLog'] = str(e)
                return data

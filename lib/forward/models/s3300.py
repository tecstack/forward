
#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for s3300.
"""

import re,pexpect,re
# from base.sshv2 import sshv2
#from models.baseSSHV2 import BASESSHV1
from forward.models.baseSSHV1 import BASESSHV1
from forward.models_utils.forwardError import ForwardError
from forward.models_utils.ban import BAN,adminPermissionCheck
class S3300(BASESSHV1):

        def __init__(self,*args,**kws):
                BASESSHV1.__init__(self,*args,**kws)
                self.moreFlag = re.escape('....press ENTER to next line, Q to quit, other key to next page....')

	@adminPermissionCheck
        def _configMode(self):
                data = {
                        'status':False,
                        'content':'',
                        'errLog':''
                }
                self.isConfigMode = False
                self.cleanBuffer()
                self.channel.send('conf term\n')
                data=self._recv(self.basePrompt)
                self.getPrompt()
                if data['content']:
                        self.isConfigMode = True
                return data

        def _recv(self,_prompt):
                data = {
                        'status':False,
                        'content':'',
                        'errLog':''
                }
                i = self.channel.expect([r"%s"%_prompt,pexpect.TIMEOUT],timeout = self.timeout)
                result = ''
                try:
                        if i == 0:
                                result = self.channel.before # get result
                                data['status'] = True
                        elif i == 2:
                                raise ForwardError('Error: receive timeout')
                        else:
                                data['errLog'] = self.channel.before
                        data['content'] = result
                except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                return data

        def _exitConfigMode(self):
                exitCommand = "end"
                data = {
                        'status':False,
                        'content':'',
                        'errLog':''
                }
                try:
                        if self.isConfigMode: # Check current status
                                self.channel.send("%s\n"%(cmd))
                                data = self._recv(self.basePrompt)
                                if data['status']:
                                        self.isConfigMode = False
                        else:
                                raise ForwardError('Error: The current state is not configuration mode')
                except ForwardError,e:
                        data['errLog'] = str(e)
                self.getPrompt() # release host prompt
                return data

        def _commit(self):
                data = {
                        'status':False,
                        'content':'',
                        'errLog':''
                }
                saveCommand = "copy running-config startup-config"
                try:
                        if self.isConfigMode:
                                self._exitConfigMode()
                                self.channel.send('%s\n' % (saveCommand)) # save setup to system
                                data = self._recv(self.prompt)
                                if re.search('user "admin" only',data['content']):
                                        raise ForwardError(data['content'])
                                else:
                                        data['status'] = True
                        else:
                                raise ForwardError('Error: The current state is not configuration mode')
                except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                return data

        def addUser(self,username = '',password = '',userLevel = 1):
                data = {
                        'status':False,
                        'content':'',
                        'errLog':''
                }
                try:
                        if not username or not password:
                                raise ForwardError('Please specify the username = your-username and password = your-password') # Specify a user name and password parameters here.
                        checkPermission = self._configMode() # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode: # check terminal status
                                self.channel.send("""username {username} privilege  {userLevel} password 0 {password}\n""".format(username = username,password = password,userLevel = userLevel))
                                _result = self._recv(self.prompt)
                                _tmp = re.search("""This command can be used by user "admin" only""",_result['content'])
                                if _tmp:
                                        raise ForwardError(_tmp.group())
                                elif not _result['status']:
                                        raise ForwardError(_result['errLog'])
                                self.channel.send("""username {username} terminal ssh\n""".format(username = username,password = password,userLevel = userLevel))
                                _result = self._recv(self.prompt)
                                if _result['status']:
                                        data = self._commit()
                                else:
                                        data = _result
                        else:
                                raise ForwardError('Has yet to enter configuration mode')
                except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                return data
        def deleteUser(self,username=''):
                data = {
                        'status':False,
                        'content':'',
                        'errLog':''
                }
                try:
                        if not username:
                                raise ForwardError('Please specify a username')
                        checkPermission = self._configMode() # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode: # check terminal status
                                self.channel.send("""no username  {username}\n""".format(username = username))
                                _result = self._recv(self.prompt)
                                _tmp = re.search("""This command can be used by user "admin" only""",_result['content'])
                                if _tmp:
                                        raise ForwardError(_tmp.group())
                                elif not _result['status']:
                                        raise ForwardError(_result['errLog'])
                                if re.search('error|invalid',data['content'],flags = re.IGNORECASE):
                                        raise ForwardError(data['content'])
                                if _result['status']:
                                        data = self._commit()
                                else:
                                        data = _result

                        else:
                                raise ForwardError('Has yet to enter configuration mode')
                except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                return data

        def changePassword(self,username = '',password = '',userLevel = 1):
                data = {
                        'status':False,
                        'content':'',
                        'errLog':''
                }
                try:
                        if not username or not password:
                                raise ForwardError('Please specify the username = your-username and password = your-password') # Specify a user name and password parameters here.
                        checkPermission = self._configMode() # swith to config terminal mode.
                        if not checkPermission['status']:
                                raise ForwardError(checkPermission['errLog'])
                        if self.isConfigMode: # check terminal status
                                self.channel.send("""username {username}  password 0 {password}\n""".format(username = username,password = password,userLevel = userLevel))
                                _result = self._recv(self.prompt)
                                _tmp = re.search("""This command can be used by user "admin" only""",_result['content'])
                                if _tmp:
                                        raise ForwardError(_tmp.group())
                                elif not _result['status']:
                                        raise ForwardError(_result['errLog'])
                                if _result['status']:
                                        data = self._commit()
                                else:
                                        data = _result
                        else:
                                raise ForwardError('Has yet to enter configuration mode')
                except ForwardError,e:
                        data['errLog'] = str(e)
                        data['status'] = False
                return data

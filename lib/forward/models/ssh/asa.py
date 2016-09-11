
#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for asa.
"""

import re
# from base.sshv2 import sshv2
from forward.models.ssh.baseSSHV2 import BASESSHV2
from forward.models_utils.forwardError import ForwardError
class ASA(BASESSHV2):

        def cleanBuffer(self):
                if self.shell.recv_ready():
                        self.shell.recv(4096)
                self.shell.send('\r\n')
                buff = ''
                while not re.search(self.basePrompt,buff.split('\n')[-1]):  # When after switching mode, the prompt will change, it should be based on basePromptto check and at last line
                        try:
                                buff += self.shell.recv(1024)
                        except:
                                raise ForwardError('Receive timeout [%s]' %(buff))

        def addUser(self,username = '',password = ''):
                return BASESSHV2.addUser(self,username = username,password = password,addCommand = 'username {username} password {password}\n')


        def changePassword(self,username = '',password = ''):
                return BASESSHV2.addUser(self,username = username,password = password,addCommand = 'username {username} password {password}\n')

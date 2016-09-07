
#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for n7010.
"""

import re
# from base.sshv2 import sshv2
from forward.models.baseSSHV2 import BASESSHV2
class N7010(BASESSHV2):

        def addUser(self,username = '',password = '',admin=False):
		# param admin: defualt is not admin
		if admin:
                	return BASESSHV2.addUser(self,username = username,password = password,addCommand = 'user {username} password {password} role network-admin\n')
		else:
                	return BASESSHV2.addUser(self,username = username,password = password,addCommand = 'user {username} password {password} role priv-1\n')
			

        def _commit(self):
                return BASESSHV2._commit(self,saveCommand = 'copy running-config startup-config',exitCommand = 'end')

        def changePassword(self,username = '',password = ''):
                return BASESSHV2.addUser(self,username = username,password = password,addCommand = 'user {username} password {password} role network-admin\n')

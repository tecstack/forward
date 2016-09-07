
#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for n5800.
"""

import re
# from base.sshv2 import sshv2
from forward.models.baseSSHV2 import BASESSHV2
class S5800(BASESSHV2):

        def addUser(self,username = '',password = ''):
                return BASESSHV2.addUser(self,username = username,password = password,addCommand = 'user {username} password {password} role network-admin\n')

        def _commit(self):
                return BASESSHV2._commit(self,saveCommand = 'copy running-config startup-config',exitCommand = 'end')

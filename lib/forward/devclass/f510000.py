#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for F510000.
Author: Cheung Kei-chuen
"""
from forward.devclass.baseF5 import BASEF5


class F510000(BASEF5):
    """This is a manufacturer of F5, it is integrated with BASEF5 library.
    """

    def addUser(self, username, password):
    	"""Because the device of this model is different from the other F5
        devices in creating user parameters, it is rewritten.
        """
        return BASEF5.addUser(self,
                              username=username,
                              password=password,
                              addCommand='user {username} password {password} role network-admin\n')

    def _commit(self):
    	"""Because the device of this model is different from the other
        F5 devices in deleting user parameters, it is rewritten.
        """
        return BASEF5._commit(self,
                              saveCommand='copy running-config startup-config',
                              exitCommand='end')

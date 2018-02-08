#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for ASR1006.
Author: Cheung Kei-chuen
"""

from forward.devclass.baseCisco import BASECISCO


class ASR1006(BASECISCO):
    """The device model belongs to the cisco series
    so the attributes and methods of BASECISCO are inherited.
    """
    def addUser(self, username, password):
        # Overriding methods
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} secret {password}\n')

    def changePassword(self, username, password):
        # Overriding methods
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} secret {password}\n')

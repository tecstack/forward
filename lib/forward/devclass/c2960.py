#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for c2960.
Author: Cheung Kei-chuen
"""

from forward.devclass.baseCisco import BASECISCO


class C2960(BASECISCO):
    """This is a manufacturer of cisco, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """

    def addUser(self, username, password):
        """Because the device of this model is different from the other Cisco
        devices in creating user parameters, it is rewritten.
        """
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} secret {password}\n')

    def changePassword(self, username, password):
        """Because the device of this model is different from the other
        Cisco devices in deleting user parameters, it is rewritten.
        """
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username  {username} secret {password}\n')

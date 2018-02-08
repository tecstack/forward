#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for n5548.
Author: Cheung Kei-Chuen
"""
from forward.devclass.baseCisco import BASECISCO


class N5548(BASECISCO):
    """This is a manufacturer of cisco, so it is integrated with BASECISCO library.
    """

    def addUser(self, username, password, admin=False):
        """Because the device of this model is different from the other Cisco
        devices in creating user parameters, it is rewritten.
        """
        # default is not admin
        if admin:
            return BASECISCO.addUser(self,
                                     username=username,
                                     password=password,
                                     addCommand='user {username} password {password} role network-admin\n')
        else:
            return BASECISCO.addUser(self,
                                     username=username,
                                     password=password,
                                     addCommand='user {username} password {password} role priv-1\n')

    def _commit(self):
        """Because the device of this model is different from the other
        Cisco devices in commit  parameters, it is rewritten.
        """
        return BASECISCO._commit(self,
                                 saveCommand='copy running-config startup-config',
                                 exitCommand='end')

    def changePassword(self, username, password):
        """Because the device of this model is different from the other
        Cisco devices in change user's password  parameters, it is rewritten.
        """
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='user {username} password {password} role network-admin\n')

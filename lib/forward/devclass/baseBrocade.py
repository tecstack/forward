#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for Brocade.
Author: Cheung Kei-chuen
"""
from forward.devclass.baseSSHV2 import BASESSHV2


class BASEBROCADE(BASESSHV2):
    """This is a manufacturer of brocade, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    pass

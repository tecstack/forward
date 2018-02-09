#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Azrael <azrael-ex@139.com>

"""
-----Introduction-----
[Core][forward] Base device class for sshv2 method, by using paramiko module.
Author: Wangzhe
"""

import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError


class BASELINUX(BASESSHV2):
    """This is a manufacturer of linux, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    pass

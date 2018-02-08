#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

"""
-----Introduction-----
[Core][forward] Base device class for huawei basic device method, by using paramiko module.
Author: Cheung Kei-Chuen, Wangzhe
"""

import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError


class BASEHUAWEI(BASESSHV2):
    """This is a manufacturer of huawei, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    pass

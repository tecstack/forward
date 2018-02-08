#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for asa.
Author: Cheung Kei-chuen
"""

import re
from forward.devclass.baseCisco import BASECISCO
from forward.utils.forwardError import ForwardError


class ASA(BASECISCO):
    """The device model belongs to the cisco series
    so the attributes and methods of BASECISCO are inherited.
    """
    def cleanBuffer(self):
        """Since the device is inconsistent with the details
        of the other Cisco series, the method needs to be rewritten
        to fit the device of this type.
        """
        if self.shell.recv_ready():
                self.shell.recv(4096)
        self.shell.send('\r\n')
        buff = ''
        """ When after switching mode, the prompt will change,
        it should be based on basePromptto check and at last line"""
        while not re.search(self.basePrompt, buff.split('\n')[-1]):
            try:
                # Cumulative return result
                buff += self.shell.recv(1024)
            except Exception:
                raise ForwardError('Receive timeout [%s]' % (buff))

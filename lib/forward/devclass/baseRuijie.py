#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for Ruijie.
Author: Cheung Kei-Chuen
"""
import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError


class BASERUIJIE(BASESSHV2):
    """This is a manufacturer of maipu, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """

    def cleanBuffer(self):
        """Because the device USES the cleanBuffer method in different details,
        it can be rewritten to modify the function.
        """
        if self.shell.recv_ready():
            self.shell.recv(4096)
        # Ruijie equipment does not support sending line, must be sent to some characters
        self.shell.send(' \n')
        buff = ''
        # When after switching mode, the prompt will change, it should be based on basePrompt to check and at last line
        while not re.search(self.basePrompt, buff.split('\n')[-1]):
            try:
                # Accumulative results
                buff += self.shell.recv(1024)
            except Exception:
                raise ForwardError('[Clean Buffer Error]: %s: Receive timeout [%s]' % (self.ip, buff))

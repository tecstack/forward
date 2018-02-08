#!/usr/bin/evn python
# coding:utf-8
"""
-----Introduction-----
[Core][forward] Device class for USG1000.
Author: Cheung Kei-Chuen
"""
import re
from forward.devclass.baseVenustech import BASEVENUSTECH
from forward.utils.forwardError import ForwardError


class USG1000(BASEVENUSTECH):
    """This is a manufacturer of venustech, so it is integrated with BASEVENUSTECH library.
    """

    def _recv(self, _prompt):
        # Gets the return message after the command is executed.
        data = {"status": False,
                "content": "",
                "errLog": ""}
        # If the received message contains the host prompt, stop receiving.
        i = self.channel.expect([r"%s" % _prompt], timeout=self.timeout)
        try:
            if i[0] == -1:
                # The supplied host prompt is incorrect, resulting in the receive message timeout.
                raise ForwardError('Error: receive timeout')
            # Successed.
            data['status'] = True
            # Get result.
            data['content'] = i[-1]
        except ForwardError, e:
            data['errLog'] = str(e)
        return data

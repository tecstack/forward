#!/usr/bin/evn python
# coding:utf-8
"""     It applies only to models of network equipment  mx960
        See the detailed comments mx960.py
"""
import re
from forward.devclass.baseTELNET import BASETELNET
from forward.utils.forwardError import ForwardError


class BASEJUNIPER(BASETELNET):
    """This is a manufacturer of juniper, using the
    telnet version of the protocol, so it is integrated with BASELTELNET library.
    """
    def _recv(self, _prompt):
        """The user receives the message returned by the device.
        """
        data = {"status": False,
                "content": "",
                "errLog": ""}
        # If the host prompt is received, the message is stopped.
        i = self.channel.expect([r"%s" % _prompt], timeout=self.timeout)
        try:
            if i[0] == -1:
                raise ForwardError('Error: receive timeout')
            data['status'] = True
            # Get result
            data['content'] = i[-1]
        except ForwardError, e:
            data['errLog'] = str(e)
        return data

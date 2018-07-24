#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for n7018.
Author: Cheung Kei-Chuen
"""
from forward.devclass.baseRaisecom import BASERAISECOM
from forward.utils.forwardError import ForwardError
import re


class R3048G(BASERAISECOM):
    """This is a manufacturer of raisecom, so it is integrated with BASERAISECOM library.
    """
    def _configMode(self, cmd="configure"):
        """Used to switch from privileged mode to config mode for command line mode.
        Does not apply to other modes to switch to config mode.
        """
        # Flag config mode is False
        self.isConfigMode = False
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Clean buffer.
        self.cleanBuffer()
        self.shell.send("%s\n" % (cmd))
        while not re.search(self.basePrompt, result['content'].split('\n')[-1]):
            result['content'] += self.shell.recv(1024)
        # release host prompt
        self.getPrompt()
        # Flag config mode is True.
        self.isConfigMode = True
        result['status'] = True
        return result

    def _exitConfigMode(self, cmd='quit'):
        """Exit from configuration mode to privileged mode.
        """
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            # Check current status
            if self.isConfigMode:
                self.shell.send("%s\n" % (cmd))
                while not re.search(self.basePrompt, result['content'].split('\n')[-1]):
                    result['content'] += self.shell.recv(1024)
                # Flag config mode is False.
                self.isConfigMode = False
                result["status"] = True
            else:
                raise ForwardError('Error: The current state is not configuration mode')
        except ForwardError, e:
            result["status"] = False
            result['errLog'] = str(e)
        # release host prompt
        self.getPrompt()
        return result

    def _commit(self, saveCommand='write', exitCommand='quit'):
        """To save the configuration information of the device,
        it should be confirmed that the device is under the Config Mode before use.
        """
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            # Status check.
            if self.isConfigMode:
                self._exitConfigMode(exitCommand)
                # save setup to system
                self.shell.send('%s\n' % (saveCommand))
                while not re.search(self.prompt, result['content'].split('\n')[-1]):
                    result['content'] += self.shell.recv(1024)
                """
                If the program finds information like ‘success’, 'OK' etc.
                in the received information, it indicates that the save configuration is successful.
                """
                if re.search('(\[OK\])|(Copy complete)|(successfully)', result['content'], flags=re.IGNORECASE):
                    result['status'] = True
            else:
                raise ForwardError('[Commit Config Error]: The current state is not configuration mode')
        except ForwardError, e:
            result['errLog'] = str(e)
            result['status'] = False
        return result

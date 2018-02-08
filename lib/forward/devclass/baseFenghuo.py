#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for Fenghuo.
Author: Cheung Kei-Chuen
"""
import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError


class BASEFENGHUO(BASESSHV2):
    """This is a manufacturer of fenghuo, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def privilegeMode(self):
        """Used to switch from normal mode to privileged mode for command line mode.
        Does not apply to other modes to switch to privileged mode.
        """
        self.privilegeModeCommand = 'enable'
        result = {
            'status': True,
            'content': '',
            'errLog': ''
        }
        self.cleanBuffer()
        if self.isLogin and (len(self.privilegePw) > 0):
            """This can only be performed when the device
            has been successfully logged in and the privilege mode password is specified."""
            # (login succeed status) and (self.privilegePw exist)
            self.cleanBuffer()
            self.shell.send('%s\n' % (self.privilegeModeCommand))
            enableResult = ''
            while True:
                """
                etc:
                [admin@NFJD-PSC-MGMT-COREVM60 ~]$ super
                [admin@NFJD-PSC-MGMT-COREVM60 ~]$

                or

                [admin@NFJD-PSC-MGMT-COREVM60 ~]$ super
                 Password:
                """
                """
                    fg3950: enable command result : 'enable\r\r\nUnknown action 0\r\n'
                """
                # need password
                passwordChar = """%s[\r\n]+ *[pP]assword""" % self.privilegeModeCommand
                promptChar = """{command}[\r\n]+[\s\S]*{basePrompt}""".format(
                    command=self.privilegeModeCommand,
                    basePrompt=self.basePrompt
                )

                # Second layers of judgment, Privileged command  char 'super/enable'  must be received.
                # otherwise recv continue... important!
                if re.search(passwordChar, enableResult):
                    # if received 'password'
                    break
                # no password
                elif re.search(promptChar, enableResult):
                    # if no password
                    break
                else:
                    # not finished,continue
                    enableResult += self.shell.recv(1024)

            if re.search('assword', enableResult):
                # need password
                self.shell.send("%s\n" % self.privilegePw)
                result = ''
                while not re.search(self.basePrompt, result) and (not re.search('assword|denied|Denied', result)):
                    result += self.shell.recv(1024)
                if re.search('assword|denied|Denied', result):
                    # When send the self.privilegePw, once again encountered a password hint password wrong.
                    result['status'] = False
                    result['errLog'] = '[Switch Mode Failed]: Password incorrect'
                elif re.search(self.basePrompt, result):
                    # Switch mode succeed
                    self.getPrompt()
                    result['status'] = True

            # Check the error information in advance
            elif re.search('\%|Invalid|\^', enableResult):
                # bad enable command
                result['status'] = False
                result['errLog'] = '[Switch Mode Failed]: Privileged mode command incorrect-A'
            elif re.search(self.basePrompt, enableResult):
                # Switch mode succeed, don't need password
                self.getPrompt()
                result['status'] = True
            else:
                result['stauts'] = False
                result['errLog'] = '[Switch Mode Failed]: Unknown device status'

        elif not self.isLogin:
            # login failed
            result['status'] = False
            result['errLog'] = '[Switch Mode Failed]: Not login yet'

        elif len(self.privilegePw) == 0:
            # self.privilegePw dosen't exist, do nothing
            pass
        return result

    def _commit(self, saveCommand='write file', exitCommand='quit'):
        """To save the configuration information of the device,
        it should be confirmed that the device is under the Config Mode before use.
        """
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            if self.isConfigMode:
                self._exitConfigMode(exitCommand)
                # save setup to system
                self.shell.send('%s\n' % (saveCommand))
                while not re.search(self.prompt, result['content'].split('\n')[-1]):
                    result['content'] += self.shell.recv(1024)
                    # When prompted, reply Y,Search range at last line
                    if re.search(re.escape("Are you sure?(y/n) [y]"), result['content'].split('\n')[-1]):
                        self.shell.send("y\n")
                        continue
                """
                If the program finds information like ‘success’, ‘OK’, ‘copy complete’, etc.
                in the received information, it indicates that the save configuration is successful.
                """
                if re.search('(\[OK\])|(Copy complete)|(successfully)', result['content'], flags=re.IGNORECASE):
                    result['status'] = True
                # Clean buffer
                self.cleanBuffer()
            else:
                raise ForwardError('[Commit Config Error]: The current state is not configuration mode')
        except ForwardError, e:
            result['errLog'] = str(e)
            result['status'] = False
        return result

    def _configMode(self, cmd='configure'):
        """Used to switch from privileged mode to config mode for command line mode.
        Does not apply to other modes to switch to config mode.
        """
        # Flag isCOnfigMode is False
        self.isConfigMode = False
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        self.cleanBuffer()
        self.shell.send("%s\n" % (cmd))
        while not re.search(self.basePrompt, result['content'].split('\n')[-1]):
            result['content'] += self.shell.recv(1024)
        # release host prompt
        self.getPrompt()
        # Flag isCOnfigMode is True
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
                """Exit from configuration mode to privileged mode.
                """
                while not re.search(self.basePrompt, result['content'].split('\n')[-1]):
                    result['content'] += self.shell.recv(1024)
                # Flag isCOnfigMode is False
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

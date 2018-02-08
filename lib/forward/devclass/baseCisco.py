#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Azrael <azrael-ex@139.com>

"""
-----Introduction-----
[Core][forward] Base device class for cisco basic device method, by using paramiko module.
Author: Cheung Kei-Chuen, Wangzhe
"""

import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError


class BASECISCO(BASESSHV2):
    """This is a manufacturer of cisco, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def privilegeMode(self):
        """Used to switch from normal mode to privileged mode for command line mode.
        Does not apply to other modes to switch to privileged mode.
        """
        result = {
            'status': True,
            'content': '',
            'errLog': ''
        }
        # Clean buffer.
        self.cleanBuffer()
        if self.isLogin and (len(self.privilegePw) > 0):
            """This can only be performed when the device
            has been successfully logged in and the privilege mode password is specified."""
            # (login succeed status) and (self.privilegePw exist)
            self.privilegeModeCommand = 'enable'
            self.cleanBuffer()
            self.shell.send('%s\n' % (self.privilegeModeCommand))
            enableResult = ''
            while True:
                """It's not until you have a password prompt or when you switch successfully
                that you stop popping out of the loop."""
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
                _data = ''
                while not re.search(self.basePrompt, _data) and (not re.search('assword|denied|Denied', _data)):
                    _data += self.shell.recv(1024)
                if re.search('assword|denied|Denied', _data):
                    # When send the self.privilegePw, once again encountered a password hint password wrong.
                    result['status'] = False
                    result['errLog'] = '[Switch Mode Failed]: Password incorrect'
                elif re.search(self.basePrompt, _data):
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

    def _commit(self, saveCommand='write', exitCommand='end'):
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
                # Exit from configuration mode to privileged mode.
                self._exitConfigMode(exitCommand)
                # save setup to system
                self.shell.send('%s\n' % (saveCommand))
                while not re.search(self.prompt, result['content'].split('\n')[-1]):
                    result['content'] += self.shell.recv(1024)
                """
                If the program finds information like ‘success’, ‘OK’, ‘copy complete’, etc.
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

    def addUser(self, username, password, addCommand='username {username} password {password}\n'):
        """Create a user on the device.
        """
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            if not addCommand:
                raise ForwardError("Please specify the add user's command")
            if not username or not password:
                # Specify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                self.cleanBuffer()
                # adduser
                self.shell.send(addCommand.format(username=username, password=password))
                while not re.search(self.prompt, result['content'].split('\n')[-1]):
                    result['content'] += self.shell.recv(1024)
                """If the program is in the received message, it searches for character
                information such as error and inavalid, indicating that the account creation failed.
                """
                if re.search('error|invalid', result['content'], flags=re.IGNORECASE):
                    result['content'] = ''
                    raise ForwardError(result['content'])
                else:
                    # set password is successed.
                    result = self._commit()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            result['status'] = False
            result['errLog'] = str(e)
        return result

    def deleteUser(self, username=''):
        """Delete a user on the device
        """
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            if not username:
                raise ForwardError("Please specify a username")
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                self.cleanBuffer()
                # delete username
                self.shell.send("no username {username}\n".format(username=username))
                while not re.search(self.prompt, result['content'].split('\n')[-1]):
                    result['content'] += self.shell.recv(1024)
                if re.search('error|invalid', result['content'], flags=re.IGNORECASE):
                    raise ForwardError(result['content'])
                else:
                    # deleted username
                    result = self._commit()
                    result['status'] = True
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            result['status'] = False
            result['errLog'] = str(e)
        return result

    def getUser(self, command="show running-config | in username"):
        """Gets the list of users on the device.
        """
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            # [{"username":"zhang-qichuan","secret":5},{}....]
            userList = []
            # execute query command
            info = self.execute(command)
            if not info["status"]:
                raise ForwardError("Error:get user list failed: %s" % info["errLog"])
            # process result
            result = info["content"]
            for line in result.split('\n'):
                # Each line
                index = 0
                # ['username' , 'test-user' , 'secret', '5','$.........']
                segments = line.split()
                for segment in segments:
                    if index <= 1:
                        index += 1
                        # Check after second fields username my-username secret/password .....
                        continue
                    else:
                        if segment == "secret" or segment == "password":
                            # get secret level
                            userData = {"username": segments[1], "secret": segments[index + 1]}
                            userList.append(userData)
                            break
                    index += 1
            result["content"] = userList
            result["status"] = True
        except ForwardError, e:
            result['status'] = False
            result['errLog'] = str(e)
        return result

    def _configMode(self, cmd='conf term'):
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
        # Flag config mode is True
        self.isConfigMode = True
        result['status'] = True
        return result

    def _exitConfigMode(self, cmd='end'):
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
                """Because the mode is switched, it is only based on basePrompt
                to determine whether the message is returned when the message is received.
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

    def changePassword(self, username, password, addCommand='username {username} password {password}\n'):
        """Modify the password for the device account.
        Because the password command to modify the account on the device is consistent with the creation
        of the user's command, the interface to create the account is called.
        """
        self.addUser(self, username=username, password=password, addCommand=addCommand)

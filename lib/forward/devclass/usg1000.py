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

    def privilegeMode(self):
        """Used to switch from normal mode to privileged mode for command line mode.
        Does not apply to other modes to switch to privileged mode.
        """
        # Set command.
        cmd = 'enable'
        # Flag privilege mode is False.
        self.isPrivilegeMode = False
        data = {"status": False,
                "content": "",
                "errLog": ""}
        # Clean buffer.
        self.cleanBuffer()
        self.channel.write("%s\n" % (cmd))
        # Get result.
        data = self._recv(self.basePrompt)
        if data['status']:
            # Flag privilege mode is True.
            self.isPrivilegeMode = True
        # Get host prompt.
        self.getPrompt()
        return data

    def _configMode(self, cmd='conf term'):
        """Used to switch from privileged mode to config mode for command line mode.
        Does not apply to other modes to switch to config mode.
        """
        # Flag config mode is False.
        self.isConfigMode = False
        data = {"status": False,
                "content": "",
                "errLog": ""}
        # Clean buffer.
        self.cleanBuffer()
        self.channel.write("%s\n" % (cmd))
        # Get result.
        data = self._recv(self.basePrompt)
        if data['status']:
            # Flag config mode is True.
            self.isConfigMode = True
        # Get host prompt.
        self.getPrompt()
        return data

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

    def _exitConfigMode(self):
        """Exit from configuration mode to privileged mode.
        """
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            # Check config mode status.
            if self.isConfigMode:
                # Check current status
                self.channel.write("end\n")
                # Get result.
                data = self._recv(self.basePrompt)
                if data['status']:
                    # Flag config mode is False.
                    self.isConfigMode = False
            else:
                raise ForwardError('Error: The current state is not configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
        # Get host prompt.
        self.getPrompt()
        return data

    def _commit(self):
        """To save the configuration information of the device,
        it should be confirmed that the device is under the Config Mode before use.
        """
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            # Check config mode status.
            if self.isConfigMode:
                # Exit config mode.
                self._exitConfigMode()
                # exit config terminal mode.
                self.channel.write('copy running-config startup-config\n')
                # Get result.
                result = self._recv(self.prompt)
                """The search receives messages that contain characters
                similar to "Current config" to indicate success.
                """
                if re.search('Current configuration:', result['content'], flags=re.IGNORECASE):
                    data['status'] = True
                else:
                    data['content'] = result['content']
            else:
                raise ForwardError('Error: The current state is not configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def addUser(self, username, password, admin=False):
        """Create a user on the device.
        """
        # Set command.
        if admin:
            command = """user administrator {username} local {password} \
                       authorized-table admin\n""".format(username=username, password=password)
        else:
            command = """user administrator {username} local {password} \
                       authorized-table admsee\n""".format(username=username, password=password)
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            # parameters check.
            if not username or not password:
                # Spcify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            if self.isConfigMode:
                # check terminal status
                self.channel.write(command)
                # adduser
                data = self._recv(self.prompt)
                # recv result
                if not data['status']:
                    # break
                    raise ForwardError(data['errLog'])
                result = data['content']
                if re.search('error|invalid|assword', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                # set password is successed, save the configuration.
                data = self._commit()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def deleteUser(self, username):
        """Delete a user on the device
        """
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # Check config mode status.
            if self.isConfigMode:
                # check terminal status
                # deleteUser
                self.channel.write("""no user administrator {username}\n""".format(username=username))
                # recv result
                data = self._recv(self.prompt)
                if not data['status']:
                    # break
                    raise ForwardError(data['errLog'])
                # Get result.
                result = data['content']
                # Search for keywords to determine if the command execution is successful.
                if re.search('error|invalid|assword', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                # delete user is successed, save the configuration.
                data = self._commit()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def changePassword(self, username, password):
        """Modify the password for the device account.
        Because the password command to modify the account on the device is consistent with the creation
        of the user's command, the interface to create the account is called.
        """
        return self.addUser(username=username, password=password)

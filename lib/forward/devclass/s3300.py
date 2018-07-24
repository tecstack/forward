# coding:utf-8
# (c) 2015-2018, Wang Zhe <azrael-ex@139.com>, Zhang Qi Chuan <zhangqc@fits.com.cn>
#
# This file is part of Ansible
#
# Forward is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Forward is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
-----Introduction-----
[Core][forward] Device class for s3300.
"""
import pexpect
import re
from forward.devclass.baseMaipu import BASEMAIPU
from forward.utils.forwardError import ForwardError


class S3300(BASEMAIPU):
    """This is a manufacturer of maipu, so it is integrated with BASEMAIPU library.
    """

    def __init__(self, *args, **kws):
        """Since the device's host prompt is different from BASESSHV1,
        the basic prompt for the device is overwritten here.
        """
        BASEMAIPU.__init__(self, *args, **kws)
        self.moreFlag = re.escape('....press ENTER to next \
line, Q to quit, other key to next page....')

    def _configMode(self):
        """Used to switch from privileged mode to config mode for command line mode.
        Does not apply to other modes to switch to config mode.
        """
        data = {'status': False,
                'content': '',
                'errLog': ''}
        # Flag config mode is False.
        self.isConfigMode = False
        # Clean buffer.
        self.cleanBuffer()
        self.channel.send('conf term\n')
        # Get result.
        data = self._recv(self.basePrompt)
        self.getPrompt()
        if data['content']:
            self.isConfigMode = True
        return data

    def _recv(self, _prompt):
        """A message returned after the receiving device has executed the command.
        """
        data = {'status': False,
                'content': '',
                'errLog': ''}
        # If the received message contains the host prompt, stop accepting.
        i = self.channel.expect([r"%s" % _prompt, pexpect.TIMEOUT], timeout=self.timeout)
        result = ''
        try:
            if i == 0:
                # Get result.
                result = self.channel.before
                data['status'] = True
            elif i == 2:
                raise ForwardError('Error: receive timeout')
            else:
                """If the program does not receive the message correctly,
                and does not timeout, the program runs failed.
                """
                data['errLog'] = self.channel.before
            data['content'] = result
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def _exitConfigMode(self):
        """Exit from configuration mode to privileged mode.
        """
        # Set command.
        exitCommand = "end"
        data = {'status': False,
                'content': '',
                'errLog': ''}
        try:
            # Check config mode status.
            if self.isConfigMode:
                # Check current status
                self.channel.send("%s\n" % (exitCommand))
                # Get result.
                data = self._recv(self.basePrompt)
                if data['status']:
                    # Flag config mode is False.
                    self.isConfigMode = False
            else:
                raise ForwardError('Error: The current state is not configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
        self.getPrompt()
        # release host prompt
        return data

    def _commit(self):
        """To save the configuration information of the device,
        it should be confirmed that the device is under the Config Mode before use.
        """
        data = {'status': False,
                'content': '',
                'errLog': ''}
        # Set command.
        saveCommand = "copy running-config startup-config"
        try:
            # Check config mode status.
            if self.isConfigMode:
                # Exit config mode.
                self._exitConfigMode()
                self.channel.send('%s\n' % (saveCommand))
                # save setup to system
                data = self._recv(self.prompt)
                # Permission denied
                if re.search('user "admin" only', data['content']):
                    raise ForwardError(data['content'])
                else:
                    data['status'] = True
            else:
                raise ForwardError('Error: The current state is not configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def addUser(self, username, password, userLevel=1):
        """Create a user on the device.
        """
        data = {'status': False,
                'content': '',
                'errLog': ''}
        try:
            if not username or not password:
                raise ForwardError('Please specify the username = your-username \
                                   and password = your-password')
                # Specify a user name and password parameters here.
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            if self.isConfigMode:
                # check terminal status
                self.channel.send("""username {username} privilege  {userLevel} \
                                     password 0 {password}\n""".format(username=username,
                                                                       password=password,
                                                                       userLevel=userLevel))
                # Get result.
                _result = self._recv(self.prompt)
                _tmp = re.search("""This command can be used by user "admin" only""", _result['content'])
                # Permission denied
                if _tmp:
                    raise ForwardError(_tmp.group())
                elif not _result['status']:
                    # Message acceptance failed
                    raise ForwardError(_result['errLog'])
                # Send the command to create an account.
                self.channel.send("""username {username} terminal ssh\n""".format(username=username,
                                                                                  password=password,
                                                                                  userLevel=userLevel))
                # Get result.
                _result = self._recv(self.prompt)
                if _result['status']:
                    # Save the configuration
                    data = self._commit()
                else:
                    data = _result
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def deleteUser(self, username):
        """Delete a user on the device
        """
        data = {'status': False,
                'content': '',
                'errLog': ''}
        try:
            if not username:
                raise ForwardError('Please specify a username')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # Check config mode status.
            if self.isConfigMode:
                # check terminal status
                self.channel.send("""no username  {username}\n""".format(username=username))
                # Get result.
                _result = self._recv(self.prompt)
                # Permission denied
                _tmp = re.search("""This command can be used by user "admin" only""", _result['content'])
                if _tmp:
                    raise ForwardError(_tmp.group())
                elif not _result['status']:
                    # Message acceptance failed
                    raise ForwardError(_result['errLog'])
                if re.search('error|invalid', data['content'], flags=re.IGNORECASE):
                    raise ForwardError(data['content'])
                if _result['status']:
                    # Save the configuration
                    data = self._commit()
                else:
                    data = _result
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def changePassword(self, username, password, userLevel=1):
        """Modify the password for the device account.
        """
        data = {'status': False,
                'content': '',
                'errLog': ''}
        try:
            if not username or not password:
                # Specify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # Check config mode stauts.
            if self.isConfigMode:
                # check terminal status
                self.channel.send("""username {username}  password 0 {password}\n""".format(username=username,
                                                                                            password=password,
                                                                                            userLevel=userLevel))
                # Get result.
                _result = self._recv(self.prompt)
                _tmp = re.search("""This command can be used by user "admin" only""", _result['content'])
                # Permission denied
                if _tmp:
                    raise ForwardError(_tmp.group())
                elif not _result['status']:
                    # Message acceptance failed
                    raise ForwardError(_result['errLog'])
                if _result['status']:
                    # Save the configuration
                    data = self._commit()
                else:
                    data = _result
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

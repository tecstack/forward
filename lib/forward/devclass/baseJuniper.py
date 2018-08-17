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

    def addUser(self, username, password, admin=False):
        """Create a user on the device.
        """
        # Separate commands to create administrator accounts and common accounts.
        if admin:
            command = "set system login user {username} class read-only\n".format(username=username)
        else:
            command = "set system login user {username} class  ABC\n".format(username=username)
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if not username or not password:
                # Specify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            checkPermission = self._configMode()   # swith to config terminal mode.
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                # adduser
                self.channel.write(command)
                # recv result
                data = self._recv(self.prompt)
                if not data['status']:
                    # break
                    raise ForwardError(data['errLog'])
                # execute useradd command
                self.channel.write('set system login user {username} \
                                   authentication plain-text-password\n'.format(username=username))
                i = self.channel.expect([r"New password:", r"%s" % self.prompt], timeout=self.timeout)
                result = i[-1]
                if re.search('error|invalid', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                # Enter password
                self.channel.write("{password}\n".format(password=password))
                # check password
                i = self.channel.expect([r"Retype new password:", r"%s" % self.prompt], timeout=self.timeout)
                # repassword
                if i[0] == 0:
                    self.channel.write("{password}\n".format(password=password))
                    # check password
                    i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
                    if i[0] == 0:
                        result = i[-1]
                        if re.search('error|invalid', result, flags=re.IGNORECASE):
                            raise ForwardError(result)
                        else:
                            # set password is successed.
                            data = self._commit()
                            # exit config terminal mode.
                            self._exitConfigMode()
                    elif i[0] == -1:
                        raise ForwardError('Error: receive timeout')
                elif i[0] == 1:
                    # password wrong
                    raise ForwardError(i[-1])
                elif i[0] == -1:
                    # timeout
                    raise ForwardError('Error: receive timeout')
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
            if not username:
                raise ForwardError('Please specify a username')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                # delete user
                self.channel.write('delete system login user {username}\n'.format(username=username))
                i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
                result = i[-1]
                if re.search('error|invalid', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                else:
                    # Save
                    data = self._commit()
                    # exit config terminal mode.
                    self._exitConfigMode()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def changePassword(self, username, password):
        """Modify the password for the device account.
        """
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if not username or not password:
                # Specify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                # execute useradd command
                self.channel.write('set system login user {username} \
                                    authentication plain-text-password\n'.format(username=username))
                i = self.channel.expect([r"New password:", r"%s" % self.prompt], timeout=self.timeout)
                result = i[-1]
                if re.search('error|invalid', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                # Enter password
                self.channel.write("{password}\n".format(password=password))
                # check password
                i = self.channel.expect([r"Retype new password:", r"%s" % self.prompt], timeout=self.timeout)
                if i[0] == 0:
                    # repassword
                    self.channel.write("{password}\n".format(password=password))
                    # check password
                    i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
                    if i[0] == 0:
                        # Get result.
                        result = i[-1]
                        if re.search('error|invalid', result, flags=re.IGNORECASE):
                            raise ForwardError(result)
                        else:
                            # change password is successed.
                            data = self._commit()
                            # exit config terminal mode.
                            self._exitConfigMode()
                    elif i[0] == -1:
                        raise ForwardError('Error: receive timeout')
                elif i[0] == 1:
                    # password wrong
                    raise ForwardError(i[-1])
                elif i[0] == -1:
                    # timeout
                    raise ForwardError('Error: receive timeout')
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
                data['errLog'] = str(e)
                data['status'] = False
        return data

    # def bindBandwidth(self, ip='', bandwidth=''):
    #     njInfo = {"status": False,
    #               "content": "",
    #               "errLog": ""}
    #     mx960Bandwidth = Bandwidth(ip=ip, bandwidth=bandwidth, shell=self)
    #     njInfo = mx960Bandwidth.bindBandwidth()
    #     return njInfo
    #
    # def deleteBindIPAndBandwidth(self, ip='', bandwidth=''):
    #     njInfo = {"status": False,
    #               "content": "",
    #               "errLog": ""}
    #     mx960Bandwidth = Bandwidth(ip=ip, bandwidth=bandwidth, shell=self)
    #     njInfo = mx960Bandwidth.deleteBindIPAndBandwidth()
    #     return njInfo

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
[Core][forward] Base device class for sshv2 method, by using paramiko module.
"""

import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError


class BASELINUX(BASESSHV2):
    """This is a manufacturer of linux, using the
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
        return result

    def addUser(self, username, password, **kwargs):
        """Create a user on the device.
        """
        # Extra parameters
        group = kwargs['group'] if 'group' in kwargs else username
        commandAdduser = 'adduser %s' % username if group == username else 'adduser --gid %s %s' % (group, username)
        commandPw = 'passwd %s\n' % username

        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            # legal check
            if not group:
                raise ForwardError("[Add User Error]: %s: Group could NOT be blank." % self.ip)
            if not username or not password:
                raise ForwardError("[Add User Error]: %s: Username or Password could NOT be blank." % self.ip)

            if self.isLogin:
                # execute adduser
                addUserResult = self.execute(commandAdduser)
                if addUserResult['status']:
                    dirExtPattern = '(目录已经存在|home directory already exists)'

                    if not addUserResult['content']:
                        # success
                        pass
                    elif re.search(dirExtPattern, addUserResult['content']):
                        # success, but homedir already exist
                        pass
                    else:
                        # other errors
                        raise ForwardError("[Add User Error]: %s: %s" % (self.ip, addUserResult['content']))

                    # set passwd
                    self.shell.send(commandPw)
                    buff = ''
                    while not (re.search(self.basePrompt, buff) or re.search('New password:', buff)):
                        buff += self.shell.recv(256)
                    if re.search('New password:', buff):
                        # send password
                        self.shell.send(password + '\n')
                        buff = ''
                        while not (re.search(self.basePrompt, buff) or re.search('Retype new password:', buff)):
                            buff += self.shell.recv(256)
                        if re.search('Retype new password:', buff):
                            # Confirm password
                            self.shell.send(password + '\n')
                            buff = ''
                            while not re.search(self.prompt, buff):
                                buff += self.shell.recv(256)
                            # successed.
                            if re.search('updated successfully', buff):
                                result['status'] = True
                                return result

                    # error somewhere, raise
                    raise ForwardError("[Set Password Error]: %s: %s" % (self.ip, buff))
                else:
                    raise ForwardError("[Add User Error]: %s: %s" % (self.ip, addUserResult['errLog']))
            else:
                raise ForwardError("[Add User Error]: %s: Not login yet." % self.ip)
        except ForwardError, e:
            result['status'] = False
            result['errLog'] = str(e)
        return result

    def deleteUser(self, username):
        """Delete a user on the device
        """
        # set command
        commandDelUser = 'userdel %s' % username
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            if not username:
                raise ForwardError("[Delete User Error]: %s: Username could NOT be blank." % self.ip)
            # Login status check.
            if self.isLogin:
                # send command.
                delUserResult = self.execute(commandDelUser)
                if delUserResult['status']:
                    if not delUserResult['content']:
                        # success
                        pass
                    else:
                        # failed.
                        raise ForwardError("[Delete User Error]: %s: %s" % (self.ip, delUserResult['content']))
                    result['status'] = True
                    return result
                else:
                    raise ForwardError("[Delete User Error]: %s: %s" % (self.ip, delUserResult['errLog']))
            else:
                raise ForwardError("[Delete User Error]: %s: Not login yet." % self.ip)
        except ForwardError, e:
            result['status'] = False
            result['errLog'] = str(e)
        return result

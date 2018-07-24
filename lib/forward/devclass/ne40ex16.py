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
[Core][forward] Device class for ne40ex16.
"""
import re
from forward.devclass.baseHuawei import BASEHUAWEI
from forward.utils.sshv2 import sshv2


class NE40EX16(BASEHUAWEI):
    """This is a manufacturer of huawei, so it is integrated with BASEHUAWEI library.
    """

    def _commit(self):
        """Because the device of this model is different from the other
        huawei devices in commit  parameters, it is rewritten.
        """
        saveCommand = "save"
        # exitCommand = "return"
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            # Check the config mode status.
            if self.isConfigMode:
                self._exitConfigMode()
                # exit config mode
                self.shell.send('%s\n' % (saveCommand))
                # save setup to system
                while not re.search(self.prompt, data['content'].split('\n')[-1]):
                    data['content'] += self.shell.recv(1024)
                    # When prompted, reply Y,Search range at last line
                    if re.search(re.escape('Are you sure to continue?[Y/N]'), data['content'].split('\n')[-1]):
                        # interact,send y
                        self.shell.send("y\n")
                """
                If the program finds information like ‘success’, etc.
                in the received information, it indicates that the save configuration is successful.
                """
                if re.search(re.escape('Save the configuration successfully'), data['content'], flags=re.IGNORECASE):
                    data['status'] = True
            else:
                raise IOError('Error: The current state is not configuration mode')
        except Exception, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def login(self):
        """Because the device of this model is different from the other
        huawei devices in commit  parameters, it is rewritten.
        """
        njInfo = {"status": False,
                  "content": "",
                  "errLog": ""}
        # sshv2(ip,username,password,timeout,port=22)
        sshChannel = sshv2(self.ip, self.username, self.password, self.timeout, self.port)
        if sshChannel['status']:
            # Login succeed, init shell
            try:
                njInfo['status'] = True
                self.channel = sshChannel['content']
                # resize virtual console window size to 10000*10000
                self.shell = self.channel.invoke_shell(width=1000, height=1000)
                tmpBuffer = ''
                while not re.search(self.basePrompt, tmpBuffer.split('\n')[-1]):
                    tmpBuffer += self.shell.recv(1024)
                    # When prompted, reply N
                    if re.search('\[Y/N\]:', tmpBuffer):
                        self.shell.send('N\n')
                # set session timeout
                self.shell.settimeout(self.timeout)
                # Flag login status is True.
                self.isLogin = True
                # Get host prompt.
                self.getPrompt()
                njInfo["status"] = True
            except Exception as e:
                njInfo['status'] = False
                njInfo['errLog'] = str(e)
        else:
            # Login failed
            njInfo['errLog'] = sshChannel['errLog']
        return njInfo

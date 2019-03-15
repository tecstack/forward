# coding:utf-8
#
# This file is part of Forward.
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
[Core][forward] Device class for asa.
"""

import re
from forward.devclass.baseCisco import BASECISCO
from forward.utils.forwardError import ForwardError


class ASA(BASECISCO):
    """The device model belongs to the cisco series
    so the attributes and methods of BASECISCO are inherited.
    """
    def cleanBuffer(self):
        """Since the device is inconsistent with the details
        of the other Cisco series, the method needs to be rewritten
        to fit the device of this type.
        """
        if self.shell.recv_ready():
            self.shell.recv(4096).decode()
        self.shell.send('\r\n')
        buff = ''
        """ When after switching mode, the prompt will change,
        it should be based on basePromptto check and at last line"""
        while not re.search(self.basePrompt, buff.split('\n')[-1]):
            try:
                # Cumulative return result
                buff += self.shell.recv(1024).decode()
                # Remove the \x charactor
                buff += re.sub("\x07", "", buff)
            except Exception:
                raise ForwardError('Receive timeout [%s]' % (buff))

    def addUser(self, username, password):
        # Overriding methods
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} password {password}\n')

    def changePassword(self, username, password):
        # Overriding methods
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} password {password}\n')

    def basicInfo(self):
        njInfo = BASECISCO.basicInfo(self)
        cmd = "show version"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        tmp = self.privilegeMode()
        runningDate = -1
        if  tmp["status"]:
            result = self.command(cmd=cmd, prompt=prompt)
            if result["state"] == "success":
                dataLine = re.search(" up .*", result["content"])
                if dataLine is not None:
                    tmp = re.search("([0-9]+) years", dataLine.group())
                    if tmp:
                        runningDate += int(tmp.group(1) * 365)
                    tmp = re.search("([0-9]+) weeks", dataLine.group())
                    if tmp:
                        runningDate += int(tmp.group(1) * 7)
                    tmp = re.search("([0-9]+) day(s)?", dataLine.group())
                    if tmp:
                        runningDate += int(tmp.group(1))
                    # Weather running-time of the device is more than 7 days
                    if runningDate > 7:
                        njInfo["content"]["noRestart"]["status"] = True
                    elif runningDate == -1:
                        pass
                    else:
                        njInfo["content"]["noRestart"]["status"] = False
                    # Return detail to Forward.
                    njInfo["content"]["noRestart"]["content"] = dataLine.group().strip()
                else:
                    # Forward did't find the uptime of the device.
                    pass
        else:
            return tmp
        return njInfo

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
[Core][forward] Device class for n7018.
"""
import re
from forward.devclass.baseCisco import BASECISCO


class N7018(BASECISCO):
    """This is a manufacturer of cisco, so it is integrated with BASECISCO library.
    """

    def addUser(self, username, password, admin=False):
        """Because the device of this model is different from the other Cisco
        devices in creating user parameters, it is rewritten.
        """
        # default not is Admin
        if admin:
            return BASECISCO.addUser(self,
                                     username=username,
                                     password=password,
                                     addCommand='user {username} password {password} role network-admin\n')
        else:
            return BASECISCO.addUser(self,
                                     username=username,
                                     password=password,
                                     addCommand='user {username} password {password} role priv-1\n')

    def _commit(self):
        """Because the device of this model is different from the other
        Cisco devices in commit  parameters, it is rewritten.
        """
        return BASECISCO._commit(self,
                                 saveCommand='copy running-config startup-config',
                                 exitCommand='end')

    def changePassword(self, username, password):
        """Because the device of this model is different from the other
        Cisco devices in change user's password  parameters, it is rewritten.
        """
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='user {username} password {password} role network-admin\n')

    def basicInfo(self):
        njInfo = BASECISCO.basicInfo(self)
        cmd = "show system uptime"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        tmp = self.privilegeMode()
        if tmp["status"]:
            result = self.command(cmd=cmd, prompt=prompt)
            if result["state"] == "success":
                dataLine = re.search("System uptime: +([0-9]+) days", result["content"])
                if dataLine.lastindex == 1 and dataLine is not None:
                    # Get year,month and day of the uptime.
                    # Weather running-time of the device is more than 7 days
                    runningDate = int(dataLine.group(1))
                    if runningDate > 7:
                        njInfo["content"]["noRestart"]["status"] = True
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

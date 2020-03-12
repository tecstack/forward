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
[Core][forward] Device class for ce16808.
"""
from forward.devclass.baseHuawei import BASEHUAWEI
import re


class CE16808(BASEHUAWEI):
    """This is a manufacturer of huawei, so it is integrated with BASEHUAWEI library.
    """
    def showHostname(self):
        '''show hostname
        Return:
           device hostname
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        cmd = 'display current-configuration | include sysname'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status']:
            njInfo['errLog'] = result['errLog']
            return njInfo
        if result['state'] == 'success':
            njInfo['content'] = re.findall('sysname (\S+)', result['content'])[0]
            njInfo['status'] = True
            return njInfo
        njInfo['errLog'] = result['errLog']
        return njInfo

    def showNtp(self):
        # Gets the NTP server address of the device
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "dis current-configuration | i ntp"
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("ntp unicast-server ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"])
            if tmp:
                njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

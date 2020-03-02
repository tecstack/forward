# coding:utf-8
#
# This file is part of Forward
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
[Core][forward] Device class for APV 11600D.
"""

from forward.devclass.baseArray import BASEARRAY
import re


class APV11600(BASEARRAY):
    """The device model belongs to the BROCADE series
    so the attributes and methods of BASEBROCADE are inherited.
    """
    def showVersion(self):
        # cmd = 'show version'
        # ArrayOS Rel.APV.10.3.0.35 build on Tue Jul 16 03:29:46 2019 -> Rel.APV.10.3.0.35
        njInfo = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        prompt = {
            "success": "[\r\n]+\S+# ?$",
            "eror": "Bad command[\s\S]+"
        }
        result = self.command("show version", prompt=prompt)
        if result["state"] == "success":
            # ArrayOS Rel.APV.10.3.0.35 build on Tue Jul 16 03:29:46 2019 -> Rel.APV.10.3.0.35
            tmp = re.search("(Rel\S+)", result["content"])
            if tmp:
                njInfo["content"] = tmp.group(1)
            else:
                njInfo["errLog"] = "Version information was not available."
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showHostname(self):
        # cmd = 'show hostname'
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
        cmd = 'show hostname'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status']:
            njInfo['errLog'] = result['errLog']
            return njInfo
        if result['state'] == 'success':
            njInfo['content'] = result['content']
            njInfo['status'] = True
            return njInfo
        njInfo['errLog'] = result['errLog']
        return njInfo

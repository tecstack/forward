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
[Core][forward] Device class for zte,zhong-xing.
"""
from forward.devclass.baseSSHV2 import BASESSHV2
import re


class BASEZTE(BASESSHV2):
    """This is a manufacturer of zte, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def showVersion(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = "show version"
        prompt = {
            "success": "[vV]ersion[\s\S]+[\r\n]+\S+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("(software|system).*version ?:? ?(\S+)", result["content"], flags=re.IGNORECASE)
            if tmp.lastindex == 2:
                njInfo["content"] = tmp.group(2).strip(",")
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

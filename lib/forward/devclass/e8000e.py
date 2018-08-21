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
[Core][forward] Device class for E8000E.
"""
from forward.devclass.baseHuawei import BASEHUAWEI
import re


class E8000E(BASEHUAWEI):
    """This is a manufacturer of huawei, it is integrated with BASEHUAWEI library.
    """
    def showVlan(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "display  vlan"
        prompt = {
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            # When encountered '------' characters, start statistics.
            isBegin = False
            for _vlanInfo in result["content"].split("\r\n"):
                if re.search("\-\-\-\-\-\-\-", _vlanInfo):
                    isBegin = True
                    continue
                if isBegin is False:
                    continue
                """
                VLAN ID Type         Status   MAC Learning Broadcast/Multicast/Unicast Property
                --------------------------------------------------------------------------------
                12      common       enable   enable       forward   forward   forward default
                """
                # Get the line of vlan.
                tmp = re.search("([0-9]+)\s+(\S+)\s+(\S+)", _vlanInfo)
                if tmp:
                    lineInfo = {
                        "id": tmp.group(1),
                        "description": "",
                        "type": tmp.group(2),
                        "interface": [],
                        "status": tmp.group(3),
                    }
                    njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

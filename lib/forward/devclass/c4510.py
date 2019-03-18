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
[Core][forward] Device class for c4510.
"""

from forward.devclass.baseCisco import BASECISCO
import re


class C4510(BASECISCO):
    """This is a manufacturer of cisco, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def addUser(self, username, password):
        """Because the device of this model is different from the other Cisco
        devices in creating user parameters, it is rewritten.
        """
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} secret {password}\n')

    def changePassword(self, username, password):
        """Because the device of this model is different from the other
        Cisco devices in deleting user parameters, it is rewritten.
        """
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} secret {password}\n')

    def showInterface(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show interface"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        tmp = self.privilegeMode()
        if not tmp["status"]:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            i = 0
            for _interfaceInfo in re.findall(".*is[\s\S]+?swapped out", result["content"]):
                i += 1
                lineInfo = {"interfaceName": "",
                            "members": [],
                            "lineState": "",
                            "adminState": "",
                            "description": "",
                            "speed": "",
                            "type": "",
                            "duplex": "",
                            "inputRate": "",
                            "outputRate": "",
                            "crc": "",
                            "linkFlap": "",
                            "mtu": "",
                            }
                # Get name of the interface
                if i == 0:
                    _interfaceInfo = _interfaceInfo.split("\r\r\n")[1]
                    tmp = re.search("(.*) is", _interfaceInfo)
                    if tmp:
                        lineInfo["interfaceName"] = tmp.group(1).strip()
                        njInfo["content"].append(lineInfo)
                    continue
                else:
                    tmp = re.search("(.*?) is", _interfaceInfo)
                    if tmp:
                        lineInfo["interfaceName"] = tmp.group(1).strip()
                    else:
                        continue
                    tmp = re.search("admin state is (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["adminState"] = tmp.group(1).strip()
                    # MTU
                    tmp = re.search("MTU ([0-9]+)", _interfaceInfo)
                    if tmp:
                        lineInfo["mtu"] = tmp.group(1)
                    # description
                    tmp = re.search("Description: (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["description"] = tmp.group(1).strip()
                    # duplex
                    tmp = re.search("([a-z]+)\-duplex", _interfaceInfo)
                    if tmp:
                        lineInfo["duplex"] = tmp.group(1)
                    # Speed.
                    tmp = re.search("\-duplex, (.*),?", _interfaceInfo)
                    if tmp:
                        lineInfo["speed"] = tmp.group(1)
                    # ip.
                    tmp = re.search("Internet Address is (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["ip"] = tmp.group(1).split("/")[0]
                    # mac.
                    tmp = re.search(", address: ([\S]+)", _interfaceInfo)
                    if tmp:
                        lineInfo["mac"] = tmp.group(1)
                    # Last link flapped
                    tmp = re.search("Last link flapped (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["linkFlap"] = tmp.group(1).strip()
                    # Inpute rate.
                    tmp = re.search("300 seconds input rate (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["inputRate"] = tmp.group(1).strip()
                    # Output rate.
                    tmp = re.search("300 seconds ouput rate (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["outputRate"] = tmp.group(1).strip()

                    njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

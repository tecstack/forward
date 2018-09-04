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
[Core][forward] Device class for F5.
"""
from forward.devclass.baseSSHV2 import BASESSHV2
import re


class BASEF5(BASESSHV2):
    """This is a manufacturer of F5, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def showVersion(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = "tmsh  show /sys version"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "command not found[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("Version +([0-9\.]+)", result["content"])
            if tmp:
                njInfo["content"] = tmp.group(1)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showNtp(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "tmsh list /sys ntp"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "command not found[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"])
            njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showSnmp(self):
        # Get SNMP informatinos.
        njInfo = {
            "status": False,
            # [{"ip:"10.1.1.1","port":"456"}]
            "content": [],
            "errLog": ""
        }
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "command not found[\s\S]+",
        }
        cmd = "tmsh list /sys snmp"
        result = self.command(cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("host.*(\d+\.\d+\.\d+\.\d+)\r\n\s+(port \d+)?",
                             result["content"])
            """
            xxxx_1 {
            community xxxx_2015
            host 10.1.1.5
            prot 8888
            }
            yyyyy_1 {
            community yyyyy_2015
            host 10.1.1.1
            }
            """
            for line in tmp:
                ip, port = line
                port = re.sub("port ", "", port)
                njInfo["content"].append({"ip": ip, "port": port})
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showInterface(self):
        # Get the interface information
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "tmsh  list /net interface"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "command not found[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = re.findall("net[\s\S]+?\r\n\}", result["content"])
            for line in allLine:
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
                            "ip": ""}
                #  Get name of the interface.
                tmp = re.search("net interface (\S+)", line)
                if tmp:
                    lineInfo["interfaceName"] = tmp.group(1)
                # Get mtu of the interface.
                tmp = re.search("mtu (\d+)", line)
                if tmp:
                    lineInfo["mtu"] = tmp.group(1).strip()
                # Get mac of the interface.
                tmp = re.search("mac-address (.*)", line)
                if tmp:
                    lineInfo["mac"] = tmp.group(1).strip()
                # Get description of the interface.
                tmp = re.search("description (.*)", line)
                if tmp:
                    lineInfo["description"] = tmp.group(1).strip()
                njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showLog(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "tmsh list /sys syslog"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "command not found[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("host ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"])
            njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showRoute(self,):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "tmsh list /net route"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "command not found[\s\S]+",
        }
        # Get name of routes.
        result = self.command(cmd=cmd, prompt=prompt)
        """
        net route default_route {
            gw 10.1.1.1
                network default
                }
        """
        if result["state"] == "success":
            allLine = re.findall("net[\s\S]+?\r\n\}", result["content"])
            for section in allLine:
                lineInfo = {
                    "net": "",
                    "mask": "",
                    "metric": "",
                    "type": "",
                    "description": "",
                    "interface": "",
                    "via": ""}
                # Get via of the routing.
                tmp = re.search("gw (\d+\.\d+\.\d+\.\d+)", section)
                if tmp:
                    lineInfo["via"] = tmp.group(1)
                else:
                    continue
                # Get destination of the routing.
                tmp = re.search("network (.*)", section)
                if tmp:
                    # Intercept the prefix of the destination-network
                    lineInfo["net"] = re.search("(.*)/?", tmp.group(1)).group(1).strip()
                    # Intercept the sufix of the destination-network,but may be no sufix.
                    mask = re.search("/(\d+)", tmp.group(1))
                    if mask:
                        lineInfo["mask"] = mask.group(1)
                else:
                    continue
                # Get description of the routing.
                tmp = re.search("description(.*)", section)
                if tmp:
                    lineInfo["description"] = tmp.group(1).strip()
                njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showVlan(self,):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "tmsh list /net vlan"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "command not found[\s\S]+",
        }
        # Get name of routes.
        result = self.command(cmd=cmd, prompt=prompt)
        """
        net route default_route {
            gw 10.1.1.1
                network default
                }
        """
        if result["state"] == "success":
            allLine = re.findall("net [\s\S]+?\r\n\}", result["content"])
            for section in allLine:
                lineInfo = {"id": "",
                            "description": "",
                            "status": "",
                            "interface": [],
                            "type": ""}
                # Get id of the vlan.
                tmp = re.search("tag (\d+)", section)
                if tmp:
                    lineInfo["id"] = tmp.group(1)
                # Get interfaes of the vlan.
                tmp = re.search("interfaces \{([\s\S]+?)\}", section)
                if tmp:
                    lineInfo["interface"] = re.findall("[A-Za-z0-9\.\-]+", tmp.group(1))
                # Get description of the routing.
                tmp = re.search("description(.*)", section)
                if tmp:
                    lineInfo["description"] = tmp.group(1).strip()
                njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

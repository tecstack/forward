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
[Core][forward] Device class for fg3800.
"""
from forward.devclass.baseFortinet import BASEFORTINET
import re


class FG3800(BASEFORTINET):
    """This is a manufacturer of fortinet, so it is integrated with BASEFORTINET library.
    """
    def configMode(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = 'config global'
        prompt = {
            "success": "",
            "normal": "Unknown action[\s\S]+"
        }
        result = self.command(cmd, prompt=prompt)
        if not result["state"] is None:
            njInfo["status"] = True
            self.mode = 3
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showVersion(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = "get system  status"
        result = self.execute(cmd=cmd)
        if result["status"] is True:
            tmp = re.search("Version:.*v(.*)", result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp.group(1).strip()
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showHostname(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = "get system  status"
        result = self.execute(cmd=cmd)
        if result["status"] is True:
            tmp = re.search("Hostname:(.*)", result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp.group(1).strip()
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showNtp(self):
        if self.mode != 3:
            self.configMode()
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = 'diagnose sys ntp status'
        prompt = {
            "success": "HA master[\s\S]+",
            "error": "Unknown action[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            p1 = re.compile(r'ipv4 server[(](.*?)[)]', re.S)
            tmp = re.findall(p1, result["content"])
            if tmp:
                njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showInterface(self):
        if self.mode != 3:
            self.configMode()
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show full-configuration system interface"
        prompt = {
            "success": "[\r\n]+\S+(#|>) ?$",
            "error": "Unknown action[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            interfacesFullInfo = re.split("next", result["content"])
            for _interfaceInfo in interfacesFullInfo:
                lineInfo = {"members": [],
                            "interfaceState": "",
                            "interfaceName": "",
                            "speed": "",
                            "type": "",
                            "inputRate": "",
                            "outputRate": "",
                            "ip": "",
                            "lineState": "",
                            "adminState": "",
                            "mtu": "",
                            "duplex": "",
                            "description": "",
                            "crc": ""}
                # Get name of the interface.
                tmp = re.search('edit "(.+)"', _interfaceInfo)
                if tmp:
                    lineInfo['interfaceName'] = tmp.group(1)
                else:
                    continue
                # Only interface information is obtained here, not vlan information
                if re.search("vlan", lineInfo['interfaceName']):
                    continue
                tmp = re.search("set description(.*)", _interfaceInfo)
                if tmp:
                    lineInfo["description"] = tmp.group(1).strip().strip('"\'')
                njInfo["content"].append(lineInfo)
            # Get the details through the physical interface name
            detail = self.command(cmd="get system  interface  physical", prompt=prompt)
            """
            ==[npu1-vlink0]
                mode: static
                ip: 0.0.0.0 0.0.0.0
                ipv6: ::/0
                status: down
                speed: n/a
            ==[npu1-vlink1]
                mode: static
                ip: 0.0.0.0 0.0.0.0
                ipv6: ::/0
                status: down
                speed: n/a
            """
            if detail["state"] == "success":
                interfacesFullInfo = re.split("==", detail["content"])
                for _interfaceInfo in interfacesFullInfo:
                    data = {"ip": "",
                            "type": "",
                            "interfaceState": "",
                            "speed": "",
                            "duplex": ""}
                    tmp = re.search("(\[\S+\])", _interfaceInfo)
                    if tmp:
                        _interfaceName = tmp.group(1).strip("[]")
                        # Get ip
                        tmp = re.search("ip: (\S*)", _interfaceInfo)
                        if tmp:
                            data["ip"] = tmp.group(1)
                        # Get type
                        tmp = re.search("mode: (\S*)", _interfaceInfo)
                        if tmp:
                            data["type"] = tmp.group(1)
                        # Get status
                        tmp = re.search("status: (\S*)", _interfaceInfo)
                        if tmp:
                            data["interfaceState"] = tmp.group(1)
                        # Get speed
                        tmp = re.search("speed: (\S*)", _interfaceInfo)
                        if tmp:
                            data["speed"] = tmp.group(1)
                        # Get duplex
                        tmp = re.search("Duplex: ([A-Za-z]+)", _interfaceInfo)
                        if tmp:
                            data["duplex"] = tmp.group(1)
                        # Update data
                        index = 0
                        for _line in njInfo["content"]:
                            if _interfaceName == _line["interfaceName"]:
                                njInfo["content"][index].update(**data)
                            index += 1
                    else:
                        continue
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showLog(self):
        if self.mode != 3:
            self.configMode()
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        """
        Since the syslog information needs to be obtained according to the
        configuration name of the syslog on the device of this model,
        the name of the syslog needs to be trained until the configuration does not exist.
        For example:
        syslog
        syslog2
        syslog3
        """
        prompt = {
            "success": "end[\r\n]+\S+(#|>) ?$",
            "error": "Return code \-61[\s\S]+",
        }
        i = 0
        while True:
            i += 1
            if i == 1:
                cmd = "show full-configuration  log syslogd setting"
            else:
                cmd = "show full-configuration  log syslogd{i} setting".format(i=i)
            result = self.command(cmd=cmd, prompt=prompt)
            if result["state"] == "success":
                tmp = re.search('set server "([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"',
                                result["content"])
                if tmp:
                    njInfo["content"].append(tmp.group(1))
                njInfo["status"] = True
            else:
                # Exit if the configuration does not exist
                njInfo["errLog"] = result["errLog"]
                break
        return njInfo

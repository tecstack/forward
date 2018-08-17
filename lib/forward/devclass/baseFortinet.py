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
[Core][forward] Device class for Fortinet.
"""
from forward.devclass.baseSSHV2 import BASESSHV2
import re


def exchange_int_to_mask(mask_int):
    bin_arr = ['0' for i in range(32)]
    for i in range(mask_int):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)


class BASEFORTINET(BASESSHV2):
    """This is a manufacturer of foritinet, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """

    def privilegeMode(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = '''end'''
        prompt = {
            "success": "end\r\r\n\r\n\S+.+(#|>) ?$",
            "normal": "Unknown action[\s\S]+",
        }
        result = self.command(cmd, prompt=prompt)
        if not result["state"] is None:
            njInfo["status"] = True
            self.mode = 2
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def configMode(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = '''end'''
        prompt = {
            "success": "end\r\r\n\r\n\S+.+(#|>) ?$",
            "normal": "Unknown action[\s\S]+",
        }
        result = self.command(cmd, prompt=prompt)
        if not result["state"] is None:
            njInfo["status"] = True
            self.mode = 3
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def commit(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = '''end'''
        prompt = {
            "success": "end\r\r\n\r\n\S+.+(#|>) ?$",
            "normal": "Unknown action[\s\S]+",
        }
        result = self.command(cmd, prompt=prompt)
        if not result["state"] is None:
            njInfo["status"] = True
            self.mode = 2
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showNtp(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = '''show full-configuration  system ntp'''
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unknown action[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall('set server "([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"',
                             result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showSnmp(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = '''show full-configuration  system  snmp community'''
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unknown action[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall('set ip ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',
                             result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showInterface(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show full-configuration  system interface"
        prompt = {
            "success": "[\r\n]+\S+.*(#|>) ?$",
            "error": "Unrecognized[\s\S]+",
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

    def showVlan(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show full-configuration  system interface"
        prompt = {
            "success": "[\r\n]+\S+.*(#|>) ?$",
            "error": "Unrecognized[\s\S]",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            interfacesFullInfo = re.split("next", result["content"])
            for _interfaceInfo in interfacesFullInfo:
                lineInfo = {"id": "",
                            "description": "",
                            "status": "",
                            "interface": [],
                            "type": ""}
                # Get name of the interface.
                tmp = re.search('set vlanid (\d+)', _interfaceInfo)
                if tmp:
                    lineInfo['id'] = tmp.group(1)
                else:
                    # Only Vlan information is obtained here, not vlan information
                    continue
                # Get description.
                tmp = re.search("set description(.*)", _interfaceInfo)
                if tmp:
                    lineInfo["description"] = tmp.group(1).strip().strip('"\'')
                # Get status.
                tmp = re.search("set status (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["status"] = tmp.group(1).strip().strip('"\'')
                # Get interface.
                tmp = re.search('set interface "(.*)"', _interfaceInfo)
                if tmp:
                    lineInfo["interface"] = re.split(",| ", tmp.group(1).strip('"'))
                # Get type.
                tmp = re.search('set mode ([A-Za-z]+)', _interfaceInfo)
                if tmp:
                    lineInfo["type"] = tmp.group(1).strip()
                njInfo["content"].append(lineInfo)
            njInfo["status"] = True
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
        prompt = {
            "success": "Release[\s\S]+[\r\n]+\S+.+(#|>) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("Version:.*v(.*)", result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp.group(1).strip()
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showRoute(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "get router  info routing-table  all"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unrecognized[\s\S]+[\r\n]+[\S]+.+(#|>) ?$",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            interfacesFullInfo = re.split("[\r\n]+", result["content"])
            for _interfaceInfo in interfacesFullInfo:
                lineInfo = {"net": "",
                            "mask": "",
                            "metric": "",
                            "description": "",
                            "type": "",
                            "interface": "",
                            "via": ""}
                tmp = re.search("(\S)\s+", _interfaceInfo)
                # Get type of routing.
                if tmp:
                    """
                    S       1.1.1.0/24 [10/0] via 100.11.1.97, inter-vlanxxxx
                    S       1.1.2.0/24 [10/0] via 100.11.1.113, inter-vlanyyyy
                    S       1.1.4.0/24 [10/0] via 100.11.1.129, inter-vlanzzzz
                    """
                    _type = tmp.group(1)
                    if _type == "S":
                        lineInfo["type"] = "static"
                    elif _type == "C":
                        lineInfo["type"] = "direct"
                    elif _type == "O":
                        lineInfo["type"] = "ospf"
                    elif _type == "R":
                        lineInfo["type"] = "rip"
                    elif _type == "B":
                        lineInfo["type"] = "bgp"
                    else:
                        lineInfo["type"] = "unkown"
                    # Get net,mask and interface of routing.
                    tmp = re.search("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d{1,2})", _interfaceInfo)
                    if tmp:
                        dataLine = _interfaceInfo.split()
                        lineInfo["net"] = tmp.group(1)
                        lineInfo["mask"] = tmp.group(2)
                        lineInfo["interface"] = dataLine[-1]
                        if lineInfo["type"] == "static":
                            lineInfo["via"] = dataLine[4].strip(",")
                    else:
                        continue
                    # Saving above data.
                    njInfo["content"].append(lineInfo)
                    continue
                elif re.search("^\s+\[\d+/\d+\]", _interfaceInfo):
                    """
                    S       1.3.3.0/24 [10/0] via 192.168.19.129, inter-vlanyyyy
                    S       1.1.1.4/32 [10/0] via 192.168.93.41, inter-vlanxxxx
                                          [10/0] via 192.168.199.1, mgxxx   <------ Get this line
                    """
                    # Get net and mask from njInfo["content"],then added new via and interface of routing to list.
                    lineInfo = njInfo["content"][-1]
                    dataLine = _interfaceInfo.split()
                    lineInfo["via"] = dataLine[2]
                    lineInfo["interface"] = dataLine[3]
                    njInfo["content"].append(lineInfo)
            # Get description of routing for static routing only.
            detail = self.command("show router static", prompt=prompt)
            if detail["state"] == "success":
                index = 0
                for line in njInfo["content"]:
                    # Get original net and mask from njInfo.
                    net = line["net"]
                    mask = int(line["mask"])
                    # Only static routing.
                    if not line["type"] == "static":
                        continue
                    for config in detail["content"].split("next"):
                        # Match the description.
                        reg = "set comment(.*)[\r\n]+.*[\r\n]+\s+set dst %s %s" % (net, exchange_int_to_mask(mask))
                        tmp = re.search(reg, config)
                        if tmp:
                            # Get description.
                            njInfo["content"][index]["description"] = tmp.group(1).strip().strip('"\'')
                    index += 1
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

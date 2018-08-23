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
[Core][forward] Device class for Maipu.
"""
from forward.devclass.baseSSHV1 import BASESSHV1
import re


class BASEMAIPU(BASESSHV1):
    """This is a manufacturer of maipu, using the
    SSHV1 version of the protocol, so it is integrated with BASESSHV1 library.
    """
    def __init__(self, *args, **kws):
        """Since the device's host prompt is different from BASESSHV1,
        the basic prompt for the device is overwritten here.
        """
        BASESSHV1.__init__(self, *args, **kws)
        self.moreFlag = re.escape('....press ENTER to next \
line, Q to quit, other key to next page....')

    def privilegeMode(self):
        # Switch to privilege mode.
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Get the current position Before switch to privileged mode.
        # Demotion,If device currently mode-level greater than 2, It only need to execute `end`.
        if self.mode > 2:
            exitResult = self.command("end", prompt={"success": "[\r\n]+\S+.+# ?$",
                                                     "eror": "Unrecognized[\s\S]+"})
            if not exitResult["state"] == "success":
                result["errLog"] = "Demoted from configuration-mode to privilege-mode failed."
                return result
            else:
                # Switch is successful.
                self.mode = 2
                result["status"] = True
                return result
        elif self.mode == 2:
            # The device is currently in privilege-mode ,so there is no required to switch.
            result["status"] = True
            return result
        # else, command line of the device is in general-mode.
        # Start switching to privilege-mode.
        sendEnable = self.command("enable", prompt={"password": "[pP]assword.*", "noPassword": "[\r\n]+\S+# ?$"})
        if sendEnable["state"] == "noPassword":
            # The device not required a password,thus switch is successful.
            result["status"] = True
            self.mode = 2
            return result
        elif sendEnable["state"] is None:
            result["errLog"] = "Unknow error."
            return result
        # If device required a password,then send a password to device.
        sendPassword = self.command(self.privilegePw, prompt={"password": "[pP]assword.*",
                                                              "noPassword": "[\r\n]+\S+# ?$"})
        if sendPassword["state"] == "password":
            # Password error,switch is failed.
            result["errLog"] = "Password of the privilege mode is wrong."
            return result
        elif sendPassword["state"] == "noPassword":
            # switch is successful.
            result["status"] = True
            self.mode = 2
            return result
        else:
            result["errLog"] = "Unknown error."
            return result

    def configMode(self):
        # Switch to config mode.
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Program need to go from privileged mode to configuration mode anyway,Becauseof
        # you might be in interface mode, but you don't have a marks value of the mode
        _result = self.privilegeMode()
        if _result["status"] is False:
            # "enter to privilege-mode failed."
            result["status"] = False
            return result
        else:
            # If value of the mode is 2,start switching to configure-mode.
            sendConfig = self.command("config term", prompt={"success": "[\r\n]+\S+.+\(config\)# ?$",
                                                             "error": "Unrecognized[\s\S]+"})
            if sendConfig["state"] == "success":
                # switch to config-mode was successful.
                result["status"] = True
                self.mode = 3
                return result
            else:
                result["errLog"] = sendConfig["errLog"]
                return result

    def commit(self):
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Switch to privilege-mode.
        result = self.privilegeMode()
        if not result["status"]:
            # Switch failure.
            return result
        prompt = {
            "success": "are you sure\(y/n\)\? \[n\]",
            "error": "Unrecognized[\s\S]+",
        }
        # Excute a command.
        data = self.command("write running-config startup-config", prompt=prompt)
        if data["state"] == "success":
            data = self.command("y", prompt={"success": "successfully[\s\S]+[\r\n]+\S+.+(#|>) ?$",
                                             "error": "Unrecognized[\s\S]+"})
            if data["state"] == "success":
                result["content"] = "The configuration was saved successfully.[%s]" % data["content"]
                result["status"] = True
            else:
                result["errLog"] = "Failed save configuration, \
                                   Info: [{content}] , [{errLog}]".format(content=data["content"],
                                                                          errLog=data["errLog"])

        else:
            result["errLog"] = "Failed save configuration, \
                               Info: [{content}] , [{errLog}]".format(content=data["content"], errLog=data["errLog"])
        return result

    def showVersion(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = "show version"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("Software Version(.*)", result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp.group(1).strip()
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
        cmd = "show vlan"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = re.split("show VLAN information", result["content"])
            for line in allLine:
                lineInfo = {"id": "",
                            "description": "",
                            "status": "",
                            "interface": [],
                            "type": "",
                            "state": ""}
                # Get id of the vlan.
                tmp = re.search("VLAN ID                : (\d+)", line)
                if tmp:
                    lineInfo["id"] = tmp.group(1)
                else:
                    continue
                # Get stats of the vlan.
                tmp = re.search("VLAN status            : ([a-zA-Z]+)", line)
                if tmp:
                    lineInfo["status"] = tmp.group(1)
                # Get interfaces of the vlan.
                tmp = re.search("VLAN member            : (\S+)", line)
                if tmp:
                    # Separate each set of ports with a `,`
                    _interfaces = tmp.group(1).strip(".").split(",")
                    for tmpInterface in _interfaces:
                        _interface = tmpInterface.split("-")
                        # ['e0/1/2','e0/1/7']
                        if len(_interface) == 1:
                            # e0/1/2 --> 2 --> 3
                            tmp = int(_interface[0].split("/")[-1]) + 1
                            # e0/1/2 --> e0/1/3
                            tmp = "/".join(_interface[0].split("/")[0:-1]) + "/" + str(tmp)
                            # ['e0/1/2'] -- >['e0/1/2','e0/1/3']
                            _interface.append(tmp)
                        else:
                            # e0/1/2 --> 2 --> 3
                            tmp = int(_interface[-1].split("/")[-1]) + 1
                            # e0/1/2 --> e0/1/3
                            tmp = "/".join(_interface[0].split("/")[0:-1]) + "/" + str(tmp)
                            # ['e0/1/2','e0/1/3'] -- >['e0/1/2','e0/1/4']
                            _interface[-1] = tmp
                        # Intercepts the prefix symbol of the port and generates the completed port range
                        interfacePrefix = "/".join(_interface[0].split("/")[:-1])
                        portRange = [int(p.split("/")[-1]) for p in _interface]
                        for i in range(*portRange):
                            tmp = interfacePrefix + "/" + str(i)
                            lineInfo["interface"].append(tmp)
                njInfo["content"].append(lineInfo)
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
        result = self.command("show run snmp", prompt={"success": "[\r\n]+\S+.+(#|>) ?$",
                                                                  "eror": "Unrecognized[\s\S]+"})
        if result["state"] == "success":
            tmp = re.findall("snmp-server host (\d+\.\d+\.\d+\.\d+).*?udp-port (\d+)",
                             result["content"], flags=re.DOTALL)
            """
            snmp-server host ip1 version 2c xxx udp-port 612 notify-ty
            snmp-server host ip2 version 2c xxx udp-port 621 notify-ty
            """
            if tmp.__len__() > 0:
                njInfo["content"] = [{"ip": group[0], "port": group[-1]} for group in tmp]
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
        cmd = "show ip route"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _interfaceInfo in result["content"].split("\r\n"):
                # record the route table.
                if re.search("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]{1,2}", _interfaceInfo):
                    lineInfo = {
                        "net": "",
                        "mask": "",
                        "via": "",
                        "metric": "",
                        "type": "",
                        "via": "",
                    }
                    # Get net of the routing.
                    lineInfo["net"] = _interfaceInfo.split("/")[0]
                    # Get mask of net of the route.
                    lineInfo["mask"] = _interfaceInfo.split()[0].split("/")[-1]
                    lineInfo["via"] = _interfaceInfo.split()[1]
                    lineInfo["interface"] = re.search("[a-zA-z]+.*", _interfaceInfo.split()[-3]).group()
                    lineInfo["metric"] = re.search("\d+", _interfaceInfo.split()[-2]).group()
                    njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showLog(self):
        # Get syslog's servers informatinos.
        njInfo = {
            "status": False,
            "content": [],
            "errLog": ""
        }
        result = self.command("show run syslog", prompt={"success": "[\r\n]+\S+.+(#|>) ?$",
                                                         "eror": "Unrecognized[\s\S]+"})
        if result["state"] == "success":
            tmp = re.findall("logging (\d+\.\d+\.\d+\.\d+)",
                             result["content"])
            if tmp.__len__() > 0:
                njInfo["content"] = tmp
                njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showInterface(self):
        # Get the interfaces information
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show interface"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = re.findall(".*current state[\s\S]+?unicasts", result["content"])
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
                tmp = re.search("(.*)current state", line)
                if tmp:
                    lineInfo["interfaceName"] = tmp.group(1).strip()
                # Get line state of the interface.
                tmp = re.search("port link is (.*)", line)
                if tmp:
                    lineInfo["lineState"] = tmp.group(1).strip()
                # Get the admin state of the interface.
                tmp = re.search("current state:(.*),", line)
                if tmp:
                    lineInfo["adminState"] = tmp.group(1).strip()
                # Get mac of the interface.
                tmp = re.search("Hardware address is (.*)", line)
                if tmp:
                    lineInfo["mac"] = tmp.group(1).strip()
                # Get the type of the interface.
                tmp = re.search("Current port type: (\S+)", line)
                if tmp:
                    lineInfo["type"] = tmp.group(1).strip()
                # Get the speed of the interface.
                tmp = re.search("ActualSpeed is (\S+),", line)
                if tmp:
                    lineInfo["speed"] = tmp.group(1)
                # Get duplex of the interface.
                tmp = re.search("Duplex mode is (\S+)", line)
                if tmp:
                    lineInfo['duplex'] = tmp.group(1).strip()
                # Get input rate of the interface.
                tmp = re.search("Input  : (.*)", line)
                if tmp:
                    lineInfo["inputRate"] = tmp.group(1).strip()
                #  Get output rate of the interface.
                tmp = re.search("Output : (.*)", line)
                if tmp:
                    lineInfo["outputRate"] = tmp.group(1).strip()
                njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showNtp(self):
        # Gets the NTP server address of the device
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show running-config   | include  ntp"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("ntp server.*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"])
            njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

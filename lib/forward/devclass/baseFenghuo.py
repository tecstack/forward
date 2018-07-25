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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.n

"""
-----Introduction-----
[Core][forward] Device class for Fenghuo.
"""
import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError


class BASEFENGHUO(BASESSHV2):
    """This is a manufacturer of fenghuo, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def commit(self):
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Switch to privilege-mode.
        tmp = self.privilegeMode()
        if not tmp["status"]:
            # Switch failure.
            return tmp
        # Excute a command.
        tmp = self.command("write file",
                           prompt={"success": "Are you sure\?\(y/n\) \[y\] ?$",
                                   "error": "Unknown command[\s\S]+"})
        if tmp["state"] == "success":
            continueCommandResult = self.command("y", prompt={"success": "\[OK\][\s\S]+[\r\n]+\S+# ?$"})
            if continueCommandResult["state"] == "success":
                # Successfully.
                result["status"] = True
            else:
                # Failed.
                result["errLog"] = "Failed save configuration,\
                                   relate-information: [{content}]".format(content=continueCommandResult["content"])
                result["status"] = False
        elif tmp["state"] == "error":
            result["errLog"] = "The command failed to execute.info: [{content}]".format(content=tmp["content"])
        else:
            result["errLog"] = "Failed save configuration, \
                               Info: [{content}] , [{errLog}]".format(content=tmp["content"], errLog=tmp["errLog"])
            result["content"] = "The configuration was saved successfully."
            result["status"] = True
        return result

    def configMode(self):
        # Switch to privilege mode.
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
            return _result
        else:
            # If value of the mode is 2,start switching to configure-mode.
            sendConfig = self.command("config", prompt={"success": "[\r\n]+\S+\(config\)# ?$"})
            if sendConfig["state"] == "success":
                # switch to config-mode was successful.
                result["status"] = True
                self.mode = 3
                return result
            elif sendConfig["state"] is None:
                result["errLog"] = sendConfig["errLog"]
                return result

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
            exitResult = self.command("end", prompt={"success": "[\r\n]+\S+# ?$"})
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

    def showNtp(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show running-config  include  substring   ntp"
        prompt = {
            "success": "ntp[\s\S]+[\r\n]+\S+(#|>|\]|\$) ?$",
            "error": "Unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("unicast-server ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", result["content"])
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
        cmd = "show running-config  include  substring   snmp"
        prompt = {
            "success": "trap-server[\s\S]+[\r\n]+\S+(#|>|\]|\$) ?$",
            "error": "Unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("trap-server ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", result["content"])
            if tmp:
                njInfo["content"] = tmp
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
        cmd = "show version"
        prompt = {
            "success": "[sS]oftware[\s\S]+[\r\n]+\S+(#|>|\]|\$) ?$",
            "error": "Unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("software.*version(.*)", result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp.group(1).strip()
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
        cmd = "show running-config  include  substring  syslog"
        prompt = {
            "success": "syslog server[\s\S]+[\r\n]+\S+(#|>|\]|\$) ?$",
            "error": "Unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("syslog server ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp
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
            "success": "vlans is[\s\S]+[\r\n]+\S+(#|>|\]|\$) ?$",
            "error": "Unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = result["content"].split("\r\n")
            i = 0
            for _vlanInfo in allLine:
                _vlanInfo = _vlanInfo.strip()
                if re.search("^VID", _vlanInfo):
                    # Get the line of vlan.
                    lineInfo = {
                        "id": "",
                        "description": "",
                        "status": "",
                        "interface": [],
                        "type": "",
                    }
                    # Split the interface-line
                    for _interface in _vlanInfo.split()[1:]:
                        # VID   ge-1/0/1-ge-1/0/48   xge-1/1/1-xge-1/1/2  xge-1/2/1-xge-1/2/2
                        interfaceGroup = re.findall("[a-z]+\-[0-9]+/[0-9]+/[0-9]+", _interface)
                        interfaceProfix = re.search("([a-z]+\-[0-9]+/[0-9]+)/[0-9]+\-", _interface).group(1)
                        startNum = int(re.search("([0-9]+)$", interfaceGroup[0]).group(1))
                        endNum = int(re.search("([0-9]+)$", interfaceGroup[1]).group(1)) + 1
                        for realInterface in range(startNum, endNum):
                            realInterface = "{interfaceProfix}/{realInterface}".format(interfaceProfix=interfaceProfix,
                                                                                       realInterface=realInterface)
                            lineInfo["interface"].append(realInterface)
                    lineInfo["id"] = allLine[i + 1].split()[0].strip()
                    njInfo["content"].append(lineInfo)

                i += 1
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
        cmd = "show ip route"
        prompt = {
            "success": "Gateway[\s\S]+[\r\n]+\S+(#|>|\]|\$) ?$",
            "error": "Unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _interfaceInfo in result["content"].split("\r\n"):
                if re.search("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]{1,2}", _interfaceInfo):
                    lineInfo = {
                        "net": "",
                        "mask": "",
                        "metric": "",
                        "via": [],
                    }
                    tmp = re.search("([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/([0-9]{1,2})\s+\
                                     ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+([0-9]+/[0-9]+)\s+\
                                     (\S+)\s+(\S+)", _interfaceInfo)
                    if tmp:
                        lineInfo["net"] = tmp.group(1)
                        lineInfo["mask"] = tmp.group(2)
                        lineInfo["via"] = {"via": tmp.group(3)},
                        lineInfo["metric"] = tmp.group(4)
                        lineInfo["interface"] = tmp.group(5)
                        lineInfo["type"] = tmp.group(6)
                        njInfo["content"].append(lineInfo)
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
        cmd = "show interface"
        prompt = {
            "success": "up/down[\s\S]+[\r\n]+\S+(#|>|\]|\$) ?$",
            "error": "Unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _interfaceInfo in result["content"].split("\r\n"):
                lineInfo = {"members": [],
                            "lineState": "",
                            "speed": "",
                            "type": "",
                            "inputRate": "",
                            "outputRate": "",
                            "crc": "",
                            }
                # Get name of the interface
                tmp = re.search("([a-z]+\-[0-9]+/[0-9]+/[0-9]+)", _interfaceInfo)
                if tmp:
                    lineInfo["interfaceName"] = tmp.group(1)
                else:
                    # it is not interface
                    continue
                # Get state of the interface.
                lineInfo["interfaceState"] = re.search("(up|down)/(up|down)", _interfaceInfo).group()
                # Get description of the interface.
                lineInfo["description"] = _interfaceInfo.split()[-1].strip()
                njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def isVlan(self, vlan):
        """Check if the Vlan exists.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # swith to config mode
        # info = self._configMode()
        # if not info["status"]:
        #    raise ForwardError(info["errLog"])
        # switch to enable mode.
        tmp = self.privilegeMode()
        if not tmp:
            raise ForwardError(tmp["errLog"])
        while True:
            # Send command.
            tmp = self.execute("show vlan {vlan} verbose".format(vlan=vlan))
            if not tmp["status"]:
                raise ForwardError(tmp["errLog"])
            if re.search("VLAN ID:{vlan}".format(vlan=vlan), tmp["content"]):
                # vlan is exists
                info["status"] = True
                break
            elif re.search("Command is in use by", tmp["content"]):
                # check failed,recheck
                print 'Rechecking vlan...'
                continue
            else:
                # vlan not is exitsts
                info["status"] = False
                info["errLog"] = tmp["content"]
                break
        return info

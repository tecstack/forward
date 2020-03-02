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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.n

"""
-----Introduction-----
[Core][forward] Device class for Fenghuo.
"""
import re
from forward.devclass.baseSSHV2 import BASESSHV2
# from forward.utils.forwardError import ForwardError


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
        if self.mode >= 2:
            exitResult = self.command("end", prompt={"success": "[\r\n]+\S+# ?$"})
            if not exitResult["state"] == "success":
                result["errLog"] = "Demoted from configuration-mode to privilege-mode failed."
                return result
            else:
                # Switch is successful.
                self.mode = 2
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
            "success": "[\r\n]+\S+(#|>|\]|\$) ?$",
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
            "success": "[\r\n]+\S+(#|>|\]) ?$",
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
            "success": "[\r\n]+\S+(#|>|\]|\$) ?$",
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
        cmd = "show vlan all"
        prompt = {
            "success": "[\r\n]+\S+(#|>|\]|\$) ?$",
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
            "success": "[\r\n]+\S+(#|>|\]|\$) ?$",
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
                        "type": "",
                        "description": "",
                        "interface": "",
                        "via": "",
                    }
                    tmp = re.search("([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/([0-9]{1,2})\s+\
                    ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+([0-9]+/[0-9]+)\s+\
                    (\S+)\s+(\S+)", _interfaceInfo)
                    if tmp:
                        lineInfo["net"] = tmp.group(1)
                        lineInfo["mask"] = tmp.group(2)
                        lineInfo["via"] = tmp.group(3)
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
            "success": "[\r\n]+\S+(#|>|\]|\$) ?$",
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

    def vlanExist(self, vlan_id):
        # Check if the vlan exists.
        result = {
            "status": False,
            "content": {},
            "errLog": ""
        }
        vlan_id = str(vlan_id)
        vlan_list = self.showVlan()
        # check
        if not vlan_list["status"]:
            return vlan_list
        for line in vlan_list["content"]:
            if vlan_id == line["id"]:
                result["status"] = True
                return result
        result["errLog"] = "Vlan {vlan_id} does not exist.".format(vlan_id=vlan_id)
        return result

    def createVlan(self, vlan_id, name=None):
        """
        @param vlan_id: vlan-id,
        @param name: name of vlan.

        """
        # Crate vlan.
        result = {
            "status": False,
            "content": {},
            "errLog": ""
        }
        vlan_id = str(vlan_id)
        # Enter config-mode.
        tmp = self.configMode()
        if not tmp["status"]:
            # Failed to enter configuration mode
            return tmp
        if name is None:
            # no name.
            cmd = "vlan {vlan_id}".format(vlan_id=vlan_id)
        else:
            cmd = "vlan {vlan_id}\rname {name}".format(vlan_id=vlan_id, name=name)
        prompt = {
            "success": "[\r\n]+\S+\(vlan\-{vlan_id}\)# ?$".format(vlan_id=vlan_id),
            "error": "[\r\n]+(Invalid|Error)[\s\S]+",
        }
        tmp = self.command(cmd, prompt=prompt)
        if tmp["state"] == "success" and not re.search(prompt["error"], tmp["content"]):
            # The vlan was created successfuly, then to save configration if save is True.
            result["content"] = "The vlan {vlan_id} was created.".format(vlan_id=vlan_id)
            result["status"] = True
            return result
        else:
            self.deleteVlan(vlan_id)
            result["errLog"] = tmp["content"]
            return result

    def deleteVlan(self, vlan_id):
        # Delete vlan.
        result = {
            "status": False,
            "content": {},
            "errLog": ""
        }
        # Enter config-mode.
        tmp = self.configMode()
        if not tmp["status"]:
            # Failed to enter configuration mode
            return tmp
        cmd = "no vlan {vlan_id}".format(vlan_id=vlan_id)
        prompt = {
            "success": "[\r\n]+\S+config\)(#|>) ?$",
        }
        tmp = self.command(cmd, prompt=prompt)
        if not self.vlanExist(vlan_id)["status"]:
            # The vlan was deleted successfuly, then to save configration if save is True.
            result["content"] = "The vlan {vlan_id} was deleted.".format(vlan_id=vlan_id)
            result["status"] = True
            return result
        else:
            result["errLog"] = "The vlan {vlan_id} was not deleted.".format(vlan_id=vlan_id)
            return result

    def basicInfo(self, cmd="show version"):
        njInfo = {"status": True,
                  "content": {"noRestart": {"status": None, "content": ""},
                              "systemTime": {"status": None, "content": ""},
                              "cpuLow": {"status": None, "content": ""},
                              "memLow": {"status": None, "content": ""},
                              "boardCard": {"status": None, "content": ""},
                              "tempLow": {"status": None, "content": ""},
                              "firewallConnection": {"status": None, "content": ""}},
                  "errLog": ""}
        prompt = {"success": "[\r\n]+\S+(>|\]|#) ?$",
                  "error": "([Uu]nknown command|Unrecognized command|Invalid command)[\s\S]+"}
        tmp = self.privilegeMode()
        runningDate = -1
        if tmp["status"]:
            result = self.command(cmd=cmd, prompt=prompt)
            if result["state"] == "success":
                dataLine = re.search(" [Uu]ptime:? .+(day|year|week).*", result["content"])
                if dataLine is not None:
                    tmp = re.search("([0-9]+) year", dataLine.group())
                    if tmp:
                        runningDate += int(tmp.group(1)) * 365
                    tmp = re.search("([0-9]+) week", dataLine.group())
                    if tmp:
                        runningDate += int(tmp.group(1)) * 7
                    tmp = re.search("([0-9]+) day", dataLine.group())
                    if tmp:
                        runningDate += int(tmp.group(1))
                    # Weather running-time of the device is more than 7 days
                    if runningDate > 7:
                        njInfo["content"]["noRestart"]["status"] = True
                    elif runningDate == -1:
                        pass
                    else:
                        njInfo["content"]["noRestart"]["status"] = False
                    # Return detail to Forward.
                    njInfo["content"]["noRestart"]["content"] = dataLine.group().strip()
                else:
                    # Forward did't find the uptime of the device.
                    pass
            else:
                # That forwarder execute the command is failed.
                result["status"] = False
                return result
        else:
            return tmp
        return njInfo

    def showRun(self):
        cmd = "show run"
        tmp = self.privilegeMode()
        if not tmp["status"]:
            # Switch failure.
            return tmp
        njInfo = self.command(cmd, prompt={"success": "[\r\n]+\S+# ?$"})
        if not njInfo["state"] == "success":
            njInfo["status"] = False
        else:
            njInfo["content"] = "\r\n".join(njInfo["content"].split("\r\n")[1:-1])
        return njInfo

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
[Core][forward] Device class for Ruijie.
"""
import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError


class BASERUIJIE(BASESSHV2):
    """This is a manufacturer of maipu, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def __init__(self, *args, **kws):
        """Since the device's host prompt is different from BASESSHV2,
        the basic prompt for the device is overwritten here.
        """
        BASESSHV2.__init__(self, *args, **kws)
        self.basePrompt = r'(>|#) *$'

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
        # Excute a command.
        data = self.command("write",
                            prompt={"success": "\[OK\][\s\S]+[\r\n]+\S+(>|#) ?$",
                                    "error": "Unknown command[\s\S]+[\r\n]+\S+(>|#).*(>|#) ?$"})
        if data["state"] == "success":
            result["content"] = "The configuration was saved successfully."
            result["status"] = True
        else:
            result["errLog"] = "Failed save configuration, \
                               Info: [{content}] , [{errLog}]".format(content=data["content"], errLog=data["errLog"])
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
            result["status"] = False
            return result
        else:
            # If value of the mode is 2,start switching to configure-mode.
            sendConfig = self.command("config term",
                                      prompt={"success": "[\r\n]+\S+\(config\)# ?$",
                                              "error": "Unknown command[\s\S]+[\r\n]+\S+(>|#) ?$"})
            if sendConfig["state"] == "success":
                # switch to config-mode was successful.
                result["status"] = True
                self.mode = 3
                return result
            else:
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
            exitResult = self.command("end", prompt={"success": "[\r\n]+\S+(#|>|\]) ?$",
                                                     "error": "(#|>)"})
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
        sendEnable = self.command("enable", prompt={"password": "[pP]assword.*",
                                                    "noPassword": "[\r\n]+\S+(#|>|\]|\$) ?$"})
        if sendEnable["state"] == "noPassword":
            # The device not required a password,thus switch is successful.
            result["status"] = True
            self.mode = 2
            return result
        elif sendEnable["state"] is None:
            result["errLog"] = sendEnable["errLog"]
            return result
        # If device required a password,then send a password to device.
        sendPassword = self.command(self.privilegePw, prompt={"password": "[pP]assword.*",
                                                              "noPassword": "[\r\n]+\S+(#|>|\]|\$) ?$"})
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
        cmd = '''show run | include  ntp'''
        prompt = {
            "success": "[\r\n]+\S+(#|>|\]) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        # Before you execute the show command, you must go into privilege mode
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("ntp server ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp
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
        cmd = '''show run | include  logging'''
        prompt = {
            "success": "[\r\n]+\S+(#|>) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        # Before you execute the show command, you must go into privilege mode
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = result["content"].split("\r\n")
            for line in allLine:
                if re.search("logging server", line):
                    tmp = re.findall("([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                                     result["content"])
                    if len(tmp) > 0:
                        njInfo["content"].extend(tmp)
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
        cmd = '''show run | include  snmp'''
        prompt = {
            "success": "[\r\n]+\S+(#|>|\]) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        # Before you execute the show command, you must go into privilege mode
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("snmp-server host ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showVersion(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show  version"
        prompt = {
            "success": "[\r\n]+\S+(#|>|\]) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("Software version : (.*)", result["content"], flags=re.IGNORECASE)
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
        cmd = "show  vlan"
        prompt = {
            "success": "[\r\n]+\S+(>|#|\$) *$",
            "error": "Unrecognized[\s\S]+",
        }
        # Before you execute the show command, you must go into privilege mode
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            currentSection = "vlanName"
            isContinueLine = False
            for _vlanInfo in result["content"].split("\r\n"):
                _vlanInfo = _vlanInfo.strip()
                if re.search("\-\-\-\-", _vlanInfo):
                    continue
                if re.search("^[0-9]", _vlanInfo) and currentSection == "vlanName":
                    isContinueLine = True
                    # Get the line of vlan.
                    lineInfo = {
                        "id": "",
                        "description": "",
                        "status": "",
                        "interface": [],
                        "type": "",
                    }
                    tmp = re.search("([0-9]+)\s+(\S+)\s+(\S+)(.*)", _vlanInfo)
                    if tmp:
                        lineInfo["id"] = tmp.group(1)
                        lineInfo["description"] = tmp.group(2)
                        lineInfo["status"] = tmp.group(3)
                        if tmp.lastindex == 4:
                            lineInfo["interface"] = tmp.group(4).split(", ")
                        njInfo["content"].append(lineInfo)
                elif isContinueLine is True:
                    for _interface in _vlanInfo.split(", "):
                        lineInfo = njInfo["content"].pop()
                        lineInfo["interface"].append(_interface.strip())
                        njInfo["content"].append(lineInfo)
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
            "success": "[\r\n]+\S+(#|>|\]) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        # Before you execute the show command, you must go into privilege mode
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _interfaceInfo in result["content"].split("\r\n"):
                lineInfo = {
                    "net": "",
                    "mask": "",
                    "metric": "",
                    "type": "",
                    "description": "",
                    "interface": "",
                    "via": "",
                }
                tmp = re.search("([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/([0-9]{1,2})", _interfaceInfo)
                if tmp:
                    lineInfo["net"] = tmp.group(1)
                    lineInfo["mask"] = tmp.group(2)
                    via = re.search("via ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", _interfaceInfo)
                    if via:
                        lineInfo["via"] = via.group(1)
                    # Match the route table
                    tmp = re.search("([A-Za-z0-9])\*? +([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/([0-9]{1,2})", _interfaceInfo)
                    if tmp:
                        _type = tmp.group(1)
                        if _type == "C":
                            _type = "connected"
                        elif _type == "S":
                            _type = "static"
                        elif _type == "R":
                            _type = "rip"
                        elif _type == "O":
                            _type = "ospf"
                        elif _type == "K":
                            _type = "kernel"
                        elif _type == "I":
                            _type = "isis"
                        elif _type == "B":
                            _type = "bgp"
                        elif _type == "G":
                            _type == "guard"
                        elif _type == "*":
                            _type = "fib"
                    else:
                        _type = "default"
                    lineInfo["type"] = _type
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
            "success": "[\r\n]+\S+(#|>|\]) ?$",
            "error": "Unrecognized[\s\S]+",
        }
        # Before you execute the show command, you must go into privilege mode
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            interfacesFullInfo = re.split("========================== ", result["content"])[1::]
            for _interfaceInfo in interfacesFullInfo:
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
                # Get name of the interface.
                lineInfo['interfaceName'] = re.search("(.*) ========================", _interfaceInfo).group(1)
                tmp = re.search("\d+(/\d+)? is (.*), line protocol", _interfaceInfo)
                if tmp:
                    if tmp.lastindex == 1:
                        lineInfo["interfaceState"] = tmp.group(1).strip()
                    else:
                        lineInfo["interfaceState"] = tmp.group(2).strip()
                tmp = re.search("Interface address is:(.*)", _interfaceInfo)
                if tmp:
                    lineInfo["ip"] = tmp.group(1).strip()
                tmp = re.search("line protocol is (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["lineState"] = tmp.group(1).strip()
                tmp = re.search("MTU (\d+)", _interfaceInfo)
                if tmp:
                    lineInfo["mtu"] = tmp.group(1).strip()
                tmp = re.search("Port-type: (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["type"] = tmp.group(1).strip()
                tmp = re.search("input rate (\d+)", _interfaceInfo)
                if tmp:
                    lineInfo["inputRate"] = tmp.group(1).strip()
                tmp = re.search("output rate (\d+)", _interfaceInfo)
                if tmp:
                    lineInfo["outputRate"] = tmp.group(1).strip()
                tmp = re.search("duplex is (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["duplex"] = tmp.group(1).strip()
                tmp = re.search("Description: (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["description"] = tmp.group(1).strip()
                tmp = re.search("oper speed is (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["speed"] = tmp.group(1).strip()
                njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def cleanBuffer(self):
        """Because the device USES the cleanBuffer method in different details,
        it can be rewritten to modify the function.
        """
        if self.shell.recv_ready():
            self.shell.recv(4096).decode()
        # Ruijie equipment does not support sending line, must sent some space characters to device.
        self.shell.send(' \n')
        buff = ''
        # When after switching mode, the prompt will change, it should be based on basePrompt to check and at last line
        while not re.search(self.basePrompt, buff.split('\n')[-1]):
            try:
                # Accumulative results
                buff += self.shell.recv(1024).decode()
            except Exception:
                raise ForwardError('[Clean Buffer Error]: %s: Receive timeout [%s]' % (self.ip, buff))

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
        result["errLog"] = "Vlan {vlan_id} doest not exist.".format(vlan_id=vlan_id)
        return result

    def createVlan(self, vlan_id, name="None"):
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
        cmd = "vlan {vlan_id}\rname {name}".format(vlan_id=vlan_id, name=name)
        prompt = {
            "success": "[\r\n]+\S+config\-vlan\)(#|>) ?$",
            "error": "Invalid[\s\S]+config\)(#|>) ?$",
        }
        tmp = self.command(cmd, prompt=prompt)
        if tmp["state"] == "success":
            # The vlan was created successfuly, then to save configration if save is True.
            result["content"] = "The vlan {vlan_id} was created.".format(vlan_id=vlan_id)
            result["status"] = True
            return result
        else:
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
        prompt = {
            "success": "[\r\n]+\S+(>|\]|#) ?$",
            "error": "(Invalid input|[Uu]nknown command|Unrecognized command|Invalid command)[\s\S]+",
        }
        tmp = self.privilegeMode()
        runningDate = -1
        if tmp["status"]:
            result = self.command(cmd=cmd, prompt=prompt)
            if result["state"] == "success":
                dataLine = re.search("[Uu]ptime +: +([0-9]+).*", result["content"])
                if dataLine is not None:
                    runningDate = int(dataLine.group(1))
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

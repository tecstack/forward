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
[Core][forward] Device class for Brocade.
"""
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.paraCheck import mask_to_int
import re


class BASEBROCADE(BASESSHV2):
    """This is a manufacturer of brocade, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
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
        data = self.command("write  memory sync",
                            prompt={"success": "startup-config done[\s\S]+[\r\n]+\S+# ?$",
                                    "error": "need to configure config-sync peer before issuing this command[\S\s]+"})
        if data["state"] is None:
            result["errLog"] = "Failed save configuration, \
                               Info: [{content}] , [{errLog}]".format(content=data["content"], errLog=data["errLog"])
        elif data["state"] == "success":
            result["content"] = "The configuration was saved successfully."
            result["status"] = True
        else:
            result["content"] = "You cannot save the configuration on a slave device."
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
            sendConfig = self.command("config term", prompt={"success": "[\r\n]+\S+\(config\)# ?$"})
            if sendConfig["state"] == "success":
                # switch to config-mode was successful.
                result["status"] = True
                self.mode = 3
                return result
            elif sendConfig["state"] is None:
                result["errLog"] = sendConfig["errLog"]
                return result

    def showVersion(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = "show version"
        prompt = {
            "success": "[vV]ersion[\s\S]+[\r\n]+\S+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("[vV]ersion (\S+)", result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp.group(1)
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
            "success": "[\r\n]+\S+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = re.split("PORT-VLAN", result["content"])
            for _vlanInfo in allLine:
                _vlanInfo = _vlanInfo.strip()
                # Get the line of vlan.
                lineInfo = {"id": "",
                            "description": "",
                            "status": "",
                            "interface": [],
                            "type": ""}
                # Get id of the vlan.
                tmp = re.search("^\d+", _vlanInfo)
                if tmp:
                    lineInfo["id"] = tmp.group()
                    njInfo["content"].append(lineInfo)
                else:
                    continue
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
            "success": "[\r\n]+\S+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        result = self.command("show  running-config   | include  snmp", prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("snmp-server host (\d+\.\d+\.\d+\.\d+).*?port (\d+)",
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

    def showNtp(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show run ntp"
        prompt = {
            "success": "[\r\n]+\S+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("ntp.*?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"])
            njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showLog(self):
        # Get server address of syslog.
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = '''show running-config  | include  logging'''
        prompt = {
            "success": "[\r\n]+\S+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            # Gets the row containing the word logging + IP
            validLine = re.search("logging[\s\S]+?[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", result["content"])
            if validLine:
                # Get the ip of snmp.
                tmp = re.findall("([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", validLine)
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
        cmd = "show ip route"
        prompt = {
            "success": "[\r\n]+\S+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
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
                tmp = re.search("([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+\
([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+\
([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+\
(\S+)\s+\
\S+\s+\
(\S+)", _interfaceInfo)
                if tmp:
                    lineInfo["net"] = tmp.group(1)
                    lineInfo["mask"] = mask_to_int(tmp.group(2))
                    lineInfo["via"] = tmp.group(3)
                    lineInfo["interface"] = tmp.group(4)
                    lineInfo["type"] = tmp.group(5)
                    if lineInfo["type"] == "B":
                        lineInfo["type"] = "bgp"
                    elif lineInfo["type"] == "Be":
                        lineInfo["type"] = "ebgp"
                    elif lineInfo["type"] == "Bi":
                        lineInfo["type"] = "ibgp"
                    elif lineInfo["type"] == "D":
                        lineInfo["type"] = "Connected"
                    elif lineInfo["type"] == "R":
                        lineInfo["type"] = "rip"
                    elif lineInfo["type"] == "S":
                        lineInfo["type"] = "static"
                    elif lineInfo["type"] == "O":
                        lineInfo["type"] = "ospf"
                    elif lineInfo["type"] == "Oi":
                        lineInfo["type"] = "ospf inter area"
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
            "success": "[\r\n]+\S+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = re.findall("Port[\s\S]+?DMA.*", result["content"])
            for _interfaceInfo in allLine:
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
                tmp = re.search("^Port\s+(\S+)", _interfaceInfo)
                if tmp:
                    lineInfo["interfaceName"] = tmp.group(1)
                else:
                    continue
                # Get line state of the interface.
                tmp = re.search("line protocol is (\S+)", _interfaceInfo)
                if tmp:
                    lineInfo["lineState"] = tmp.group(1).strip(",")
                # Get adminState of the interface.
                tmp = re.search("link keepalive is (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["adminState"] = tmp.group(1).strip()
                # Get mac of the interface.
                tmp = re.search("MAC address is (\S+)", _interfaceInfo)
                if tmp:
                    lineInfo["mac"] = tmp.group(1).strip()
                # Get speed of the interface
                tmp = re.search("speed \S+, actual (\S+),", _interfaceInfo)
                if tmp:
                    lineInfo["speed"] = tmp.group(1)
                # Get the duplex of the interface.
                tmp = re.search("duplex \S+, actual (\S+)", _interfaceInfo)
                if tmp:
                    lineInfo["duplex"] = tmp.group(1).strip()
                # Get type of the interface.
                tmp = re.search("port state is (\S+)", _interfaceInfo)
                if tmp:
                    lineInfo["type"] = tmp.group(1).strip()
                # Get mtu of the interface.
                tmp = re.search("MTU (\d+)", _interfaceInfo)
                if tmp:
                    lineInfo["mtu"] = tmp.group(1)
                # Get input rate of the interface.
                tmp = re.search("300 second input rate: (.*sec)", _interfaceInfo)
                if tmp:
                    lineInfo["inputRate"] = tmp.group(1)

                # Get output rate of the interface.
                tmp = re.search("300 second output rate: (.*sec)", _interfaceInfo)
                if tmp:
                    lineInfo["outputRate"] = tmp.group(1)
                njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

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
            "error": "(Invalid input|Bad command|[Uu]nknown command|Unrecognized command|Invalid command)[\s\S]+",
        }
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

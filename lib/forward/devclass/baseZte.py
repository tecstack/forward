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
[Core][forward] Device class for zte,zhong-xing.
"""
from forward.devclass.baseSSHV2 import BASESSHV2
import re


class BASEZTE(BASESSHV2):
    """This is a manufacturer of zte, using the
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
        data = self.command("write",
                            prompt={"success": "OK[\s\S]+[\r\n]+\S+# ?$"})
        if data["state"] is None:
            result["errLog"] = "Failed save configuration, \
                               Info: [{content}] , [{errLog}]".format(content=data["content"], errLog=data["errLog"])
        else:
            result["content"] = "The configuration was saved successfully."
            result["status"] = True
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

    def showVersion(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = "show version"
        prompt = {
            "success": "[vV]ersion[\s\S]+[\r\n]+\S+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("(software|system).*version ?:? ?(\S+)", result["content"], flags=re.IGNORECASE)
            if tmp.lastindex == 2:
                njInfo["content"] = tmp.group(2).strip(",")
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
        cmd = "show ntp status"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
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
            "error": "Invalid input[\s\S]+",
        }
        result = self.command("show snmp config", prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("snmp-server host.*(\d+\.\d+\.\d+\.\d+).*?udp-port (\d+)",
                             result["content"])
            """
            snmp-server host vrf mng 192.168.1.1 trap version 2c xxx udp-port 163
            snmp-server host vrf mng 192.168.2.1 trap version 2c xxxxx udp-port 162
            """
            if tmp.__len__() > 0:
                njInfo["content"] = [{"ip": group[0], "port": group[-1]} for group in tmp]
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
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _vlanInfo in result["content"].split("\r\n"):
                tmp = re.search("^([0-9]+)", _vlanInfo)
                # Get the line of vlan.
                lineInfo = {
                    "id": "",
                    "description": "",
                    "status": "",
                    "interface": [],
                    "type": "",
                }
                if tmp:
                    lineInfo["id"] = tmp.group(1)
                    njInfo["content"].append(lineInfo)
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
        cmd = "show interface"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = re.findall(".*line protocol[\s\S]+?output", result["content"])
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
                tmp = re.search("(.*?) is.*,", line)
                if tmp:
                    lineInfo["interfaceName"] = tmp.group(1).strip()
                # Get line state of the interface.
                tmp = re.search("line protocol is (.*),", line)
                if tmp:
                    lineInfo["lineState"] = tmp.group(1).strip()
                # Get the admin state of the interface.
                tmp = re.search(".+ is (.*),", line)
                if tmp:
                    lineInfo["adminState"] = tmp.group(1).strip()
                # Get mtu of the interface.
                tmp = re.search("[\r\n]+\s+MTU (\d+)", line)
                if tmp:
                    lineInfo["mtu"] = tmp.group(1).strip()
                # Get mac of the interface.
                tmp = re.search(" Hardware.*address is (.*)", line)
                if tmp:
                    lineInfo["mac"] = tmp.group(1).strip()
                # Get the type of the interface.
                tmp = re.search("The port is (\S+)", line)
                if tmp:
                    lineInfo["type"] = tmp.group(1).strip()
                # Get duplex of the interface.
                tmp = re.search("Duplex (\S+)", line)
                if tmp:
                    lineInfo['duplex'] = tmp.group(1).strip()
                # Get input rate of the interface.
                tmp = re.search("input\s+(\S+)", line)
                if tmp:
                    lineInfo["inputRate"] = tmp.group(1).strip()
                #  Get output rate of the interface.
                tmp = re.search("ouput\s+(\S+)", line)
                if tmp:
                    lineInfo["outputRate"] = tmp.group(1).strip()
                # Get description of the interface.
                tmp = re.search("Description is (.*)", line)
                if tmp:
                    lineInfo["description"] = tmp.group(1).strip()
                # Get ip of the interface.
                tmp = re.search("Internet address is (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                if tmp:
                    lineInfo["ip"] = tmp.group(1)
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
        cmd = "show logging configuration"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("syslog-server.*?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
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
        cmd = "show ip vrf brief"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid input[\s\S]+",
        }
        # Get name of routes.
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allRouteList = []
            for line in result["content"].split("\r\n"):
                name = re.search("^\s+(\S+)", line)
                if name:
                    allRouteList.append(name.group(1))
            for name in allRouteList:
                # Get relevant information according to the name of the route.
                cmd = "show ip protocol  routing  vrf {name}".format(name=name)
                result = self.command(cmd=cmd, prompt=prompt)
                if not result["state"] == "success":
                    continue
                for line in result["content"].split("\r\n"):
                    tmp = re.search("(\d+\.\d+\.\d+\.\d+)/(\d{1,2})\s+(\d+\.\d+\.\d+\.\d+).*\s+(\S+)", line)
                    if tmp:
                        lineInfo = {
                            "net": "",
                            "mask": "",
                            "metric": "",
                            "type": "",
                            "description": "",
                            "interface": "",
                            "via": ""}
                        lineInfo["net"] = tmp.group(1)
                        lineInfo["mask"] = tmp.group(2)
                        lineInfo["via"] = tmp.group(3)
                        lineInfo["type"] = tmp.group(4).lower()
                        njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def basicInfo(self, cmd="show version"):
        njInfo={
                "status":True,
                "content":{
                        "noRestart": {"status":None,"content":""},
                        "systemTime": {"status": None, "content": ""},
                        "cpuLow": {"status": None, "content": ""},
                        "memLow": {"status": None, "content": ""},
                        "boardCard": {"status": None, "content": ""},
                        "tempLow": {"status": None, "content": ""},
                        "firewallConnection": {"status": None, "content": ""}},
                "errLog":""
                }
        prompt = {
            "success": "[\r\n]+\S+.+(>|\]|#) ?$",
            "error": "(Bad command|[Uu]nknown command|Unrecognized command|Invalid command)[\s\S]+",
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

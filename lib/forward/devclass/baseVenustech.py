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
[Core][forward] Device class for Venustech.
"""
from forward.devclass.baseTELNET import BASETELNET
import re


class BASEVENUSTECH(BASETELNET):
    """This is a manufacturer of venustech, using the
    telnet version of the protocol, so it is integrated with BASETELNET library.
    """
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
            exitResult = self.command("end", prompt={"success": "[\r\n]+\S+# ?$",
                                                     "error": "Unknown command[\s\S]+"})
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
        data = self.command("write file",
                            prompt={"success": "Current[\s\S]+[\r\n]+\S+# ?$",
                                    "error": "Unknow[\s\S]+"})

        if data["state"] is None:
            result["errLog"] = "Failed save configuration, \
                               Info: [{content}] , [{errLog}]".format(content=data["content"], errLog=data["errLog"])
        elif data["state"] == "error":
            result["content"] = data["content"]
        else:
            result["content"] = "The configuration was saved successfully.[%s]" % data["content"]
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
            result["status"] = False
            return result
        else:
            # If value of the mode is 2,start switching to configure-mode.
            sendConfig = self.command("config term", prompt={"success": "[\r\n]+\S+\(config\)# ?$",
                                                             "error": "Unknown command[\s\S]+"})
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
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("VSOS                    :(.*)", result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp.group(1).strip()
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
            "success": "[\r\n]+\S+.+# ?$",
            "error": "Unknown command[\s\S]+",
        }
        # Swtich to privilege-mode before getting the information of the interfaces.
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            njInfo["errLog"] = tmp["errLog"]
            return njInfo
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = re.findall(".*Link[\s\S]+?TX rate.*", result["content"])
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
                tmp = re.search("(.*)Link status", line)
                if tmp:
                    lineInfo["interfaceName"] = tmp.group(1).strip()
                # Get line state of the interface.
                tmp = re.search("Link status is (.*),", line)
                if tmp:
                    lineInfo["lineState"] = tmp.group(1).strip()
                # Get the admin state of the interface.
                tmp = re.search("Admin status is(.*)", line)
                if tmp:
                    lineInfo["adminState"] = tmp.group(1).strip()
                # Get mtu of the interface.
                tmp = re.search("mtu (\d+)", line)
                if tmp:
                    lineInfo["mtu"] = tmp.group(1).strip()
                # Get mac of the interface.
                tmp = re.search("HWaddr: (.*)", line)
                if tmp:
                    lineInfo["mac"] = tmp.group(1).strip()
                # Get the type of the interface.
                tmp = re.search("media type: (\S+)", line)
                if tmp:
                    lineInfo["type"] = tmp.group(1).strip()
                # Get the speed of the interface.
                tmp = re.search("speed: (\S+)", line)
                if tmp:
                    lineInfo["speed"] = tmp.group(1)
                # Get duplex of the interface.
                tmp = re.search("duplex:(\S+)", line)
                if tmp:
                    lineInfo['duplex'] = tmp.group(1)
                # Get metric of the interface.
                tmp = re.search("Metric:(\d+)", line)
                if tmp:
                    lineInfo["metric"] = tmp.group(1)
                # Get input rate of the interface.
                tmp = re.search("RX rate: (.*)", line)
                if tmp:
                    lineInfo["inputRate"] = tmp.group(1).strip()
                #  Get output rate of the interface.
                tmp = re.search("TX rate:(.*)", line)
                if tmp:
                    lineInfo["outputRate"] = tmp.group(1).strip()
                njInfo["content"].append(lineInfo)
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
        cmd = "show ntp config"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unknown command[\s\S]+",
        }
        # Swtich to privilege-mode before getting the ntp informations.
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            njInfo["errLog"] = tmp["errLog"]
            return njInfo
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", result["content"], flags=re.IGNORECASE)
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
        cmd = "show run snmp"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unknown command[\s\S]+",
        }
        # Swtich to privilege-mode before getting the snmp informations.
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            njInfo["errLog"] = tmp["errLog"]
            return njInfo
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", result["content"], flags=re.IGNORECASE)
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
        cmd = "show run syslog"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unknown command[\s\S]+",
        }
        # Swtich to privilege-mode before getting the snmp informations.
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            njInfo["errLog"] = tmp["errLog"]
            return njInfo
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            # Intercept the line containing the server address
            tmp = re.search("log server addr.*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", result["content"])
            if tmp:
                tmp = re.findall("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", tmp.group(), flags=re.IGNORECASE)
                njInfo["content"] = tmp
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
            "success": "[\r\n]+\S+.+# ?$",
            "error": "Unknown command[\s\S]+",
        }
        # Swtich to privilege-mode before getting the routing informations.
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            njInfo["errLog"] = tmp["errLog"]
            return njInfo
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
                if re.search("\S?>\* [0-9]", _interfaceInfo):
                    tmp = re.search(">\* ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/([0-9]{1,2})", _interfaceInfo)
                    lineInfo["net"] = tmp.group(1)
                    lineInfo["mask"] = tmp.group(2)
                    via = re.search("via ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", _interfaceInfo)
                    if via:
                        lineInfo["via"] = via.group(1)
                    # Match the route table
                    tmp = re.search("([A-Z])>\*", _interfaceInfo)
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
                        _type == "select"
                    lineInfo["type"] = _type
                    njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def basicInfo(self, cmd="show system uptime"):
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
            "error": "(Unrecognized command|Invalid command)[\s\S]+",
        }
        tmp = self.privilegeMode()
        runningDate = -1
        if tmp["status"]:
            result = self.command(cmd=cmd, prompt=prompt)
            if result["state"] == "success":
                dataLine = re.search(" runtime .+(day|year|week).*", result["content"])
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

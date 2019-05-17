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
[Core][forward] Device class for Baer.
"""
from forward.devclass.baseSSHV2 import BASESSHV2
import re


class BASEBAER(BASESSHV2):
    """This is a manufacturer of baer, using the
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
        data = self.command("admin save",
                            prompt={"success": "Completed[\s\S]+[\r\n]+\S+# ?$"})
        if data["state"] is None:
            result["errLog"] = "Failed save configuration, \
                               Info: [{content}] , [{errLog}]".format(content=data["content"], errLog=data["errLog"])
        else:
            result["content"] = "The configuration was saved successfully."
            result["status"] = True
        return result

    def privilegeMode(self):
        # Switch to privilege mode.
        njInfo = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        """
        *A:NFJD-PSC-S-SR7750-1# configure
        *A:NFJD-PSC-S-SR7750-1>config# service
        *A:NFJD-PSC-S-SR7750-1>config>service#
        """
        result = self.command("exit all", prompt={"success": "[\r\n]+\S+# ?$"})
        if result["state"] == "success":
            if re.search("[\r\n]+\S+.+>config>[a-z>]+# ?$", result["content"]):
                njInfo["errLog"] = "Switch to privilegeMode is faild. current located config mode."
            else:
                self.mode == 2
                njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def configMode(self):
        # Switch to config mode.
        njInfo = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            return tmp
        result = self.command("config", prompt={"success": "[\r\n]+\S+>config# ?$"})
        if result["state"] == "success":
            self.mode == 3
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showVersion(self):
        # Switch to config mode.
        njInfo = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        result = self.command("show version", prompt={"success": "[\r\n]+\S+# ?$",
                                                      "eror": "Bad command[\s\S]+"})
        if result["state"] == "success":
            # TiMOS-C-10.0.R12 cpm/hops ALCATEL SR 7750 Copyright (c) 2000-2013 Alcatel-Lucent. --> TiMOS-C-10.0.R12
            tmp = re.search("(TiMOS\S+)", result["content"])
            if tmp:
                njInfo["content"] = tmp.group(1)
            else:
                njInfo["errLog"] = "Version information was not available."
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showRoute(self):
        # Switch to config mode.
        njInfo = {
            "status": False,
            "content": [],
            "errLog": ""
        }
        result = self.command("show router  route-table", prompt={"success": "[\r\n]+\S+# ?$",
                                                                  "eror": "Bad command[\s\S]+"})
        """
        Dest Prefix[Flags]                            Type    Proto     Age        Pref
        Next Hop[Interface Name]                                    Metric
        -------------------------------------------------------------------------------
        0.0.0.0/0                                     Remote  OSPF(10)  28d14h34m  190
            10.32.2.2                                                    102
        0.0.0.0/0                                     Remote  OSPF(10)  28d14h34m  190
           10.32.2.6                                                    102
        10.32.0.1/32                                  Remote  OSPF(10)  0484d16h   10
            10.32.2.2                                                    2
        10.32.0.1/32                                  Remote  OSPF(10)  0484d16h   10
            10.32.2.6                                                    2
        10.32.0.2/32                                  Remote  OSPF(10)  0484d16h   10
            10.32.2.2                                                    2
        """
        if result["state"] == "success":
            allLine = result["content"].split("\r\n")
            i = 0
            for line in allLine:
                lineInfo = {"net": "",
                            "mask": "",
                            "metric": "",
                            "description": "",
                            "type": "",
                            "interface": "",
                            "via": ""}
                tmp = re.search("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d{1,2})\s+\S+\s+([A-Za-z]+)", line)
                if tmp:
                    lineInfo["net"] = tmp.group(1)
                    lineInfo["mask"] = tmp.group(2)
                    lineInfo["type"] = tmp.group(3)
                    # Get via and metric of routing from next line.
                    tmp = re.search("([\s\S]+)(\d+)", allLine[i + 1])
                    if tmp:
                        lineInfo["via"] = tmp.group(1).split()[0].strip("()")
                        lineInfo["metric"] = tmp.group(2)
                        njInfo["content"].append(lineInfo)
                    else:
                        continue
                i += 1
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
        cmd = "show port detail"
        result = self.command(cmd, prompt={"success": "[\r\n]+\S+# ?$",
                                           "eror": "Bad command[\s\S]+"})
        if result["state"] == "success":
            reg = "Description        :[\s\S]+?========================================"
            allLine = re.findall(reg, result["content"])
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
                            "mac": "",
                            "ip": ""}
                # Get name of the interface
                tmp = re.search("Interface          : (\S+)", _interfaceInfo)
                if tmp:
                    lineInfo["interfaceName"] = tmp.group(1)
                else:
                    continue
                # Get description of the interface.
                tmp = re.search("Description        : (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["description"] = tmp .group(1).strip()
                # Get speed of the interface.
                tmp = re.search("Oper Speed       : (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["speed"] = tmp.group(1).strip()
                # Get adminState of the interface.
                tmp = re.search("Admin State        : ([a-zA-Z]+)", _interfaceInfo)
                if tmp:
                    lineInfo["adminState"] = tmp.group(1)
                # Get duplex of the interface.
                tmp = re.search("Oper Duplex      : ([a-zA-Z]+)", _interfaceInfo)
                if tmp:
                    lineInfo["duplex"] = tmp.group(1)
                # Get state of the interface.
                tmp = re.search("Oper State         : ([a-zA-Z]+)", _interfaceInfo)
                if tmp:
                    lineInfo["interfaceState"] = tmp.group(1)
                # Get mtu of the interface.
                tmp = re.search("MTU              : (\d+)", _interfaceInfo)
                if tmp:
                    lineInfo["mtu"] = tmp.group(1)
                # Get Egress of the interface.
                tmp = re.search("Egress Rate        : (\S+)", _interfaceInfo)
                if tmp:
                    lineInfo["outputRate"] = tmp.group(1)
                # Get Igress of the interface.
                tmp = re.search("Ingress Rate     : (\S+)", _interfaceInfo)
                if tmp:
                    lineInfo["inputRate"] = tmp.group(1)
                # Get mac of the interface.
                tmp = re.search("Hardware Address   : (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["mac"] = tmp.group(1).strip()
                njInfo["content"].append(lineInfo)
            # Get type of interface.
            result = self.command("show port", prompt={"success": "[\r\n]+\S+.+# ?$",
                                  "eror": "Bad command[\s\S]+"})
            if result["state"] == "success":
                i = 0
                """
                5/2/nat-in-ip Up    Yes  Up                   - accs qinq vport
                5/2/nat-out-ip
                              Up    Yes  Up                   - accs qinq vport   <----convert to a row
                5/2/nat-in-l2 Up    Yes  Up                   - netw dotq vport
                """
                # Convert to a row.
                content = re.sub("\r\n\s+\S+$", " ", result["content"])
                for line in njInfo["content"]:
                    # Match interfaceName from njInfo["content"]
                    interfaceName = line["interfaceName"]
                    tmp = re.search("%s.*" % interfaceName, content)
                    """
                    Port          Admin Link Port    Cfg  Oper LAG/ Port Port Port   C/QS/S/XFP/
                    Id            State      State   MTU  MTU  Bndl Mode Encp Type   MDIMDX
                    4/1/1         Up    Yes  Up      9192 9192   22 netw null xlgige 40GBASE-SR4
                    4/1/1         Up    Yes  Up      9192 9192   22 netw null xlgige
                    4/1/1         Up    Yes  Up                  22 netw null xlgige
                    """
                    if tmp:
                        # Get type of interface.
                        key = tmp.group().split()
                        # Port type in the penultimate first or second field
                        if len(key) == 11:
                            njInfo["content"][i]["type"] = key[9]
                        else:
                            njInfo["content"][i]["type"] = key[-1]
                    i += 1
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showSnmp(self):
        # Switch to config mode.
        njInfo = {
            "status": False,
            "content": [{"ip": "",
                         "port": ""}],
            "errLog": ""
        }
        result = self.command("show log snmp-trap-group", prompt={"success": "[\r\n]+\S+# ?$",
                                                                  "eror": "Bad command[\s\S]+"})
        if result["state"] == "success":
            tmp = re.findall("\d+\.\d+\.\d+\.\d+:\d+", result["content"])
            """
            90        172.21.31.103:162
            90        172.21.31.103:16222
            """
            if tmp.__len__() > 0:
                njInfo["content"] = [{"ip": group.split(":")[0], "port": group.split(":")[-1]} for group in tmp]
                njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showLog(self):
        njInfo = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        result = self.command("show log  syslog", prompt={"success": "[\r\n]+\S+# ?$",
                                                          "eror": "Bad command[\s\S]+"})
        if result["state"] == "success":
            tmp = re.findall("[\r\n]+\d+\s+(\d+\.\d+\.\d+\.\d+)\s+\d+", result["content"])
            """
            1      172.21.11.109                                   514         warning
            """
            if tmp.__len__() > 0:
                njInfo["content"] = tmp
                njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showNtp(self):
        # Switch to config mode.
        njInfo = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        result = self.command("show system ntp", prompt={"success": "[\r\n]+\S+# ?$",
                                                         "eror": "Bad command[\s\S]+"})
        if result["state"] == "success":
            tmp = re.findall("\d+\.\d+\.\d+\.\d+", result["content"])
            """
            Clock Source       : 172.20.152.1
            """
            if tmp.__len__() > 0:
                njInfo["content"] = tmp
                njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showVlan(self):
        # Get list of vlans.
        njInfo = {
            "status": False,
            "content": [],
            "errLog": ""
        }
        result = self.command("show service sap-using", prompt={"success": "[\r\n]+\S+# ?$",
                                                                "eror": "Bad command[\s\S]+"})
        if result["state"] == "success":
            for line in result["content"].split("\r\n"):
                lineInfo = {"id": "",
                            "description": "",
                            "status": "",
                            "interface": [],
                            "type": ""}
                tmp = re.search("^(\S+):(\d+)\s+\S+\s+(\S+)\s+\S+\s+(.*)", line)
                """
                lag-24                             100          Up   Up   (Not Specified)
                lag-31:221                         1000         Up   Up   (Not Specified)
                1/2/6                              1001         Up   Up   (Not Specified)
                lag-31:9                           2000         Up   Up   (Not Specified)
                """
                if tmp:
                    lineInfo["interface"] = [tmp.group(1)]
                    lineInfo["id"] = tmp.group(2)
                    lineInfo["status"] = tmp.group(3)
                    # Remove the '(' and ')'
                    lineInfo["description"] = tmp.group(4).strip("()")
                    njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def basicInfo(self, cmd="show uptime"):
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
            "error": "(Bad command|[Uu]nknown command|Unrecognized command|Invalid command)[\s\S]+",
        }
        tmp = self.privilegeMode()
        runningDate = -1
        if tmp["status"]:
            result = self.command(cmd=cmd, prompt=prompt)
            if result["state"] == "success":
                dataLine = re.search(" up ?time:? .+(day|year|week).*", result["content"], flags=re.IGNORECASE)
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
        cmd = "admin display-config"
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

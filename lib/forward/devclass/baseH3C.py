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
[Core][forward] Base device class for H3C basic device method, by using paramiko module.
"""

import re
import logging
import time
import random
from forward.devclass.baseSSHV2 import BASESSHV2
# from forward.utils.forwardError import ForwardError
from forward.utils.paraCheck import checkIP
from forward.utils.deviceListSplit import DEVICELIST


class BASEH3C(BASESSHV2):
    """This is a manufacturer of h3c, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def commit(self):
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Switch to privilege-mode.
        tmp = self.generalMode()
        if not tmp["status"]:
            # Switch failure.
            return tmp
        # Excute a command.
        tmp = self.command("save",
                           prompt={"success": "Are you sure\? \[Y/N\]: ?$",
                                   "error": "Error:Incomplete command[\s\S]+"})
        if tmp["state"] == "success":
            tmp = self.command("Y", prompt={"success": "press the enter key\): ?$"})
            if tmp["state"] == "success":
                tmp = self.command("", prompt={"success": "overwrite\? \[Y/N\]: ?$"})
                if tmp["state"] == "success":
                    tmp = self.command("Y", prompt={"success": "successfully\.[\r\n]+<\S+>?$"})
                    if tmp["state"] == "success":
                        result["status"] = True
                        result["content"] = tmp["content"]
                    else:
                        result["errLog"] = "That save configuration is failed.related information: [{content}]".format(content=tmp["content"])
                else:
                    result["errLog"] = "That save configuration is failed.related information: [{content}]".format(content=tmp["content"])

            else:
                result["errLog"] = "Failed save configuration,related information: [{content}]".format(content=tmp["content"])
        else:
            result["errLog"] = "Failed save configuration, \
                               Info: [{content}] , [{errLog}]".format(content=tmp["content"], errLog=tmp["errLog"])
        return result

    def generalMode(self):
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Get the current position before switch to general mode.
        # Demotion,If device currently mode-level greater than 2, It only need to execute `end`.
        if self.mode > 1:
            tmp = self.command("return", prompt={"success": "[\r\n]+\S+> ?$"})
            if tmp["state"] == "success":
                result["status"] = True
                self.mode = 1
                return result
            else:
                result["errLog"] = tmp["errLog"]
                return result
        else:
            result["status"] = True
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
            toGeneralModeResult = self.generalMode()
            if toGeneralModeResult["status"] is False:
                result["errLog"] = "Demoted from hight-mode to general-mode failed."
                return result
            # else,go into privilege-mode.
        # else, command line of the device is in general-mode.
        # Start switching to privilege-mode.
        sendEnableResult = self.command("system-view", prompt={"success": "[\r\n]+\S+\] ?$",
                                                               "error": "[\r\n]+\S+> ?$"})
        if sendEnableResult["state"] == "success":
            # The device not required a password,thus switch is successful.
            result["status"] = True
            self.mode = 2
            return result
        elif sendEnableResult["state"] == "error":
            result["errLog"] = "Failed to switch to privilege mode, \
                               related information: [{errLog}],[{content}]".format(errLog=sendEnableResult["errLog"],
                                                                                   content=sendEnableResult["content"])
            return result
        else:
            return sendEnableResult

    def showLog(self):
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = "display current-configuration | i log"
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("loghost ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
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
            'content': "",
            'errLog': ''
        }
        cmd = "dis version"
        prompt = {
            "success": "[\s\S]+[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
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

    def showNtp(self):
        # Gets the NTP server address of the device
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "dis current-configuration | i ntp"
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("ntp-service unicast-server ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"])
            if tmp:
                njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showSnmp(self):
        # Gets the SNMP server address of the device
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "dis current-configuration | i snmp"
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("udp-domain ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", result["content"])
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
        cmd = "display  vlan"
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            currentSection = "vlanName"
            isContinueLine = False
            for _vlanInfo in result["content"].split("\r\r\n"):
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
                    tmp = re.search("([0-9]+)\s+(\S+)[\s\S]+:(.*)", _vlanInfo)
                    if tmp:
                        lineInfo["id"] = tmp.group(1)
                        lineInfo["type"] = tmp.group(2)
                        if tmp.lastindex == 3:
                            lineInfo["interface"] = tmp.group(3).split()
                        njInfo["content"].append(lineInfo)
                    else:
                        # Vlan has not yet configured interfaces.
                        tmp = re.search("([0-9]+)\s+([a-z]+)", _vlanInfo)
                        if tmp:
                            lineInfo["id"] = tmp.group(1)
                            lineInfo["type"] = tmp.group(2)
                            njInfo["content"].append(lineInfo)
                elif isContinueLine is True and not re.search("VID  Status",
                                                              _vlanInfo) and currentSection == "vlanName":
                    for _interface in _vlanInfo.split():
                        lineInfo = njInfo["content"].pop()
                        lineInfo["interface"].append(_interface.strip())
                        njInfo["content"].append(lineInfo)
                    continue
                else:
                    isContinueLine = False
                if re.search("VID  Status", _vlanInfo):
                    currentSection = "vlanType"
                    continue
                if currentSection == "vlanType":
                    if re.search("^[0-9]", _vlanInfo.strip()):
                        tmp = re.search("([0-9]+)[ \t]+([a-z]+).*", _vlanInfo)
                        if tmp:
                            vlanID = tmp.group(1)
                            vlanStatus = tmp.group(2)
                            vlanDescription = tmp.group().split()[-1].strip()
                            i = 0
                            for _vlan in njInfo["content"]:
                                if vlanID == _vlan["id"]:
                                    njInfo["content"][i]["status"] = vlanStatus
                                    njInfo["content"][i]["description"] = vlanDescription
                                i += 1

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
        cmd = "display  ip routing-table"
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _interfaceInfo in result["content"].split("\r\r\n"):
                # record the route table.
                lineInfo = {"net": "",
                            "mask": "",
                            "metric": "",
                            "description": "",
                            "type": "",
                            "interface": "",
                            "via": ""}
                tmp = re.search("([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/([0-9]{1,2})\s+(\S+)\s+\
                                 \S+\s+\S+\s+\S+\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(\S+)", _interfaceInfo)
                if tmp:
                    lineInfo["net"] = tmp.group(1)
                    lineInfo["mask"] = tmp.group(2)
                    lineInfo["type"] = tmp.group(3)
                    lineInfo["via"] = tmp.group(4)
                    lineInfo["interface"] = tmp.group(5)
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
        cmd = "display interface"
        # There are Special characters in some descriptions.
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            interfacesFullInfo = re.findall(".*current state[\s\S]+?Output bandwidth utilization :.*",
                                            result["content"])
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
                            "mac": "",
                            "ip": ""}
                # Get name of the interface.
                lineInfo['interfaceName'] = re.search("(.*)current state", _interfaceInfo).group(1).strip()
                # Get state of the interface and remove extra character.
                lineInfo['interfaceState'] = re.search("current state :(.*)", _interfaceInfo).group(1).strip()
                # Get state of line protocol of the interface and remove extra character.
                lineInfo['lineState'] = re.search("Line protocol current state :(.*)", _interfaceInfo).group(1).strip()
                # Get description of the interface.
                lineInfo['description'] = re.search("Description:(.*)", _interfaceInfo).group(1).strip()
                # Get MUT of the interface.
                tmpMTU = re.search("The Maximum Transmit Unit is ([0-9]+)", _interfaceInfo)
                if tmpMTU:
                    lineInfo["mtu"] = tmpMTU.group(1)
                else:
                    lineInfo["mtu"] = ""
                # Get speed of the interface.
                tmp = re.search("Speed : ([0-9]+)", _interfaceInfo)
                if tmp:
                    lineInfo["speed"] = int(tmp.group(1))
                else:
                    lineInfo["speed"] = ""
                # Get duplex of the interface.
                tmp = re.search("([a-z]+)\-duplex", _interfaceInfo, flags=re.IGNORECASE)
                if tmp:
                    lineInfo["duplex"] = tmp.group(1)
                else:
                    lineInfo["duplex"] = ""
                # Get duplex of the interface for s9312
                tmp = re.search("Duplex: ([a-z]+)", _interfaceInfo, flags=re.IGNORECASE)
                if tmp:
                    lineInfo["duplex"] = tmp.group(1)
                # Get ip of the interface.
                tmp = re.search("Internet Address is (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["ip"] = tmp.group(1).split("/")[0]
                else:
                    lineInfo["ip"] = ""
                # Get mac of the interface.
                tmpMAC = re.search("Hardware address is (.*)", _interfaceInfo)
                if tmpMAC:
                    lineInfo["mac"] = tmpMAC.group(1).strip()
                else:
                    lineInfo["mac"] = ""
                # Get port type of the interface.
                tmpPortType = re.search("Physical is (\S+)", _interfaceInfo)
                if tmpPortType:
                    lineInfo["type"] = tmpPortType.group(1).strip().strip(",")
                else:
                    lineInfo["type"] = ""
                # Last 300 seconds input rate
                tmp = re.search("Last 300 seconds input rate (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["inputRate"] = tmp.group(1).strip()
                else:
                    lineInfo["inputRate"] = ""
                tmp = re.search("Last 300 seconds output rate (.*)", _interfaceInfo)
                if tmp:
                    lineInfo["outputRate"] = tmp.group(1).strip()
                else:
                    lineInfo["outputRate"] = ""
                # CRC:
                tmp = re.search("CRC:.*([0-9]+)", _interfaceInfo)
                if tmp:
                    lineInfo["crc"] = tmp.group(1)
                else:
                    lineInfo["crc"] = ""
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
        @param description: description of vlan.

        """
        # Crate vlan.
        result = {
            "status": False,
            "content": {},
            "errLog": ""
        }
        vlan_id = str(vlan_id)
        # Enter config-mode.
        tmp = self.privilegeMode()
        if not tmp["status"]:
            # Failed to enter configuration mode
            return tmp
        if name is None:
            cmd = "vlan {vlan_id}".format(vlan_id=vlan_id)
        else:
            cmd = "vlan {vlan_id}\rname {name}".format(vlan_id=vlan_id, name=name)
        prompt = {
            "success": "[\r\n]+\S+vlan{vlan_id}\] ?$".format(vlan_id=vlan_id),
            "error": "Error:[\s\S]+",
        }
        # runing command of vlan.
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
        # Deleting vlan.
        result = {
            "status": False,
            "content": {},
            "errLog": ""
        }
        # Enter config-mode.
        tmp = self.privilegeMode()
        if not tmp["status"]:
            # Failed to enter configuration mode
            return tmp
        cmd = "undo vlan {vlan_id}".format(vlan_id=vlan_id)
        prompt = {
            "success": "{cmd}[\r\n]+\S+\] ?$".format(vlan_id=vlan_id, cmd=cmd),
            "error": "(Error):[\s\S]+",
        }
        tmp = self.command(cmd, prompt=prompt)
        logging.debug("runing command result:" + str(tmp))
        if tmp["state"] == "success":
            # The vlan was deleted successfuly, then to save configration if save is True.
            result["content"] = "The vlan {vlan_id} was deleted.".format(vlan_id=vlan_id)
            result["status"] = True
            return result
        else:
            result["errLog"] = "The vlan {vlan_id} was not deleted[{content},{errLog}].".format(vlan_id=vlan_id,
                                                                                                content=tmp["content"],
                                                                                                errLog=tmp["errLog"])
            return result

    def interfaceVlanExist(self, vlan_id):
        # parameter vlan_id: Vlan123
        result = {
            "status": False,
            "content": {},
            "errLog": ""
        }
        # Checking parameter
        vlan_id = str(vlan_id).strip()
        if re.search("^[0-9]+$", vlan_id):
            vlan_id = "Vlanif" + vlan_id
        for line in self.showInterface()["content"]:
            if vlan_id == line["interfaceName"]:
                result["status"] = True
                return result
        result["errLog"] = "The interface-vlan {vlan_id} does not exist.".format(vlan_id=vlan_id)
        return result

    def deleteInterfaceVlan(self, vlan_id):
        # Deleting virtual vlan.
        result = {
            "status": False,
            "content": {},
            "errLog": ""
        }
        # Enter privilege-mode.
        tmp = self.privilegeMode()
        if not tmp["status"]:
            # Failed to enter configuration mode
            return tmp
        cmd = "undo interface vlanif {vlan_id}".format(vlan_id=vlan_id)
        prompt = {
            "success": "[\r\n]+\S+(\]|>) ?$",
        }
        tmp = self.command(cmd, prompt=prompt)
        if not self.interfaceVlanExist(vlan_id)["status"]:
            # The interface-vlan was deleted successfuly.
            result["content"] = "The interface-vlan {vlan_id} was deleted.".format(vlan_id=vlan_id)
            result["status"] = True
            return result
        else:
            result["errLog"] = "The interface-vlan {vlan_id} was not deleted.".format(vlan_id=vlan_id)
            return result

    def createInterfaceVlan(self, vlan_id, ip=None, mask=None, description="None"):
        # Creating virtual vlan.
        result = {
            "status": False,
            "content": {},
            "errLog": ""
        }
        # Checking parameters.
        if ip is None or mask is None:
            result["errLog"] = "parameter of ip and mask can not be None."
            return result
        elif checkIP(ip) is False:
            result["errLog"] = "Illegal IP address."
            return result
        elif checkIP(mask) is False:
            result["errLog"] = "Illegal net mask."
            return result
        # Enter privilege-mode.
        tmp = self.privilegeMode()
        if not tmp["status"]:
            # Failed to enter configuration mode
            return tmp
        cmd1 = "interface vlanif {vlan_id}".format(vlan_id=vlan_id)
        cmd2 = "description {description}".format(description=description)
        cmd3 = "ip address {ip} {mask}".format(ip=ip, mask=mask)
        # Forward need to check if The vlan exists,before creating.
        if not self.vlanExist(vlan_id)["status"]:
            # no exists.
            result["errLog"] = "The vlan({vlan_id}) does not exists,\
            thus can't create interface-vlan.".format(vlan_id=vlan_id)
            return result
        prompt1 = {
            "success": "[\r\n]+\S+Vlanif{vlan_id}\] ?$".format(vlan_id=vlan_id),
            "error": "[\r\n]+\S+\] ?$",
            # "error": "(Invalid|Error|Illegal|marker|Incomplete)[\s\S]+",
        }
        prompt2 = {
            "success": "{cmd2}[\r\n]+\S+Vlanif{vlan_id}\] ?$".format(vlan_id=vlan_id, cmd2=cmd2),
            "error": "(Invalid|Error|Illegal|marker|Incomplete)[\s\S]+",
        }
        prompt3 = {
            "success": "{cmd3}[\r\n]+\S+Vlanif{vlan_id}\] ?$".format(vlan_id=vlan_id, cmd3=cmd3),
            "error": "(Invalid|Error|Illegal|marker|Incomplete)[\s\S]+",
        }
        # Running cmd1.
        tmp = self.command(cmd1, prompt=prompt1)
        if not tmp["state"] == "success":
            self.deleteInterfaceVlan(vlan_id)
            result["errLog"] = tmp["errLog"]
            return result
        # Running cmd2
        tmp = self.command(cmd2, prompt=prompt2)
        if not tmp["state"] == "success":
            self.deleteInterfaceVlan(vlan_id)
            result["errLog"] = tmp["errLog"]
            return result
        # Running cmd3
        tmp = self.command(cmd3, prompt=prompt3)
        if not tmp["state"] == "success":
            self.deleteInterfaceVlan(vlan_id)
            result["errLog"] = tmp["errLog"]
            return result
        # Checking...
        if self.interfaceVlanExist(vlan_id)["status"]:
            result["conent"] = "The configuration was created by Forwarder."
            result["status"] = True
        else:
            # The configuration was not created and rolled back.
            self.deleteInterfaceVlan(vlan_id)
            result["errLog"] = tmp["errLog"]
        return result

    def basicInfo(self, cmd="display version"):
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
            "error": "(Unrecognized command|Invalid command)[\s\S]+",
        }
        tmp = self.privilegeMode()
        runningDate = -1
        if tmp["status"]:
            result = self.command(cmd=cmd, prompt=prompt)
            if result["state"] == "success":
                dataLine = re.search(" uptime:? .+(day|year|week).*", result["content"])
                if dataLine is not None:
                    tmp = re.search("([0-9]+) years?", dataLine.group())
                    if tmp:
                        runningDate += int(tmp.group(1)) * 365
                    tmp = re.search("([0-9]+) weeks?", dataLine.group())
                    if tmp:
                        runningDate += int(tmp.group(1)) * 7
                    tmp = re.search("([0-9]+) days?", dataLine.group())
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

    def showOSPF(self, cmd="display ospf peer  brief"):
        njInfo = {
            "status": True,
            "content": [],
            "errLog": ""
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "(Invalid Input|Bad command|[Uu]nknown command|Unrecognized command|Invalid command)[\s\S]+",
        }
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            return tmp
        result = self.command(cmd, prompt)
        dataLine = re.findall("[0-9]{1,3}.*", result["content"])
        if len(dataLine) == 0:
            return njInfo
        for line in dataLine:
            line = line.split()
            if len(line) == 4:
                njInfo["content"].append(
                    {
                        "neighbor-id": line[2],
                        "pri": "",
                        "state": line[3],
                        "uptime": "",
                        "address": line[0],
                        "deadTime": "",
                        "interface": line[1]
                    }
                )
            else:
                # The line does not matched data of expection.
                continue
        return njInfo

    def createObjectGroupIPAddress(self, host=[]):
        njInfo = {
            "status": True,
            "content": [],
            "errLog": ""
        }
        if isinstance(host, list):
            if len(host) == 0:
                raise IOError("hosts's value should not be empty.")
        else:
            raise IOError("host's formate is incorrect.")
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            raise IOError(tmp["errLog"])
        objectGroupName = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + "." + str(random.randint(100000, 999999))
        cmd = "object-group ip address {objectGroupName}".format(objectGroupName=objectGroupName)
        prompt = {
            "success": "[\r\n]+\S+{objectGroup}\] ?$".format(objectGroup="-obj-grp-ip-" + objectGroupName)
        }
        # Mode of entry into object-group-ip-address
        result = self.command(cmd, prompt)
        if not result["state"] == "success":
            raise IOError(result["errLog"])
        # Create object-group ip address
        i = 0
        for ip in host:
            if re.search("\-", ip):
                ipA, ipB = ip.split("-")
                cmd = "{i} network host address {ipA} {ipB}".format(i=i, ipA=ipA, ipB=ipB)
            else:
                cmd = "{i} network host address {ip}".format(i=i, ip=ip)
            i += 1
            result = self.command(cmd, prompt)
            errLine = "(Invalid Input|Bad command|[Uu]nknown command|Unrecognized command|Invalid command|Wrong|Too many)"
            if not result["state"] == "success" or re.search(errLine, result["content"], flags=re.IGNORECASE):
                raise IOError(result["content"])
        njInfo = {"status": True, "content": objectGroupName}
        return njInfo

    def createObjectGroupService(self, configuration, serviceName):
        """
        @ parame configuration: 'service udp source gt 0 destination eq 30002' or 'service udp source gt 0 destination eq 30002'
        @ parame serviceName: name of object-group-service.
        """
        njInfo = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        cmdA = "object-group service {serviceName}".format(serviceName=serviceName)
        promptA = {
            "success": "[\r\n]+\S+{serviceName}\] ?$".format(serviceName="-obj-grp-service-" + serviceName)
        }
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            raise IOError(tmp["errLog"])
        result = self.command(cmdA, promptA)
        if not result["state"] == "success":
            raise IOError(result["errLog"])
        promptB = {
            "success": "[\r\n]+\S+{serviceName}\] ?$".format(serviceName="-obj-grp-service-" + serviceName)
        }
        result = self.command(configuration, promptB)
        errLine = "(Invalid Input|Bad command|[Uu]nknown command|Unrecognized command|Invalid command|Wrong|Too many)"
        if not result["state"] == "success" or re.search(errLine, result["content"]):
            raise IOError(result["errLog"])
        njInfo = {"status": True, "content": serviceName}
        return njInfo

    def isExistObjectGroupService(self, configuration):
        """
        @ parame configuration: 'service udp source gt 0 destination eq 30002' or 'service udp source gt 0 destination eq 30002'
        """
        njInfo = {
            "status": False,
            "content": "",
            "errLog": "The object-group is not exist."
        }
        prompt = {
            "success": "[\r\n]+\S+\] ?$",
        }
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            raise IOError(tmp["errLog"])
        cmd = '''display object-group service'''
        result = self.command(cmd, prompt)
        if not result["state"] == "success":
            raise IOError(result["errLog"])
        serviceName = None
        for line in result["content"].split("\r\n"):
            tmp = re.search("Service object group (\S+):", line)
            # Get name of object-group's service
            if tmp:
                serviceName = tmp.group(1)
                continue
            # Match configuration
            if re.search(configuration, line):
                njInfo = {"status": True, "content": serviceName}
                break
        return njInfo

    def isExistObjectPolicyIP(self, policyName):
        """
        @parame policyName: any string
        """
        njInfo = {
            "status": False,
            "content": "",
            "errLog": "The object-group-policy {policyName} is not exist.".format(policyName=policyName)
        }
        prompt = {
            "success": "[\r\n]+\S+\] ?$",
        }
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            raise IOError(tmp["errLog"])
        cmd = "display object-policy ip"
        tmp = self.command(cmd=cmd, prompt=prompt)
        if not tmp["state"] == "success":
            raise IOError(tmp["errLog"])
        cmdA = "object-policy ip {policyName}".format(policyName=policyName)
        cmdB = "display this"
        promptA = {
            "success": "[\r\n]+\S+\-object-policy-ip-{policyName}\] ?$".format(policyName=policyName),
        }
        if re.search("Object-policy ip {policyName}".format(policyName=policyName), tmp["content"]):
            tmp = self.command(cmdA, promptA)
            if not tmp["state"] == "success":
                raise IOError(tmp["errLog"])
            # Get list of rules.
            tmp = self.command(cmdB, promptA)
            if not tmp["state"] == "success":
                raise IOError(tmp["errLog"])
            ruleID = 0
            for line in tmp["content"].split("\r\r\n"):
                result = re.search("rule ([0-9]+)", line)
                if result:
                    ruleID = int(result.group(1)) + 1
            njInfo = {"status": True, "content": ruleID}
        return njInfo

    def isExistObjectGroupIPAddress(self, hostList=[]):
        """
        @param hostList: ['10.0.0.1','10.0.0.2-10.0.0.3']
        njInfo = {"status":True,"content":"object-group-name"}
        """
        if not isinstance(hostList, list):
            raise IOError("The parameter's formate is incorrect.Its formate should is ['10.,0.0.1','192.168.1.1','192.168.2.100-192.168.2.200']")
        hostList = DEVICELIST(hostList).getIpList()
        hostList = sorted(hostList)
        njInfo = {
            "status": False,
            "content": "",
            "errLog": "The object-group ip is not exist."
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "(Invalid Input|Bad command|[Uu]nknown command|Unrecognized command|Invalid command)[\s\S]+",
        }
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            raise IOError(tmp["errLog"])
        cmd = '''dis object-group ip address | include "Ip address object group"'''
        result = self.command(cmd, prompt)
        if not result["state"] == "success":
            return result
        allGroups = []
        # Getting all groups of object.
        for line in result["content"].split("\r\n"):
            tmp = re.search("Ip address object group (\S+):", line)
            if tmp:
                allGroups.append(tmp.group(1))
        # Enter a mode of object-group,and then get hosts of all.
        # example: {"object-group-a":["10.0.0.1","10.0.0.2"]}
        allObjectIP = {}
        for group in allGroups:
            cmdA = "object-group ip address {objectGroup}".format(objectGroup=group)
            prompt = {
                "success": "[\r\n]+\S+{objectGroup}\] ?$".format(objectGroup="-obj-grp-ip-" + group)
            }
            # Enter a mode of object-group
            tmp = self.command(cmd=cmdA, prompt=prompt)
            if not tmp["state"] == "success":
                raise IOError(tmp["errLog"])
            cmdB = "dis this"
            # Get datas of object-group
            tmp = self.command(cmd=cmdB, prompt=prompt)
            if not tmp["state"] == "success":
                raise IOError(tmp["errLog"])
            hosts = []
            for line in tmp["content"].split("\r\n"):
                # Get single ip.
                info = re.search("[0-9]+ network host address ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", line)
                if info:
                    hosts.append(info.group(1))
                    continue
                # Get ip range.
                info = re.search("[0-9]+ network range ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", line)
                if info:
                    iplist = [info.group(1) + "-" + info.group(2)]
                    hosts.append(DEVICELIST(iplist).getIpList())
            cmdC = "quit"
            promptC = {
                "success": "[\r\n]+\S+\] ?$"
            }
            tmp = self.command(cmd=cmdC, prompt=promptC)
            if not tmp["state"] == "success":
                raise IOError(tmp["errLog"])
            allObjectIP[group] = hosts
        # Match whether there are existing object-group.
        for group, value in allObjectIP.items():
            if hostList == sorted(value):
                njInfo = {"status": True, "content": group}
                break
        return njInfo

    def addObjectPolicyIP(self, policyName, configuration, comment):
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            raise IOError(tmp["errLog"])
        cmdA = "object-policy ip {policyName}".format(policyName=policyName)
        promptA = {
            "success": "[\r\n]+\S+\-object-policy-ip-{policyName}\] ?$".format(policyName=policyName),
        }
        errLine = "(Invalid Input|Bad command|[Uu]nknown command|Unrecognized command|Invalid command|Wrong|Too many)"
        tmp = self.command(cmdA, promptA)
        if not tmp["state"] == "success":
            return tmp
        # Create rule
        tmp = self.command(configuration, promptA)
        if not tmp["state"] == "success" or re.search(errLine, tmp["content"]):
            raise IOError(tmp["content"])
        # set comment
        tmp = self.command(comment, promptA)
        if not tmp["state"] == "success":
            if re.search(errLine, tmp["content"]):
                raise IOError(tmp["content"])
            else:
                return tmp
        return tmp

    def createSecurityPolicy(self,
                             sourceHost=[],
                             destinationHost=[],
                             policyName=None,
                             comment="",
                             serviceParam={"protocol": "tcp/udp",
                                           "sourcePort": None,  # '80' or '80-90'
                                           "sourcePortType": "eq/gt/lt/range",
                                           "destinationPort": None,  # '80' or '80-90'
                                           "destinationPortType": "eq/gt/lt/range"}):
        """
        @sourcdeHost:     list type, ex: ["10.0.0.1",".10.0.0.3-10.0.0.5","192.168.1.1"];
        @destinationHost: list type, ex: ["10.0.0.1","10.0.0.2-10.0.0.5","192.168.1.1"];
        @policyName:      string type , ex: TestName;
        @comment:         strying type, ex: test-comment;
        @ serviceParam:   dict type, ex:
                          {"protocol":"tcp",
                           "sourcePort":None or '890' or '900-999',
                           "sourcePortType":"eq" or "lt" or "gt" or "range",
                           "destinationPort":None or '890' or '900-999',
                           "destinationPortType":"eq" or "lt" or "gt" or "range",
                          }
        return {"status":False/True,"content":"...","errLog":"Cause failed facotr"}
        """
        # Check whether parameters meet thee requirements.
        if not isinstance(comment, str):
            raise IOError("comment's formate should be a string and not be empty.")
        else:
            if re.search("^ *$", comment):
                raise IOError("comment's format should not be empty")
        if not isinstance(policyName, str):
            raise IOError("policyName's format should be a string and not be empty")
        else:
            if re.search("^ *$", policyName):
                raise IOError("policyName's format should not be empty")
        if not isinstance(sourceHost, list):
            raise IOError("sourceHost's formate should is a list,ex: ['10.0.0.1','10.0.0.1-10.0.0.3']")
        elif not isinstance(destinationHost, list):
            raise IOError("destinationHost's formate should is a list,ex: ['10.0.0.1','10.0.0.1-10.0.0.3']")
        elif not isinstance(serviceParam, dict):
            raise IOError("serviceParam's formate should is a dict.plase use help(createSecurityPolicy) to see details.")
        else:
            if serviceParam.has_key("protocol"):
                if (not serviceParam["protocol"] == "tcp") and (not serviceParam["protocol"] == "udp"):
                    raise IOError("serviceParam's formate is incorrect.plase use help(createSecurityPolicy) to see details.")
            else:
                raise IOError("serviceParam's formate should is a dict and incloude key of protocol.plase use help(createSecurityPolicy) to see details.")
            if serviceParam.has_key("sourcePort"):
                if (not isinstance(serviceParam["sourcePort"], str)) and (not serviceParam["sourcePort"] is None):
                    raise IOError("serviceParam's formate is incorrect.plase use help(createSecurityPolicy) to see details.")
            else:
                raise IOError("serviceParam's formate is incorrect.plase use help(createSecurityPolicy) to see details.")
            if serviceParam["sourcePort"] is not None:
                if serviceParam.has_key("sourcePortType"):
                    if (not serviceParam["sourcePortType"] == "eq") and (not serviceParam["sourcePortType"] == "gt") and (not serviceParam["sourcePortType"] == "lt") and (not serviceParam["sourcePortType"] == "range"):
                        raise IOError("serviceParam's formate is incorrect.plase use help(createSecurityPolicy) to see details.")
                else:
                    raise IOError("serviceParam's formate is incorrect.plase use help(createSecurityPolicy) to see details.")
            else:
                if serviceParam.has_key("sourcePortType"):
                    raise IOError("Since serviceParame['sourcePort'] is None,serviceParam['sourcePortType'] should not be exist.")
            if serviceParam.has_key("destinationPort"):
                if (not isinstance(serviceParam["destinationPort"], str)) and (not serviceParam["destinationPort"] is None):
                    raise IOError("serviceParam's formate is incorrect.plase use help(createSecurityPolicy) to see details.")
            else:
                raise IOError("serviceParam's formate is incorrect.plase use help(createSecurityPolicy) to see details.")
            if not serviceParam["destinationPort"] is None:
                if serviceParam.has_key("destinationPortType"):
                    if (not serviceParam["destinationPortType"] == "eq") and (not serviceParam["destinationPortType"] == "gt") and (not serviceParam["destinationPortType"] == "lt") and (not serviceParam["destinationPortType"] == "range"):
                        raise IOError("serviceParam's formate is incorrect.plase use help(createSecurityPolicy) to see details.")
                else:
                    raise IOError("serviceParam's formate is incorrect.plase use help(createSecurityPolicy) to see details.")
            else:
                if serviceParam.has_key("destinationPortType"):
                    raise IOError("Since serviceParame['destinationPort'] is None,serviceParam['destinationPortType'] should not be exist.")
        # Check the service section.
        if serviceParam["sourcePort"] is None:
            sourceSection = ""
        else:
            if serviceParam["sourcePortType"] == "range":
                if not re.search("^[0-9]+\-[0-9]+$", serviceParam["sourcePort"]):
                    raise IOError("sourcePort's format of serviceParam is incorrect.")
                portA, portB = serviceParam["sourcePort"].split("-")
                sourceSection = "source range {portA} {portB}".format(portA=portA, portB=portB)
            else:
                if not re.search("^[0-9]+$", serviceParam["sourcePort"]):
                    raise IOError("sourcePort's format of serviceParam is incorrect.")
                sourceSection = "source {sourcePortType} {port}".format(sourcePortType=serviceParam["sourcePortType"], port=serviceParam["sourcePort"])
        if serviceParam["destinationPort"] is None:
            destinationSection = ""
        else:
            if serviceParam["destinationPortType"] == "range":
                if not re.search("^[0-9]+\-[0-9]+$", serviceParam["destinationPort"]):
                    raise IOError("destinationPort's format of serviceParam is incorrect.")
                portA, portB = serviceParam["destinationPort"].split("-")
                destinationSection = "destination range {portA} {portB}".format(portA=portA, portB=portB)
            else:
                if not re.search("^[0-9]+$", serviceParam["destinationPort"]):
                    raise IOError("destinationPort's format of serviceParam is incorrect.")
                destinationSection = "destination {destinationPortType} {port}".format(destinationPortType=serviceParam["destinationPortType"], port=serviceParam["destinationPort"])
        configuration = "0 service {protocol} {sourceSection} {destinationSection}".format(protocol=serviceParam["protocol"], sourceSection=sourceSection, destinationSection=destinationSection)
        # Check whether the object-policy is exist.
        tmp = self.isExistObjectPolicyIP(policyName)
        if not tmp["status"]:
            return tmp
        ruleID = tmp["content"]
        result = self.isExistObjectGroupIPAddress(sourceHost)
        # Create object-group-ip-address of sourceHost if the object-group is not exist.
        if result["status"] is True:
            sourceObjectGroupIPName = result["content"]
        else:
            tmp = self.createObjectGroupIPAddress(sourceHost)
            if tmp["status"] is False:
                return tmp
            sourceObjectGroupIPName = tmp["content"]
        result = self.isExistObjectGroupIPAddress(destinationHost)
        # Create object-group-ip-address of destinationHost if the object-group is not exist.
        if result["status"] is True:
            destinationObjectGroupIPName = result["content"]
        else:
            tmp = self.createObjectGroupIPAddress(destinationHost)
            if tmp["status"] is False:
                return tmp
            destinationObjectGroupIPName = tmp["content"]
        tmp = self.isExistObjectGroupService(configuration)
        serviceName = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + "." + str(random.randint(100000, 999999))
        if not tmp["status"]:
            # Create object-group-service if that is not exist.
            tmp = self.createObjectGroupService(configuration, serviceName)
            if not tmp["status"]:
                return tmp
        configurationB = "rule {ruleID} pass source-ip {sourceObjectGroupIPName} destination-ip {destinationObjectGroupIPName} service {serviceName} counting ".format(ruleID=ruleID, sourceObjectGroupIPName=sourceObjectGroupIPName, destinationObjectGroupIPName=destinationObjectGroupIPName, serviceName=serviceName)
        comment = "rule {ruleID} comment {comment}".format(comment=comment, ruleID=ruleID)
        tmp = self.addObjectPolicyIP(policyName, configurationB, comment)
        if tmp["status"] is True:
            tmp = self.commit()
        return tmp

    def showRun(self):
        cmd = "display current-configuration"
        tmp = self.generalMode()
        if not tmp["status"]:
            # Switch failure.
            return tmp
        njInfo = self.command(cmd, prompt={"success": "[\r\n]+\S+> ?$"})
        if not njInfo["state"] == "success":
            njInfo["status"] = False
        else:
            njInfo["content"] = "\r\r\n".join(njInfo["content"].split("\r\r\n")[1:-1])
        return njInfo

    def showHostname(self):
        # cmd = 'display current-configuration | i sysname'
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        cmd = "display current-configuration | i sysname"
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = result["content"].split()
            if tmp:
                njInfo["content"] = tmp[1]
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

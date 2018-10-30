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
[Core][forward] Base device class for huawei basic device method, by using paramiko module.
"""

import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError
from forward.utils.paraCheck import checkIP


class BASEHUAWEI(BASESSHV2):
    """This is a manufacturer of huawei, using the
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
                           prompt={"success": "Are you sure to continue\?\[Y/N\] ?$",
                                   "error": "Error:Incomplete command[\s\S]+"})
        if tmp["state"] == "success":
            continueCommandResult = self.command("Y", prompt={"success": "successfully[\s\S]+[\r\n]+\S+.+> ?$"})
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

    def generalMode(self):
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Get the current position before switch to general mode.
        # Demotion,If device currently mode-level greater than 2, It only need to execute `end`.
        if self.mode > 1:
            tmp = self.command("return", prompt={"success": "[\r\n]+\S+.+> ?$"})
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
        sendEnableResult = self.command("system-view", prompt={"success": "[\r\n]+\S+.+\] ?$",
                                                               "error": "[\r\n]+\S+.+> ?$"})
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
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
            "success": "[sS]oftware[\s\S]+[\r\n]+\S+(>|\]) ?$",
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            currentSection = "vlanName"
            isContinueLine = False
            for _vlanInfo in result["content"].split("\r\n"):
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _interfaceInfo in result["content"].split("\r\n"):
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
            "success": "\r\n\r\n\S+.+(>|\]) ?$",
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
                tmp = re.search("([a-z]+)\-duplex", _interfaceInfo)
                if tmp:
                    lineInfo["duplex"] = tmp.group(1)
                else:
                    lineInfo["duplex"] = ""
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
        result["errLog"] = "Vlan {vlan_id} doest not exist.".format(vlan_id=vlan_id)
        return result

    def createVlan(self, vlan_id, description="None"):
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
        cmd = "vlan {vlan_id}\rdescription {description}".format(vlan_id=vlan_id, description=description)
        prompt = {
            "success": "[\r\n]+\S+.+vlan{vlan_id}\] ?$".format(vlan_id=vlan_id),
            "error": "Error:[\s\S]+",
        }
        # runing command of vlan.
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
            "success": "[\r\n]+\S+.+vlan{vlan_id}\] ?$".format(vlan_id=vlan_id),
            "error": "Error:[\s\S]+",
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
            "success": "[\r\n]+\S+.+(\]|>) ?$",
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
            result["errLog"] = "The vlan({vlan_id}) doest not exists,\
thus can't create interface-vlan.".format(vlan_id=vlan_id)
            return result
        prompt1 = {
            "success": "[\r\n]+\S+.+Vlanif{vlan_id}\] ?$".format(vlan_id=vlan_id),
            "error": "[\r\n]+\S+.+\] ?$",
            # "error": "(Invalid|Error|Illegal|marker|Incomplete)[\s\S]+",
        }
        prompt2 = {
            "success": "{cmd2}[\r\n]+\S+.+Vlanif{vlan_id}\] ?$".format(vlan_id=vlan_id, cmd2=cmd2),
            "error": "(Invalid|Error|Illegal|marker|Incomplete)[\s\S]+",
        }
        prompt3 = {
            "success": "{cmd3}[\r\n]+\S+.+Vlanif{vlan_id}\] ?$".format(vlan_id=vlan_id, cmd3=cmd3),
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

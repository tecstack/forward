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
#

"""
-----Introduction-----
[Core][forward] Base device class for cisco basic device method, by using paramiko module.
"""

import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError
from forward.utils.paraCheck import checkIP


class BASECISCO(BASESSHV2):
    """This is a manufacturer of cisco, using the
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
        data = self.command("copy running-config  startup-config",
                            prompt={"success": "Copy complete[\s\S]+[\r\n]+\S+# ?$"})
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
        sendPassword = self.command(self.privilegePw, prompt={"password": "[pP]assword.*|Access denied.*|Bad secrets.*",
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
        cmd = "show run ntp"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        tmp = self.privilegeMode()
        if not tmp["status"]:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("ntp server ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"])
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
        cmd = '''show running-config  |  i log'''
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        tmp = self.privilegeMode()
        if not tmp["status"]:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("loggin server ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"], flags=re.IGNORECASE)
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
        cmd = '''show run | i  "snmp-server host"'''
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        tmp = self.privilegeMode()
        if not tmp["status"]:
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
            'content': "",
            'errLog': ''
        }
        cmd = "show version"
        prompt = {
            "success": "[vV]ersion[\s\S]+[\r\n]+\S+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        tmp = self.privilegeMode()
        if not tmp["status"]:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("(software|system).*version(.*)", result["content"], flags=re.IGNORECASE)
            if tmp.lastindex == 2:
                njInfo["content"] = tmp.group(2).strip()
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
            "error": "Invalid command[\s\S]+",
        }
        """
        2206 VLAN2206                         active    Po12, Po13, Eth1/3, Eth1/2/1
                                              Eth1/2/2, Eth1/2/3, Eth1/2/4
        2207 VLAN2207                         active    Po12, Po13, Eth1/3, Eth1/2/1
                                              Eth1/2/2, Eth1/2/3, Eth1/2/4

        LAN Type         Vlan-mode
        ---- -----        ----------
        1    enet         CE
        """
        tmp = self.privilegeMode()
        if not tmp["status"]:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            currentSection = "vlanName"
            isContinueLine = False
            for _interfaceInfo in result["content"].split("\r\n"):
                if re.search("\-\-\-\-", _interfaceInfo):
                    continue
                if re.search("^[0-9]", _interfaceInfo) and currentSection == "vlanName":
                    isContinueLine = True
                    # Get the line of vlan.
                    lineInfo = {
                        "id": "",
                        "description": "",
                        "status": "",
                        "interface": [],
                        "type": "",
                    }
                    tmp = re.search("([0-9]+)\s+(\S+)\s+([a-z]+)\s+(.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["id"] = tmp.group(1)
                        lineInfo["description"] = tmp.group(2)
                        lineInfo["status"] = tmp.group(3)
                        if tmp.lastindex == 4:
                                lineInfo["interface"] = tmp.group(4).split(", ")
                        njInfo["content"].append(lineInfo)
                    continue
                elif isContinueLine is True and not re.search("VLAN Type",
                                                              _interfaceInfo) and currentSection == "vlanName":
                    for _interface in _interfaceInfo.split(","):

                        lineInfo = njInfo["content"].pop()
                        lineInfo["interface"].append(_interface.strip())
                        njInfo["content"].append(lineInfo)
                    continue
                else:
                    isContinueLine = False
                if re.search("VLAN Type", _interfaceInfo):
                    currentSection = "vlanType"
                    continue
                if currentSection == "vlanType":
                    if re.search("^[0-9]", _interfaceInfo):
                        tmp = re.search("([0-9]+) ([a-z]+)", _interfaceInfo)
                        if tmp:
                            vlanID = tmp.group(1)
                            vlanType = tmp.group(2)
                            i = 0
                            for _vlan in njInfo["content"]:
                                if vlanID == _vlan["id"]:
                                    njInfo["content"][i]["type"] = vlanType
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
        cmd = "show routing"
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        tmp = self.privilegeMode()
        if not tmp["status"]:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _interfaceInfo in result["content"].split("\r\n"):
                # record the route table.
                if re.search("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]{1,2}", _interfaceInfo):
                    '''try:
                        """Store the previously acquired routing information
                        before processing the new routing information"""
                        njInfo["content"].append(lineInfo)
                    except Exception:
                        pass'''
                    lineInfo = {
                        "net": "",
                        "mask": "",
                        "via": "",
                        "metric": "",
                        "type": "",
                        "via": "",
                    }
                    # Get net of the route.
                    lineInfo["net"] = _interfaceInfo.split("/")[0]
                    # Get mask of net of the route.
                    lineInfo["mask"] = _interfaceInfo.split("/")[1].split(",")[0]
                    njInfo["content"].append(lineInfo)
                elif re.search("\*via [0-9]", _interfaceInfo):
                    lineInfo = njInfo["content"].pop()
                    lineInfo["via"] = re.search("\*via (.*?),", _interfaceInfo).group(1)
                    lineInfo["interface"] = _interfaceInfo.split(",")[1].strip()
                    lineInfo["type"] = _interfaceInfo.split()[-1]
                    njInfo["content"].append(lineInfo)
            # save the last record.
            try:
                njInfo["content"].append(lineInfo)
            except Exception:
                pass
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
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        tmp = self.privilegeMode()
        if not tmp["status"]:
            return tmp
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            i = 0
            for _interfaceInfo in result["content"].split("\r\n\r\n"):
                i += 1
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
                if i == 0:
                    _interfaceInfo = _interfaceInfo.split("\r\r\n")[1]
                    tmp = re.search("(.*) is", _interfaceInfo)
                    if tmp:
                        lineInfo["interfaceName"] = tmp.group(1).strip()
                        njInfo["content"].append(lineInfo)
                    continue
                else:
                    tmp = re.search("(.*?) is", _interfaceInfo)
                    if tmp:
                        lineInfo["interfaceName"] = tmp.group(1).strip()
                    else:
                        continue
                    tmp = re.search("admin state is (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["adminState"] = tmp.group(1).strip()
                    # MTU
                    tmp = re.search("MTU ([0-9]+)", _interfaceInfo)
                    if tmp:
                        lineInfo["mtu"] = tmp.group(1)
                    # description
                    tmp = re.search("Description: (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["description"] = tmp.group(1).strip()
                    # duplex
                    tmp = re.search("([a-z]+)\-duplex", _interfaceInfo)
                    if tmp:
                        lineInfo["duplex"] = tmp.group(1)
                    # Speed.
                    tmp = re.search("\-duplex, (.*),?", _interfaceInfo)
                    if tmp:
                        lineInfo["speed"] = tmp.group(1)
                    # ip.
                    tmp = re.search("Internet Address is (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["ip"] = tmp.group(1).split("/")[0]
                    # mac.
                    tmp = re.search(", address: ([\S]+)", _interfaceInfo)
                    if tmp:
                        lineInfo["mac"] = tmp.group(1)
                    # Last link flapped
                    tmp = re.search("Last link flapped (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["linkFlap"] = tmp.group(1).strip()
                    # Inpute rate.
                    tmp = re.search("300 seconds input rate (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["inputRate"] = tmp.group(1).strip()
                    # Output rate.
                    tmp = re.search("300 seconds ouput rate (.*)", _interfaceInfo)
                    if tmp:
                        lineInfo["outputRate"] = tmp.group(1).strip()

                    njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def addUser(self, username, password):
        """Increating a user on the device.
        """
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Assembling command
        cmd = "username {username} password {password}".format(username=username, password=password)

        # Switch to privilege mode.
        switch = self.privilegeMode()
        if not switch["status"]:
            # Switch failure.
            return switch
        # Switch to configure-mode.
        switch = self.configMode()
        if not switch["status"]:
            # Switch failed.
            return switch
        # Run a command
        data = self.command(cmd, prompt={"success": self.basePrompt})
        # Check status
        if re.search("% Invalid|ERROR:", data["content"]):
            result["errLog"] = "%s" % data["content"]
            return result
        if data["state"] == "success":
            result = self.commit()
            return result
        else:
            result["errLog"] = "%s" % data["content"]
        return result

    def deleteUser(self, username):
        """remove a user on the device.
        """
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Assembling command
        cmd = "no username {username} ".format(username=username)
        # Switch to privilege mode.
        switch = self.privilegeMode()
        if not switch["status"]:
            # Switch failure.
            return switch
        # Switch to configure-mode.
        switch = self.configMode()
        if not switch["status"]:
            # Switch failed.
            return switch
        # Run a command
        data = self.command(cmd, prompt={"success": self.basePrompt})
        # Check status
        if re.search("% Invalid|ERROR:", data["content"]):
            result["errLog"] = "%s" % data["content"]
            return result
        if data["state"] == "success":
            result = self.commit()
            return result
        else:
            result["errLog"] = "%s" % data["content"]
        return result

    def changePassword(self, username, password):
        return self.addUser(username, password)

    def getUserList(self, username=None):
        """Get all user from  the device.
        resunt format:
        {
            "username-1":{"username":"username-1","level"   :15},
            "username-2":{"username":"username-2","level"   :14}
        }
        """
        result = {
            "status": False,
            "content": {},
            "errLog": ""
        }
        # Assembling command
        if username is None or re.search("^ *$", username):
            cmd = "show running-config | include username"
        else:
            cmd = "show running-config | include username {username}".format(username=username)
        # Switch to privilege mode.
        switch = self.privilegeMode()
        if not switch["status"]:
            # Switch failure.
            return switch
        # Run a command
        data = self.command(cmd, prompt={"success": self.basePrompt})
        # Check status
        if re.search("% Invalid|ERROR:", data["content"]):
            result["errLog"] = "%s" % data["content"]
            return result
        if data["state"] is None:
            # The command was not executed correctly
            result["errLog"] = "%s" % data["content"]
            return result
        # Seasrch user
        tmp = re.findall("username.*", data["content"])
        for _line in tmp:
            line = _line.split()
            try:
                _username = line[1]
            except IndexError:
                continue
            result["content"][_username] = {"username": _username, "level": 0}
        result["status"] = True
        return result

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
            "success": "[\r\n]+\S+.+config\-vlan\)(#|>) ?$",
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
            "success": "[\r\n]+\S+.+config\)(#|>) ?$",
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
            vlan_id = "Vlan" + vlan_id
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
        # Enter config-mode.
        tmp = self.configMode()
        if not tmp["status"]:
            # Failed to enter configuration mode
            return tmp
        cmd = "no interface vlan {vlan_id}".format(vlan_id=vlan_id)
        prompt = {
            "success": "[\r\n]+\S+.+config\)(#|>) ?$",
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
        cmd1 = "interface vlan {vlan_id}".format(vlan_id=vlan_id)
        cmd2 = "description {description}".format(description=description)
        cmd3 = "ip address {ip} {mask}".format(ip=ip, mask=mask)
        # Forward need to check if The vlan exists,before creating.
        if not self.vlanExist(vlan_id)["status"]:
            # no exists.
            result["errLog"] = "The vlan({vlan_id}) does not exists,\
thus can't create interface-vlan.".format(vlan_id=vlan_id)
            return result
        # Enter config-mode.
        tmp = self.configMode()
        if not tmp["status"]:
            # Failed to enter configuration mode
            return tmp
        prompt1 = {
            "success": "[\r\n]+\S+.+config\-if\)# ?$",
            "error": "[\r\n]+\S+.+config\)# ?$",
            # "error": "(Invalid|Error|Illegal|marker|Incomplete)[\s\S]+",
        }
        prompt2 = {
            "success": "{cmd2}[\r\n]+\S+.+config\-if\)# ?$".format(cmd2=cmd2),
            "error": "(Invalid|Error|Illegal|marker|Incomplete)[\s\S]+",
        }
        prompt3 = {
            "success": "{cmd3}[\r\n]+\S+.+config\-if\)# ?$".format(cmd3=cmd3),
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
            result["content"] = "The configuration was created by Forwarder."
            result["status"] = True
        else:
            # The configuration was not created and rolled back.
            self.deleteInterfaceVlan(vlan_id)
            result["errLog"] = "The configuration was not created and rolled back"
        return result
    def basicInfo(self):
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
        return njInfo

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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
-----Introduction-----
[Core][forward] Device class for Raisecom.
"""
from forward.devclass.baseSSHV2 import BASESSHV2
import re


class BASERAISECOM(BASESSHV2):
    """This is a manufacturer of raisecom, using the
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
                            prompt={"success": "successfully[\s\S]+[\r\n]+.+# ?$"})
        if data["state"] is None:
            result["errLog"] = "Failed save configuration, \
                               Info: [{content}] , [{errLog}]".format(content=data["content"], errLog=data["errLog"])
        else:
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
        cmd = "show running-config  | include  ntp"
        prompt = {
            "success": "[\s\S]+[\r\n]+\S+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
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
        cmd = '''show running-config  | include log'''
        prompt = {
            "success": "[\s\S]+[\r\n]+\S+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("logging host ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
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
        cmd = '''show run | include  "snmp-server host"'''
        prompt = {
            "success": "[\s\S]+[\r\n]+.+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
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
            "success": "[vV]ersion[\s\S]+[\r\n]+.+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("(software|system).*version:?(.*)", result["content"], flags=re.IGNORECASE)
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
            "success": "[\s\S]+[\r\n]+.+(#|>) ?$",
            "error": "Error input[\s\S]+",
        }
        """
             State   Status  Priority Member-Ports           VLAN Name
        -------------------------------------------------------------------------------
        160  active  static  --       P 49-50                VLAN0160
        164  active  static  --       P 1-36,49-50           VLAN0164
        """
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _interfaceInfo in result["content"].split("\r\n"):
                if re.search("\-\-\-\-", _interfaceInfo):
                    continue
                if re.search("^[0-9]", _interfaceInfo):
                    # Get the line of vlan.
                    lineInfo = {
                        "id": "",
                        "description": "",
                        "status": "",
                        "interface": [],
                        "type": "",
                        "state": "",
                    }
                    tmp = re.search("[0-9]+", _interfaceInfo)
                    if tmp:
                        _line = _interfaceInfo.split()
                        lineInfo["id"] = _line[0]
                        lineInfo["state"] = _line[1]
                        lineInfo["status"] = _line[2]
                        # Example: "1-2,49-50,60"
                        for i in _line[5].split(","):
                            seg = i.split("-")
                            seg = [int(x) for x in seg]
                            if len(seg) == 1:
                                seg.append(seg[-1] + 1)
                            else:
                                seg[-1] = seg[-1] + 1
                            # [1,2,49,50,60]
                            lineInfo["interface"].extend(range(*seg))
                        lineInfo["description"] = _line[6]
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
        cmd = "show running-config  | include  route"
        prompt = {
            "success": "[\s\S]+[\r\n]+.+(#|>) ?$",
            "error": "Error input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _interfaceInfo in result["content"].split("\r\n"):
                # record the route table.
                if re.search("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", _interfaceInfo):
                    '''try:
                        """Store the previously acquired routing information
                        before processing the new routing information"""
                        njInfo["content"].append(lineInfo)
                    except Exception:
                        pass'''
                    lineInfo = {
                        "net": "",
                        "mask": "",
                        "metric": "",
                        "type": "",
                        "description": "",
                        "interface": "",
                        "via": "",
                    }
                    # Get net of the route.
                    lineInfo["net"] = _interfaceInfo.split()[2]
                    # Get mask of net of the route.
                    lineInfo["mask"] = _interfaceInfo.split()[3]
                    lineInfo["via"] = _interfaceInfo.split()[4]
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
        cmd = "show running-config |  include interface"
        prompt = {
            "success": "[\s\S]+[\r\n]+\S+(#|>) ?$",
            "error": "Error input[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            i = 0
            for _interfaceInfo in result["content"].split("\r\n"):
                i += 1
                lineInfo = {"interfaceName": "",
                            "members": [],
                            "lineState": "",
                            "adminState": "",
                            "description": "",
                            "speed": "",
                            "type": "",
                            "inputRate": "",
                            "outputRate": "",
                            "crc": "",
                            "linkFlap": "",
                            }
                # Get name of the interface
                tmp = re.search("interface port ([0-9]+)", _interfaceInfo)
                if not tmp:
                    continue
                port = tmp.group(1)
                lineInfo["interfaceName"] = port
                # Get the interface used to get the details of the interface.
                detail = self.command(cmd="show interface  port-list {port}".format(port=port), prompt=prompt)
                # Obtain rows with detailed information.
                tmp = re.search("P{port}.*".format(port=port), detail["content"])
                if tmp:
                    _line = tmp.group().split()
                    lineInfo["adminState"] = _line[1]
                    lineInfo["spped"] = _line[3]
                    lineInfo["duplex"] = _line[4]
                    lineInfo["lineState"] = _line[6]
                njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

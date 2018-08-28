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

"""     It applies only to models of network equipment  mx960
        See the detailed comments mx960.py
"""
import re
from forward.devclass.baseTELNET import BASETELNET
from forward.utils.forwardError import ForwardError


class BASEJUNIPER(BASETELNET):
    """This is a manufacturer of juniper, using the
    telnet version of the protocol, so it is integrated with BASETELNET library.
    """
    def __init__(self, *args, **kws):
        BASETELNET.__init__(self, *args, **kws)
        self.basePrompt = r"(>|#) *$"

    def _recv(self, _prompt):
        """The user receives the message returned by the device.
        """
        data = {"status": False,
                "content": "",
                "errLog": ""}
        # If the host prompt is received, the message is stopped.
        i = self.channel.expect([r"%s" % _prompt], timeout=self.timeout)
        try:
            if i[0] == -1:
                raise ForwardError('Error: receive timeout')
            data['status'] = True
            # Get result
            data['content'] = i[-1]
        except ForwardError, e:
            data['errLog'] = str(e)
        return data

    def addUser(self, username, password, admin=False):
        """Create a user on the device.
        """
        # Separate commands to create administrator accounts and common accounts.
        if admin:
            command = "set system login user {username} class read-only\n".format(username=username)
        else:
            command = "set system login user {username} class  ABC\n".format(username=username)
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if not username or not password:
                # Specify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            checkPermission = self._configMode()   # swith to config terminal mode.
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                # adduser
                self.channel.write(command)
                # recv result
                data = self._recv(self.prompt)
                if not data['status']:
                    # break
                    raise ForwardError(data['errLog'])
                # execute useradd command
                self.channel.write('set system login user {username} \
                                   authentication plain-text-password\n'.format(username=username))
                i = self.channel.expect([r"New password:", r"%s" % self.prompt], timeout=self.timeout)
                result = i[-1]
                if re.search('error|invalid', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                # Enter password
                self.channel.write("{password}\n".format(password=password))
                # check password
                i = self.channel.expect([r"Retype new password:", r"%s" % self.prompt], timeout=self.timeout)
                # repassword
                if i[0] == 0:
                    self.channel.write("{password}\n".format(password=password))
                    # check password
                    i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
                    if i[0] == 0:
                        result = i[-1]
                        if re.search('error|invalid', result, flags=re.IGNORECASE):
                            raise ForwardError(result)
                        else:
                            # set password is successed.
                            data = self._commit()
                            # exit config terminal mode.
                            self._exitConfigMode()
                    elif i[0] == -1:
                        raise ForwardError('Error: receive timeout')
                elif i[0] == 1:
                    # password wrong
                    raise ForwardError(i[-1])
                elif i[0] == -1:
                    # timeout
                    raise ForwardError('Error: receive timeout')
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def deleteUser(self, username):
        """Delete a user on the device
        """
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if not username:
                raise ForwardError('Please specify a username')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                # delete user
                self.channel.write('delete system login user {username}\n'.format(username=username))
                i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
                result = i[-1]
                if re.search('error|invalid', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                else:
                    # Save
                    data = self._commit()
                    # exit config terminal mode.
                    self._exitConfigMode()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def changePassword(self, username, password):
        """Modify the password for the device account.
        """
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if not username or not password:
                # Specify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                # execute useradd command
                self.channel.write('set system login user {username} \
                                    authentication plain-text-password\n'.format(username=username))
                i = self.channel.expect([r"New password:", r"%s" % self.prompt], timeout=self.timeout)
                result = i[-1]
                if re.search('error|invalid', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                # Enter password
                self.channel.write("{password}\n".format(password=password))
                # check password
                i = self.channel.expect([r"Retype new password:", r"%s" % self.prompt], timeout=self.timeout)
                if i[0] == 0:
                    # repassword
                    self.channel.write("{password}\n".format(password=password))
                    # check password
                    i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
                    if i[0] == 0:
                        # Get result.
                        result = i[-1]
                        if re.search('error|invalid', result, flags=re.IGNORECASE):
                            raise ForwardError(result)
                        else:
                            # change password is successed.
                            data = self._commit()
                            # exit config terminal mode.
                            self._exitConfigMode()
                    elif i[0] == -1:
                        raise ForwardError('Error: receive timeout')
                elif i[0] == 1:
                    # password wrong
                    raise ForwardError(i[-1])
                elif i[0] == -1:
                    # timeout
                    raise ForwardError('Error: receive timeout')
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
                data['errLog'] = str(e)
                data['status'] = False
        return data

    # def bindBandwidth(self, ip='', bandwidth=''):
    #     njInfo = {"status": False,
    #               "content": "",
    #               "errLog": ""}
    #     mx960Bandwidth = Bandwidth(ip=ip, bandwidth=bandwidth, shell=self)
    #     njInfo = mx960Bandwidth.bindBandwidth()
    #     return njInfo
    #
    # def deleteBindIPAndBandwidth(self, ip='', bandwidth=''):
    #     njInfo = {"status": False,
    #               "content": "",
    #               "errLog": ""}
    #     mx960Bandwidth = Bandwidth(ip=ip, bandwidth=bandwidth, shell=self)
    #     njInfo = mx960Bandwidth.deleteBindIPAndBandwidth()
    #     return njInfo
    def generalMode(self):
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Get the current position before switch to general mode.
        # Demotion,If device currently mode-level greater than 2, It only need to execute `end`.
        if self.mode > 1:
            tmp = self.command("quit", prompt={"success": "[\r\n]+\S+.+> ?$",
                                               "error": "unknown command[\s\S]+"})
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
        # devices of Juniper have no config-mode.
        self.mode = 2
        result["status"] = True
        return result

    def configMode(self):
        # Switch to config mode.
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # If value of the mode is 2,start switching to configure-mode.
        sendConfig = self.command("configure", prompt={"success": "[\r\n]+\S+.+# ?$",
                                                       "error": "unknown command[\s\S]+\S+.+> ?$"})
        if sendConfig["state"] == "success":
            # switch to config-mode was successful.
            result["status"] = True
            self.mode = 3
            return result
        elif sendConfig["state"] is None:
            result["errLog"] = sendConfig["errLog"]
            return result

    def commit(self):
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Switch to privilege-mode.
        result = self.configMode()
        if not result["status"]:
            # Switch failure.
            return result
        # Excute a command.
        data = self.command("commit",
                            prompt={"success": "complete[\s\S]+[\r\n]+\S+# ?$",
                                    "error": "unknown command[\s\S]+"})
        if data["state"] is None:
            result["errLog"] = "Failed save configuration, \
                               Info: [{content}] , [{errLog}]".format(content=data["content"], errLog=data["errLog"])
        else:
            result["content"] = "The configuration was saved successfully."
            result["status"] = True
        return result

    def showVersion(self):
        # All the show commands must be done in general mode.
        njInfo = {
            'status': False,
            'content': "",
            'errLog': ''
        }
        # Before you execute the show command, you must go into general mode
        tmp = self.generalMode()
        if tmp["status"] is False:
            return tmp
        cmd = "show version"
        prompt = {
            "success": "[\r\n]+\S+> ?$",
            "error": "unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("Base OS boot (\S+)", result["content"])
            if tmp:
                njInfo["content"] = tmp.group(1).strip("[]")
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
        # Before you execute the show command, you must go into general mode
        tmp = self.generalMode()
        if tmp["status"] is False:
            return tmp
        cmd = "show interfaces extensive"
        prompt = {
            "success": "[\r\n]+\S+.+> ?$",
            "error": "unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = re.findall("[\S\s]+?\r\n\r\n", result["content"])
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
                tmp = re.search("interface:? (\S+)", line)
                if tmp:
                    lineInfo["interfaceName"] = tmp.group(1).strip(",")
                else:
                    continue
                # Get line state of the interface.
                tmp = re.search("link is (.*)", line)
                if tmp:
                    lineInfo["lineState"] = tmp.group(1).strip().lower()
                # Get the admin state of the interface.
                tmp = re.search(", (.+), Physical", line)
                if tmp:
                    lineInfo["adminState"] = tmp.group(1).strip().lower()
                # Get mtu of the interface.
                tmp = re.search("MTU: (\d+)", line)
                if tmp:
                    lineInfo["mtu"] = tmp.group(1).strip()
                # Get mac of the interface.
                tmp = re.search("Hardware address: (.*)", line)
                if tmp:
                    lineInfo["mac"] = tmp.group(1).strip()
                # Get the type of the interface.
                tmp = re.search("Link-level type: ([A-Za-z]+)", line)
                if tmp:
                    lineInfo["type"] = tmp.group(1).strip()
                # Get input rate of the interface.
                tmp = re.search("Input rate     : (.*)", line)
                if tmp:
                    lineInfo["inputRate"] = tmp.group(1).strip()
                #  Get output rate of the interface.
                tmp = re.search("Output rate    : +(.*)", line)
                if tmp:
                    lineInfo["outputRate"] = tmp.group(1).strip()
                # Get description of the interface.
                tmp = re.search("Description: (.*)", line)
                if tmp:
                    lineInfo["description"] = tmp.group(1).strip()
                # Get duplex of therface.
                tmp = re.search("([A-Za-z]+)\-duplex", line)
                if tmp:
                    lineInfo["duplex"] = tmp.group(1)
                # Get speed of the interface.
                tmp = re.search("Speed: (\S+),", line)
                if tmp:
                    lineInfo["speed"] = tmp.group(1)
                njInfo["content"].append(lineInfo)
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
        # Before you execute the show command, you must go into general mode
        tmp = self.generalMode()
        if tmp["status"] is False:
            return tmp
        cmd = "show route"
        prompt = {
            "success": "[\r\n]+\S+.+> ?$",
            "error": "unknown command[\s\S]+",
        }
        # Get name of routes.
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            allLine = result["content"].split("\r\n")[1:-1]
            for line in allLine:
                tmp = re.search("(\d+\.\d+\.\d+\.\d+)/(\d{1,2}).*\[([A-Za-z]+)/.*\]", line)
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
                    lineInfo["type"] = tmp.group(3).lower()
                    njInfo["content"].append(lineInfo)
                tmp = re.findall("(\d+\.\d+\.\d+\.\d+)? ?via (.*)", line)
                if tmp:
                    lineInfo = njInfo["content"][-1]
                    lineInfo["via"] = tmp[0][0]
                    lineInfo["interface"] = tmp[0][1]
                    if njInfo["content"][-1]["via"] == "":
                        njInfo["content"][-1] = lineInfo
                    else:
                        njInfo["content"].append(lineInfo)
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
        # Before you execute the show command, you must go into general mode
        tmp = self.generalMode()
        if tmp["status"] is False:
            return tmp
        prompt = {
            "success": "[\r\n]+\S+.+> ?$",
            "error": "unknown command[\s\S]+",
        }
        result = self.command("show configuration snmp ", prompt=prompt)
        if result["state"] == "success":
            # Separate information from each configuration section
            allSection = re.findall("trap-group[\s\S]+?\r\n\}", result["content"])
            # everyone of configuration.
            """targets {
                        172.16.147.34;
                                172.16.147.35;
                     }
            """
            for section in allSection:
                # Get port of the snmp server.
                tmp = re.search("destination-port (\d+)", section)
                if tmp:
                    port = tmp.group(1)
                else:
                    port = ""
                # Get ip of the snmp server.
                ip = re.findall("\d+\.\d+\.\d+\.\d+", section)
                for address in ip:
                    lineInfo = {"ip": address, "port": port}
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
        cmd = "show configuration | display set | match ntp"
        # Before you execute the show command, you must go into general mode
        tmp = self.generalMode()
        if tmp["status"] is False:
            return tmp
        prompt = {
            "success": "[\r\n]+\S+.+> ?$",
            "error": "unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("ntp server ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"])
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
        cmd = "show configuration | display set | match syslog"
        # Before you execute the show command, you must go into general mode
        tmp = self.generalMode()
        if tmp["status"] is False:
            return tmp
        prompt = {
            "success": "[\r\n]+\S+.+> ?$",
            "error": "unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("syslog host ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"])
            njInfo["content"] = list(set(sorted(tmp)))
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
        cmd = "show configuration | display set | match vlan-id "
        # Before you execute the show command, you must go into general mode
        tmp = self.generalMode()
        if tmp["status"] is False:
            return tmp
        prompt = {
            "success": "[\r\n]+\S+.+> ?$",
            "error": "unknown command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _vlanInfo in result["content"].split("\r\n"):
                tmp = re.search("vlan-id ([0-9]+)", _vlanInfo)
                lineInfo = {
                    "id": "",
                    "description": "",
                    "status": "",
                    "interface": [],
                    "type": "",
                }
                # Get id of the vlan.
                if tmp:
                    lineInfo["id"] = tmp.group(1)
                    if lineInfo in njInfo["content"]:
                        # If the record already exists in njinfo, it is ignored
                        continue
                    else:
                        njInfo["content"].append(lineInfo)
                    continue
                # Get range of the vlans.
                vlanGroup = re.search("vlan-id-list (\d+)\-(\d+)", _vlanInfo)
                if vlanGroup:
                    # The starting id of the vlan.
                    startVlan = int(vlanGroup.group(1))
                    # The ending id of the vlan.
                    endVlan = int(vlanGroup.group(2))
                    for vlanId in range(startVlan, endVlan + 1):
                        lineInfo = {
                            "id": "",
                            "description": "",
                            "status": "",
                            "interface": [],
                            "type": "",
                        }
                        lineInfo["id"] = str(vlanId)
                        if lineInfo in njInfo["content"]:
                            # If the record already exists in njinfo, it is ignored
                            continue
                        else:
                            njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

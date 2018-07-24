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
[Core][forward] Device class for n7018.
"""
from forward.devclass.baseHuawei import BASEHUAWEI
from forward.utils.forwardError import ForwardError
import re


class S9312(BASEHUAWEI):
    """This is a manufacturer of huawei, so it is integrated with BASEHUAWEI library.
    """
    def isVlan(self, vlan):
        """Check if the Vlan exists.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # switch to enable mode.
        tmp = self.privilegeMode()
        if not tmp:
            raise ForwardError(tmp["errLog"])
        tmp = self.execute("display vlan {vlan}".format(vlan=vlan))
        if not tmp["status"]:
            raise ForwardError(tmp["errLog"])
        # If the above fails, exit immediately
        try:
            if re.search("Error: The VLAN does not exist", tmp["content"]):
                # vlan not is exitsts
                info["status"] = False
            else:
                # vlan is exists
                info["status"] = True
        except Exception, e:
            info["status"] = False
            info["errLog"] = str(e)
        return info

    def createVlan(self, vlan=None, ascription=None):
        """Create a Vlan.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        if (vlan is None) or (ascription is None):
            raise ForwardError("You must specify the `vlan` and `ascription` parameters")
        """Warning: that vlan should be checked
           by the 'self.isvlan(vlan) method
           before setting up the vlan"""
        # swith to config mode
        info = self._configMode()
        if not info["status"]:
            raise ForwardError(info["errLog"])
        try:
            # enter vlan
            info["content"] = ""
            self.shell.send("vlan {vlan}\n".format(vlan=vlan))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024)
            # Get host prompt
            self.getPrompt()
            if not re.search('.*-vlan', self.prompt):
                raise ForwardError("Failed to enter vlan mode,command:vlan {vlan}".format(vlan=vlan))
            # set host's ascription
            info["content"] = ""
            # Send command.
            self.shell.send("name {ascription}\n".format(ascription=ascription))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024)
            # Get host prompt.
            self.getPrompt()
            # save  the configuration.
            tmp = self._commit()
            if not tmp["status"]:
                raise ForwardError("The configuration command has been executed,\
                                    but the save configuration failed! [{info}]".format(info=info["content"]))
            else:
                if not self.isVlan(vlan)["status"]:
                    # check vlan
                    raise ForwardError("Vlan has been set and has been saved, but the final\
                                        check found no configuration, so failed.info:[%s]" % tmp["content"])
                else:
                    # create successed. exit config mode
                    info["status"] = True
        except Exception, e:
            info["status"] = False
            info["errLog"] = str(e)
        return info

    def isTrunkInInterface(self, port=None, vlan=None):
        """Check the relationship between interface and turnk.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        if (vlan is None) or (port is None):
            raise ForwardError('Specify the `vlan` and `port` parameters')
        # switch to enable mode
        tmp = self.privilegeMode()
        if not tmp["status"]:
            raise ForwardError(tmp['errLog'])
        # else ,successed
        while True:
            tmp = self.execute("display current-configuration interface Eth-Trunk")
            if not tmp["status"]:
                raise ForwardError(tmp["errLog"])
            if re.search("Command is in use by", tmp["content"]):
                # Recheck
                continue
            # Keyword search.
            data = re.search("#[\r\n]+(interface Eth-Trunk{port}[\r\n]+[\s\S]*?)#".format(port=port), tmp["content"])
            if not data:
                # No configuration found
                raise ForwardError("Not found port(port) info".format(port=port))
            try:
                if re.search("port trunk allow-pass vlan .*{vlan}".format(vlan=vlan), data.group(1)):
                    # found it.
                    info["status"] = True
                else:
                    info["status"] = False
                    info["errLog"] = tmp["content"]
                break
            except Exception, e:
                info["errLog"] = str(e)
                info["status"] = False
                break
        return info

    def trunkOpenVlan(self, port=None, vlan=None):
        """Create a vlan on turnk.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # Parameter check.
        if (vlan is None) or (port is None):
            raise ForwardError('Specify the `vlan` and `port` parameters')
        # get parameter
        tmp = self.execute("display cur interface Eth-Trunk {port}".format(port=port))
        if not tmp["status"]:
            raise ForwardError(tmp["errLog"])
        # search parameter
        data = re.search("#[\r\n]+(interface Eth-Trunk{port}[\r\n]+[\s\S]*?)#".format(port=port), tmp["content"])
        if not data:
            raise ForwardError("Not found port(port) [{info}]".format(port=port, info=tmp["content"]))
        else:
            # Keyword search.
            data = re.search("(port trunk allow-pass vlan.*)", data.group(1))
            if not data:
                raise ForwardError("`Port turnk allow-pass vlan ...` is not found")
            else:
                # remove the end '\n' and '\r'
                cmd = "{parameter} {vlan}".format(parameter=data.group(1).strip("\r\n"), vlan=vlan)
        # switch to config mode
        tmp = self._configMode()
        if not tmp["status"]:
            raise ForwardError(tmp["errLog"])
        try:
            # switch to port mode
            info["content"] = ""
            # Send command.
            self.shell.send("interface Eth-Trunk {port}\n".format(port=port))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024)
            # Get new host prompt.
            self.getPrompt()
            # Keyword search.
            if not re.search('Trunk{port}'.format(port=port), self.prompt):
                raise ForwardError("Failed to enter port mode,command:interface \
Eth-Trunk {port} [{info}]".format(port=port, info=info["content"]))
            # set vlan
            info["content"] = ""
            self.shell.send("{cmd}\n".format(cmd=cmd))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024)
            # Get new host prompt.
            self.getPrompt()
            # save configuration
            tmp = self._commit()
            if not tmp["status"]:
                raise ForwardError("The configuration command has been executed,\
                                    but the save configuration failed! [{info}]".format(info=info["content"]))
            # check configuration
            tmp = self.isTrunkInInterface(port=port, vlan=vlan)
            if not tmp["status"]:
                raise ForwardError("Vlan has been set and has been saved, but the final\
                                    check found no configuration, so failed.info:[%s]" % tmp["errLog"])
            else:
                info["status"] = True
        except Exception, e:
            info["errLog"] = str(e)
            info["status"] = False
        return info

    def isGateway(self, vlan):
        """Check that the gateway exists.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # switch to enable mode.
        tmp = self.privilegeMode()
        if not tmp:
            raise ForwardError(tmp["errLog"])
        # Execute command.
        tmp = self.execute("display current-configuration interface Vlanif {vlan}".format(vlan=vlan))
        if not tmp["status"]:
            raise ForwardError(tmp["errLog"])
        # If the above fails, exit immediately
        try:
            if re.search("Error: Wrong parameter found at", tmp["content"]):
                info["status"] = False
            else:
                info["status"] = True
        except Exception, e:
            info["status"] = False
            info["errLog"] = str(e)
        return info

    def setGateway(self, vlan=None, ascription=None, ip=None):
        """Create a gateway
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # Parameters check.
        if (vlan is None) or (ascription is None) or (ip is None):
            raise ForwardError("You must specify `vlan` and `ascription` and `ip` parameters")
        # Reset gateway ip address
        ip = re.sub('[0-9]+$', '254', ip)
        # switch to config mode
        tmp = self._configMode()
        if not tmp["status"]:
            raise ForwardError(tmp["errLog"])
        try:
            # switch to vlanif mode
            info["content"] = ""
            # Send command.
            self.shell.send("interface Vlanif {vlan}\n".format(vlan=vlan))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024)
            # Get new host prompt.
            self.getPrompt()
            if not re.search('Vlanif', self.prompt):
                raise ForwardError("Failed to enter Vlanif mode,command:port Vlanif {vlan}".format(vlan=vlan))
            # set ascription
            info["content"] = ""
            self.shell.send("description {ascription}\n".format(ascription=ascription))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024)
            # Get new host prompt.
            self.getPrompt()
            # set ip
            info["content"] = ""
            # Send command.
            self.shell.send("ip address {ip} 255.255.255.0\n".format(ip=ip))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024)
            # Check
            if re.search("Error: The specified IP address is invalid", info["content"]):
                raise ForwardError("Error: The specified IP address is invalid,IP should be a network segment")
            # Get new host prompt.
            self.getPrompt()
            # save the configuration
            tmp = self._commit()
            if not tmp["status"]:
                raise ForwardError("The configuration command has been executed,\
                                    but the save configuration failed! [{info}]".format(info=info["content"]))
            else:
                # Check that the gateway configuration exists.
                if not self.isGateway(vlan)["status"]:
                    # check vlan
                    raise ForwardError("Gateway has been set and has been saved, but the final\
                                        check found no configuration, so failed.info:[%s]" % tmp["content"])
                else:
                    # create successed. exit config mode
                    info["status"] = True
        except Exception, e:
            info["status"] = False
            info["errLog"] = str(e)
        return info

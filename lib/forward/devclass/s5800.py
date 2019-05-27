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
[Core][forward] Device class for S5800.
"""
from forward.devclass.baseFenghuo import BASEFENGHUO
from forward.utils.forwardError import ForwardError
import re


class S5800(BASEFENGHUO):
    """This is a manufacturer of fenghuo, so it is integrated with BASEFENGHUO library.
    """

    def isVlanInPort(self, vlan=None, port=None):
        """Check that the Vlan exists in the port.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # Parameters check.
        if (vlan is None) or (port is None):
            raise ForwardError('Specify the `vlan` and `port` parameters')
        # Execute command.
        info = self.execute("show  run")
        if not info["status"]:
            raise ForwardError(info["errLog"])
        try:
            # Keyword search
            tmp = re.search("\![\r\n]+interface gigaethernet {port}[\s\S]*por\
t link-type (access|trunk)[\s\S]*port .* vlan .*{vlan}".format(vlan=vlan, port=port), info["content"])
            if tmp:
                # Vlan in the port, case 1
                if tmp.group(1) == "access":
                    raise ForwardError("Configuration found, but port link - type is 'access', Not a trunk")
                info["content"] = tmp.group().split("ABCDEFG")
                info["status"] = True
            else:
                # No exists'
                raise ForwardError('No exists')
        except Exception as e:
            info["errLog"] = str(e)
            info["status"] = False
        return info

    def createVlanInPort(self, port=None, vlan=None):
        """Create a vlan on the port.
        """
        # Prameters check.
        if (port is None) or (vlan is None):
            raise ForwardError('Specify the `port` parameter')
        info = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            # switch to enable mode
            tmp = self.privilegeMode()
            if not tmp["status"]:
                raise ForwardError(tmp['errLog'])
            # else ,successed
            # switch to config mode
            tmp = self._configMode()
            if not tmp["status"]:
                raise ForwardError(tmp['errLog'])
            # else ,successed
            # switch to port mode
            info["content"] = ""
            self.shell.send("interface gigaethernet {port}\n".format(port=port))
            # Host prompt is modified
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode()
            # release host prompt
            self.getPrompt()
            # Check the port mode
            if not re.search('config.*-ge', self.prompt):
                raise ForwardError('Switch to port mode is failed [%s]' % info["content"])
            # else successed.
            tmp = self.execute("port link-type trunk")
            if not tmp["status"]:
                raise ForwardError(tmp["errLog"])
            tmp = self.execute("port trunk allow-pass vlan {vlan}".format(vlan=vlan))
            if not tmp["status"]:
                raise ForwardError(tmp["errLog"])
            else:
                # Check the returned 'tmp['content']', which indicates failure if it contains' Failed '
                if re.search('%Failed', tmp["content"]):
                    raise ForwardError('Execute the command "port trunk allow-pass vlan" is failed ,\
                                        result is [%s] ' % tmp["content"])
                # else  successed
            tmp = self.execute("no shutdown")
            if not tmp["status"]:
                raise ForwardError(tmp["errLog"])
            # quit port mode
            self.shell.send("quit\n")
            info["content"] = ""
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode()
            self.getPrompt()
            # save configuration
            tmp = self._commit()
            if not tmp["status"]:
                raise ForwardError(tmp["errLog"])
            # Verify that it is correct
            tmp = self.isVlanInPort(port=port, vlan=vlan)
            if not tmp["status"]:
                raise ForwardError("The configuration command has been executed,\
                                    but the check configuration does not exist! [%s]" % tmp["errLog"])
            else:
                # successed
                info["content"] = "successed"
                info["status"] = True
        except Exception as e:
            info["errLog"] = str(e)
            info["status"] = False
        return info

    def isTrunkInInterface(self, port=None, vlan=None):
        """Check the relationship between interface and turnk.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # Prameters check.
        if (vlan is None) or (port is None):
            raise ForwardError('Specify the `vlan` and `port` parameters')
        while True:
            # Execute command.
            info = self.execute("show  run")
            if not info["status"]:
                raise ForwardError(info["errLog"])
            try:
                # Keyword search.
                tmp = re.search("interface eth-trunk {port}[\r\n]+ mode .*[\r\n]+ por\
    t .*[\r\n]+ port .* vlan .*{vlan}".format(port=port, vlan=vlan), info['content'])
                if tmp:
                    # Exists.
                    info["status"] = True
                    break
                elif re.search('Command is in use by', info["content"]):
                    # Rechecking...
                    continue
                else:
                    info["errLog"] = info['errLog']
                    break
            except Exception as e:
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
        # Parameters check.
        if (vlan is None) or (port is None):
            raise ForwardError('Specify the `vlan` and `port` parameters')
        try:
            # switch to enable mode
            tmp = self.privilegeMode()
            if not tmp["status"]:
                raise ForwardError(tmp['errLog'])
            # else ,successed
            # switch to config mode
            tmp = self._configMode()
            if not tmp["status"]:
                raise ForwardError(tmp['errLog'])
            # else ,successed
            # switch to port mode
            self.shell.send("interface eth-trunk {port}\n".format(port=port))
            # Host prompt is modified
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode()
            # release host prompt
            self.getPrompt()
            # Keyword search.
            if not re.search("config.*-eth.*-trunk.*-{port}".format(port=port), self.prompt):
                raise ForwardError('[trunkOpenVlan] Switch to port mode is failed [%s]' % info["content"])
            # Execute command.
            tmp = self.execute("port trunk allow-pass vlan {vlan}".format(vlan=vlan))
            if not tmp["status"]:
                raise ForwardError(tmp["errLog"])
            else:
                # Check the returned 'tmp['content']', which indicates failure if it contains' Failed '
                if re.search('%Failed', tmp["content"]):
                    raise ForwardError('Execute the command "port trunk allow-pass vlan" is failed ,\
                                        result is [%s] ' % tmp["content"])
            # quit port mode
            self.shell.send("quit\n")
            info["content"] = ""
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode()
            # save configuration
            self.getPrompt()
            # Save the configuration.
            tmp = self._commit()
            if not tmp["status"]:
                raise ForwardError(tmp["errLog"])
            # Verify that it is correct
            tmp = self.isTrunkInInterface(port=port, vlan=vlan)
            if not tmp["status"]:
                raise ForwardError("The configuration command has been executed,\
                                    but the check configuration does not exist! [%s]" % tmp['errLog'])
            info["status"] = True
        except Exception as e:
            info["errLog"] = str(e)
            info["status"] = False
        return info

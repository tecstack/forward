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
[Core][forward] Base device class for cisco basic device method, by using paramiko module.
Author: Cheung Kei-Chuen, Wang Zhe
"""

import re
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.utils.forwardError import ForwardError


class BASECISCO(BASESSHV2):
    """This is a manufacturer of cisco, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def privilegeMode(self):
        # Switch to privilege mode.
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Get the current position Before switch to privileged mode.
        if (not self.mode == 1) and (not self.mode == 2) and (not self.mode == 3):
            result["errLog"] = "The mode level of the current device is too high,\
                                please reduce to configuration-mode and then switch."
            return result
        # Demotion,If device currently mode  is config-mode, just need to execute `end`.
        if self.mode == 3:
            exitResult = self.command("end", prompt={"success": self.basePrompt})
            if not exitResult["state"] == "success":
                result["errLog"] = "Demoted from configuration-mode to privilege-mode failed."
                return result
            else:
                # Switch is successful.
                self.mode = 2
                result["status"] = True
                return result
        if self.mode == 2:
            # The device is currently in privilege-mode ,so there is no required to switch.
            result["status"] = True
            return result
        # Start switching.
        sendEnable = self.command("enable", prompt={"password": "[pP]assword.*", "noPassword": self.basePrompt})
        if sendEnable["state"] == "noPassword":
            # The device not required a password,thus switch is successful.
            result["statue"] = True
            self.mode = 2
            return result
        elif sendEnable["state"] is None:
            result["errLog"] = "Unknow error."
            return result
        # If device required a password,then send a password to device.
        sendPassword = self.command(self.privilegePw, prompt={"password": "[pP]assword.*",
                                                              "noPassword": self.basePrompt})
        if sendPassword["state"] == "password":
            # Password error,switch is failed.
            result["errLog"] = "Password of the privilege mode is wrong."
        elif sendPassword["state"] == "noPassword":
            # switch is successful.
            result["sttus"] = True
            self.mode = 2
            return result
        else:
            result["errLog"] = "Unknow error."
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
        data = self.command("write", prompt={"success": self.prompt})
        if data["state"] is None:
            result["errLog"] = "Excute a command is failed, Info: %s" % data["content"]
            return result
        # Checking key words.
        if re.search("(\[OK\])|(Copy complete)|(successfully)", data["content"]):
            result['status'] = True
        else:
            result["errLog"] = "The save command has been run, but the result failed.Info:%s" % data["content"]
        return result

    def addUser(self, username, password):
        """Increating a user on the device.
        """
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        # Assembling command
        cmd = "username {username} password {password}\n"
        # Switch to privilege mode.
        result = self.privilegeMode()
        if not result["status"]:
            # Switch failure.
            return result
        # Excute a command
        data = self.command(cmd, prompt={"success": self.prompt})
        if data["sate"] == "success":
            result = self.commit()
            return result
        else:
            result["errLog"] = "‘add user’ was failed: %s" % data["content"]
        return result

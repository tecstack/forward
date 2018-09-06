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
[Core][forward] Device class for vlb.
Author: wangzhe
"""

import re
from forward.devclass.baseBrocade import BASEBROCADE


class VLB(BASEBROCADE):
    """This is a manufacturer of brocade, so it is integrated with BASEBROCADE library.
    """
    def zcliMode(self):
        """Execute the czli command and enter a new mode.
        """
        # Flag zcli mode is False.
        self.isZcliMode = False
        # Set command.
        cmd = "zcli\n"
        # Set host prompt.
        zcliPrompt = re.escape("admin@127.0.0.1 > ")
        result = {
            'status': True,
            'content': '',
            'errLog': ''
        }
        # Clean buffer.
        self.cleanBuffer()
        # Login status check.
        if self.isLogin:
            self.shell.send(cmd)
            try:
                while not re.search(zcliPrompt, result["content"]):
                    result['content'] += self.shell.recv(1024).decode
                # Save the host prompt before entering the zcli mode
                self.oldPrompt = self.prompt
                # update host prompt
                self.prompt = zcliPrompt
                # Flag zcli mode is True.
                self.isZcliMode = True
                result['status'] = True
            except Exception as e:
                # Error,flag zcli mode is False.
                self.isZcliMode = False
                result['status'] = False
                result['errLog'] = '[ZCLI Error]: {info}'.format(info=str(e))
        else:
            # not login
            result['status'] = False
            result['errLog'] = '[Execute Error]: device not login'
        return result

    def exitZcli(self):
        # Exit the zcli mode and return to normal mode.
        cmd = "exit\n"
        result = {
            'status': False,
            'content': '',
            'errLog': ''
        }
        # Login status check.
        if self.isLogin:
            if self.isZcliMode:
                self.shell.send(cmd)
                # Restore the host prompt
                self.prompt = self.oldPrompt
                try:
                    while not re.search(self.prompt, result["content"]):
                        result['content'] += self.shell.recv(1024).decode
                    # The switch mode status is False
                    self.isZcliMode = False
                    result['status'] = True
                except Exception as e:
                    result['status'] = False
                    result['errLog'] = '[ZCLI Error]: {info}'.format(info=str(e))
            else:
                result["errLog"] = "Error: The current state is not zcli mode"
        else:
            # not login
            result['status'] = False
            result['errLog'] = '[Execute Error]: device not login'
        return result

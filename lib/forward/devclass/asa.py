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
[Core][forward] Device class for asa.
"""

import re
from forward.devclass.baseCisco import BASECISCO
from forward.utils.forwardError import ForwardError


class ASA(BASECISCO):
    """The device model belongs to the cisco series
    so the attributes and methods of BASECISCO are inherited.
    """
    def cleanBuffer(self):
        """Since the device is inconsistent with the details
        of the other Cisco series, the method needs to be rewritten
        to fit the device of this type.
        """
        if self.shell.recv_ready():
                self.shell.recv(4096)
        self.shell.send('\r\n')
        buff = ''
        """ When after switching mode, the prompt will change,
        it should be based on basePromptto check and at last line"""
        while not re.search(self.basePrompt, buff.split('\n')[-1]):
            try:
                # Cumulative return result
                buff += self.shell.recv(1024)
                # Remove the \x charactor
                buff += re.sub("\x07", "", buff)
            except Exception:
                raise ForwardError('Receive timeout [%s]' % (buff))

    def addUser(self, username, password):
        # Overriding methods
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} password {password}\n')

    def changePassword(self, username, password):
        # Overriding methods
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} password {password}\n')

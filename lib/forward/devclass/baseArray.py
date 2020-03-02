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
[Core][forward] Device class for Array.
"""
from forward.devclass.baseSSHV2 import BASESSHV2
# import re


class BASEARRAY(BASESSHV2):
    """This is a manufacturer of baer, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def generalMode(self):
        pass

    def privilegeMode(self):
        pass

    def showLog(self):
        pass

    def showVersion(self):
        pass

    def showNtp(self):
        pass

    def showInterface(self):
        pass

    def showRun(self):
        pass

    def showHostname(self):
        pass

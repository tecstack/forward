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
[Core][forward] Device class for n5596.
"""
# import re
from forward.devclass.baseCisco import BASECISCO


class N5596(BASECISCO):
    """This is a manufacturer of cisco, so it is integrated with BASECISCO library.
    """

    def addUser(self, username, password, admin=False):
        """Because the device of this model is different from the other Cisco
        devices in creating user parameters, it is rewritten.
        """
        # default is not admin
        if admin:
            return BASECISCO.addUser(self,
                                     username=username,
                                     password=password,
                                     addCommand='user {username} password {password} role network-admin\n')
        else:
            return BASECISCO.addUser(self,
                                     username=username,
                                     password=password,
                                     addCommand='user {username} password {password} role priv-1\n')

    def _commit(self):
        """Because the device of this model is different from the other
        Cisco devices in commit  parameters, it is rewritten.
        """
        return BASECISCO._commit(self,
                                 saveCommand='copy running-config startup-config',
                                 exitCommand='end')

    def changePassword(self, username, password):
        """Because the device of this model is different from the other
        Cisco devices in change user's password  parameters, it is rewritten.
        """
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='user {username} password {password} role network-admin\n')

    def basicInfo(self):
        return BASECISCO.basicInfo(self, "show version")

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
[Core][forward] Device class for F510000.
"""
from forward.devclass.baseF5 import BASEF5


class F510000(BASEF5):
    """This is a manufacturer of F5, it is integrated with BASEF5 library.
    """

    def addUser(self, username, password):
        """Because the device of this model is different from the other F5
        devices in creating user parameters, it is rewritten.
        """
        return BASEF5.addUser(self,
                              username=username,
                              password=password,
                              addCommand='user {username} password {password} role network-admin\n')

    def _commit(self):
        """Because the device of this model is different from the other
        F5 devices in deleting user parameters, it is rewritten.
        """
        return BASEF5._commit(self,
                              saveCommand='copy running-config startup-config',
                              exitCommand='end')

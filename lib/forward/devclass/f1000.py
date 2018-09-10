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
[Core][forward] Device class for f1000.
"""
from forward.devclass.baseDepp import BASEDEPP


class F1000(BASEDEPP):
    """This is a manufacturer of depp, it is integrated with BASEDEPP library.
    """
    def showLog(self):
        # Firewall has no syslog configuration
        njInfo = {
            "status": False,
            "content": [],
            "errLog": ""
        }
        njInfo["status"] = True
        return njInfo

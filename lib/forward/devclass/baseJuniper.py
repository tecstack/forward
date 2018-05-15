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
    telnet version of the protocol, so it is integrated with BASELTELNET library.
    """
    def _recv(self, _prompt):
        """The user receives the message returned by the device.
        """
        data = {"status": False,
                "content": "",
                "errLog": ""}
        # If the host prompt is received, the message is stopped.
        i = self.channel.expect([r"%s" % _prompt],
                                timeout=self.timeout)

        if i[0] == -1:
            data["errLog"] = 'Error: receive timeout'
        else:
            data['status'] = True
            # Get result
            data['content'] = i[-1]
        return data

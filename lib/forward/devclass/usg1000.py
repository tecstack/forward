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
[Core][forward] Device class for USG1000.
Author: Cheung Kei-Chuen
"""

import re
from forward.devclass.baseVenustech import BASEVENUSTECH
from forward.utils.forwardError import ForwardError


class USG1000(BASEVENUSTECH):
    """This is a manufacturer of venustech, so it is integrated with BASEVENUSTECH library.
    """

    def _recv(self, _prompt):
        # Gets the return message after the command is executed.
        data = {"status": False,
                "content": "",
                "errLog": ""}
        # If the received message contains the host prompt, stop receiving.
        i = self.channel.expect([r"%s" % _prompt], timeout=self.timeout)
        if i[0] == -1:
            # The supplied host prompt is incorrect, resulting in the receive message timeout.
            data["errLog"] = 'Error: receive timeout'
        else:
            # Successed.
            data['status'] = True
            # Get result.
            data['content'] = i[-1]
        return data

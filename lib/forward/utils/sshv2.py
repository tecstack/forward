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
[Core][forward] Function for sshv2, by using paramiko module.
Author: Cheung Kei-Chuen, Wang Zhe
"""

import paramiko


def sshv2(ip='', username='', password='', timeout=30, port=22):
    # return SSH channel, use ssh.invoke_shell() to active a shell, and resize window size
    njInfo = {
        'status': True,
        'errLog': '',
        'content': ''
    }
    try:
        port = int(port)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password, timeout=timeout)
        njInfo['content'] = ssh
    except Exception, e:
        njInfo['status'] = False
        njInfo['errLog'] = str(e)
    return njInfo

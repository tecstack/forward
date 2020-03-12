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
[Core][forward] Device class for ne40ex8/ne40ex8a.
"""
import re
from forward.devclass.baseHuawei import BASEHUAWEI
# from forward.utils.sshv2 import sshv2


class NE40EX8(BASEHUAWEI):
    """This is a manufacturer of huawei, so it is integrated with BASEHUAWEI library.
    """

    def showRun(self):
        """show the system config
        Returns:
            the system config of the device
        """
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(#|>) ?$",
            "error": "Invalid command[\s\S]+",
        }
        cmd = 'dis cur'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status']:
            njInfo['errLog'] = result['errLog']
            return njInfo
        if result['state'] == 'success':
            njInfo['status'] = True
            njInfo['content'] = result['content']
        return njInfo

    def showHostname(self):
        '''show hostname
        Return:
           device hostname
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        cmd = 'display current-configuration | include sysname'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status']:
            njInfo['errLog'] = result['errLog']
            return njInfo
        if result['state'] == 'success':
            njInfo['content'] = re.findall('sysname (\S+)', result['content'])[0]
            njInfo['status'] = True
            return njInfo
        njInfo['errLog'] = result['errLog']
        return njInfo

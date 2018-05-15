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
[Core][forward] Device class for f1000.
Author: Cheung Kei-chuen
"""

from forward.devclass.baseDepp import BASEDEPP


class F1000(BASEDEPP):
    """This is a manufacturer of depp, it is integrated with BASEDEPP library.
    """
    def getMore(self, bufferData):
        """Automatically get more echo infos by sending a blank symbol
        """
        # if check buffer data has 'more' flag, at last line.
        # if re.search(self.moreFlag, bufferData.split('\n')[-1]):
        # can't used to \n and ' \r' ,because product enter character
        self.shell.send(' ')

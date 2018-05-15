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
[Core][forward] Device class for rg5510.
Author: Cheung Kei-Chuen
"""

from forward.devclass.baseRuijie import BASERUIJIE


class RG5510(BASERUIJIE):
    """This is a manufacturer of ruijie, so it is integrated with BASERUIJIE library.
    """
    def __init__(self, *args, **kws):
        """Since the device's host prompt is different from BASESSHV2,
        the basic prompt for the device is overwritten here.
        """
        BASERUIJIE.__init__(self, *args, **kws)
        self.basePrompt = r'(>|#.*#|\]|\$|\)) *$'

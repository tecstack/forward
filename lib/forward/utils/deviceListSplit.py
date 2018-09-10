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
[Core][Forward] Split deviceList.
['1.1.1.1','2.2.2.2-2.2.2.4'] -> ['1.1.1.1','2.2.2.2','2.2.2.3','2.2.2.4']
Author: Skate from CSDN blog. Wang Zhe
"""


class DEVICELIST:
    def __init__(self, deviceList):
        self.deviceList = deviceList
        self.deviceListSplited = []

    def ipToNum(self, ip):
        # ip address transformat into binary
        ip = [int(x) for x in ip.split('.')]
        return ip[0] << 24 | ip[1] << 16 | ip[2] << 8 | ip[3]

    def numToIp(self, num):
        # binary ip address transformat into x.x.x.x
        return '%s.%s.%s.%s' % ((num & 0xff000000) >> 24,
                                (num & 0x00ff0000) >> 16,
                                (num & 0x0000ff00) >> 8,
                                num & 0x000000ff)

    def getIp(self, ip):
        # input 'x.x.x.x-y.y.y.y' or 'z.z.z.z'
        # output all ip within list belongs to 'x.x.x.x-y.y.y.y', except '0.0.0.0'
        ipRangeList = [self.ipToNum(x) for x in ip.split('-')]
        start, end = ipRangeList[0], ipRangeList[-1]
        return [self.numToIp(num) for num in range(start, end + 1) if num & 0xff]

    def getIpList(self):
        # deviceList:['1.1.1.1','2.2.2.2-2.2.3.4']
        # output all legal ip address within list
        for element in self.deviceList:
            self.deviceListSplited.extend(self.getIp(element))
        return self.deviceListSplited

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
[Core][forward] Device class for sr7750.
"""
from forward.devclass.baseBaer import BASEBAER
import string
import re


class SR7750(BASEBAER):
    """This is a manufacturer of baer, so it is integrated with BASEBAER library."""
    def showInterfacePower(self, port):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unknown command[\s\S]+",
        }
        cmd = 'show port ' + port + ' detail | match dBm'
        resultPower = self.command(cmd=cmd, prompt=prompt)
        if not resultPower['status'] or resultPower['state'] != 'success':
            njInfo['errLog'] = resultPower['errLog']
            return njInfo
        result = {}
        resultPower = resultPower['content'].split('\r\n')
        resultPower.pop(0)
        resultPower.pop(-1)
        for line in resultPower:
            power = line.strip().split()
            if power[4] == 'dBm)':
                _power = power[5]
                _power_high = power[7]
                _power_low = power[8]
            else:
                _power = power[4]
                _power_high = power[6]
                _power_low = power[7]
            if string.atof(_power) > string.atof(_power_high):
                result['TX'] = 'HIGH'
            elif string.atof(_power) < string.atof(_power_low):
                result['TX'] = 'LOW'
            else:
                result['TX'] = 'normal'
            if string.atof(_power) > string.atof(_power_high):
                result['RX'] = 'HIGH'
            elif string.atof(_power) < string.atof(_power_low):
                result['RX'] = 'LOW'
            else:
                result['RX'] = 'normal'
        njInfo['status'] = True
        njInfo['content'] = result
        return njInfo

    def showSyslog(self):
        """show the system syslog server and logbuffer
        example cmd:
            show log syslog

        Returns:
            logbuffer level and syslog server level
        """
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+.+(#|>) ?$",
            "error": "Unknown command[\s\S]+",
        }
        logInfo = {
            'status':True,
            'errLog':'',
            'content':{}
        }
        cmd = 'show log syslog'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo
        syslogList= re.findall('(\d+\.\d+\.\d+\.\d+)\s+\d+\s+(\w+)', result['content'])
        logInfo['content']['syslog_server'] = {}
        for serinfo in syslogList:
            logInfo['content']['syslog_server'][serinfo[0]] = serinfo[1]
        logInfo['content']['logbuffer'] = 'NULL'
        njInfo['status'] = True
        njInfo['content'] = logInfo
        return njInfo

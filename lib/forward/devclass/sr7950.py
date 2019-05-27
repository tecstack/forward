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
[Core][forward] Device class for sr7950.
"""
from forward.devclass.baseBaer import BASEBAER
import string


class SR7950(BASEBAER):
    """This is a manufacturer of baer, so it is integrated with BASEBAER library.
    """
    def showInterfacePower(self, port):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(#|>) ?$",
            "error": "Unknown command[\s\S]+",
        }
        portResult = port.split('/')

        if portResult[0] == '1' and portResult[1] == '1':
            cmd = 'show port ' + port + ' detail | match +'
            resultPower = self.command(cmd=cmd, prompt=prompt)
            if not resultPower['status'] or resultPower['state'] != 'success':
                njInfo['errLog'] = resultPower['errLog']
                return njInfo
            powerLevel = {}
            resultPower = resultPower['content'].split('\r\n')
            resultPower.pop(0)
            resultPower.pop(-1)
            for line in  resultPower:
                power = line.strip().split()
                if power[0] == '1':
                  result['TX_1'] = power[3]
                  result['RX_1'] = power[4]
                elif power[0] == '2':
                  result['TX_2'] = power[3]
                  result['RX_2'] = power[4]
                elif power[0] == '3':
                  result['TX_3'] = power[3]
                  result['RX_3'] = power[4]
                elif power[0] == '4':
                  result['TX_4'] = power[3]
                  result['RX_4'] = power[4]
            if result['TX_1'] < '-4.80' or result['TX_2'] < '-4.80' or result['TX_3'] < '-4.80' or result['TX_4'] < '-4.80':
                powerLevel['TX'] = 'LOW'
            elif result['TX_1'] > '5.00' or result['TX_2'] > '5.00' or result['TX_3'] > '5.00' or result['TX_4'] > '5.00':
                powerLevel['TX'] = 'HIGH'
            else:
                powerLevel['TX'] = 'normal'
            if result['RX_1'] < '-12.10' or result['RX_2'] < '-12.10' or result['RX_3'] < '-12.10' or result['RX_4'] < '-12.10':
                powerLevel['RX'] = 'LOW'
            elif result['RX_1'] > '5.00' or result['RX_2'] > '5.00' or result['RX_3'] > '5.00' or result['RX_4'] > '5.00':
                powerLevel['RX'] = 'HIGH'
            else:
                powerLevel['RX'] = 'normal'
            njInfo['status'] = True
            njInfo['content'] = powerLevel
            return njInfo
        else:
            cmd = 'show port ' + port + ' detail | match dBm'
            resultPower = self.command(cmd=cmd, prompt=prompt)
            if not resultPower['status'] or resultPower['state'] != 'success':
                njInfo['errLog'] = resultPower['errLog']
                return njInfo
            powerLevel = {}
            resultPower = resultPower['content'].split('\r\n')
            resultPower.pop(0)
            resultPower.pop(-1)
            result = {}
            for line in resultPower:
                power = line.strip().split()
                if power[4] == 'dBm)':
                    per = power[5]
                    powerHight = power[7]
                    powerLow = power[8]
                else:
                    per = power[4]
                    powerHight = power[6]
                    powerLow = power[7]
                if string.atof(per) > string.atof(powerHight):
                    result['TX'] = 'HIGH'
                elif string.atof(per) < string.atof(powerLow):
                    result['TX'] = 'LOW'
                else:
                    result['TX'] = 'normal'
                if string.atof(per) > string.atof(powerHight):
                    result['RX'] = 'HIGH'
                elif string.atof(per) < string.atof(powerLow):
                    result['RX'] = 'LOW'
                else:
                    result['RX'] = 'normal'
            njInfo['status'] = True
            njInfo['content'] = result
            return njInfo        

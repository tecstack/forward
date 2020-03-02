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
[Core][forward] Device class for E8000E.
"""
from forward.devclass.baseHuawei import BASEHUAWEI
import re
import string


class E8000E(BASEHUAWEI):
    """This is a manufacturer of huawei, it is integrated with BASEHUAWEI library.
    """
    def showVlan(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "display  vlan"
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            # When encountered '------' characters, start statistics.
            isBegin = False
            for _vlanInfo in result["content"].split("\r\n"):
                if re.search("\-\-\-\-\-\-\-", _vlanInfo):
                    isBegin = True
                    continue
                if isBegin is False:
                    continue
                """
                VLAN ID Type         Status   MAC Learning Broadcast/Multicast/Unicast Property
                --------------------------------------------------------------------------------
                12      common       enable   enable       forward   forward   forward default
                """
                # Get the line of vlan.
                tmp = re.search("([0-9]+)\s+(\S+)\s+(\S+)", _vlanInfo)
                if tmp:
                    lineInfo = {
                        "id": tmp.group(1),
                        "description": "",
                        "type": tmp.group(2),
                        "interface": [],
                        "status": tmp.group(3),
                    }
                    njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

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

    def showSystemUptime(self):
        '''display version
        Return:
           days_of_uptime
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
        cmd = 'display version '
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status']:
            njInfo['errLog'] = result['errLog']
            return njInfo
        if result['state'] == 'success':
            # line=result['content'].split('\n')
            # line.pop(0)
            # line.pop(-1)
            daysUptime = re.findall('is\s+(\d+)\s+days', result['content'])
            njInfo['status'] = True
            njInfo['content'] = 'days: ' + daysUptime[0]
            return njInfo
        else:
            njInfo['errLog'] = result['errLog']
            return njInfo

    def showSystemClock(self):
        '''show the system clock
        Return:
           system clock of the device
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
        cmd = 'display clock'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status']:
            njInfo['errLog'] = result['errLog']
            return njInfo
        if result['state'] == 'success':
            njInfo['status'] = True
            njInfo['content'] = result['content']
            return njInfo
        else:
            njInfo['errLog'] = result['errLog']
            return njInfo

    def showHardware(self):
        """show temperature,fan,power status
        Returns:
            as above
        """
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        tResult = self.command(cmd='display temperature', prompt=prompt)
        if not tResult['status'] or tResult['state'] != 'success':
            njInfo['errLog'] = tResult['errLog']
            return njInfo

        usefulList = []
        dashLine = 0
        emptyLine = 0
        mystr = tResult['content'].split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
            if re.findall('----------', line):
                dashLine = 1
                emptyLine = 0
                continue
            if (line == '\r') or (re.findall('Power monitor cable state', line)):
                dashLine = 0
                emptyLine = 1
                continue
            if (dashLine == 1) and (emptyLine == 0):
                usefulList.append(line)
        temperatureResult = usefulList
        errorDevice = []
        for line in temperatureResult:
            if not re.findall('NORMAL', line):
                errorDevice.append(line)
        pResult = self.command(cmd='display power', prompt=prompt)
        if not pResult['status'] or pResult['state'] != 'success':
            njInfo['errLog'] = pResult['errLog']
            return njInfo
        usefulList = []
        dashLine = 0
        emptyLine = 0
        mystr = pResult['content'].split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
            if re.findall('----------', line):
                dashLine = 1
                emptyLine = 0
                continue
            if (line == '\r') or (re.findall('Power monitor cable state', line)):
                dashLine = 0
                emptyLine = 1
                continue
            if (dashLine == 1) and (emptyLine == 0):
                usefulList.append(line)
        powerResult = usefulList
        for line in powerResult:
            if not re.findall('Normal', line):
                errorDevice.append(line)
        fResult = self.command(cmd='display fan', prompt=prompt)
        if not fResult['status'] or fResult['state'] != 'success':
            njInfo['errLog'] = fResult['errLog']
            return njInfo
        fResult = fResult['content'].split('\n')
        fResult.pop(0)
        fResult.pop(-1)
        for line in fResult:
            if re.findall('Registered', line):
                if not re.findall('YES', line):
                    errorDevice.append('fan')
        if not errorDevice:
            njInfo['status'] = True
            njInfo['content'] = 'check pass'
            return njInfo
        else:
            njInfo['status'] = True
            njInfo['content'] = errorDevice
            return njInfo

    def showCpu(self):
        """show cpu usage
        Returns:
            the device memory used
        """
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        cpuEnough = True
        cmd = 'display health'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo
        dashCount = 1
        contentMatch = False
        usefulList = []
        mystr = result['content'].split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
            if re.findall('CPU Usage', line):
                contentMatch = True
                continue
            if contentMatch is False:
                continue
            if re.findall('----------', line):
                dashCount = dashCount - 1
                continue
            if dashCount < 1:
                usefulList.append(line)
        result = usefulList
        cpuResult = []
        for line in result:
            try:
                value = re.findall('(\d+%)', line.split()[2])[0]
                cpuResult.append(value)
                # for debug print 'cpu===',value
                if float(value[:-1]) > 60:
                    # cpu load >60% means overload
                    cpuEnough = False
            except Exception:
                pass
        njInfo['status'] = True
        njInfo['content'] = cpuEnough, cpuResult
        return njInfo

    def showMemory(self):
        """show Memory usage
        Returns:
            the device memory used
        """
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        memoryEnough = True
        cmd = 'display health'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo
        dashCount = 1
        contentMatch = False
        usefulList = []
        mystr = result['content'].split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
            if re.findall('CPU Usage', line):
                contentMatch = True
                continue
            if contentMatch is False:
                continue
            if re.findall('----------', line):
                dashCount = dashCount - 1
                continue
            if dashCount < 1:
                usefulList.append(line)
        mResult = usefulList
        memoryResult = []
        for line in mResult:
            try:
                value = re.findall('(\d+%)', line.split()[3])[0]
                memoryResult.append(value)
                if float(value[:-1]) > 80:
                    memoryEnough = False
            except Exception:
                pass
        njInfo['status'] = True
        njInfo['content'] = memoryEnough, memoryResult
        return njInfo

    def showIpObject(self, ip=None, mask=None):
        '''show ip whether defind
        Argv:
            ip: ip address
            msak: ip address mask
        Return:
            True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        if ip is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the ip."
            return njInfo
        if mask is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the mask."
            return njInfo
        cmd = 'display ip address-set address %s mask %s type object' % (ip, mask)
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo
        if re.search('Item\(s\)\:\r\n address \d+ %s mask %s' % (ip, mask), result):
            njInfo['status'] = True
            njInfo['content'] = re.findall('Address-set: (.*%s)' % ip, result)[0]
        return njInfo

    def showIpRangeObject(self, sIP=None, eIP=None):
        '''show ip range whether defind
        Argv:
            sIP: start ip address
            eIP: start ip address
            msak: ip address mask
        Return:
            True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        if sIP is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the sIP."
            return njInfo
        if eIP is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the eIP."
            return njInfo
        preIP = re.search('(\d+\.\d+\.\d+\.)(\d+)', sIP)
        lastIP = re.search('\d+\.\d+\.\d+\.(\d+)', eIP)
        if not preIP or not lastIP:
            njInfo['errLog'] = 'Not correct ip.'
            return njInfo
        else:
            preIP = preIP.groups()
            lastIP = lastIP.groups()
        multiIP = preIP[0] + '[' + preIP[1] + '_' + lastIP[0] + ']'
        cmd = 'display ip address-set address range %s %s type object' % (sIP, eIP)
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo
        if multiIP in result['content']:
            njInfo['status'] = True
            njInfo['content'] = re.findall('Address-set: ([a-z|\_]+%s)' % re.escape(multiIP), result['content'])[0]
        return njInfo

    def showPortObject(self, pType, port):
        '''show port whether defind
        Argv:
            pType: tcp or udp
            port: port
        Return:
            True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        if pType is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the pType."
            return njInfo
        if port is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the port."
            return njInfo
        cmd = 'display ip service-set verbose %s_any_%s item' % (pType, port)
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo
        if re.search('protocol %s source-port 0-65535 destination-port %s' % (pType, port), result['conent']):
            njInfo['status'] = True
            njInfo['content'] = re.findall('Service-set Name: (.*)\r', result['conent'])[0]
        return njInfo

    def showPortRangeObject(self, pType, pStart, pEnd):
        '''show port range whether defind
        Argv:
            pStart: start port address
            pEnd: start port address
            pType: tcp or udp
        Return:
            True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        if pType is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the pType."
            return njInfo
        if pStart is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the pStart."
            return njInfo
        if pEnd is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the pEnd."
            return njInfo
        cmd = 'display ip service-set verbose %s_any_[%s_%s] item' % (pType, pStart, pEnd)
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo
        if result == '':
            return njInfo
        if re.search('protocol %s source-port 0-65535 destination-port %s-%s' % (pType,
                                                                                 pStart, pEnd), result['content']):
            njInfo['status'] = True
            njInfo['content'] = re.findall('Service-set Name: (.*)\r', result['content'])[0]
        return njInfo

    def showPolicy(self, sZone, dZone, bound, sourceAddress, destAddress, service):
        '''show port range whether defind
        Argv:
            port_start: start port address
            port_end: start port address
            port_type: tcp or udp
        Return:
            True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        if sZone is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the sZone."
            return njInfo
        if dZone is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the dZone."
            return njInfo
        if bound is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the bound."
            return njInfo
        if sourceAddress is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the sourceAddress."
            return njInfo
        if destAddress is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the destAddress."
            return njInfo
        if service is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the service."
            return njInfo
        cmd = 'display policy interzone %s \
        %s %s source address-set %s destination \
        address-set %s service-set %s' % (sZone, dZone, bound, sourceAddress, destAddress, service)
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo
        if result["state"] == "success":
            if re.search(re.escape(sourceAddress), result['content']) and\
               re.search(re.escape(destAddress), result['content']) and \
               re.search(re.escape(service), result['content']):
                njInfo["content"] = result['content']
                njInfo["status"] = True
        else:
            njInfo['errLog'] = result['errLog']
        return njInfo

    def createIpObject(self, ip, mask, description):
        '''config ip object
            Argv:
                ip: ip address
                msak: ip address mask
                location: core or dmz or test
                nettype: gl or yw
                system:this ip belong system
            Return:
                True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        if ip is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the ip."
            return njInfo
        if mask is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the mask."
            return njInfo
        if description is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the description."
            return njInfo
        pMode = self.privilegeMode()
        if not pMode['status']:
            njInfo['errLog'] = pMode['errLog']
            return njInfo
        cmd1 = 'ip address-set %s_%s type object' % (description, ip)
        cmd2 = 'address 0 %s mask %s' % (ip, mask)
        resultIP = self.command(cmd=cmd1, prompt=prompt)
        if not resultIP['status'] or resultIP['state'] != 'success':
            njInfo['errLog'] = resultIP['errLog']
            return njInfo
        resultMask = self.command(cmd=cmd2, prompt=prompt)
        if not resultMask['status'] or resultMask['state'] != 'success':
            njInfo['errLog'] = resultMask['errLog']
            return njInfo
        result = re.findall('\d+:\d+:\d+', resultMask['content'])
        if resultIP['status'] and resultMask['status'] and len(result) > 0:
            njInfo['status'] = True
            njInfo['content'] = 'create ip success'
        return njInfo

    def createIpRangeObject(self, startIP, endIP, description):
        '''config ip range
            Argv:
                startIP: start ip address
                endIP: start ip addressi
                msak: ip address mask
                location: core or dmz or test
                nettype: gl or yw
                system:this ip belong system
            Return:
                True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        if startIP is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the startIP."
            return njInfo
        if endIP is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the endIP."
            return njInfo
        if description is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the description."
            return njInfo
        pMode = self.privilegeMode()
        if not pMode['status']:
            njInfo['errLog'] = pMode['errLog']
            return njInfo
        fIP = re.findall('\d+.\d+.\d+', startIP)[0]
        sIP = re.findall('\d+.\d+.\d+', endIP)[0]
        if fIP == sIP:
            tIP = re.findall('\d+', startIP)[3]
            lIP = re.findall('\d+', endIP)[3]
            pointIP = fIP + '.[' + tIP + '_' + lIP + ']'
        else:
            njInfo["errLog"] = "ip start is not same segment as the end ip"
            return njInfo
        cmd1 = 'ip address-set %s_%s type object' % (description, pointIP)
        cmd2 = 'address 0 range %s %s' % (startIP, endIP)
        resultIP = self.command(cmd=cmd1, prompt=prompt)
        if not resultIP['status'] or resultIP['state'] != 'success':
            njInfo['errLog'] = resultIP['errLog']
            return njInfo
        resultMask = self.command(cmd=cmd2, prompt=prompt)
        if not resultMask['status'] or resultMask['state'] != 'success':
            njInfo['errLog'] = resultMask['errLog']
            return njInfo
        result = re.findall('\d+:\d+:\d+', resultMask['content'])
        if resultIP['status'] and resultMask['status'] and len(result) > 0:
            njInfo['status'] = True
            njInfo['content'] = 'ip create success'
        return njInfo

    def createPortObject(self, pType, port):
        '''config port
        Argv:
            pType: tcp or udp
            port: port
        Return:
            True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        if pType is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the pType."
            return njInfo
        if port is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the port."
            return njInfo
        pMode = self.privilegeMode()
        if not pMode['status']:
            njInfo['errLog'] = pMode['errLog']
            return njInfo
        cmd1 = 'ip service-set %s_any_%s type object' % (pType, port)
        cmd2 = 'service 0 protocol %s source-port 0 to 65535 destination-port %s' % (pType, port)

        resultIP = self.command(cmd=cmd1, prompt=prompt)
        if not resultIP['status'] or resultIP['state'] != 'success':
            njInfo['errLog'] = resultIP['errLog']
            return njInfo
        resultPort = self.command(cmd=cmd2, prompt=prompt)
        if not resultPort['status'] or resultPort['state'] != 'success':
            njInfo['errLog'] = resultPort['errLog']
            return njInfo
        result = re.findall('\d+:\d+:\d+', resultPort['content'])
        if resultIP['status'] and resultPort['status'] and len(result) > 0:
            njInfo['status'] = True
            njInfo['content'] = 'port create success'
        return njInfo

    def createPortRangeObject(self, pType, portStart, portEnd):
        '''config port range
        Argv:
            portStart: start port address
            portEnd: start port address
            pType: tcp or udp
        Return:
            True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        if pType is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the pType."
            return njInfo
        if portStart is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the portStart."
            return njInfo
        if portEnd is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the portEnd."
            return njInfo
        pMode = self.privilegeMode()
        if not pMode['status']:
            njInfo['errLog'] = pMode['errLog']
            return njInfo
        cmd1 = 'ip service-set %s_any_[%s_%s] type object' % (pType, portStart, portEnd)
        cmd2 = 'service 0 protocol %s source-port 0 to 65535 destination-port %s to %s' % (pType,
                                                                                           portStart,
                                                                                           portEnd)
        resultIP = self.command(cmd=cmd1, prompt=prompt)
        if not resultIP['status'] or resultIP['state'] != 'success':
            njInfo['errLog'] = resultIP['errLog']
            return njInfo
        resultPort = self.command(cmd=cmd2, prompt=prompt)
        if not resultPort['status'] or resultPort['state'] != 'success':
            njInfo['errLog'] = resultPort['errLog']
            return njInfo
        result = re.findall('\d+:\d+:\d+', resultPort['content'])

        if resultIP['status'] and resultPort['status'] and len(result) > 0:
            njInfo['status'] = True
            njInfo['content'] = 'port create success'
        return njInfo

    def createSecurityPolicy(self, sZone, dZone, srcAddress, descAddress, portService, description):
        '''show port range whether defind
        Argv:
            port_start: start port address
            port_end: start port address
            port_type: tcp or udp
        Return:
            True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        if sZone is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the sZone."
            return njInfo
        if dZone is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the dZone."
            return njInfo
        if srcAddress is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the srcAddress."
            return njInfo
        if descAddress is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the descAddress."
            return njInfo
        if portService is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the portService."
            return njInfo
        if description is None:
            njInfo["errLog"] = "[Forward Error] Please specify a parameter for the description."
            return njInfo
        pMode = self.privilegeMode()
        if not pMode['status']:
            njInfo['errLog'] = pMode['errLog']
            return njInfo
        if sZone == 'trust' and dZone == 'trust':
            njInfo["errLog"] = 'source_address and destination_address all belong to core, need not open policy'
            return njInfo
        elif sZone == 'trust' and dZone != 'trust' or sZone == 'dmz' and dZone == 'untrust':
            directin = 'outbound'
        elif sZone != 'trust' and dZone == 'trust' or sZone == 'untrust' and dZone == 'dmz':
            directin = 'inbound'
        elif sZone != 'trust' and dZone != 'trust':
            njInfo['errLog'] = 'this policy not access in this firewall,please check the script'
            return njInfo
        cmdZone = 'policy interzone %s %s %s' % (sZone, dZone, directin)
        while True:
            resultZone = self.command(cmd=cmdZone, prompt=prompt)
            if resultZone['status']:
                break
        if not resultZone['status'] or resultZone['state'] != 'success':
            njInfo['errLog'] = resultZone['errLog']
            return njInfo

        cmdSearch = 'display policy interzone %s %s %s' % (sZone, dZone, directin)
        resultSearch = self.command(cmd=cmdSearch, prompt=prompt)
        if not resultSearch['status'] or resultSearch['state'] != 'success':
            njInfo['errLog'] = resultSearch['errLog']
            return njInfo

        policyNum = max(list(map(int, re.findall('policy (\d+) ', resultSearch['content'])))) + 1
        # policyNum = int(re.findall('policy (\d+) ', result)[-1]) + 1
        cmdNum = 'policy %s' % str(policyNum)
        resultNum = self.command(cmd=cmdNum, prompt=prompt)
        if not resultNum['status'] or resultNum['state'] != 'success':
            njInfo['errLog'] = resultNum['errLog']
            return njInfo

        cmdDesc = 'description %s' % description
        resultDesc = self.command(cmd=cmdDesc, prompt=prompt)
        if not resultDesc['status'] or resultDesc['state'] != 'success':
            njInfo['errLog'] = resultDesc['errLog']
            return njInfo

        cmdPermit = 'action permit'
        resultPermit = self.command(cmd=cmdPermit, prompt=prompt)
        if not resultPermit['status'] or resultPermit['state'] != 'success':
            njInfo['errLog'] = resultPermit['errLog']
            return njInfo

        for service in portService:
            cmd = 'policy service service-set %s' % service
            result = self.command(cmd=cmd, promt=prompt)
            if not result['status'] or result['state'] != 'success':
                njInfo['errLog'] = result['errLog']
                return njInfo
        for sAddr in srcAddress:
            cmd = 'policy source address-set %s' % sAddr
            result = self.command(cmd=cmd, promt=prompt)
            if not result['status'] or result['state'] != 'success':
                njInfo['errLog'] = result['errLog']
                return njInfo
        for descAddr in descAddress:
            cmd = 'policy destination address-set %s' % descAddr
            result = self.command(cmd=cmd, promt=prompt)
            if not result['status'] or result['state'] != 'success':
                njInfo['errLog'] = result['errLog']
                return njInfo
        njInfo['status'] = True
        njInfo['content'] = 'Policy create success!'
        return njInfo

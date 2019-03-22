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
[Core][forward] Device class for n7018.
"""
from forward.devclass.baseHuawei import BASEHUAWEI
from forward.utils.forwardError import ForwardError
import re


class S9312(BASEHUAWEI):
    """This is a manufacturer of huawei, so it is integrated with BASEHUAWEI library.
    """
    def isVlan(self, vlan):
        """Check if the Vlan exists.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # switch to enable mode.
        tmp = self.privilegeMode()
        if not tmp:
            raise ForwardError(tmp["errLog"])
        tmp = self.execute("display vlan {vlan}".format(vlan=vlan))
        if not tmp["status"]:
            raise ForwardError(tmp["errLog"])
        # If the above fails, exit immediately
        try:
            if re.search("Error: The VLAN does not exist", tmp["content"]):
                # vlan not is exitsts
                info["status"] = False
            else:
                # vlan is exists
                info["status"] = True
        except Exception as e:
            info["status"] = False
            info["errLog"] = str(e)
        return info

    def createVlan(self, vlan=None, ascription=None):
        """Create a Vlan.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        if (vlan is None) or (ascription is None):
            raise ForwardError("You must specify the `vlan` and `ascription` parameters")
        """Warning: that vlan should be checked
           by the 'self.isvlan(vlan) method
           before setting up the vlan"""
        # swith to config mode
        info = self._configMode()
        if not info["status"]:
            raise ForwardError(info["errLog"])
        try:
            # enter vlan
            info["content"] = ""
            self.shell.send("vlan {vlan}\n".format(vlan=vlan))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode()
            # Get host prompt
            self.getPrompt()
            if not re.search('.*-vlan', self.prompt):
                raise ForwardError("Failed to enter vlan mode,command:vlan {vlan}".format(vlan=vlan))
            # set host's ascription
            info["content"] = ""
            # Send command.
            self.shell.send("name {ascription}\n".format(ascription=ascription))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode()
            # Get host prompt.
            self.getPrompt()
            # save  the configuration.
            tmp = self._commit()
            if not tmp["status"]:
                raise ForwardError("The configuration command has been executed,\
                                    but the save configuration failed! [{info}]".format(info=info["content"]))
            else:
                if not self.isVlan(vlan)["status"]:
                    # check vlan
                    raise ForwardError("Vlan has been set and has been saved, but the final\
                                        check found no configuration, so failed.info:[%s]" % tmp["content"])
                else:
                    # create successed. exit config mode
                    info["status"] = True
        except Exception as e:
            info["status"] = False
            info["errLog"] = str(e)
        return info

    def isTrunkInInterface(self, port=None, vlan=None):
        """Check the relationship between interface and turnk.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        if (vlan is None) or (port is None):
            raise ForwardError('Specify the `vlan` and `port` parameters')
        # switch to enable mode
        tmp = self.privilegeMode()
        if not tmp["status"]:
            raise ForwardError(tmp['errLog'])
        # else ,successed
        while True:
            tmp = self.execute("display current-configuration interface Eth-Trunk")
            if not tmp["status"]:
                raise ForwardError(tmp["errLog"])
            if re.search("Command is in use by", tmp["content"]):
                # Recheck
                continue
            # Keyword search.
            data = re.search("#[\r\n]+(interface Eth-Trunk{port}[\r\n]+[\s\S]*?)#".format(port=port), tmp["content"])
            if not data:
                # No configuration found
                raise ForwardError("Not found port(port) info".format(port=port))
            try:
                if re.search("port trunk allow-pass vlan .*{vlan}".format(vlan=vlan), data.group(1)):
                    # found it.
                    info["status"] = True
                else:
                    info["status"] = False
                    info["errLog"] = tmp["content"]
                break
            except Exception as e:
                info["errLog"] = str(e)
                info["status"] = False
                break
        return info

    def trunkOpenVlan(self, port=None, vlan=None):
        """Create a vlan on turnk.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # Parameter check.
        if (vlan is None) or (port is None):
            raise ForwardError('Specify the `vlan` and `port` parameters')
        # get parameter
        tmp = self.execute("display cur interface Eth-Trunk {port}".format(port=port))
        if not tmp["status"]:
            raise ForwardError(tmp["errLog"])
        # search parameter
        data = re.search("#[\r\n]+(interface Eth-Trunk{port}[\r\n]+[\s\S]*?)#".format(port=port), tmp["content"])
        if not data:
            raise ForwardError("Not found port(port) [{info}]".format(port=port, info=tmp["content"]))
        else:
            # Keyword search.
            data = re.search("(port trunk allow-pass vlan.*)", data.group(1))
            if not data:
                raise ForwardError("`Port turnk allow-pass vlan ...` is not found")
            else:
                # remove the end '\n' and '\r'
                cmd = "{parameter} {vlan}".format(parameter=data.group(1).strip("\r\n"), vlan=vlan)
        # switch to config mode
        tmp = self._configMode()
        if not tmp["status"]:
            raise ForwardError(tmp["errLog"])
        try:
            # switch to port mode
            info["content"] = ""
            # Send command.
            self.shell.send("interface Eth-Trunk {port}\n".format(port=port))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode()
            # Get new host prompt.
            self.getPrompt()
            # Keyword search.
            if not re.search('Trunk{port}'.format(port=port), self.prompt):
                raise ForwardError("Failed to enter port mode,command:interface \
Eth-Trunk {port} [{info}]".format(port=port, info=info["content"]))
            # set vlan
            info["content"] = ""
            self.shell.send("{cmd}\n".format(cmd=cmd))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode()
            # Get new host prompt.
            self.getPrompt()
            # save configuration
            tmp = self._commit()
            if not tmp["status"]:
                raise ForwardError("The configuration command has been executed,\
                                    but the save configuration failed! [{info}]".format(info=info["content"]))
            # check configuration
            tmp = self.isTrunkInInterface(port=port, vlan=vlan)
            if not tmp["status"]:
                raise ForwardError("Vlan has been set and has been saved, but the final\
                                    check found no configuration, so failed.info:[%s]" % tmp["errLog"])
            else:
                info["status"] = True
        except Exception as e:
            info["errLog"] = str(e)
            info["status"] = False
        return info

    def isGateway(self, vlan):
        """Check that the gateway exists.
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # switch to enable mode.
        tmp = self.privilegeMode()
        if not tmp:
            raise ForwardError(tmp["errLog"])
        # Execute command.
        tmp = self.execute("display current-configuration interface Vlanif {vlan}".format(vlan=vlan))
        if not tmp["status"]:
            raise ForwardError(tmp["errLog"])
        # If the above fails, exit immediately
        try:
            if re.search("Error: Wrong parameter found at", tmp["content"]):
                info["status"] = False
            else:
                info["status"] = True
        except Exception as e:
            info["status"] = False
            info["errLog"] = str(e)
        return info

    def setGateway(self, vlan=None, ascription=None, ip=None):
        """Create a gateway
        """
        info = {"status": False,
                "content": "",
                "errLog": ""}
        # Parameters check.
        if (vlan is None) or (ascription is None) or (ip is None):
            raise ForwardError("You must specify `vlan` and `ascription` and `ip` parameters")
        # Reset gateway ip address
        ip = re.sub('[0-9]+$', '254', ip)
        # switch to config mode
        tmp = self._configMode()
        if not tmp["status"]:
            raise ForwardError(tmp["errLog"])
        try:
            # switch to vlanif mode
            info["content"] = ""
            # Send command.
            self.shell.send("interface Vlanif {vlan}\n".format(vlan=vlan))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode()
            # Get new host prompt.
            self.getPrompt()
            if not re.search('Vlanif', self.prompt):
                raise ForwardError("Failed to enter Vlanif mode,command:port Vlanif {vlan}".format(vlan=vlan))
            # set ascription
            info["content"] = ""
            self.shell.send("description {ascription}\n".format(ascription=ascription))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode
            # Get new host prompt.
            self.getPrompt()
            # set ip
            info["content"] = ""
            # Send command.
            self.shell.send("ip address {ip} 255.255.255.0\n".format(ip=ip))
            while not re.search(self.basePrompt, info['content'].split('\n')[-1]):
                info['content'] += self.shell.recv(1024).decode
            # Check
            if re.search("Error: The specified IP address is invalid", info["content"]):
                raise ForwardError("Error: The specified IP address is invalid,IP should be a network segment")
            # Get new host prompt.
            self.getPrompt()
            # save the configuration
            tmp = self._commit()
            if not tmp["status"]:
                raise ForwardError("The configuration command has been executed,\
                                    but the save configuration failed! [{info}]".format(info=info["content"]))
            else:
                # Check that the gateway configuration exists.
                if not self.isGateway(vlan)["status"]:
                    # check vlan
                    raise ForwardError("Gateway has been set and has been saved, but the final\
                                        check found no configuration, so failed.info:[%s]" % tmp["content"])
                else:
                    # create successed. exit config mode
                    info["status"] = True
        except Exception as e:
            info["status"] = False
            info["errLog"] = str(e)
        return info

    def showInterfacePower(self, port):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        if port.startswith('XGi'):
            port = re.findall('\d+\S+', port)[0]
            cmd = 'display transceiver interface XGigabitEthernet ' + port + ' verbose '
        elif port.startswith('Gi'):
            port = re.findall('\d+\S+',port)[0]
            cmd = 'display transceiver interface GigabitEthernet ' + port + ' verbose '
        _result = self.command(cmd=cmd, prompt=prompt)
        if not _result['status'] or _result['state'] != 'success':
            njInfo['errLog'] = _result['errLog']
            return njInfo
        info = re.findall(r'dBM.*:(.*)\r', _result['content'])
        result = {}
        if string.atof(info[0]) > string.atof(info[6]):
            result['TX'] = 'HIGH'
        elif string.atof(info[0]) < string.atof(info[7]):
            result['TX'] = 'LOW'
        else:
            result['TX'] = 'normal'

        if string.atof(info[3]) > string.atof(info[8]):
            result['RX'] = 'HIGH'
        elif string.atof(info[3]) < string.atof(info[9]):
            result['RX'] = 'LOW'
        else:
            result['RX'] = 'normal'
        njInfo['status'] = True
        njInfo['content'] = result
        return njInfo

    def aclGet(self, acl_name='LOGIN', acl_ip='1.1.1.5'):
        """show ip acl

        Returns:
            the ip acl list
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
        acl = {}
        acl_name = re.sub(' *', '', acl_name)
        cmd = "display current-configuration | begin user-interface"
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['status'] = result['errLog']
            return njInfo
        acl_num = re.findall('acl (\d+)', result['content'])[0]
        cmd = 'display acl %s | include %s' % (acl_num, acl_ip)
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['status'] = result['errLog']
            return njInfo
        if len(re.findall(acl_ip, result['content'])) > 0:
            njInfo['status'] = True
        else:
            njInfo['status'] = False
        return njInfo

    def showSystemUptime(self):
        '''display version
        Return:
           weeks_of_uptime,days_of_uptime
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        cmd = 'display version '
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['status'] = result['errLog']
        uptime=re.search('Switch uptime is\s+(\d+)\s+weeks, (\d+)\s+days',result['content'])
        weeksUptime = uptime.groups()[0]
        daysUptime= uptime.groups()[1]
        njInfo['status'] = True
        njInfo['content'] = weeksUptime,daysUptime
        return njInfo

    def usefulContent(self,mystr,matchContent):
        '''
        Args:
            matchContent
        Return:
              useful content between 2nd lines of '----' and 3rd line of '-----'
        input like:
           System memory usage at 2018-04-13 09:41:18
           -------------------------------------------------------------------------------
            Slot     Total Memory(MB)   Used Memory(MB)   Used Percentage   Upper Limit
           -------------------------------------------------------------------------------
           1          173                77                44%               85%
           2          173                77                44%               85%
           3          173                77                44%               85%
           -------------------------------------------------------------------------------
        output:
           1          173                77                44%               85%
           2          173                77                44%               85%
           3          173                77                44%               85%

        '''
        dash_count=3
        content_match=False
        usefulList=[]
        mystr = mystr.split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
          if re.findall(matchContent, line):
            content_match=True
            continue
          if content_match==False :
            continue
          if  re.findall('----------',line):
            dash_count=dash_count-1
            continue
          if dash_count==1:
            usefulList.append(line) #print line
            continue
          elif dash_count == 0 :
            content_match=False
            dash_count=3
        return usefulList

    def usefulContent2(self,mystr,matchContent):
        '''
        Args:
            matchContent
        Return:
              useful content between 1st lines of '----' and 2nd line of '-----'
        input like:
        PowerID  Online  Mode   State      Current(A)   Voltage(V)   RealPwr(W)
        --------------------------------------------------------------------------
        PWR1     Present AC     Supply     5.31         53.50        284.08
        PWR2     Present AC     Supply     5.66         53.53        302.98
        -------------------------------------------------------------------------------
        output:
        PWR1     Present AC     Supply     5.31         53.50        284.08
        PWR2     Present AC     Supply     5.66         53.53        302.98

        '''
        dash_count=2
        content_match=False
        usefulList=[]
        mystr = mystr.split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
          if re.findall(matchContent, line):
            content_match=True
            continue
          if content_match==False :
            continue
          if  re.findall('----------',line) or re.findall('System Memory Usage Information:',line):
            dash_count=dash_count-1
            continue
          if dash_count==1:
            usefulList.append(line) #print line
            continue
          elif dash_count == 0 :
            content_match=False
            dash_count=2
        return usefulList

    def showHardware(self):
        """show hardware statu
        Returns:
            sensor,temperature,power,Fan status
            True or False
        """
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        cmd='display health'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo

        dashCount=2
        contentMatch=False
        usefulList=[]
        mystr = result['content'].split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
          if re.findall('Slot  Card  Sensor SensorName       Status', line):
            contentMatch=True
            continue
          if contentMatch==False :
            continue
          if  re.findall('----------',line) or re.findall('System Memory Usage Information:',line):
            dashCount=dashCount-1
            continue
          if dashCount==1:
            usefulList.append(line) #print line
            continue
          elif dashCount == 0 :
            contentMatch=False
            dashCount=2
        resultSensor = usefulList

        dashCount=2
        contentMatch=False
        usefulList=[]
        mystr = result['content'].split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
          if re.findall('PowerID  Online  Mode   State      Current', line):
            contentMatch=True
            continue
          if contentMatch==False :
            continue
          if  re.findall('----------',line) or re.findall('System Memory Usage Information:',line):
            dashCount=dashCount-1
            continue
          if dashCount==1:
            usefulList.append(line) #print line
            continue
          elif dashCount == 0 :
            contentMatch=False
            dashCount=2
        reultTemperature = usefulList

        dashCount=2
        contentMatch=False
        usefulList=[]
        mystr = result['content'].split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
          if re.findall('PowerID  Online  Mode   State      Current', line):
            contentMatch=True
            continue
          if contentMatch==False :
            continue
          if  re.findall('----------',line) or re.findall('System Memory Usage Information:',line):
            dashCount=dashCount-1
            continue
          if dashCount==1:
            usefulList.append(line) #print line
            continue
          elif dashCount == 0 :
            contentMatch=False
            dashCount=2
        resultPower = usefulList

        dashCount=2
        contentMatch=False
        usefulList=[]
        mystr = result['content'].split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
          if re.findall('FanID   FanNum   Online   Register', line):
            contentMatch=True
            continue
          if contentMatch==False :
            continue
          if  re.findall('----------',line) or re.findall('System Memory Usage Information:',line):
            dashCount=dashCount-1
            continue
          if dashCount==1:
            usefulList.append(line) #print line
            continue
          elif dashCount == 0 :
            contentMatch=False
            dashCount=2
        result_fan = usefulList

        sensorNormal=True
        temperatureNormal=True
        powerNormal=True
        fanNormal=True
        errorDevice = []
        for line in resultSensor:
          if not re.findall('Normal', line): #health output for sensor: If a line include 'Normal', it is normal
            sensorNormal=False
            errorDevice.append(line)
        for line in reultTemperature:
          if not re.findall('Normal', line): #health output for temperature: If a line include 'Normal', it is normal
            temperatureNormal=False
            errorDevice.append(line)
        for line in resultPower:#health output for power: If a line include 'Present' and 'Supply' together, it is normal
            if re.findall('Present', line):
                if not re.findall('Supply',line):
                    temperatureNormal=False
                    errorDevice.append(line)
            if re.findall('FAN', line):
                if not (re.findall('Registered', line)):
                    fanNormal = False
                    errorDevice.append(line)
        if not errorDevice:
            njInfo['content'] = 'check pass'
        else:
            njInfo['content'] = errorDevice
        njInfo['status'] = True
        return njInfo

    def showMemory(self):
        """show memory used
        Returns:
            the device memory used
        """
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        memoryEnough = True
        cmd = 'display health | after 17 include System memory usage at'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo
        dashCount = 3
        contentMatch = False
        usefulList = []
        mystr = result['content'].split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
            if re.findall('System memory usage at', line):
                contentMatch=True
                continue
            if contentMatch==False :
                continue
            if re.findall('----------',line):
                dashCount = dashCount-1
                continue
            if dashCount == 1:
              usefulList.append(line)
              continue
            elif dashCount == 0 :
              contentMatch = False
              dashCount = 3
        resultMemory = usefulList
        # resultMemory=self.usefulContent(result['content'],'System memory usage at') #strip off unuseful line
        for line in resultMemory:
          value = re.findall('(\d+)%', line)
          if float(value[0]) >= float(value[1]):
            memoryEnough = False
        njInfo['status'] = True
        njInfo['content'] = memoryEnough
        return njInfo

    def showCpu(self):
        """show cpu used
        Returns:
            the device memory used
        """
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        cpu_enough = True
        cmd = 'display health | after 17 include System cpu usage at'
        result = self.command(cmd=cmd, prompt=prompt)
        if not result['status'] or result['state'] != 'success':
            njInfo['errLog'] = result['errLog']
            return njInfo
        dashCount = 3
        contentMatch = False
        usefulList = []
        mystr = result['content'].split('\n')
        mystr.pop(0)
        mystr.pop(-1)
        for line in mystr:
            if re.findall('System memory usage at', line):
                contentMatch=True
                continue
            if contentMatch==False :
                continue
            if  re.findall('----------',line):
                dashCount = dashCount-1
                continue
            if dashCount == 1:
                usefulList.append(line)
                continue
            elif dashCount == 0 :
                contentMatch = False
                dashCount = 3
        resultMemory = usefulList
        # result_cpu=self.usefulContent(result['content'],'System cpu usage at') #strip off unuseful line
        for line in resultCPU:
          value = re.findall('(\d+)%', line)
          if float(value[0]) >= float(value[1]):
            cpu_enough = False
        njInfo['status'] = True
        njInfo['content'] = cpu_enough,resultCPU
        return njInfo

    def showSpanningTreeStatus(self):
        """show spanning tree stat
           judge if the root bridge ID equal local bridge ID ---S9312 must be root
        Returns:
            the spanning tree status
        """
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        prompt = {
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Invalid command[\s\S]+",
        }
        # cpu_enough=True
        cmdLocla = 'display stp bridge local'
        cmdRoot = 'display stp bridge root'
        resultLocal = self.command(cmd=cmdLocla, prompt=prompt)
        resultRoot = self.command(cmd=cmdRoot, prompt=prompt)
        if not resultLocal['status'] or resultLocal['state'] != 'success':
            njInfo['errLog'] = resultLocal['errLog']
            return njInfo
        if not resultRoot['status'] or resultRoot['state'] != 'success':
            njInfo['errLog'] = resultRoot['errLog']
            return njInfo
        resultLocal = resultLocal['content'].split('\n')
        resultRoot = resultRoot['content'].split('\n')
        resultLocal.pop(0)
        resultLocal.pop(-1)
        resultRoot.pop(0)
        resultRoot.pop(-1)
        rootBridge = ''
        spanning_tree_change = False
        for i in range(len(resultRoot)):
            if i <= 2:
                continue
            if rootBridge == '':
                rootBridge = resultRoot[i].split()[1]
                continue
            if not resultRoot[i].split()[1] == rootBridge:
                spanning_tree_change = True
            else:
                pass
        for i in range(len(resultLocal)):
            if i <= 2:
                continue
            if not resultLocal[i].split()[1] == rootBridge:
                spanning_tree_change = True
            else:
                pass
        njInfo['status'] = True
        njInfo['content'] = rootBridge, spanning_tree_change
        return njInfo

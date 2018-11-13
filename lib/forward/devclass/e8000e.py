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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
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

    def showIpObject(self, ip, mask):
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        cmd = 'display ip address-set address %s mask %s type object' % (ip, mask)
        result = self.command(cmd, prompt=prompt)['content']
        if re.search('Item\(s\)\:\r\n address \d+ %s mask %s' % (ip, mask), result):
            njInfo['status'] = True
            njInfo['content'] = re.findall('Address-set: (.*%s)' % ip, result)[0]
        return njInfo

    def showIpRangeObject(self, ip_start, ip_end):
        '''show ip range whether defind
        Argv:
            ip_start: start ip address
            ip_end: start ip address
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        pre_ip = re.search('(\d+\.\d+\.\d+\.)(\d+)', ip_start).groups()
        last_ip = re.search('\d+\.\d+\.\d+\.(\d+)', ip_end).groups()
        ip_groups = pre_ip[0] + '[' + pre_ip[1] + '_' + last_ip[0] + ']'
        cmd = 'display ip address-set address range %s %s type object' % (ip_start, ip_end)
        result = self.command(cmd, prompt=prompt)['content']
        if ip_groups in result:
            njInfo['status'] = True
            njInfo['content'] = re.findall('Address-set: (.*%s)' % ip_groups, result)[0]
        return njInfo

    def showPortObject(self, port_type, port):
        '''show port whether defind
        Argv:
            port_type: tcp or udp
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        cmd = 'display ip service-set verbose %s_any_%s item' % (port_type, port)
        result = self.command(cmd, prompt=prompt)['content']
        if re.search('protocol %s source-port 0-65535 destination-port %s' % (port_type, port), result):
            njInfo['status'] = True
            njInfo['content'] = re.findall('Service-set Name: (.*)\r', result)[0]
        return njInfo

    def showPortRangeObject(self, port_type, port_start, port_end):
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        cmd = 'display ip service-set verbose %s_any_[%s_%s] item' % (port_type, port_start, port_end)
        result = self.command(cmd, prompt=prompt)['content']
        if re.search('protocol %s source-port 0-65535 destination-port %s-%s' % (port_type,
                                                                                 port_start, port_end), result):
            njInfo['status'] = True
            njInfo['content'] = re.findall('Service-set Name: (.*)\r', result)[0]
        return njInfo

    def showPolicy(self, src_zone, dst_zone, inout, src_add, dst_add, service):
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        cmd = 'display policy interzone %s\
%s %s source address-set %s destination\
address-set %s service-set %s' % (src_zone, dst_zone, inout, src_add, dst_add, service)
        result = self.command(cmd, prompt=prompt)
        if result["state"] == "success":
            if re.search(src_add, result['content']) and\
               re.search(dst_add, result['content']) and re.search(service, result['content']):
                njInfo["content"] = result['content']
                njInfo["status"] = True
        return njInfo

    def createIpObject(self, ip, mask, dist):
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
        cmd_1 = 'system-view'
        cmd_2 = 'ip address-set %s_%s type object' % (dist, ip)
        cmd_3 = 'address 0 %s mask %s' % (ip, mask)
        prompt1 = {'success': re.escape('[NFJD-PSC-'),
                   'error': re.escape('<NFJD-PSC-')}
        prompt2 = {'success': re.escape('-object-'),
                   'error': 'E8000E-\d+]'}
        """prompt3 = {'success': re.escape('<NFJD-PSC-'),
                   'error': re.escape('[NFJD-PSC-')}"""
        # cmd_4 = 'quit'
        result1 = self.command(cmd_1, prompt1)
        result2 = self.command(cmd_2, prompt2)
        result3 = self.command(cmd_3, prompt2)
        # result4 = self.command(cmd_4, prompt1)
        # result5 = self.command(cmd_4, prompt3)
        result_3 = re.findall('\d+:\d+:\d+', result3['content'])
        if result1['status'] and result2['status'] and len(result_3) > 0:
            njInfo['status'] = True
        return njInfo

    def createIpRangeObject(self, ip_start, ip_end, dist):
        '''config ip range
            Argv:
                ip_start: start ip address
                ip_end: start ip addressi
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
        cmd_1 = 'system-view'
        ip_1_3 = re.findall('\d+.\d+.\d+', ip_start)[0]
        ip_2_3 = re.findall('\d+.\d+.\d+', ip_end)[0]
        if ip_1_3 == ip_2_3:
            ip_1_4 = re.findall('\d+', ip_start)[3]
            ip_2_4 = re.findall('\d+', ip_end)[3]
            point_ip_obj = ip_1_3 + '.[' + ip_1_4 + '_' + ip_2_4 + ']'
        else:
            return 'ip start is not same segment as the end ip'
        cmd_2 = 'ip address-set %s_%s type object' % (dist, point_ip_obj)
        cmd_3 = 'address 0 range %s %s' % (ip_start, ip_end)
        prompt1 = {'success': re.escape('[NFJD-PSC-'),
                   'error': re.escape('<NFJD-PSC-')}
        prompt2 = {'success': re.escape('-object-'),
                   'error': 'E8000E-\d+]'}
        """prompt3 = {'success': re.escape('<NFJD-PSC-'),
                   'error': re.escape('[NFJD-PSC-')}"""
        # cmd_4 = 'quit'
        result1 = self.command(cmd_1, prompt1)
        result2 = self.command(cmd_2, prompt2)
        result3 = self.command(cmd_3, prompt2)
        # result4 = self.command(cmd_4, prompt1)
        # result5 = self.command(cmd_4, prompt3)
        result_3 = re.findall('\d+:\d+:\d+', result3['content'])
        if result1['status'] and result2['status'] and len(result_3) > 0:
            njInfo['status'] = True
        return njInfo

    def createPortObject(self, port_type, port):
        '''config port
        Argv:
            port_type: tcp or udp
            port: port
        Return:
            True or False
        '''
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd_1 = 'system-view'
        cmd_2 = 'ip service-set %s_any_%s type object' % (port_type, port)
        cmd_3 = 'service 0 protocol %s source-port 0 to 65535 destination-port %s' % (port_type, port)
        prompt1 = {'success': re.escape('[NFJD-PSC-'),
                   'error': re.escape('<NFJD-PSC-')}
        prompt2 = {'success': re.escape('-object-'),
                   'error': 'E8000E-\d+]'}
        # prompt3 = {'success': re.escape('<NFJD-PSC-'),
        #            'error': re.escape('[NFJD-PSC-')}
        # cmd_4 = 'quit'
        result1 = self.command(cmd_1, prompt1)
        result2 = self.command(cmd_2, prompt2)
        result3 = self.command(cmd_3, prompt2)
        # result4 = self.command(cmd_4, prompt1)
        # result5 = self.command(cmd_4, prompt3)
        result_3 = re.findall('\d+:\d+:\d+', result3['content'])
        if result1['status'] and result2['status'] and len(result_3) > 0:
            njInfo['status'] = True
        return njInfo

    def createPortRangeObject(self, port_type, port_start, port_end):
        '''config port range
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
        cmd_1 = 'system-view'
        cmd_2 = 'ip service-set %s_any_[%s_%s] type object' % (port_type, port_start, port_end)
        cmd_3 = 'service 0 protocol %s source-port 0 to 65535 destination-port %s to %s' % (port_type,
                                                                                            port_start,
                                                                                            port_end)
        prompt1 = {'success': re.escape('[NFJD-PSC-'),
                   'error': re.escape('<NFJD-PSC-')}
        prompt2 = {'success': re.escape('-object-'),
                   'error': 'E8000E-\d+]'}
        # prompt3 = {'success': re.escape('<NFJD-PSC-'),
        #           'error': re.escape('[NFJD-PSC-')}
        # cmd_4 = 'quit'
        result1 = self.command(cmd_1, prompt1)
        result2 = self.command(cmd_2, prompt2)
        result3 = self.command(cmd_3, prompt2)
        result_3 = re.findall('\d+:\d+:\d+', result3['content'])
        # result4 = self.command(cmd_4, prompt1)
        # result5 = self.command(cmd_4, prompt3)
        if result1['status'] and result2['status'] and len(result_3) > 0:
            njInfo['status'] = True
        return njInfo

    def createSecurityPolicy(self, src_zone, dst_zone, src_add_list, dst_add_list, service_list, description):
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
            "success": "[\r\n]+\S+.+(>|\]) ?$",
            "error": "Unrecognized command[\s\S]+",
        }
        prompt1 = {'success': re.escape('[NFJD-PSC-'),
                   'error': re.escape('<NFJD-PSC-')}
        prompt2 = {'success': re.escape('-policy-'),
                   'error': 'E8000E-\d+]'}

        cmd_1 = 'system-view'
        result1 = self.command(cmd_1, prompt1)
        if result1['status']:
            if src_zone == 'trust' and dst_zone == 'trust':
                return 'source_address and destination_address all belong to core, need not open policy'
            elif src_zone == 'trust' and dst_zone != 'trust' or src_zone == 'dmz' and dst_zone == 'untrust':
                directin = 'outbound'
            elif src_zone != 'trust' and dst_zone == 'trust' or src_zone == 'untrust' and dst_zone == 'dmz':
                directin = 'inbound'
            elif src_zone != 'trust' and dst_zone != 'trust':
                return 'this policy not access in this firewall,please check the script'
            cmd_2 = 'policy interzone %s %s %s' % (src_zone, dst_zone, directin)
            while True:
                result2 = self.command(cmd_2, prompt2)
                if result2['status']:
                    break
            if result2['status']:
                cmd_search = 'display policy interzone %s %s %s' % (src_zone, dst_zone, directin)
                result = self.command(cmd_search, prompt)['content']
                policy_num = int(re.findall('policy (\d+) ', result)[-1]) + 1
                cmd_3 = 'policy %s' % str(policy_num)
                result3 = self.command(cmd_3, prompt2)
                if result3['status']:
                    cmd_4 = 'description %s' % description
                    result4 = self.command(cmd_4, prompt2)
                    if result4['status']:
                        cmd_5 = 'action permit'
                        result5 = self.command(cmd_5, prompt2)
                        if result5['status']:
                            for service in service_list:
                                cmd = 'policy service service-set %s' % service
                                result = self.command(cmd, prompt2)
                                if result['status']:
                                    continue
                                else:
                                    return False
                            for src_add in src_add_list:
                                cmd = 'policy source address-set %s' % src_add
                                result = self.command(cmd, prompt2)
                                if result['status']:
                                    continue
                                else:
                                    return False
                            for dst_add in dst_add_list:
                                cmd = 'policy destination address-set %s' % dst_add
                                result = self.command(cmd, prompt2)
                                if result['status']:
                                    continue
                                else:
                                    return False
                            njInfo['status'] = True
                            njInfo['content'] = 'Policy configer success!'
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False

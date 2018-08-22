# coding:utf-8
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
[Core][forward] Function for sshv1, by using pexpect module.
"""
import os
import sys
import re
from forward.utils.forwardError import ForwardError
import pexpect


def checkPassWord(ssh, password, P=False):
    njInfo = {"status": False,
              "content": "",
              "errLog": ""}
    # througt SSH chanel determine whether there is interaction password prompt
    if not P:
        ssh.expect([r"[Pp]assword:", ".*"])
    ssh.send(password + '\n')
    # Multiple identical characters may appear
    p = ssh.expect([r"[Pp]assword:", r"(>|#|\]|\$){1,}.*$"])
    if p == 0:
        njInfo['errLog'] = "Username or Password wrong"
        # if expect characters is password,then the account password is wrong
    elif p == 1:
        # if expect host's prompt characters,then normal
        njInfo["status"] = True
        njInfo["content"] = ssh
        # return  password cross-examination after the SSH channel
    else:
        njInfo['content'] = "Unknown login wrong"
    return njInfo


class NJSSHV1Wraper(pexpect.spawn):

    def __init__(self,
                 ip='',
                 username='',
                 port=22,
                 timeout=30):
            self.ip = ip
            self.port = port
            self.timeout = timeout
            self.username = username
            self.njInfo = {"status": False,
                           "content": "",
                           'errLog': ""}

    def login(self, password=None):
        pexpect.spawn.__init__(self, 'ssh -p %d %s@%s' % (self.port, self.username, self.ip))
        self.setwinsize(1000, 1000)
        i = self.expect([r'[Pp]assword.*:.*',
                        'Are you sure you want to continue connecting (yes/no)?',
                         'Connection refused', pexpect.TIMEOUT], self.timeout)
        if i == 0:
            self.njInfo = checkPassWord(self, password, True)
            # True
        elif i == 1:
            self.sendline('yes')
            self.njInfo = checkPassWord(self, password)
        elif i == 2:
            self.njInfo['errLog'] = 'port timeout [%s]' % self.ip
        elif i == 3:
            self.njInfo['errLog'] = 'port timeout [%s]' % self.ip
        else:
            self.njInfo['errLog'] = 'The error is unknown'
        return self.njInfo


def sshv1(ip='',
          username=None,
          password=None,
          port=22,
          timeout=30):
    njSSHv1Wraper = NJSSHV1Wraper(ip=ip, username=username, timeout=timeout)
    return njSSHv1Wraper.login(password=password)

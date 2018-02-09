#!/usr/bin/python
# coding:utf-8
"""
-----Introduction-----
[Core][forward] Function for sshv1, by using pexpect module.
Author: Cheung Kei-Chuen,Wangzhe
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
        ssh.expect([r"[Pp]assword", ".*"])
    ssh.send(password + '\n')
    p = ssh.expect([r"[Pp]assword", r"(>|#|\]|\$) *$"])
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
        i = self.expect([r'[Pp]assword',
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

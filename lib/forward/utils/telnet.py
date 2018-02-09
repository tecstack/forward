#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Function for telnet, by using telnetlib module.
Author: Azrael, Cheung Kei-Chuen
"""

import telnetlib
import re


class NJTELNETWraper(telnetlib.Telnet):

    def __init__(self, ip=None, port=23, timeout=30):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.njInfo = {'content': "",
                       'status': False,
                       'errLog': ""}
        self.prompt = "(>|#|\]|\$) *$"

    def login(self, username, password):
        # login by username and password
        njInfo = {"status": False,
                  "content": ""}
        try:
            telnetlib.Telnet.__init__(self,
                                      host=self.ip,
                                      port=self.port,
                                      timeout=self.timeout)
            # self.set_debuglevel(2)
            # username
            self.expect([r"Username|login"])
            self.write('%s\n' % username)
            # password
            self.expect([r"assword"])
            self.write('%s\n' % password)
            T = self.expect([r"Login incorrect|assword", r"%s" % self.prompt])
            # is tuple ,notice \r \n
            NT = T[0]
            if NT == 1:
                njInfo['content'] = self
                # return telnetlib instance
                njInfo['status'] = True
            elif NT == 0:
                njInfo['errLog'] = 'Username or Password wrong'
            else:
                njInfo['errLog'] = 'Login status is unknown'
        except Exception, e:
            njInfo['errLog'] = str(e)
        return njInfo

    def send(self, command=None):
        telnetlib.Telnet.write(self, command)
    # def recv(self,prompt):
    #       return telnetlib.Telnet.expect(prompt)[-1]

    def rfc1073(self):
        # resize the virtual console window size to 10000*10000 by use RFC1073 protocal
        cmd = telnetlib.IAC + telnetlib.WILL + telnetlib.NAWS
        self.get_socket().send(cmd)
        cmd = telnetlib.IAC + telnetlib.SB + telnetlib.NAWS \
            + chr(39) + chr(16) + chr(39) + chr(16)\
            + telnetlib.IAC + telnetlib.SE
        self.get_socket().send(cmd)


def telnet(ip=None, username=None, password=None, port=23, timeout=30):
    njTelnetInstance = NJTELNETWraper(ip=ip, port=port, timeout=timeout)
    njInfo = njTelnetInstance.login(username=username, password=password)
    if njInfo['status']:
        njTelnetInstance.rfc1073()
    return njInfo


if __name__ == '__main__':
        telnet('10.0.0.1', 'username', 'password', 23, 30)

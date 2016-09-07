#!/usr/bin/env python
#coding:utf-8
"""	For TELNET  use the login function
        The login module channel through python's telnetlib
"""
import telnetlib,re

class NJTELNETWraper(telnetlib.Telnet):

        def __init__(self,ip = '',port = 23,timeout = 30):
                self.ip = ip
                self.port = port
                self.timeout = timeout
                self.njInfo = {
                                'content':"",
                                'status':False,
                                'errLog':""
                }
                self.prompt = "(>|#|\]|\$) *$"

        def login(self,username,password):
                njInfo = {
                           "status":False,
                           "content":""
                }
                try:
                        telnetlib.Telnet.__init__(self,host = self.ip,port = self.port,timeout = self.timeout)
                        #self.set_debuglevel(2)
                        #username
                        self.expect([r"Username|login"])
                        self.write('%s\n' % username)
                        #password
                        self.expect([r"assword"])
                        self.write('%s\n' % password)
                        T = self.expect([r"Login incorrect|assword",r"%s"%self.prompt]) ###is tuple ,notice \r \n
                        NT = T[0]
                        if NT == 1:
                                njInfo['content'] = self #return telnetlib instance
                                njInfo['status'] = True
                        elif NT == 0:
                                njInfo['errLog'] = 'Username or Password wrong'
                        else:
                                njInfo['errLog'] = 'Login status is unknown'
                except Exception,e:
                        njInfo['errLog'] = str(e)
                return njInfo
        def send(self,command = ''):
                telnetlib.Telnet.write(self,command)
        #def recv(self,prompt):
        #       return telnetlib.Telnet.expect(prompt)[-1]
        def rfc1073(self):
                cmd = telnetlib.IAC + telnetlib.WILL + telnetlib.NAWS
                self.get_socket().send(cmd)
                cmd = telnetlib.IAC + telnetlib.SB + telnetlib.NAWS + chr(3) + chr(232) + chr(3) + chr(232) + telnetlib.IAC + telnetlib.SE
                self.get_socket().send(cmd)

def telnet(ip = '',username = '',password = '',port = 23,timeout = 30):
        njTelnetInstance = NJTELNETWraper(ip = ip,port = port,timeout = timeout)
        njInfo = njTelnetInstance.login(username = username,password = password)
        njTelnetInstance.rfc1073()
        return njInfo


if __name__=='__main__':
        njTelnet('10.1.1.1','username','password','a',23,1000)

#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Azrael <azrael-ex@139.com>

"""
-----Introduction-----
[Core][forward] Base device class for sshv2 method, by using paramiko module.
Author: Azrael, Cheung Kei-Chuen
"""

import re
from forward.utils.sshv2 import sshv2
from forward.utils.forwardError import ForwardError


class BASESSHV2(object):
    def __init__(self, ip, username, password, **kwargs):
        """Init a sshv2-like class instance, accept port/timeout/privilegePw as extra parameters
        """
        self.ip = ip
        self.username = username
        self.password = password

        self.port = kwargs['port'] if 'port' in kwargs else 22
        self.timeout = kwargs['timeout'] if 'timeout' in kwargs else 30
        self.privilegePw = kwargs['privilegePw'] if 'privilegePw' in kwargs else ''

        self.isLogin = False
        self.isEnable = False

        self.channel = ''
        self.shell = ''
        self.basePrompt = r'(>|#|\]|\$|\)) *$'
        self.prompt = ''
        self.moreFlag = '(\-)+( |\()?[Mm]ore.*(\)| )?(\-)+'

        """
        - parameter ip: device's ip
        - parameter port : device's port
        - parameter timeout : device's timeout(Only for login,not for execute)
        - parameter channel: storage device connection channel session
        - parameter shell: paramiko shell, used to send(cmd) and recv(result)
        - parameter prompt: [ex][wangzhe@cloudlab100 ~]$
        """

    def __del__(self):
        # Logout after the program leaves.
        self.logout()

    def login(self):
        """Login method.
        Creates a login session for the program to send commands to the target device.
        """
        result = {
            'status': False,
            'errLog': ''
        }
        # sshv2(ip,username,password,timeout,port=22)
        sshChannel = sshv2(self.ip, self.username, self.password, self.timeout, self.port)
        if sshChannel['status']:
            # Login succeed, init shell
            try:
                result['status'] = True
                self._channel = sshChannel['content']
                # resize virtual console window size to 10000*10000
                self.shell = self._channel.invoke_shell(width=10000, height=10000)
                self.channel = self.shell
                tmpBuffer = ''
                while (
                    not re.search(self.basePrompt, tmpBuffer.split('\n')[-1])
                ) and (
                    not re.search('new +password', tmpBuffer.split('\n')[-1], flags=re.IGNORECASE)
                ):
                    tmpBuffer += self.shell.recv(1024)
                # if prompt is 'New Password' ,raise Error.
                if re.search('new +password', tmpBuffer.split('\n')[-1], flags=re.IGNORECASE):
                    raise ForwardError(
                        '[Login Error]: %s: Password expired, needed to be updated!' % self.ip
                    )
                self.shell.settimeout(self.timeout)
                # Record login status to True.
                self.isLogin = True
                self.getPrompt()
            except Exception as e:
                result['status'] = False
                result['errLog'] = str(e)
        else:
            # Login failed
            self.isLogin = False
            result['errLog'] = sshChannel['errLog']
        return result

    def logout(self):
        """Logout method
        A session used to log out of a target device
        """
        result = {
            'status': False,
            'errLog': ''
        }
        try:
            # Close SSH
            self._channel.close()
            # Modify login status to False.
            self.isLogin = False
            result['status'] = True
        except Exception as e:
            result['status'] = False
            result['errLog'] = str(e)
        return result

    def execute(self, cmd):
        """execute a command line, only suitable for the scene when
        the prompt is equal before and after execution
        """
        result = {
            'status': True,
            'content': '',
            'errLog': ''
        }
        self.cleanBuffer()
        if self.isLogin:
            # check login status
            # [ex] when send('ls\r'),get 'ls\r\nroot base etc \r\n[wangzhe@cloudlab100 ~]$ '
            # [ex] data should be 'root base etc '
            self.shell.send(cmd + "\r")
            resultPattern = '[\r\n]+([\s\S]*)[\r\n]+' + self.prompt
            try:
                while not re.search(self.prompt, result['content'].split('\n')[-1]):
                    self.getMore(result['content'])
                    result['content'] += self.shell.recv(1024)
                # try to extract the return data
                tmp = re.search(resultPattern, result['content']).group(1)
                # Delete special characters caused by More split screen.
                tmp = re.sub("<--- More --->\\r +\\r", "", tmp)
                result['content'] = tmp
            except Exception as e:
                # pattern not match
                result['status'] = False
                result['content'] = result['content']
                result['errLog'] = str(e)
        else:
            # not login
            result['status'] = False
            result['errLog'] = '[Execute Error]: device not login'
        return result

    def command(self, cmd=None, prompt=None, timeout=30):
        """execute a command line, powerful and suitable for any scene,
        but need to define whole prompt dict list
        """
        result = {
            'status': True,
            'content': '',
            'errLog': '',
            "state": None
        }
        # Parameters check
        if (cmd is None) or (not isinstance(prompt, list)) or (not isinstance(timeout, int)):
            raise ForwardError("""You should pass such a form of argument: \
CMD = 'Your command', prompt = [{" success ": ['prompt1', 'prompt2']}, {" error" : ['prompt3', 'prompt4']}]""")
        for section in prompt:
            if not isinstance(section.values(), list):
                raise ForwardError("""you should pass such a form of argument:\
prompt = [{" success ": ['prompt1', 'prompt2']}, {" error" : ['prompt3', 'prompt4']}]""")
        try:
            self.shell.send("{cmd}\r".format(cmd=cmd))
            try:
                while True:
                    self.getMore(result['content'])
                    result["content"] += self.shell.recv(1024)
                    for section in prompt:
                        # section.values() is : [ [p1,p2,p3] ]
                        for _prompt in section.values()[0]:
                            if re.search(_prompt, result["content"].split("\n")[-1]):
                                result["state"] = section.keys()[0]
                                break
                        # Find the specified state type
                        if not result["state"] is None:
                            break
                    # Find the specified state type,exit
                    if not result["state"] is None:
                        break
                result["content"] = re.sub("<--- More --->\\r +\\r", "", result["content"])
            # If you accept a timeout, cancel SSH
            except Exception, e:
                self.logout()
                raise ForwardError(str(e))
        except Exception, e:
            result["errLog"] = str(e)
            result["status"] = False
        return result

    def getPrompt(self):
        """Automatically get the current system prompt by sending a carriage return
        """
        if self.isLogin:
            # login status True
            result = ''
            self.cleanBuffer()
            self.shell.send('\n')
            # set recv timeout to self.timeout/10 fot temporary
            while not re.search(self.basePrompt, result):
                result += self.shell.recv(1024)
            if result:
                # recv() get something
                # select last line character,[ex]' >[localhost@labstill019~]$ '
                self.prompt = result.split('\n')[-1]
                # [ex]'>[localhost@labstill019~]$'
                # self.prompt=self.prompt.split()[0]
                # [ex]'[localhost@labstill019~]'
                # self.prompt=self.prompt[1:-1]
                # [ex]'\\[localhost\\@labstill019\\~\\]$'
                self.prompt = re.escape(self.prompt)
                return self.prompt
            else:
                # timeout,get nothing,raise error
                raise ForwardError('[Get Prompt Error]: %s: Timeout,can not get prompt.' % self.ip)
        else:
            # login status failed
            raise ForwardError('[Get Prompt Error]: %s: Not login yet.' % self.ip)

    def getMore(self, bufferData):
        """Automatically get more echo infos by sending a blank symbol
        """
        # if check buffer data has 'more' flag, at last line.
        if re.search(self.moreFlag, bufferData.split('\n')[-1]):
            # can't used to \n and ' \r' ,because product enter character
            self.shell.send(' ')

    def cleanBuffer(self):
        """Clean the shell buffer whatever they are, by sending a carriage return
        """
        if self.shell.recv_ready():
            self.shell.recv(4096)
        self.shell.send('\n')
        buff = ''
        # When after switching mode, the prompt will change, it should be based on basePrompt to check and at last line
        while not re.search(self.basePrompt, buff.split('\n')[-1]):
            try:
                buff += self.shell.recv(1024)
            except Exception:
                raise ForwardError('[Clean Buffer Error]: %s: Receive timeout [%s]' % (self.ip, buff))

#!/usr/bin/evn python
# coding:utf-8
#
# (c) 2017, Azrael <azrael-ex@139.com>

"""
-----Introduction-----
[Core][forward] Base device class for telnet method, by using telnetlib module.
Author: Azrael, Cheung Kei-Chuen
"""
import re
from forward.utils.telnet import telnet
from forward.utils.forwardError import ForwardError


class BASETELNET(object):
    def __init__(self, ip, username, password, **kwargs):
        """Init a telnet-like class instance, accept port/timeout/privilegePw as extra parameters
        """
        self.ip = ip
        self.username = username
        self.password = password

        self.port = kwargs['port'] if 'port' in kwargs else 23
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
        - parameter njInfo : return interactive data's format
        """

    def login(self):
        """Login method
        Creates a login session for the program to send commands to the target device.
        """
        result = {
            'status': False,
            'errLog': ''
        }
        # telnet(ip,username,password,port=23,timeout)
        sshChannel = telnet(ip=self.ip,
                            username=self.username,
                            password=self.password,
                            port=self.port,
                            timeout=self.timeout)
        if sshChannel['status']:
            # Login succeed, init shell
            self.channel = sshChannel['content']
            # Record login status to True.
            self.isLogin = True
            # Get host prompt.
            self.getPrompt()
            result['status'] = True
        else:
            result['errLog'] = sshChannel['errLog']
        return result

    def __del__(self):
        # Logout after the program leaves.
        self.logout()

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
            self.channel.close()
            # Modify login status to False.
            self.isLogin = False
            result['status'] = True
        except Exception, e:
            result['status'] = False
            result['content'] = str(e)
        return result

    def execute(self, cmd):
        """execute a command line, only suitable for the scene when
        the prompt is equal before and after execution
        """
        dataPattern = '[\r\n]+([\s\S]*)[\r\n]+' + self.prompt
        # Spaces will produce special characters and re.escape('show ver') --> show \\ ver
        data = {'status': False,
                'content': '',
                'errLog': ''}
        if self.isLogin:
            # check login status
            # [ex] when send('ls\r'),get 'ls\r\nroot base etc \r\n[wangzhe@cloudlab100 ~]$ '
            # [ex] data should be 'root base etc '
            self.cleanBuffer()
            self.channel.write(cmd + "\n")
            i = self.channel.expect([r'%s' % self.moreFlag, r"%s" % self.prompt], timeout=self.timeout)
            # Get result
            result = i[-1]
            try:
                if i[0] == 0:
                    # Receive more characters
                    result += self.getMore()
                elif i[0] == -1:
                    # Recvive timeout
                    raise ForwardError('Error: receive timeout ')
                data['content'] += result
                try:
                    # Intercept command result
                    tmp = re.search(dataPattern, data['content']).group(1)
                    # Delete special characters caused by More split screen.
                    tmp = re.sub("<--- More --->\\r +\\r", "", tmp)
                    data['content'] = tmp
                    data['status'] = True
                except Exception, e:
                    # Not found host prompt
                    raise ForwardError('not found host prompt Errorr(%s)' % str(e))
            except Exception, e:
                # Not found host prompt
                data['status'] = False
                data['errLog'] = data['errLog'] + 'not found host prompt Errorr(%s)' % str(e)
        else:
            # Not login
            data['status'] = False
            data['content'] = 'ERROR:device not login'
        return data

    def getMore(self):
        # Apply to the execute method
        """Automatically get more echo infos by sending a blank symbol
        """
        result = ''
        while True:
            # The return message is received until there is no More character like More.
            self.channel.send(' ')
            i = self.channel.expect([r'%s' % self.moreFlag, self.prompt], timeout=self.timeout)
            # Get result
            result += i[-1]
            if i[0] == 1:
                break
        return result

    def newGetMore(self, prompt, timeout):
        # Applies to the command method
        """Automatically get more echo infos by sending a blank symbol
        """
        result = ''
        state = None
        continueRecv = False
        while True:
            # If the acceptance is not complete, you cannot send a space
            if not continueRecv:
                self.channel.send(' ')
            i = self.channel.expect([r'%s' % self.moreFlag, self.basePrompt], timeout=timeout)
            # Get result
            result += i[-1]
            if i[0] == 0:
                # Get more
                continue
            if i[0] == 1:
                # Find the base host prompt.
                for section in prompt:
                    # section.values() is : [ [p1,p2,p3] ]
                    for _prompt in section.values()[0]:
                        if re.search(_prompt, result.split("\n")[-1]):
                            state = section.keys()[0]
                            break
                    # Find the specified state type
                    if state is not None:
                        break
                # Find the specified state type,exit
                if state is not None:
                    break
                else:
                    # Not  found,Continue to receive
                    continueRecv = True
            else:
                raise ForwardError('getMore recv timeout:[%s]' % result)
        return (result, state)

    def getPrompt(self):
        """Automatically get the current system prompt by sending a carriage return
        """
        self.channel.send('\n')
        i = self.channel.expect([r"%s" % self.basePrompt], timeout=self.timeout)
        # select last line character,[ex]' >[localhost@labstill019~]$ '
        # [ex]'>[localhost@labstill019~]$'
        # self.prompt=self.prompt.split()[0]
        # [ex]'[localhost@labstill019~]'
        # self.prompt=self.prompt[1:-1]
        # [ex]'\\[localhost\\@labstill019\\~\\]$'
        self.prompt = re.escape(i[-1].split('\n')[-1])
        return self.prompt

    def cleanBuffer(self):
        """Clean the shell buffer whatever they are, by sending a carriage return
        """
        self.channel.send('\n')
        i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
        result = i[-1]
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
CMD = 'Your command', prompt = [{" success ": ['prompt1', 'prompt2']}, {" error" : ['prompt3', 'prompt4']}] ,\
timeout=30""")
        for section in prompt:
            if not isinstance(section.values(), list):
                raise ForwardError("""you should pass such a form of argument:\
prompt = [{" success ": ['prompt1', 'prompt2']}, {" error" : ['prompt3', 'prompt4']}]""")
        try:
            self.channel.write("{cmd}\r".format(cmd=cmd))
            try:
                info = ''
                while True:
                    """ First, the program accepts the return message based on the base prompt, and if you accept
                    it directly from the specified prompt, there will be many times out of time in the middle,
                    resulting in reduced efficiency"""
                    i = self.channel.expect([r'%s' % self.moreFlag, r"%s" % self.basePrompt], timeout=timeout)
                    info += i[-1]
                    if i[0] == 0:
                        tmp = self.newGetMore(prompt, timeout)
                        info += tmp[0]
                        result["state"] = tmp[1]
                        break
                    elif i[0] == -1:
                        raise ForwardError('Error: receive timeout ')
                    else:
                        for section in prompt:
                            # section.values() is : [ [p1,p2,p3] ]
                            for _prompt in section.values()[0]:
                                if re.search(_prompt, info.split("\n")[-1]):
                                    result["state"] = section.keys()[0]
                                    break
                            # Find the specified state type
                            if not result["state"] is None:
                                break
                        # Find the specified state type,exit
                        if not result["state"] is None:
                            break
                result['content'] += info
                result["content"] = re.sub("<--- More --->\\r +\\r", "", result["content"])
            # If you accept a timeout, cancel SSH
            except Exception, e:
                self.logout()
                raise ForwardError(str(e))
        except Exception, e:
            result["errLog"] = str(e)
            result["status"] = False
        return result

#!/usr/bin/evn python
# coding:utf-8
#
# (c) 2017, Azrael <azrael-ex@139.com>

"""
-----Introduction-----
[Core][forward] Base device class for sshv1 method, by using pexpect module.
Author: Azrael, Cheung Kei-Chuen
"""
import re
from forward.utils.sshv1 import sshv1
from forward.utils.forwardError import ForwardError
import pexpect


class BASESSHV1(object):
    def __init__(self, ip, username, password, **kwargs):
        """Init a sshv1-like class instance, accept port/timeout/privilegePw as extra parameters
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
        - parameter njInfo : return interactive data's format
        """

    def login(self):
        """Loging method
        Creates a login session for the program to send commands to the target device.
        """
        result = {
            'status': False,
            'errLog': ''
        }
        # sshv1(ip,username,password,tport=22,timeout,)
        sshChannel = sshv1(ip=self.ip,
                           username=self.username,
                           password=self.password,
                           port=self.port,
                           timeout=self.timeout)
        if sshChannel['status']:
            # Login succeed, init shell
            result['status'] = True
            self.channel = sshChannel['content']
            # Record login status to True.
            self.isLogin = True
            # Get host prompt.
            self.getPrompt()
            # Clear legacy characters
            self.cleanBuffer()
        else:
            # Login failed.
            self.isLogin = False
            result['errLog'] = sshChannel['errLog']
        return result

    def __del__(self):
        # Logout after the program leaves.
        self.logout()

    def logout(self):
        """Login method
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
            # If the close fails, set the login status to False and record the failure message
            result['status'] = False
            result['errLog'] = str(e)
        return result

    def enable(self, password):
        """No use.
        """
        pass

    def execute(self, cmd):
        """execute a command line, only suitable for the scene when
        the prompt is equal before and after execution
        """
        # Remove legacy data from the SSH before executing the command.
        self.cleanBuffer()
        # dataPattern = re.escape(cmd)+'.*\r\n([\s\S]*)\r\n'+self.prompt
        dataPattern = '[\r\n]+([\s\S]*)[\r\n]+'
        # SSHV1 pexpect not have self.prompt end
        data = {'status': False,
                'content': '',
                'errLog': ''}
        if self.isLogin:
            # check login status
            # [ex] when send('ls\r'),get 'ls\r\nroot base etc \r\n[wangzhe@cloudlab100 ~]$ '
            # [ex] data should be 'root base etc '
            self.channel.send(cmd + '\n')
            i = self.channel.expect([r'%s' % self.moreFlag, r"%s" % self.prompt, pexpect.TIMEOUT], timeout=self.timeout)
            result = ''
            if i == 0:
                """If the data received by the program contains the last line of information
                similar to the More type-ending message, it indicates that the command needs
                to send a space for More messages.
                """
                result = self.channel.before
                # Get more result
                result += self.getMore()
            elif i == 2:
                # Execute timeout
                data['errLog'] = 'Error: receive timeout '
            else:
                # Execute successed.
                result = self.channel.before
            data['content'] += result
            data["status"] = True
            try:
                tmp = re.search(dataPattern, data['content']).group(1)
                # Delete special characters caused by More split screen.
                tmp = re.sub("<--- More --->\\r +\\r", "", tmp)
                data['content'] = tmp
            except Exception, e:
                # Unable to find the host prompt, command execution failed.
                data['status'] = False
                data['errLog'] = data['errLog'] + "not fond host prompt:Error(%s)" % str(e)
        else:
            data['status'] = False
            data['errLog'] = 'ERROR:device not login'
        return data

    def getMore(self):
        # Applies to the execute method
        """Automatically get the current system prompt by sending a carriage return
        """
        result = ''
        while True:
            # The return message is received until there is no More character like More.
            self.channel.send(' ')
            i = self.channel.expect([r'%s' % self.moreFlag, r"%s" % self.prompt, pexpect.TIMEOUT], timeout=self.timeout)
            if i == 0:
                result += self.channel.before
                # After the encounter `moreFlag`, need to get the message
            elif i == 1:
                result += self.channel.before
                # After the encounter prompt, need to get the result
                break
            else:
                break
        return result

    def newGetMore(self, prompt, timeout):
        # Applies to the command method
        # The return message is received until there is no More character like More.
        result = ''
        state = None
        continueRecv = False
        while True:
            if not continueRecv:
                self.channel.send('\r')
            i = self.channel.expect([r'%s' % self.moreFlag, r"%s" % self.basePrompt, pexpect.TIMEOUT], timeout=timeout)
            if i == 0:
                result += self.channel.before
                # After the encounter `moreFlag`, need to get the message
            elif i == 1:
                result += self.channel.before
                result += self.channel.after
                # After the encounter prompt, need to get the result
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
                raise ForwardError("function: getMore recv timeout")
        return (result, state)

    def getPrompt(self):
        """Automatically get the current system prompt by sending a carriage return
        """
        if self.isLogin:
            # login status True
            self.channel.send('\n')
            """The host base prompt is the end of the received flag, and if the data is
            not received at the set time, the timeout is exceeded.
            """
            self.channel.expect([r"%s" % self.basePrompt, pexpect.TIMEOUT], timeout=self.timeout)
            # select last line character,[ex]' >[localhost@labstill019~]$ '
            # [ex]'>[localhost@labstill019~]$'
            # self.prompt=self.prompt.split()[0]
            # [ex]'[localhost@labstill019~]'
            # self.prompt=self.prompt[1:-1]
            # [ex]'\\[localhost\\@labstill019\\~\\]$'
            self.prompt = self.channel.before.split('\n')[-1] + "(>|#|\$|\]|\)) *$"
        else:
            raise ForwardError('[Get Prompt Error]: %s: Not login yet.' % self.ip)
        return self.prompt

    def cleanBuffer(self):
        """Clean the shell buffer whatever they are, by sending a carriage return
        """
        self.channel.send('\n')
        try:
            """When after switching mode, the prompt will change, it should be based
            on basePrompt to check and at last line
            """
            return self.channel.expect(self.prompt, timeout=self.timeout)
        except pexpect.TIMEOUT:
            # No legacy data.
            return ''

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
            self.channel.send("{cmd}\r".format(cmd=cmd))
            try:
                info = ''
                while True:
                    """ First, the program accepts the return message based on the base prompt, and if program
                    accept it directly from the specified prompt, there will be many times out of time in the
                    middle,resulting in reduced efficiency"""
                    i = self.channel.expect([r'%s' % self.moreFlag, r"%s" % self.basePrompt,
                                             pexpect.TIMEOUT], timeout=timeout)
                    if i == 2:
                        """The host prompt is not finished with the traditional # $ >
                        and you need to set it like that.
                        """
                        raise ForwardError('Error: base prompt receive timeout')
                    if i == 0:
                        info += self.channel.before
                        # Get More then result
                        tmp = self.newGetMore(prompt, timeout)
                        info += tmp[0]
                        result["state"] = tmp[1]
                        # To complete the receiving
                        break
                    else:
                        # To complete the receiving
                        info += self.channel.before
                        # read base prompt
                        info += self.channel.after
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
                # Delete special characters caused by More split screen.
                result["content"] = re.sub("<--- More --->\\r +\\r", "", result["content"])
            except Exception, e:
                # If program accept a timeout, cancel SSH
                self.logout()
                raise ForwardError(str(e))
        except Exception, e:
            # Program run failed
            result["errLog"] = str(e)
            result["status"] = False
        return result

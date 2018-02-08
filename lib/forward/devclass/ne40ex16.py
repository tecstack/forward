#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for ne40ex16.
"""
import re
from forward.devclass.baseHuawei import BASEHUAWEI
from forward.utils.sshv2 import sshv2


class NE40EX16(BASEHUAWEI):
    """This is a manufacturer of huawei, so it is integrated with BASEHUAWEI library.
    """

    def login(self):
        """Because the device of this model is different from the other
        huawei devices in commit  parameters, it is rewritten.
        """
        njInfo = {"status": False,
                  "content": "",
                  "errLog": ""}
        # sshv2(ip,username,password,timeout,port=22)
        sshChannel = sshv2(self.ip, self.username, self.password, self.timeout, self.port)
        if sshChannel['status']:
            # Login succeed, init shell
            try:
                njInfo['status'] = True
                self.channel = sshChannel['content']
                # resize virtual console window size to 10000*10000
                self.shell = self.channel.invoke_shell(width=1000, height=1000)
                tmpBuffer = ''
                while not re.search(self.basePrompt, tmpBuffer.split('\n')[-1]):
                    tmpBuffer += self.shell.recv(1024)
                    # When prompted, reply N
                    if re.search('\[Y/N\]:', tmpBuffer):
                        self.shell.send('N\n')
                # set session timeout
                self.shell.settimeout(self.timeout)
                # Flag login status is True.
                self.isLogin = True
                # Get host prompt.
                self.getPrompt()
                njInfo["status"] = True
            except Exception as e:
                njInfo['status'] = False
                njInfo['errLog'] = str(e)
        else:
            # Login failed
            njInfo['errLog'] = sshChannel['errLog']
        return njInfo

#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Azrael <azrael-ex@139.com>

"""
-----Introduction-----
[Core][forward] Function for sshv2, by using paramiko module.
Author: Cheung Kei-Chuen, Azrael
"""

import paramiko


def sshv2(ip='', username='', password='', timeout=30, port=22):
    # return SSH channel, use ssh.invoke_shell() to active a shell, and resize window size
    njInfo = {
        'status': True,
        'errLog': '',
        'content': ''
    }
    try:
        port = int(port)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password, timeout=timeout)
        njInfo['content'] = ssh
    except Exception, e:
        njInfo['status'] = False
        njInfo['errLog'] = str(e)
    return njInfo

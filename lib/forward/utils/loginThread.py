#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Azrael <azrael-ex@139.com>

"""
-----Introduction-----
[Core][Forward] Login method thread function, used for the initialize multithread step
Author: Azrael
"""


def loginThread(instance):
    # Login method thread function, used for the initialize multithread step
    if not instance.isLogin:
        result = instance.login()
        if not result['status']:
            print '[Login Error]: %s :%s' % (instance.ip, result['errLog'])

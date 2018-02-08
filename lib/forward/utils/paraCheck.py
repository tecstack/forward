#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Azrael <azrael-ex@139.com>

"""
-----Introduction-----
[Core][Forward] addTargets parameters legal check function
Author: Azrael
"""


def paraCheck(targets):
    # Legal targets: [target1, target2, target3....]
    # Legal target type: [ip-str, model-str, user-str, pw-str, kwargs-dict]
    # Legal target: ['192.168.1.1', 'n7k', 'admin', 'admin_pw', {'port': 22, 'timeout': 30}]
    # Legal target: ['192.168.1.1', 'n7k', 'admin', 'admin_pw', {'port': 22}]
    # Legal target: ['192.168.1.1', 'n7k', 'admin', 'admin_pw', {'timeout': 30}]
    # Legal target: ['192.168.1.1', 'n7k', 'admin', 'admin_pw']
    bool_legal = isinstance(targets, list)

    if bool_legal:
        for target in targets:
            try:
                bool_legal &= (len(target) >= 4 and len(target) < 6)
                bool_legal &= isinstance(target[0], str)
                bool_legal &= isinstance(target[1], str)
                bool_legal &= isinstance(target[2], str)
                bool_legal &= isinstance(target[3], str)
                if len(target) > 4:
                    bool_legal &= isinstance(target[4], dict)
                else:
                    bool_legal &= True
            except Exception:
                return False
            if not bool_legal:
                break
        return bool_legal
    else:
        return False

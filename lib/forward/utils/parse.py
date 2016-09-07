#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import re


def is_quoted(data):
    return len(data) > 1 and data[0] == data[-1] \
        and data[0] in ('"', "'") and data[-2] != '\\'


def unquote(data):
    """
        removes first and last quotes from a string,
        if the string starts and ends with the same quotes
    """
    if is_quoted(data):
        return data[1:-1]
    return data


def check_ip_format(ip_str):
    pattern_string = r"""
       \b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
       (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
       (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
       (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b
       """
    pattern = re.compile(pattern_string, re.X)
    if re.match(pattern, ip_str):
        return True
    else:
        return False


def ip_to_num(ip):
    ''' ip address transformat into binary '''
    ip = [int(x) for x in ip.split('.')]
    return ip[0] << 24 | ip[1] << 16 | ip[2] << 8 | ip[3]


def num_to_ip(num):
    ''' binary ip address transformat into x.x.x.x '''
    return '%s.%s.%s.%s' % ((num & 0xff000000) >> 24,
                            (num & 0x00ff0000) >> 16,
                            (num & 0x0000ff00) >> 8,
                            num & 0x000000ff)


def get_ip_in_range(ip_range):
    """
        input 'x.x.x.x-y.y.y.y' or 'z.z.z.z'
        output all ip within list belongs to 'x.x.x.x-y.y.y.y',
        except '0.0.0.0'
    """
    ip = [ip_to_num(x) for x in ip_range.split('-')]
    return [num_to_ip(x) for x in range(ip[0], ip[-1] + 1) if x & 0xff]


def get_ip_list(inventory):
    """
        input ['1.1.1.1','2.2.2.2-2.2.3.4']
        output all legal ip address within list
    """
    ip_list = []
    for x in inventory:
        ip_list.extend(get_ip_in_range(x))
    return ip_list

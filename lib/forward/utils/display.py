#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import sys
import errno


class Display(object):
    '''
        Display messages on screen if necessary.
    '''
    def __init__(self):
        super(Display, self).__init__()

    def display(self, msg, stderr=False):
        ''' display a message to the user '''
        if not msg.endswith(u'\n'):
            msg += u'\n'
        output = sys.stderr if stderr else sys.stdout
        output.write(msg)
        try:
            output.flush()
        except IOError as e:
            if e.errno != errno.EPIPE:
                raise

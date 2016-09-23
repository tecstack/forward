#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.


class ForwardError(Exception):
    '''
        This is the base class for all errors raised from Forward code.
    '''
    pass


class ForwardScriptError(ForwardError):
    '''
        This is the user script error.
    '''
    pass

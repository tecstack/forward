#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import os

from forward import constants as C
from forward.utils.error import ForwardError
from forward.utils.display import Display


class Output:

    @staticmethod
    def output(data, path, format):
        ''' runs a child defined method using the ouput_<action> pattern '''
        if format not in C.DEFAULT_OUTPUT_TYPES:
            raise ForwardError('Output Type Illegal.')
        output_function = getattr(Output, "output_%s" % format)
        if format == 'stdout':
            return output_function(data)
        if path and os.path.isdir(os.path.dirname(path)):
            return output_function(data, path)
        else:
            raise ForwardError('Output Path Illegal.')

    @staticmethod
    def output_stdout(data):
        '''print data to standard output'''
        data = to_string(data)
        delta = 80
        display = Display()
        display.display('\r\nOUTPUT%s' % ('-' * 74))
        for i in range(0, len(data), delta):
            display.display(data[i:(i + delta)])
            i += delta

    @staticmethod
    def output_txt(data, path):
        '''write data to specified text file'''
        data = to_string(data)
        with open('%s.txt' % path, 'w') as f:
            f.write(data)

    @staticmethod
    def output_xls(data, path):
        '''write data to specified excel'''
        pass


def to_string(data):
    try:
        data = str(data)
        return data
    except:
        raise ForwardError('Output FORMAT Illegal.')

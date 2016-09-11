#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import os
import imp

from forward.utils.error import ForwardError
from forward.utils.path import purepath

__all__ = ['TaskExecutor']


class TaskExecutor(object):
    """
        This class handles a task blocks to execute on a given set of hosts.
        Usage:
        te = TaskExecutor(instances, script, args)
        result = te.run()
    """

    def __init__(self, instances=None, script=None, args=None):
        super(TaskExecutor, self).__init__()
        self.instances = instances
        self.script = script
        self.args = args

    def run(self):
        ''' execute task script '''
        ret = None
        try:
            args = {
                'instance': self.instances,
                'parameters': self.load_args(self.args)}
            module = imp.load_source('script', self.load_module(self.script))
            ret = module.node(args)
        except ForwardError:
            raise
        except:
            raise ForwardError('Script Content Illegal.')
        return ret

    @staticmethod
    def load_module(path):
        ''' load script module '''
        if not os.path.isfile(path):
            raise ForwardError('Script File Not Found.')
        return purepath(path)

    @staticmethod
    def load_args(args):
        ''' load script arguments '''
        d = eval(args) if isinstance(args, str) else args
        if not isinstance(d, dict):
            raise ForwardError('Script Argument Illegal.')
        return d

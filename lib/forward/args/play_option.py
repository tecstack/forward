#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import os

from forward import constants as C
from forward.utils.boolean import boolean
from forward.utils.error import ForwardError


class PlayOption(object):
    """
        Forward Play Options
    """
    def __init__(
            self, worker=C.DEFAULT_WORKER,
            script=os.path.join(C.DEFAULT_HOME, C.DEFAULT_SCRIPT_PATH),
            args=None, no_std_log=False, loglevel=C.DEFAULT_LOGLEVEL,
            logfile=os.path.join(C.DEFAULT_HOME, C.DEFAULT_FORWARD_LOG_PATH),
            timeout=30, out=C.DEFAULT_OUTPUT,
            outfile=os.path.join(C.DEFAULT_HOME, C.DEFAULT_OUT_PATH)):
        super(PlayOption, self).__init__()
        try:
            self.worker = int(worker)
            self.script = str(script)
            self.args = args
            self.loglevel = str(loglevel)
            self.logfile = str(logfile)
            self.no_std_log = boolean(no_std_log)
            self.out = str(out)
            self.outfile = str(outfile)
            self.timeout = int(timeout)
        except TypeError as e:
            raise ForwardError('Bad Play Option: %s.' % e)

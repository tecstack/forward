#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.


class Option(object):
    """
        Options for NO-CLI Extension
    """
    def __init__(self, worker=4, script=None, args={},
                 loglevel='INFO', logfile=None, no_std_log=False,
                 out='stdout', outfile=None, inventory=[],
                 vender=None, model=None, connect='local',
                 conpass=None, actpass=None,
                 remote_port=22, remote_user=None, timeout=30):
        super(Option, self).__init__()
        self.worker = worker
        self.script = script
        self.args = args
        self.loglevel = loglevel
        self.logfile = logfile
        self.no_std_log = no_std_log
        self.out = out
        self.outfile = outfile
        self.inventory = inventory
        self.vender = vender
        self.model = model
        self.connect = connect
        self.conpass = conpass
        self.actpass = actpass
        self.remote_port = remote_port
        self.remote_user = remote_user
        self.timeout = timeout

#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

from forward.utils.error import ForwardError
from forward.args.play_option import PlayOption
from forward.args.host_option import HostOption
from forward.api.runner import Runner


class Forward(object):
    """
        ECI Extension
    """
    def __init__(self, **kw):
        super(Forward, self).__init__()
        self.inventory = []
        self.get_inventory(kw['inventory'])
        kw.pop('inventory')
        self.options = PlayOption(**kw)

    def run(self):
        try:
            result = Runner(
                options=self.options, inventory=self.inventory).run()
            return result
        except ForwardError:
            raise
        except:
            pass

    def get_inventory(self, hosts):
        for h in hosts:
            self.inventory.append(HostOption(**h))

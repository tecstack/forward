#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import traceback

from forward.utils.error import ForwardError
from forward.api.option import Option
from forward.api.runner import Runner


class Forward(object):
    """
        NO-CLI Extension
    """
    def __init__(self, **kw):
        super(Forward, self).__init__()
        self.options = Option(**kw)

    def run(self):
        try:
            result = Runner(options=self.options).run()
            return result
        except ForwardError:
            raise
        except Exception as e:
            self.logger.error(repr(e))
            self.logger.debug(traceback.format_exc())

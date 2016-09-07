#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import traceback

from forward import constants as C
from forward.utils.error import ForwardError
from forward.utils.log import logger as DEFAULT_LOGGER
from forward.utils.log import set_loglevel_only, add_file_logger
from forward.utils.parse import check_ip_format
from forward.utils.output import Output
from forward.executor.task_queue_manager import TaskQueueManager


class Runner(object):
    """
        Runner for NO-CLI Extension
    """
    def __init__(self, options, logger=DEFAULT_LOGGER):
        super(Runner, self).__init__()
        self.options = options
        self.logger = logger

    def run(self):
        ''' run a forward task '''
        op = self.options
        # set logger
        try:
            if op.logfile:
                self.logger = add_file_logger(
                    level=op.loglevel, file=op.logfile,
                    default=(not op.no_std_log))
            elif op.loglevel != C.DEFAULT_LOGLEVEL:
                self.logger = set_loglevel_only(level=op.loglevel)
        except ForwardError:
            raise
        except Exception as e:
            self.logger.error(repr(e))
            self.logger.debug(traceback.format_exc())
        # get connection passwords
        passwords = {'con': op.conpass, 'act': op.actpass}
        # get ip inventory of hosts
        if op.inventory and isinstance(op.inventory, list):
            for x in op.inventory:
                if not check_ip_format(x):
                    raise ForwardError('IP Inventory Illegal.')
        # now execute tasks
        self._tqm = None
        result = None
        try:
            self._tqm = TaskQueueManager(
                options=op,
                inventory=op.inventory,
                passwords=passwords,
                logger=self.logger
            )
            result = self._tqm.run()
        except ForwardError:
            raise
        except Exception as e:
            self.logger.error(repr(e))
            self.logger.debug(traceback.format_exc())
        finally:
            if self._tqm:
                self._tqm.cleanup()
        # results output
        if result:
            try:
                Output.output(result, op.outfile, op.out)
            except ForwardError:
                raise
            except Exception as e:
                self.logger.error(repr(e))
                self.logger.debug(traceback.format_exc())
        return result

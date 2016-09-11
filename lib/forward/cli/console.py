#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import traceback

from forward import constants as C
from forward.args.host_option import HostOption
from forward.cli import CLI
from forward.utils.error import ForwardError
from forward.utils.log import set_loglevel_only, add_file_logger
from forward.utils.output import Output
from forward.utils.parse import get_ip_list
from forward.executor.task_queue_manager import TaskQueueManager

try:
    from __main__ import display
except ImportError:
    from forward.utils.display import Display
    display = Display()


class ConsoleCLI(CLI):
    '''
        code behind bin/forward* programs
    '''
    def __init__(self, args):
        ''' base init method for all command line programs '''
        super(ConsoleCLI, self).__init__(args)

    def parse(self):
        self.parser = CLI.base_parser(
            usage='usage: %prog [options]',
            script_opts=True,
            inventory_opts=True,
            log_opts=True,
            output_opts=True,
            connect_opts=True,
            run_opts=True
        )
        self.options, self.args = self.parser.parse_args(self.args[1:])
        return True

    def run(self):
        ''' use Runner lib to do SSH things '''
        op = self.options
        # set logger: may raise ForwardError if illegal args
        if op.logfile:
            self.logger = add_file_logger(
                level=op.loglevel, file=op.logfile,
                default=(not op.no_std_log))
        elif op.loglevel != C.DEFAULT_LOGLEVEL:
            self.logger = set_loglevel_only(level=op.loglevel)
        # get inventory of hosts
        inventory = []
        hosts = op.hosts
        try:
            hosts = eval(hosts) \
                if isinstance(hosts, str) else hosts
            hosts = get_ip_list(hosts)
        except:
            raise ForwardError('Bad Hosts.')
        if op.share:
            # get connection passwords for all
            conpass, actpass = CLI.ask_passwords(
                op.ask_pass, op.ask_activate)
            for h in hosts:
                host = HostOption(
                    ip=h, vender=op.vender, model=op.model, connect=op.connect,
                    conpass=conpass, actpass=actpass,
                    remote_port=op.remote_port, remote_user=op.remote_user)
                inventory.append(host)
        else:
            for h in hosts:
                display.display(u'[%s]' % h.ljust(C.DEFAULT_IP_JUST))
                # get connection passwords one by one
                conpass, actpass = CLI.ask_passwords(
                    op.ask_pass, op.ask_activate)
                host = HostOption(
                    ip=h, vender=op.vender, model=op.model, connect=op.connect,
                    conpass=conpass, actpass=actpass,
                    remote_port=op.remote_port, remote_user=op.remote_user)
                inventory.append(host)
        # now execute tasks
        self._tqm = None
        result = None
        try:
            self._tqm = TaskQueueManager(
                options=op,
                inventory=inventory,
                logger=self.logger)
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

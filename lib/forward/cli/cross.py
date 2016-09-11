#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import os
import traceback
from ConfigParser import ConfigParser as cfgparse

from forward import constants as C
from forward.args.play_option import PlayOption
from forward.args.host_option import HostOption
from forward.cli import CLI
from forward.utils.error import ForwardError
from forward.utils.boolean import boolean
from forward.utils.log import set_loglevel_only, add_file_logger
from forward.utils.output import Output
from forward.utils.parse import get_ip_list
from forward.executor.task_queue_manager import TaskQueueManager

try:
    from __main__ import display
except ImportError:
    from forward.utils.display import Display
    display = Display()


class CrossCLI(CLI):
    '''
        code behind bin/forward* programs
    '''
    _InventoryIllegal = 'Inventory Information Illegal'
    _PlayOptionIllegal = 'Play Option Illegal'

    _play_matrix = {
        'runtime': frozenset(['worker']),
        'script': frozenset(['script', 'args']),
        'logging': frozenset(['loglevel', 'logfile', 'no_std_log']),
        'output': frozenset(['out', 'outfile']),
        'connection': frozenset(['timeout'])}

    _inventory_list = frozenset([
        'hosts', 'vender', 'model', 'connect', 'remote_port',
        'remote_user', 'ask_pass', 'ask_activate', 'share'])

    def __init__(self, args):
        ''' init method for doc command line programs '''
        super(CrossCLI, self).__init__(args)

    def parse(self):
        self.parser = CLI.base_parser(
            usage='usage: %prog [options]',
            doc_opts=True)
        self.options, self.args = self.parser.parse_args(self.args[1:])
        return True

    def run(self):
        ''' use Runner lib to do SSH things '''
        # get play options: may raise ForwardError if bad option
        play_options = self.get_play_options()
        # set logger: may raise ForwardError if bad log option
        if play_options.logfile:
            self.logger = add_file_logger(
                level=play_options.loglevel,
                file=play_options.logfile,
                default=(not play_options.no_std_log))
        elif play_options.loglevel != C.DEFAULT_LOGLEVEL:
            self.logger = set_loglevel_only(level=play_options.loglevel)
        # get host inventory: may raise ForwardError if bad option
        inventory = self.get_inventory()
        # now execute tasks
        self._tqm = None
        result = None
        try:
            self._tqm = TaskQueueManager(
                options=play_options,
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
                Output.output(result, play_options.outfile, play_options.out)
            except ForwardError:
                raise
            except Exception as e:
                self.logger.error(repr(e))
                self.logger.debug(traceback.format_exc())
        return result

    def read_inventory_file(self):
        ''' get and check inventory information from file '''
        op = self.options
        if op.inventoryfile and os.path.isfile(op.inventoryfile):
            config = cfgparse()
            try:
                config.read(op.inventoryfile)
                groups = {}
                for x in config.sections():
                    if 'hosts' not in [k for k, w in config.items(x)]:
                        raise ForwardError("%s: No Hosts in Group %s." % (
                            self._InventoryOptionIllegal, x))
                    gp = {}
                    for k, w in config.items(x):
                        if k in self._inventory_list:
                            gp[k] = w
                        else:
                            raise ForwardError(
                                "%s: Unknown Item '%s' in Group '%s'." % (
                                    self._InventoryOptionIllegal, k, x))
                    groups[x] = gp
                return groups
            except Exception as e:
                raise ForwardError(
                    'Inventory Information File Illegal: %s.' % e)
        else:
            raise ForwardError('Inventory Information File Not Found.')

    def read_play_file(self):
        ''' get and check play options from file '''
        op = self.options
        if op.playfile and os.path.isfile(op.playfile):
                config = cfgparse()
                try:
                    config.read(op.playfile)
                    items = {}
                    for x in config.sections():
                        if x not in self._play_matrix.keys():
                            raise ForwardError("%s: Unknown Section '%s'." % (
                                self._PlayOptionIllegal, x))
                        for k, w in config.items(x):
                            if k not in self._play_matrix[x]:
                                raise ForwardError(
                                    "%s: Unknown Item '%s' in Section '%s'."
                                    % (self._PlayOptionIllegal, k, x))
                            items[k] = w
                    return items
                except Exception as e:
                    raise ForwardError('Play Option File Illegal: %s.' % e)
        else:
            raise ForwardError('Play Option File Not Found.')

    def get_inventory(self):
        ''' get a inventory list of hosts '''
        try:
            inventory = []
            gps = self.read_inventory_file()
            for n, g in gps.items():
                # get host list
                hosts = []
                try:
                    g['hosts'] = eval(g['hosts']) \
                        if isinstance(g['hosts'], str) else g['hosts']
                    hosts = get_ip_list(g['hosts'])
                    g.pop('hosts')
                except:
                    raise ForwardError("%s: Bad Hosts in Group '%s'." % (
                        self._InventoryOptionIllegal, n))
                # get password requirement
                ask_pass = C.DEFAULT_ASK_PASS
                ask_activate = C.DEFAULT_ASK_ACTIVATE
                share = C.DEFAULT_SHARE
                if 'ask_pass' in g.keys():
                    ask_pass = boolean(g['ask_pass'])
                    g.pop('ask_pass')
                if 'ask_activate' in g.keys():
                    ask_activate = boolean(g['ask_activate'])
                    g.pop('ask_activate')
                if 'share' in g.keys():
                    share = boolean(g['share'])
                    g.pop('share')
                # get host inventory
                display.display(
                    u'GROUP %s%s' % (n.upper(), '-' * (80 - len(n) - 6)))
                if share:
                    g['conpass'], g['actpass'] = CLI.ask_passwords(
                        ask_pass, ask_activate)
                    for h in hosts:
                        g['ip'] = h
                        host = HostOption(**g)
                        inventory.append(host)
                else:
                    for h in hosts:
                        g['ip'] = h
                        display.display(u'[%s]' % h.ljust(C.DEFAULT_IP_JUST))
                        g['conpass'], g['actpass'] = CLI.ask_passwords(
                            ask_pass, ask_activate)
                        host = HostOption(**g)
                        inventory.append(host)
            return inventory
        except ForwardError:
            raise

    def get_play_options(self):
        ''' get options of a play '''
        try:
            items = self.read_play_file()
            return PlayOption(**items)
        except ForwardError:
            raise

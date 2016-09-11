#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import operator
import optparse
import os
import re
import getpass

from forward import constants as C
from forward.release import __version__
from forward.utils.log import logger as DEFAULT_LOGGER

try:
    from __main__ import display
except ImportError:
    from forward.utils.display import Display
    display = Display()


class SortedOptParser(optparse.OptionParser):
    '''
        Optparser which sorts the options by opt before outputting --help
    '''
    def format_help(self, formatter=None, epilog=None):
        self.option_list.sort(key=operator.methodcaller('get_opt_string'))
        return optparse.OptionParser.format_help(self, formatter=None)


class CLI(object):
    '''
        code behind bin/forward* programs
    '''
    def __init__(self, args, callback=None):
        ''' base init method for all command line programs '''
        self.args = args
        self.options = None
        self.parser = None
        self.logger = DEFAULT_LOGGER
        self.callback = callback

    def parse(self):
        raise Exception("Need to implement!")

    def run(self):
        ''' use Runner lib to do SSH things '''
        raise Exception("Need to implement!")

    @staticmethod
    def ask_passwords(ask_pass, ask_activate):
        ''' prompt for connection passwords if needed '''
        conpass = None
        actpass = None
        try:
            if ask_pass:
                conpass = getpass.getpass(prompt="Connection password: ")
            if ask_activate:
                actpass = getpass.getpass(prompt="Activation password: ")
        except EOFError:
            pass
        return conpass, actpass

    @staticmethod
    def expand_tilde(option, opt, value, parser):
        setattr(parser.values, option.dest, os.path.expanduser(value))

    @staticmethod
    def base_parser(
            usage='', doc_opts=False, script_opts=False, log_opts=False,
            output_opts=False, inventory_opts=False, connect_opts=False,
            run_opts=False):
        ''' create an options parser for most forward scripts '''
        # base opts
        parser = SortedOptParser(usage, version=CLI.version('%prog'))
        if doc_opts:
            parser.add_option(
                '-C', '--play-opt-file', dest='playfile', type=str,
                default=None, metavar='FILE', action='callback',
                callback=CLI.expand_tilde,
                help='specify play option file path (default=None).')
            parser.add_option(
                '-I', '--inventory-opt-file', dest='inventoryfile', type=str,
                default=None, metavar='FILE', action='callback',
                callback=CLI.expand_tilde,
                help='specify inventory option file path (default=None).')
        if run_opts:
            run_group = optparse.OptionGroup(
                parser, "RunTime Options",
                "control as how to run forward task")
            run_group.add_option(
                '-w', '--worker', dest="worker", type=int,
                help='specify number of workers to use \
                      (same as number of processor cores by default).')
            parser.add_option_group(run_group)
        if script_opts:
            script_group = optparse.OptionGroup(
                parser, "Script Options",
                "control as how to find and execute script")
            script_group.add_option(
                '-s', '--script-file', dest="script", type=str,
                default=os.path.join(C.DEFAULT_HOME, C.DEFAULT_SCRIPT_PATH),
                metavar="FILE", action='callback', callback=CLI.expand_tilde,
                help='specify node script file path \
                      (default=%s).' % C.DEFAULT_SCRIPT_PATH)
            script_group.add_option(
                '-a', '--argument', dest="args", default={},
                type=str, help='specify script arguments (default={}).')
            parser.add_option_group(script_group)
        if log_opts:
            log_group = optparse.OptionGroup(
                parser, "Logging Options", "control as how and where to log")
            log_group.add_option(
                '--loglevel', dest='loglevel', default=C.DEFAULT_LOGLEVEL,
                type=str, help='specify loglevel (default=%s).'
                % C.DEFAULT_LOGLEVEL)
            log_group.add_option(
                '-l', '--log-file', dest='logfile', type=str,
                default=os.path.join(
                    C.DEFAULT_HOME, C.DEFAULT_FORWARD_LOG_PATH),
                metavar="FILE", action='callback', callback=CLI.expand_tilde,
                help='specify log out path (default=%s).'
                % C.DEFAULT_FORWARD_LOG_PATH)
            log_group.add_option(
                '--no-stdout-log', dest='no_std_log', default=False,
                action='store_true',
                help='disable standard output for logging, available only \
                      when "-l" used.')
            parser.add_option_group(log_group)
        if output_opts:
            output_group = optparse.OptionGroup(
                parser, "Output Options", "control as how and where to output")
            output_group.add_option(
                '-t', '--output-type', dest='out', default=C.DEFAULT_OUTPUT,
                type=str, help='specify way to output \
                                (default=%s).' % C.DEFAULT_OUTPUT)
            output_group.add_option(
                '-o', '--output-file', dest='outfile', type=str,
                default=os.path.join(C.DEFAULT_HOME, C.DEFAULT_OUT_PATH),
                metavar='FILE', action='callback', callback=CLI.expand_tilde,
                help='specify result output path \
                      (default=%s).' % C.DEFAULT_OUT_PATH)
            parser.add_option_group(output_group)
        if inventory_opts:
            inventory_group = optparse.OptionGroup(
                parser, "Inventory Options",
                "control as which host to connect to")
            inventory_group.add_option(
                '-i', '--hosts', dest='hosts',
                default=[list(C.LOCALHOST)[2]],
                help='specify a group of remote hosts \
                      (default=[\'%s\']).' % list(C.LOCALHOST)[2])
            inventory_group.add_option(
                '-v', '--device-vender', dest='vender',
                default=list(C.DEFAULT_DEVICE_VENDERS)[0], type=str,
                help='specify remote device type \
                      (default=%s).' % list(C.DEFAULT_DEVICE_VENDERS)[0])
            inventory_group.add_option(
                '-m', '--device-model', dest='model',
                default=list(C.DEFAULT_DEVICE_MODELS)[0], type=str,
                help='specify remote device model \
                      (default=%s).' % list(C.DEFAULT_DEVICE_MODELS)[0])
            parser.add_option_group(inventory_group)
        if connect_opts:
            connect_group = optparse.OptionGroup(
                parser, "Connection Options",
                "control as whom and how to connect to hosts")
            connect_group.add_option(
                '--connect', dest='connect',
                type=str, default=C.DEFAULT_TRANSPORT,
                help="connection protocol to use \
                      (default=%s)" % C.DEFAULT_TRANSPORT)
            connect_group.add_option(
                '-P', '--ask-pass', default=C.DEFAULT_ASK_PASS,
                dest='ask_pass', action='store_true',
                help='ask for connection password')
            connect_group.add_option(
                '-A', '--ask-activate', default=C.DEFAULT_ASK_ACTIVATE,
                dest='ask_activate', action='store_true',
                help='ask for activation password')
            connect_group.add_option(
                '-S', '--share', default=C.DEFAULT_SHARE,
                dest='share', action='store_true',
                help='share both connection and activation passwords or not')
            connect_group.add_option(
                '-p', '--port', default=C.DEFAULT_REMOTE_PORT,
                dest='remote_port', type=int,
                help='connect to this port \
                      (default=%s)' % C.DEFAULT_REMOTE_PORT)
            connect_group.add_option(
                '-u', '--user', default=C.DEFAULT_REMOTE_USER,
                dest='remote_user', type=str,
                help='connect as this user \
                      (default=%s)' % C.DEFAULT_REMOTE_USER)
            connect_group.add_option(
                '-T', '--timeout', dest="timeout",
                default=C.DEFAULT_TIMEOUT, type=int,
                help='specify connection timeout \
                      (default=%s(s)).' % C.DEFAULT_TIMEOUT)
            parser.add_option_group(connect_group)
        return parser

    @staticmethod
    def get_option_groups(option_groups):
        ''' get option groups (and their types, str/int/float/bool)'''
        gp = option_groups
        pattern = re.compile(r'true|false')
        no_bools = {
            x.title.split(' ')[0].lower(): {
                y.__dict__['dest']: y.__dict__['type']
                for y in x.option_list if not re.search(
                    pattern, y.__dict__['action'])} for x in gp}
        bools = {
            x.title.split(' ')[0].lower(): {
                y.__dict__['dest'] for y in x.option_list if re.search(
                    pattern, y.__dict__['action'])} for x in gp}
        return no_bools, bools

    @staticmethod
    def version(prog):
        ''' return forward version '''
        result = "{0} {1}".format(prog, __version__)
        return result

    @staticmethod
    def version_info():
        ''' return full forward version info '''
        forward_version_string = __version__
        forward_version = forward_version_string.split()[0]
        forward_versions = forward_version.split('.')
        for counter in range(len(forward_versions)):
            if forward_versions[counter] == "":
                forward_versions[counter] = 0
            try:
                forward_versions[counter] = int(forward_versions[counter])
            except:
                pass
        if len(forward_versions) < 3:
            for counter in range(len(forward_versions), 3):
                forward_versions.append(0)
        return {'string': forward_version_string.strip(),
                'full': forward_version,
                'major': forward_versions[0],
                'minor': forward_versions[1],
                'revision': forward_versions[2]}

    def get_opt(self, k, defval=""):
        ''' returns an option from an Optparse values instance '''
        try:
            data = getattr(self.options, k)
            return data
        except:
            return defval

#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import os
import sys
import tempfile
from ConfigParser import ConfigParser

from forward.utils.error import ForwardError
from forward.utils.path import makedirs_safe
from forward.utils.boolean import boolean
from forward.utils.parse import unquote


def shell_expand(path, expand_relative_paths=False):
    '''
        shell_expand is needed as os.path.expanduser does not work
        when path is None, which is the default for Forward_PRIVATE_KEY_FILE
    '''
    if path:
        path = os.path.expanduser(os.path.expandvars(path))
        if expand_relative_paths and not path.startswith('/'):
            # paths are always 'relative' to the config?
            if 'CONFIG_FILE' in globals():
                CFGDIR = os.path.dirname(CONFIG_FILE)
                path = os.path.join(CFGDIR, path)
            path = os.path.abspath(path)
    return path


def get_config(
        p, section, key, env_var, default,
        isbool=False, isint=False, isfloat=False, islist=False,
        isnone=False, ispath=False, ispathlist=False, istmppath=False,
        expand_relative_paths=False):
    ''' return a configuration variable with casting '''
    value = _get_config(p, section, key, env_var, default)
    if isbool:
        value = boolean(value)
    if value:
        if isint:
            value = int(value)
        elif isfloat:
            value = float(value)
        elif islist:
            if isinstance(value, str):
                value = [x.strip() for x in value.split(',')]
        elif isnone:
            if value == "None":
                value = None
        elif ispath:
            value = shell_expand(value)
        elif istmppath:
            value = shell_expand(value)
            if not os.path.exists(value):
                makedirs_safe(value, 0o700)
            prefix = 'forward-local-%s' % os.getpid()
            value = tempfile.mkdtemp(prefix=prefix, dir=value)
        elif ispathlist:
            if isinstance(value, str):
                value = [shell_expand(
                    x, expand_relative_paths=expand_relative_paths)
                    for x in value.split(os.pathsep)]
        elif isinstance(value, str):
            value = unquote(value)
    return value


def _get_config(p, section, key, env_var, default):
    ''' helper function for get_config '''
    if env_var is not None:
        value = os.environ.get(env_var, None)
        if value is not None:
            return value
    if p is not None:
        try:
            return p.get(section, key, raw=True)
        except:
            return default
    return default


def load_config_file():
    ''' Load Config File order(first found is used):
        ENV, CWD, CWD/.conf, /apps/conf/forward
    '''
    p = ConfigParser()

    path0 = os.getenv("FORWARD_CONFIG", None)
    if path0 is not None:
        path0 = os.path.expanduser(path0)
        if os.path.isdir(path0):
            path0 += '/forward.cfg'
    path1 = os.path.join(
        os.path.dirname(sys.path[0]), 'conf/forward.cfg')

    for path in [path0, path1]:
        if path is not None and os.path.exists(path):
            try:
                p.read(path)
            except ConfigParser.Error as e:
                raise ForwardError(
                    "Error reading configuration file: \n{0}".format(e))
            return p, path
    return None, ''

p, CONFIG_FILE = load_config_file()

# sections in config file
DEFAULTS = 'defaults'

# runtime
DEFAULT_WORKER = get_config(
    p, DEFAULTS, 'worker', 'FORWARD_WORKER', 4, isint=True)

# connection
DEFAULT_TRANSPORT = get_config(
    p, DEFAULTS, 'transport', 'FORWARD_TRANSPORT', 'local')
DEFAULT_REMOTE_USER = get_config(
    p, DEFAULTS, 'remote_user', 'FORWARD_REMOTE_USER', None)
DEFAULT_ASK_PASS = get_config(
    p, DEFAULTS, 'ask_pass', 'FORWARD_ASK_PASS', False, isbool=True)
DEFAULT_ASK_ACTIVATE = get_config(
    p, DEFAULTS, 'ask_activate', 'FORWARD_ASK_ACTIVATE', False, isbool=True)
DEFAULT_REMOTE_PORT = get_config(
    p, DEFAULTS, 'remote_port', 'FORWARD_REMOTE_PORT', 22, isint=True)
DEFAULT_TIMEOUT = get_config(
    p, DEFAULTS, 'timeout', 'FORWARD_TIMEOUT', 30, isint=True)

# tmp
DEFAULT_LOCAL_TMP = get_config(
    p, DEFAULTS, 'local_tmp', 'FORWARD_LOCAL_TEMP', '.tmp', istmppath=True)

# log
DEFAULT_LOG_PATH = get_config(
    p, DEFAULTS, 'log_path', 'FORWARD_LOG_PATH', 'log', ispath=True)
DEFAULT_FORWARD_LOG_PATH = get_config(
    p, DEFAULTS, 'forward_log_path', 'FORWARD_LOG_FILE_PATH',
    '%s/forward.log' % DEFAULT_LOG_PATH, ispath=True)
DEFAULT_LOGLEVEL = get_config(
    p, DEFAULTS, 'loglevel', 'FORWARD_LOGLEVEL', 'INFO')
DEFAULT_LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s %(message)s'
DEFAULT_DATE_FORMAT = '%y%m%d %H:%M:%S'

# configuration
DEFAULT_CONF_PATH = get_config(
    p, DEFAULTS, 'conf_path', 'FORWARD_CONF_PATH', 'conf', ispath=True)

# node configuration
DEFAULT_NODE_PATH = get_config(
    p, DEFAULTS, 'node_path', 'FORWARD_NODE_PATH',
    '%s/node' % DEFAULT_CONF_PATH, ispath=True)
# 1. custom configuration
DEFAULT_CUSTOM_CONF_PATH = get_config(
    p, DEFAULTS, 'custom_path', 'FORWARD_CUSTOM_CONF_PATH',
    '%s/custom.cfg' % DEFAULT_NODE_PATH, ispath=True)
# 2. script
DEFAULT_SCRIPT_PATH = get_config(
    p, DEFAULTS, 'script_path', 'FORWARD_SCRIPT_PATH',
    '%s/script.py' % DEFAULT_NODE_PATH, ispath=True)

# data
DEFAULT_DATA_PATH = get_config(
    p, DEFAULTS, 'data_path', 'FORWARD_DATA_PATH', 'data', ispath=True)

# output
DEFAULT_OUTPUT = get_config(
    p, DEFAULTS, 'output', 'FORWARD_OUTPUT', 'txt')
DEFAULT_OUT_PATH = get_config(
    p, DEFAULTS, 'out_path', 'FORWARD_OUTPUT_PATH',
    '%s/out.%s' % (DEFAULT_DATA_PATH, DEFAULT_OUTPUT), ispath=True)
DEFAULT_OUTPUT_TYPES = frozenset(['stdout', 'txt', 'xls'])

# action
DEFAULT_EXECUTABLE = get_config(
    p, DEFAULTS, 'executable', 'FORWARD_EXECUTABLE', '/bin/sh')
DEFAULT_DEBUG = get_config(
    p, DEFAULTS, 'debug', 'FORWARD_DEBUG', False, isbool=True)

# non-configurable things
LOCALHOST = frozenset(['127.0.0.1', 'localhost', '::1'])
DEFAULT_DEVICE_VENDERS = frozenset(['unknown'])
DEFAULT_DEVICE_MODELS = frozenset(['unknown'])

# current
DEFAULT_HOME = get_config(
    p, DEFAULTS, 'forward_path', 'FORWARD_HOME', '', ispath=True)

#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import os
import sys
import getpass
import logging
from logging.handlers import TimedRotatingFileHandler

from forward import constants as C
from forward.utils.boolean import boolean
from forward.utils.error import ForwardError

formatter = logging.Formatter(C.DEFAULT_LOG_FORMAT, C.DEFAULT_DATE_FORMAT)

default_handler = logging.StreamHandler(sys.__stdout__)
default_handler.formatter = formatter
mypid = str(os.getpid())
user = getpass.getuser()
logger = logging.getLogger("p=%s u=%s |" % (mypid, user))
logger.addHandler(default_handler)
logger.setLevel(eval('logging.%s' % C.DEFAULT_LOGLEVEL))


def check_loglevel(level):
    ''' check log level legitimacy '''
    if isinstance(level, str):
        if level.isalpha():
            level = level.upper()
            if level in logging._levelNames:
                level = logging._levelNames[level]
        elif level.isdigit():
            level = int(level)
    if not (isinstance(level, int) and level in logging._levelNames):
        raise ForwardError('Unknown Loglevel.')
    return level


def set_loglevel_only(level=C.DEFAULT_LOGLEVEL):
    ''' set log level only '''
    try:
        level = check_loglevel(level)
        logger.setLevel(level)
    except:
        raise
    return logger


def add_file_logger(
        level=C.DEFAULT_LOGLEVEL,
        file=C.DEFAULT_FORWARD_LOG_PATH, default=1):
    ''' add a file logger '''
    # check file legitimacy
    if file and ((os.path.exists(file) and os.access(file, os.W_OK)) or
                 os.access(os.path.dirname(file), os.W_OK)):
        # add log file handler
        handler = TimedRotatingFileHandler(
            filename=file, when='d', backupCount=1)
        # set log format
        handler.formatter = formatter
        logger.addHandler(handler)
        if not boolean(default):
            logger.removeHandler(default_handler)
        # set log level
        level = check_loglevel(level)
        logger.setLevel(level)
    else:
        raise ForwardError('Log File Illegal.')
    return logger

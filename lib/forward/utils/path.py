#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import os
from errno import EEXIST

from forward.utils.error import ForwardError

__all__ = ['purepath', 'makedirs_safe']


def purepath(path):
    """
        returns a path that is free of symlinks, environment
        variables, relative path traversals and symbols (~)

        example:
        '$HOME/../../var/mail' becomes '/var/spool/mail'
    """
    return os.path.normpath(
        os.path.realpath(os.path.expanduser(
            os.path.expandvars(path))))


def makedirs_safe(path, mode=None):
    """ safe way to create dirs in muliprocess/thread environments """
    path = purepath(path)
    if not os.path.exists(path):
        try:
            if mode:
                os.makedirs(path, mode)
            else:
                os.makedirs(path)
        except OSError as e:
            if e.errno != EEXIST:
                raise ForwardError(
                    'Unable to create local directories(%s): %s'
                    % (path, str(e)))

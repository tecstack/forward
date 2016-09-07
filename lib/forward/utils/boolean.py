#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

BOOL_TRUE = frozenset(["true", "t", "y", "1", "yes", "on"])


def boolean(value):
    if value is None:
        return False
    val = str(value)
    if val.lower() in BOOL_TRUE:
        return True
    else:
        return False

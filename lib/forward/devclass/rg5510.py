#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for rg5510.
Author: Cheung Kei-Chuen
"""
from forward.devclass.baseRuijie import BASERUIJIE


class RG5510(BASERUIJIE):
    """This is a manufacturer of ruijie, so it is integrated with BASERUIJIE library.
    """
    def __init__(self, *args, **kws):
        """Since the device's host prompt is different from BASESSHV2,
        the basic prompt for the device is overwritten here.
        """
        BASERUIJIE.__init__(self, *args, **kws)
        self.basePrompt = r'(>|#.*#|\]|\$|\)) *$'

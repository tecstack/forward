#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for f1000.
Author: Cheung Kei-chuen
"""
from forward.devclass.baseDepp import BASEDEPP


class F1000(BASEDEPP):
    """This is a manufacturer of depp, it is integrated with BASEDEPP library.
    """
    def getMore(self, bufferData):
        """Automatically get more echo infos by sending a blank symbol
        """
        # if check buffer data has 'more' flag, at last line.
        # if re.search(self.moreFlag, bufferData.split('\n')[-1]):
        # can't used to \n and ' \r' ,because product enter character
        self.shell.send(' ')
